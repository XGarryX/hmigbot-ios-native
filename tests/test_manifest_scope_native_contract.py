"""Replayed product declaration relevance never replaces dependency inventory."""
import copy
import json
from pathlib import Path
import os
import unittest
import tempfile
import subprocess

import test_project_scope as scope_fixture
from hmigbot_ios.core import MigrationError, write_json
from hmigbot_ios.ios_facts import extract, refresh, validate_graph
from hmigbot_ios.manifest_scope import issue_dispositions


class ManifestScopeTests(unittest.TestCase):
    _write=scope_fixture.ProjectScopeTests._write

    def setUp(self):
        scope_fixture.ProjectScopeTests.setUp(self)
        target=tempfile.TemporaryDirectory(prefix='scope target ',dir=self.source.parent)
        self.addCleanup(target.cleanup);self.target=Path(target.name)
        (self.source/'Package.swift').write_text('// swift-tools-version: 5.9\nimport PackageDescription\nlet package = Package(name: "Independent")')

    def graph(self): return extract(self.source,self.variant)

    def assert_blocking(self, expected):
        graph=self.graph();rows=[r for r in issue_dispositions(graph) if r['issue'].get('code')=='executable_manifest_not_evaluated']
        self.assertEqual(len(rows),1)
        self.assertTrue(rows[0]['blocking'],rows)
        self.assertIn(expected,rows[0]['scope_reason'])
        self.assertEqual(graph['dependencies']['complete_graph'],False)
        print(json.dumps({'probe':self._testMethodName,'blocking':True,'scope_reason':rows[0]['scope_reason']}))

    def configure_include(self, text='#include? "Optional.flags"'):
        (self.source/'Config').mkdir(exist_ok=True)
        self.objects['CONFIGFILE']={'isa':'PBXFileReference','sourceTree':'SOURCE_ROOT','path':'Config/Base.xcconfig'}
        self.objects['PR']['baseConfigurationReference']='CONFIGFILE'
        (self.source/'Config/Base.xcconfig').write_text(text,encoding='utf-8');self._write()

    def test_independent_package_is_visible_while_shared_product_source_remains(self):
        graph=self.graph();row=issue_dispositions(graph)[0]
        self.assertFalse(row['blocking']);self.assertEqual(graph['issues'][0]['code'],'executable_manifest_not_evaluated')
        self.assertIn('Library.swift',graph['variant']['source_files'])
        self.assertFalse(graph['dependencies']['complete_graph']);self.assertEqual(graph['capabilities']['effective_build'],'unresolved')
        self.assertNotIn('manifest_evaluations',graph['dependencies'])
        self.assertEqual(graph['dependency_scope']['manifests'][0]['status'],'independent_of_declared_product')

    def test_unknown_config_search_link_include_module_and_per_file_flags_block(self):
        for key,value in [('HEADER_SEARCH_PATHS','../pkg'),('OTHER_LDFLAGS','-lPackage'),('SWIFT_INCLUDE_PATHS','Modules'),('SWIFT_OBJC_BRIDGING_HEADER','Bridge.h'),('UNKNOWN_SETTING','x')]:
            with self.subTest(key=key):
                self.objects['AR']['buildSettings']={key:value};self._write();self.assert_blocking(key)
        self.objects['AR']['buildSettings']={};self.objects['AB0']['settings']={'COMPILER_FLAGS':'-I Package'};self._write();self.assert_blocking('per-file')

    def test_optional_include_absence_is_explicit_and_appearance_replays_without_snapshot_suffix(self):
        self.configure_include('#include? "../.build/Optional.flags"');target=self.target
        graph=refresh(target,self.source,self.variant)
        files=graph['dependency_scope']['basis']['configuration_files']
        self.assertIn({'path':'.build/Optional.flags','exists':False,'sha256':None},files)
        old_snapshot=graph['source_sha256']
        (self.source/'.build').mkdir()
        (self.source/'.build/Optional.flags').write_text('OTHER_SWIFT_FLAGS = -I HiddenPackage')
        self.assertEqual(self.graph()['source_sha256'],old_snapshot)
        with self.assertRaisesRegex(MigrationError,'stale|edited'):validate_graph(self.source,target)
        self.assert_blocking('OTHER_SWIFT_FLAGS')

    def test_nested_includes_keep_every_file_hash_and_unknown_bridge_blocks(self):
        self.configure_include('#include "One.flags"')
        (self.source/'Config/One.flags').write_text('#include? "Two.flags"')
        (self.source/'Config/Two.flags').write_text('SWIFT_VERSION = 5.0')
        graph=self.graph();self.assertFalse(issue_dispositions(graph)[0]['blocking'])
        files=graph['dependency_scope']['basis']['configuration_files'];self.assertEqual(len(files),3);self.assertTrue(all(x['sha256'] for x in files))
        (self.source/'Config/Two.flags').write_text('LIBRARY_SEARCH_PATHS = ../Package');self.assert_blocking('LIBRARY_SEARCH_PATHS')

    def test_macro_conditional_continuation_required_missing_and_escape_includes_block(self):
        for text in ['#include "$(SRCROOT)/Some.flags"','#if DEBUG','#include "Missing.flags"','#include "../../Outside.flags"','OTHER_LDFLAGS[sdk=iphoneos*] = -lPkg','PRODUCT_NAME = Demo\\\n OTHER_LDFLAGS = -lPkg']:
            with self.subTest(text=text):
                self.configure_include(text);self.assertTrue(issue_dispositions(self.graph())[0]['blocking'])

    def test_absolute_include_is_not_reinterpreted_as_a_local_path(self):
        self.configure_include('#include "'+(self.source/'Config/Base.xcconfig').as_posix()+'"')
        self.assert_blocking('configuration path')

    def test_external_symlink_include_is_not_trusted(self):
        outside=tempfile.TemporaryDirectory(prefix='outside config ',dir=self.source.parent)
        self.addCleanup(outside.cleanup);folder=Path(outside.name)
        (folder/'Escape.flags').write_text('SWIFT_VERSION = 5.0')
        self.configure_include('#include "../.build/External/Escape.flags"')
        (self.source/'.build').mkdir();link=self.source/'.build/External'
        try:os.symlink(folder,link,target_is_directory=True)
        except OSError as exc:
            if os.name!='nt':self.skipTest('Actual symlink unavailable: '+str(exc))
            made=subprocess.run(['cmd','/d','/c','mklink','/J',str(link),str(folder)],capture_output=True)
            self.assertEqual(made.returncode,0,made.stderr)
            print(json.dumps({'probe':self._testMethodName,'actual_reparse_kind':'Windows directory junction','returncode':made.returncode}))
        self.addCleanup(lambda: link.unlink() if link.is_symlink() else os.rmdir(link))
        self.assert_blocking('escapes')

    def test_real_package_product_and_product_ref_are_rejected_by_project_authority(self):
        self.objects['A']['packageProductDependencies']=['PackageProduct'];self._write()
        with self.assertRaisesRegex(MigrationError,'package'):self.graph()
        self.objects['A'].pop('packageProductDependencies');self.objects['AB0']['productRef']='PackageProduct';self._write()
        with self.assertRaisesRegex(MigrationError,'package'):self.graph()

    def test_script_rule_external_target_and_project_references_remain_blocked(self):
        self.objects['SCRIPT']={'isa':'PBXShellScriptBuildPhase','files':[],'shellScript':'swift package build'}
        self.objects['A']['buildPhases'].append('SCRIPT');self._write()
        with self.assertRaisesRegex(MigrationError,'script'):self.graph()
        self.objects['A']['buildPhases'].remove('SCRIPT');self.objects['A']['buildRules']=['RULE'];self._write()
        with self.assertRaisesRegex(MigrationError,'rules'):self.graph()
        self.objects['A'].pop('buildRules');self.objects['PROXY']['containerPortal']='External';self._write()
        with self.assertRaisesRegex(MigrationError,'Cross-project'):self.graph()
        self.objects['PROXY']['containerPortal']='P';self.objects['P']['packageReferences']=['Package'];self._write();self.assert_blocking('package references')
        self.objects['P'].pop('packageReferences');self.objects['P']['projectReferences']=['External'];self._write();self.assert_blocking('external project')

    def test_non_sdk_conditional_import_and_implicit_header_remain_unknown(self):
        (self.source/'App.swift').write_text('#if canImport(ExternalPackage)\nimport ExternalPackage\n#endif')
        self.assert_blocking('non-SDK')
        (self.source/'App.swift').write_text('import Foundation');(self.source/'Bridge.h').write_text('// header')
        self.assert_blocking('headers')

    def test_core_missing_or_unowned_cannot_be_excluded(self):
        (self.source/'Library.swift').unlink()
        with self.assertRaisesRegex(MigrationError,'does not exist'):self.graph()
        (self.source/'Library.swift').write_text('// core');self.objects['LS']['files']=[];self._write()
        with self.assertRaisesRegex(MigrationError,'unowned'):self.graph()

    def test_facts_and_classification_cannot_be_hand_edited_or_stale(self):
        target=self.target;graph=refresh(target,self.source,self.variant)
        for field in ['manifests','basis_sha256','basis']:
            forged=copy.deepcopy(graph);forged['dependency_scope'][field]=[]
            write_json(target/'spec/baseline/ios-facts.json',forged)
            with self.subTest(field=field),self.assertRaisesRegex(MigrationError,'stale|edited'):validate_graph(self.source,target)
        write_json(target/'spec/baseline/ios-facts.json',graph)
        (self.source/'Package.swift').write_text('// changed manifest')
        with self.assertRaisesRegex(MigrationError,'Stale|stale|edited'):validate_graph(self.source,target)

    def test_repository_and_selected_build_do_not_receive_project_exemption(self):
        graph=extract(self.source);self.assertNotIn('dependency_scope',graph);self.assertTrue(issue_dispositions(graph)[0]['blocking'])
        graph=self.graph();graph['variant']['scope']='selected-build';self.assertTrue(issue_dispositions(graph)[0]['blocking'])
        with self.assertRaisesRegex(MigrationError,'captured evidence'):extract(self.source,{'scope':'selected-build','source_files':['App.swift']})

    def test_caller_cannot_supply_forged_classification_or_member_list(self):
        for field,value in [('dependency_scope',{}),('source_files',['App.swift'])]:
            with self.subTest(field=field),self.assertRaises(MigrationError):extract(self.source,{**self.variant,field:value})
