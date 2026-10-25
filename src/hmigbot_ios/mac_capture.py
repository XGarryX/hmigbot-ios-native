"""Capture real Xcode queries/builds without changing their evidence meaning."""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shlex
import subprocess

from .apple_tools import environment, run
from .core import MigrationError, digest, json_bytes, safe_child, snapshot


def capture_release(source, project_path, scheme, output, *, build=False):
    source, output = Path(source).resolve(), Path(output).resolve()
    project = safe_child(source, project_path)
    if project.name == 'project.pbxproj': project = project.parent
    if project.suffix != '.xcodeproj' or not project.is_dir():
        raise MigrationError('Capture requires an explicit .xcodeproj')
    if output.exists() or output.is_relative_to(source) or source.is_relative_to(output):
        raise MigrationError('Use a new capture directory outside the source tree')
    info, env = environment()
    before = snapshot(source)
    output.mkdir(parents=True)
    records = []
    def capture(identifier, argv, stdout, *, json_output=True):
        started = datetime.now(timezone.utc).isoformat()
        timed_out = False
        try:
            result = subprocess.run(argv, cwd=source, env=env, capture_output=True, timeout=900 if not json_output else 180, shell=False)
            code, body, error = result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired as exc:
            code, body, error, timed_out = None, exc.stdout or b'', exc.stderr or b'', True
        stderr = identifier + '.stderr.log'
        (output / stdout).write_bytes(body); (output / stderr).write_bytes(error)
        records.append({'id': identifier, 'argv': argv, 'cwd': str(source), 'started_at': started,
            'ended_at': datetime.now(timezone.utc).isoformat(), 'environment': {'DEVELOPER_DIR': info['developer_dir']},
            'exit_code': code, 'timed_out': timed_out, 'stdout': stdout, 'stderr': stderr,
            'stdout_sha256': digest(body), 'stderr_sha256': digest(error)})
        (output / 'command-execution-records.json').write_bytes(json_bytes({'commands': records, 'toolchain': info}))
        if code != 0 or timed_out:
            raise MigrationError('Xcode capture failed; diagnostics retained in ' + str(output))
        if not json_output: return body
        try: return json.loads(body)
        except ValueError as exc: raise MigrationError('Xcode did not return JSON') from exc
    listed = capture('project-list', ['/usr/bin/xcodebuild', '-list', '-json', '-project', str(project)], 'project-list.json')
    if scheme not in listed.get('project', {}).get('schemes', []):
        raise MigrationError('Selected scheme is absent from the Xcode project: ' + scheme)
    # A scheme settings query only returns its primary target. -alltargets is an
    # official, explicit project query and supplies embedded products as well.
    settings = capture('release-build-settings', ['/usr/bin/xcodebuild', '-project', str(project), '-alltargets',
        '-configuration', 'Release', '-sdk', 'iphoneos', '-showBuildSettings', '-json'], 'release-build-settings.json')
    if not isinstance(settings, list) or not settings:
        raise MigrationError('Xcode returned no target settings')
    if build:
        derived=output.parent / (output.name + '-derived-data')
        result_bundle=output.parent / (output.name + '-build.xcresult')
        if derived.exists() or result_bundle.exists():
            raise MigrationError('Use fresh derived-data and result-bundle paths for compiler evidence')
        build_log=capture('release-source-build', ['/usr/bin/xcodebuild','-project',str(project),'-scheme',scheme,
            '-configuration','Release','-sdk','iphoneos','-destination','generic/platform=iOS',
            '-derivedDataPath',str(derived),'-resultBundlePath',str(result_bundle),'CODE_SIGNING_ALLOWED=NO','build'],
            'source-build.stdout.log',json_output=False)
        arguments=swift_driver_arguments(build_log.decode('utf-8',errors='replace'))
        if not arguments: raise MigrationError('Successful build did not expose Swift compiler argument evidence')
        (output/'compiler-arguments.json').write_bytes(json_bytes({'commands':arguments}))
    after = snapshot(source)
    if after['sha256'] != before['sha256']:
        raise MigrationError('Source changed during the Xcode capture; use a fresh capture')
    (output / 'source-files.json').write_bytes(json_bytes({'files': [
        {'path': f['path'], 'kind': 'file', 'sha256': f['sha256'], 'size_bytes': f['bytes']}
        for f in before['files']]}))
    (output / 'capture.json').write_bytes(json_bytes({'schema_version': 1, 'source_sha256': before['sha256'],
        'selected_scheme': scheme, 'settings_scope': 'all targets in the explicitly selected project',
        'build_performed': build, 'behavior_verified': False, 'toolchain': info}))
    (output / 'bundle-files.sha256').write_text(''.join(
        digest(p.read_bytes()) + '  ' + p.relative_to(output).as_posix() + '\n'
        for p in sorted(output.rglob('*')) if p.is_file()), encoding='utf-8')
    return {'status': 'captured', 'output': str(output), 'targets': [t['target'] for t in settings],
            'source_sha256': before['sha256'], 'build_performed': build}


