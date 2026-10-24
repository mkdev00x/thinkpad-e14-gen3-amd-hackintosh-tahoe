#!/usr/bin/env python3
"""Build reprodutível com CLT, sem executar scripts upstream ou instalar a kext."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'source/dependencies'
BASE = ROOT / 'source/NootedRed'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sources(project):
    data = json.loads(subprocess.check_output(['/usr/bin/plutil', '-convert', 'json', '-o', '-',
                      str(project / 'NootedRed.xcodeproj/project.pbxproj')]))
    objects = data['objects']
    paths = {}
    def walk(key, parent):
        entry = objects[key]
        parent = project if entry.get('sourceTree') == 'SOURCE_ROOT' else parent
        path = parent / entry.get('path', '')
        if entry['isa'] == 'PBXGroup':
            for child in entry.get('children', []):
                walk(child, path)
        elif entry['isa'] == 'PBXFileReference':
            paths[key] = path
    walk(objects[data['rootObject']]['mainGroup'], project)
    phase = [v for v in objects.values() if v.get('isa') == 'PBXSourcesBuildPhase']
    if len(phase) != 1:
        raise RuntimeError('Fase de fontes inesperada.')
    result = []
    for item in phase[0]['files']:
        path = paths[objects[item]['fileRef']]
        if path.suffix not in ('.cpp', '.c', '.s', '.S'):
            continue
        if not path.is_file():
            path = WORK / path.relative_to(project)
        if not path.is_file():
            raise RuntimeError('Fonte ausente: ' + str(path))
        result.append(path)
    return result


def main():
    mode = 'gl'
    if len(sys.argv) != 1:
        raise RuntimeError('Esta receita compila somente a versão local GL0.9.2, sem argumentos.')
    project, version = BASE, '0.9.2'
    versions = json.loads((WORK/'versions.json').read_text())
    for name, expected in [('Lilu','0515f40b7f2a096adc85e832a4c6104fbd07f936'),
                           ('MacKernelSDK','7af1933c27aefcbdf4809ee44478829aad30f9c1')]:
        metadata = versions[name]
        if metadata['commit'] != expected:
            raise RuntimeError('Revisão divergente: '+name)
        for relative, expected_sha in metadata['files'].items():
            if digest(WORK/name/relative) != expected_sha:
                raise RuntimeError('Dependência alterada: '+name+'/'+relative)
    output = ROOT / 'build/nootedred' / datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    output.mkdir(parents=True)
    env = dict(os.environ, CLANG_MODULE_CACHE_PATH=str(output / 'module-cache'))
    compiler = '/Library/Developer/CommandLineTools/usr/bin/clang++'
    flags = ['-std=c++23', '-arch', 'x86_64', '-mmacosx-version-min=10.14', '-mkernel', '-fapple-kext',
             '-fno-rtti', '-fno-exceptions', '-fno-builtin', '-fno-asynchronous-unwind-tables', '-fno-common',
             '-mno-red-zone', '-fvisibility=hidden', '-O2', '-Wall', '-Wextra',
             '-DKERNEL', '-DKERNEL_PRIVATE', '-DDRIVER_PRIVATE', '-DPRODUCT_NAME=NootedRed', '-DMODULE_VERSION=' + version,
             '-I', str(WORK / 'MacKernelSDK/Headers'), '-I', str(WORK / 'Lilu/Lilu'), '-I', str(project / 'NootedRed')]
    inputs = sources(project)
    kmod = output / 'kmod.c'
    kmod.write_text('''#include <mach/kmod.h>
extern kern_return_t _start(kmod_info_t *, void *);
extern kern_return_t _stop(kmod_info_t *, void *);
extern kern_return_t NootedRed_kern_start(kmod_info_t *, void *);
extern kern_return_t NootedRed_kern_stop(kmod_info_t *, void *);
__attribute__((visibility("default")))
KMOD_EXPLICIT_DECL(org.ChefKiss.NootedRed, "VERSION", _start, _stop)
__attribute__((visibility("default"))) kmod_start_func_t *_realmain = NootedRed_kern_start;
__attribute__((visibility("default"))) kmod_stop_func_t *_antimain = NootedRed_kern_stop;
'''.replace('VERSION', version))
    inputs.append(kmod)
    commands, objects = [], []
    state = {'state':'building', 'mode':mode, 'version':version, 'output':str(output), 'source_hashes':{}}
    try:
        for index, path in enumerate(inputs):
            obj = output / ('%02d-' % index + path.stem + '.o')
            command = [compiler, *flags, '-x', 'c' if path.suffix == '.c' else 'c++', '-c', str(path), '-o', str(obj)]
            if path.suffix == '.c':
                command.remove('-std=c++23')
            commands.append(command)
            state['source_hashes'][str(path)] = digest(path)
            print('Compilando', path.name, flush=True)
            with (output / (obj.stem + '.log')).open('wb') as log:
                subprocess.run(command, cwd=project, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
            objects.append(obj)
        bundle = output / 'NootedRed.kext'
        binary = bundle / 'Contents/MacOS/NootedRed'
        binary.parent.mkdir(parents=True)
        command = ['/usr/bin/ld', '-kext', '-arch', 'x86_64', '-static', '-undefined', 'dynamic_lookup',
                   '-no_data_const', '-o', str(binary), *map(str, objects),
                   str(WORK / 'MacKernelSDK/Library/x86_64/libkmod.a')]
        commands.append(command)
        with (output / 'link.log').open('wb') as log:
            subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
        info = plistlib.loads((project / 'NootedRed/Info.plist').read_bytes())
        replacements = {'EXECUTABLE_NAME':'NootedRed', 'PRODUCT_BUNDLE_IDENTIFIER':'org.ChefKiss.NootedRed',
                        'PRODUCT_NAME':'NootedRed', 'PRODUCT_NAME:rfc1034identifier':'NootedRed', 'MODULE_VERSION':version}
        def expand(value):
            if isinstance(value, dict):
                return {expand(k):expand(v) for k,v in value.items()}
            if isinstance(value, list):
                return [expand(v) for v in value]
            if isinstance(value, str):
                for k,v in replacements.items():
                    value = value.replace('$(' + k + ')', v)
                if '$(' in value:
                    raise RuntimeError('Variável plist não expandida: ' + value)
            return value
        info = expand(info)
        if mode == 'patched':
            info['NRedLocalBuild'] = 'page-signing-revision-1-unvalidated'
        if mode == 'gl':
            info['NRedLocalBuild'] = 'gl-dualquad-revision-1-unvalidated'
        (bundle / 'Contents/Info.plist').write_bytes(plistlib.dumps(info, sort_keys=False))
        subprocess.run(['/usr/bin/codesign','--force','--sign','-','--timestamp=none',str(bundle)],check=True)
        subprocess.run(['/usr/bin/codesign','--verify','--strict',str(bundle)],check=True)
        state.update(state='built_not_installed', binary_sha256=digest(binary), bundle=str(bundle))
        print('Compilado:', bundle, flush=True)
    except Exception as error:
        state.update(state='failed', error=str(error))
        raise
    finally:
        (output / 'comandos.json').write_text(json.dumps(commands, indent=2) + '\n')
        (output / 'estado.json').write_text(json.dumps(state, indent=2) + '\n')
        print('Resultado:', output / 'estado.json', flush=True)


if __name__ == '__main__':
    main()