def swift_driver_arguments(text):
    """Decode Xcode's printed argument arrays; this does not parse Swift syntax."""
    commands=[]
    for line in text.splitlines():
        if not line.lstrip().startswith('builtin-SwiftDriver -- '): continue
        args=shlex.split(line.strip())[2:]
        if '-module-name' not in args or '-target' not in args or '-sdk' not in args:
            raise MigrationError('Incomplete SwiftDriver command in Xcode output')
        # File-list arguments contain source paths, not hidden compiler options.
        for arg in args:
            if arg.startswith('@') and not arg.endswith('.SwiftFileList'):
                raise MigrationError('Opaque Swift response-file arguments require an explicit compiler capture')
        definitions=[]
        for index,arg in enumerate(args):
            if arg=='-D':
                if index+1>=len(args):raise MigrationError('Missing SwiftDriver -D value')
                definitions.append(args[index+1])
            elif arg.startswith('-D'):definitions.append(arg[2:])
        commands.append({'module':args[args.index('-module-name')+1], 'argv':args,
            'custom_conditions':sorted(set(definitions)), 'target':args[args.index('-target')+1],
            'sdk':args[args.index('-sdk')+1], 'language_mode':args[args.index('-swift-version')+1] if '-swift-version' in args else None})
    return commands


def verify_unset_flags(bundle, settings, expected_conditions):
    """Keep the missing-flag refusal unless real Release compiler inputs agree."""
    bundle=Path(bundle)
    records=json.loads((bundle/'command-execution-records.json').read_text())['commands']
    builds=[r for r in records if r.get('id')=='release-source-build' and r.get('exit_code')==0 and r.get('timed_out') is False]
    if len(builds)!=1:raise MigrationError('Unset xcconfig Swift flags require capture-release --build compiler evidence')
    record=builds[0]
    args=record['argv']
    for flag,value in [('-configuration','Release'),('-sdk','iphoneos')]:
        if args.count(flag)!=1 or args[args.index(flag)+1]!=value:
            raise MigrationError('Compiler argument evidence is not from an iOS Release build')
    body=(bundle/record['stdout']).read_bytes()
    if digest(body)!=record['stdout_sha256']:raise MigrationError('Compiler build output hash differs')
    commands=swift_driver_arguments(body.decode('utf-8',errors='replace'))
    module=settings.get('PRODUCT_MODULE_NAME') or settings.get('PRODUCT_NAME')
    relevant=[c for c in commands if c['module']==module]
    if not relevant:raise MigrationError('No captured compiler command for target module: '+str(module))
    for command in relevant:
        if command['custom_conditions']!=expected_conditions or command['sdk']!=settings.get('SDKROOT'):
            raise MigrationError('Xcode settings and actual Swift compiler conditions/SDK disagree')
        if command['language_mode']!=settings.get('SWIFT_VERSION','').split('.')[0]:
            raise MigrationError('Xcode settings and actual Swift compiler language mode disagree')
        architectures=shlex.split(settings.get('ARCHS',''))
        expected_target=(architectures[0]+'-apple-ios'+settings.get('IPHONEOS_DEPLOYMENT_TARGET','')) if len(architectures)==1 else None
        if command['target']!=expected_target:
            raise MigrationError('Xcode settings and actual Swift compiler target disagree')
    return {'status':'compiler_arguments_match','module':module,'commands':len(relevant),
            'custom_conditions':expected_conditions,'evidence':'source-build.stdout.log',
            'compiler_arguments':[c['argv'] for c in relevant]}


def compiler_context(settings, custom_conditions, declared_modules, actual_arguments=None):
    info, env = environment()
    if settings.get('CONFIGURATION') != 'Release' or settings.get('PLATFORM_NAME') != 'iphoneos':
        raise MigrationError('Compiler context must be captured for iOS device Release')
    sdk = settings.get('SDKROOT')
    if not isinstance(sdk, str) or not Path(sdk).is_absolute() or not Path(sdk).is_dir():
        raise MigrationError('Xcode did not resolve the target SDK path')
    architectures = shlex.split(settings.get('ARCHS', ''))
    if len(architectures) != 1:
        raise MigrationError('Separate compiler contexts are required for multiple target architectures')
    deployment = settings.get('IPHONEOS_DEPLOYMENT_TARGET', '')
    if not re.fullmatch(r'\d+(?:\.\d+){0,2}', deployment):
        raise MigrationError('Missing iOS deployment target in Xcode settings')
    mode = settings.get('SWIFT_VERSION', '').split('.')[0]
    if mode not in {'4', '5', '6'}:
        raise MigrationError('Unsupported captured Swift language mode')
    args = ['-target', architectures[0] + '-apple-ios' + deployment, '-sdk', sdk, '-swift-version', mode]
    args += [flag for condition in custom_conditions for flag in ('-D', condition)]
    for key, flag in [('FRAMEWORK_SEARCH_PATHS', '-F'), ('SWIFT_INCLUDE_PATHS', '-I')]:
        value = settings.get(key, '')
        if not isinstance(value, str) or '$' in value:
            raise MigrationError('Unresolved Xcode search paths: ' + key)
        for path in shlex.split(value): args += [flag, path]
    flags = shlex.split(settings.get('OTHER_SWIFT_FLAGS', '') or '')
    index = 0
    while index < len(flags):
        flag = flags[index]
        if flag == '-D': index += 2; continue
        if flag.startswith('-D'): index += 1; continue
        if flag in {'-enable-upcoming-feature', '-enable-experimental-feature', '-I', '-F', '-Fsystem', '-Xcc'}:
            if index + 1 >= len(flags): raise MigrationError('Missing value for Swift flag: ' + flag)
            args += flags[index:index+2]; index += 2; continue
        if flag in {'-enable-testing', '-enable-library-evolution', '-warn-concurrency'} or flag.startswith('-strict-concurrency='):
            args.append(flag); index += 1; continue
        raise MigrationError('Capture the actual compiler invocation for unsupported Swift flag: ' + flag)
    if settings.get('SWIFT_OBJC_BRIDGING_HEADER'):
        raise MigrationError('A bridging header requires a captured compiler invocation, not guessed Clang arguments')
    if settings.get('OTHER_CFLAGS') or settings.get('OTHER_CPLUSPLUSFLAGS'):
        raise MigrationError('Custom Clang context requires a captured compiler invocation adapter')
    # Xcode can inject language features even when OTHER_SWIFT_FLAGS is unset.
    # Preserve those official arguments and the build's Swift module search paths.
    for command in actual_arguments or []:
        for flag, expected in [('-target', args[1]), ('-sdk', sdk), ('-swift-version', mode)]:
            if command.count(flag)!=1 or command[command.index(flag)+1:command.index(flag)+2]!=[expected]:
                raise MigrationError('Captured compiler context disagrees with resolved Xcode settings: '+flag)
        index=0
        while index<len(command):
            flag=command[index]
            if flag in {'-enable-upcoming-feature','-enable-experimental-feature','-I','-F','-Fsystem'}:
                if index+1>=len(command):raise MigrationError('Incomplete captured compiler option')
                pair=command[index:index+2]
                if not any(args[p:p+2]==pair for p in range(len(args)-1)):args+=pair
                index+=2;continue
            if flag in {'-enable-bare-slash-regex'} and flag not in args:args.append(flag)
            index+=1
    target_info = json.loads(run([info['swiftc'], '-print-target-info', *args], env=env).stdout)
    version = re.search(r'Swift version (\d+(?:\.\d+)+)', target_info.get('compilerVersion', ''))
    if not version or target_info.get('target', {}).get('triple') != args[1]:
        raise MigrationError('Cannot verify the selected compiler and target')
    return {'swiftc': info['swiftc'], 'arguments': args,
            'compiler_version': [int(p) for p in version[1].split('.')],
            'pointer_bit_width': target_info['target']['pointerWidthInBits'],
            'declared_modules': sorted(set(declared_modules)), 'target_info': target_info, 'toolchain': info,
            'arguments_origin':'resolved-xcode-settings-cross-checked-with-swift-driver' if actual_arguments else 'resolved-xcode-settings-profile'}
