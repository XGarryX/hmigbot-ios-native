"""Neutral permission-policy and public-CLI tests; no real SDK/device probes."""
from contextlib import redirect_stdout
from io import StringIO
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from hmigbot_ios152 import env_doctor as doctor

INTERNET='ohos.permission.INTERNET'


class PermissionPolicy(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='permission policy ')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.data={'app':{'signingConfigs':[],'products':[{'name':'default'}]},'modules':[]}

    def module(self,name='entry',permissions=(),kind='entry',products=('default',)):
        p=self.root/name/'src/main/module.json5';p.parent.mkdir(parents=True)
        p.write_text(json.dumps({'module':{'name':name,'type':kind,'requestPermissions':[{'name':v} for v in permissions]}}))
        self.data['modules'].append({'name':name,'srcPath':name,'targets':[{'name':'default','applyToProducts':list(products)}]})
        self.save()
        return p

    def save(self):
        (self.root/'build-profile.json5').write_text(json.dumps(self.data))

    def rows(self,mode=None):
        return doctor.project_checks(self.root,network_mode=mode)

    def permissions(self,mode=None):
        return next(v for v in self.rows(mode) if v['id']=='permissions')

    def test_default_unknown_missing_permission_warns(self):
        self.module()
        row=self.permissions()
        self.assertEqual(row['status'],'WARN')
        self.assertEqual(row['network_mode'],'unknown')
        self.assertEqual(row['network_mode_source'],'default')
        self.assertTrue(row['needs_confirmation'])

    def test_unknown_declared_permission_still_requires_applicability(self):
        self.module(permissions=[INTERNET])
        self.assertEqual(self.permissions()['status'],'WARN')

    def test_required_missing_permission_fails(self):
        self.module()
        self.assertEqual(self.permissions('required')['status'],'FAIL')

    def test_required_declared_permission_passes_without_network_info(self):
        self.module(permissions=[INTERNET])
        row=self.permissions('required')
        self.assertEqual(row['status'],'PASS')
        self.assertFalse(row['modules'][0]['network_info_declared'])

    def test_not_required_is_explicit_nonapplicability(self):
        self.module()
        row=self.permissions('not-required')
        self.assertEqual(row['status'],'PASS')
        self.assertFalse(row['applicable'])
        self.assertFalse(row['offline_verified'])
        self.assertEqual(row['network_mode_source'],'cli')

    def test_not_required_does_not_remove_existing_permission(self):
        p=self.module(permissions=[INTERNET]);before=p.read_bytes()
        row=self.permissions('not-required')
        self.assertEqual(row['status'],'PASS')
        self.assertTrue(row['modules'][0]['internet_declared'])
        self.assertEqual(before,p.read_bytes())

    def test_same_product_haps_share_declared_permission(self):
        self.module('entry',[INTERNET]);self.module('detail',kind='feature')
        row=self.permissions('required')
        self.assertEqual(row['status'],'PASS')
        self.assertEqual(row['provided_by'],['entry'])

    def test_feature_hap_can_provide_permission_for_same_product(self):
        self.module('entry');self.module('detail',[INTERNET],kind='feature')
        row=self.permissions('required')
        self.assertEqual(row['status'],'PASS')
        self.assertEqual(row['modules'][0]['provided_by'],['detail'])

    def test_all_haps_declared_pass_even_when_membership_unknown(self):
        self.module('entry',[INTERNET]);self.module('detail',[INTERNET],kind='feature')
        del self.data['modules'][1]['targets'];self.save()
        row=self.permissions('required')
        self.assertEqual(row['status'],'PASS')
        self.assertEqual(row['membership_unknown'],['detail'])

    def test_network_info_alone_is_not_internet(self):
        self.module(permissions=['ohos.permission.GET_NETWORK_INFO'])
        self.assertEqual(self.permissions('required')['status'],'FAIL')

    def test_all_haps_missing_permission_fail(self):
        self.module('entry');self.module('detail',kind='feature')
        self.assertEqual(self.permissions('required')['status'],'FAIL')

    def test_different_products_cannot_borrow_each_others_permission(self):
        self.data['app']['products']=[{'name':'local'},{'name':'remote'}]
        self.module('entry',[INTERNET],products=['local']);self.module('detail',kind='feature',products=['remote'])
        row=self.permissions('required')
        self.assertEqual(row['status'],'WARN')
        self.assertEqual(row['products']['remote']['provided_by'],[])
        self.assertEqual(row['products']['remote']['haps'],['detail'])
        self.assertTrue(row['needs_confirmation'])
        self.assertEqual(row['uncovered_products'],['remote'])
        self.assertIn('remote',doctor.markdown({'checks':[row],'verdict':row['status']}))

    def test_unknown_membership_is_not_a_config_failure(self):
        self.module('entry',[INTERNET]);self.module('detail',kind='feature')
        self.data['modules'][1]['targets']='unknown';self.save()
        rows=self.rows('required')
        self.assertFalse(any(x['id']=='project_config' and x['status']=='FAIL' for x in rows))
        self.assertEqual(next(x for x in rows if x['id']=='permissions')['status'],'WARN')

    def test_missing_targets_are_not_guessed(self):
        self.module('entry',[INTERNET]);self.module('detail',kind='feature')
        del self.data['modules'][1]['targets'];self.save()
        self.assertEqual(self.permissions('required')['status'],'WARN')

    def test_library_declaration_leaves_dependency_merge_unverified(self):
        self.module('entry');self.module('library',[INTERNET],kind='har')
        row=self.permissions('required')
        self.assertEqual(row['status'],'WARN')
        self.assertEqual(row['provided_by'],[])
        self.assertEqual(row['library_declarations'],['library'])
        self.assertFalse(row['dependency_permissions_verified'])
        self.assertTrue(row['needs_confirmation'])

    def test_hap_and_library_declarations_do_not_mix_providers(self):
        self.module('entry',[INTERNET]);self.module('library',[INTERNET],kind='har')
        row=self.permissions('required')
        self.assertEqual(row['status'],'PASS')
        self.assertEqual(row['provided_by'],['entry'])
        self.assertEqual(row['products']['default']['provided_by'],['entry'])
        self.assertEqual(row['library_declarations'],['library'])

    def test_library_declaration_does_not_override_explicit_mode(self):
        self.module('entry');self.module('library',[INTERNET],kind='har')
        for mode,status in [('unknown','WARN'),('not-required','PASS')]:
            with self.subTest(mode=mode):
                row=self.permissions(mode)
                self.assertEqual(row['status'],status)
                self.assertEqual(row['provided_by'],[])
                self.assertEqual(row['library_declarations'],['library'])
                self.assertFalse(row['offline_verified'])

    def test_library_without_internet_does_not_hide_missing_permission(self):
        self.module('entry');self.module('library',kind='har')
        self.assertEqual(self.permissions('required')['status'],'FAIL')

    def test_shared_library_declaration_does_not_prove_hap_permission(self):
        self.module('entry');self.module('library',[INTERNET],kind='shared')
        row=self.permissions('required')
        self.assertEqual(row['status'],'WARN')
        self.assertEqual(row['provided_by'],[])

    def test_permission_names_are_case_sensitive(self):
        self.module(permissions=['ohos.permission.internet'])
        self.assertEqual(self.permissions('required')['status'],'FAIL')

    def test_bad_library_permission_structure_still_fails_all_modes(self):
        self.module('entry');p=self.module('library',kind='har')
        p.write_text('{module:{type:"har",requestPermissions:[{}]}}')
        self.assert_all_modes_fail()

    def test_library_only_keeps_warning(self):
        self.module('library',kind='har')
        self.assertEqual(self.permissions('required')['status'],'WARN')

    def assert_all_modes_fail(self):
        for mode in (None,'unknown','required','not-required'):
            with self.subTest(mode=mode):
                self.assertEqual(doctor.worst(self.rows(mode)),'FAIL')

    def test_missing_manifest_still_fails_all_modes(self):
        p=self.module();p.unlink()
        self.assert_all_modes_fail()

    def test_broken_json5_still_fails_all_modes(self):
        p=self.module();p.write_text('{ broken')
        self.assert_all_modes_fail()

    def test_bad_permission_structure_still_fails_all_modes(self):
        p=self.module()
        for permissions in ({},['ohos.permission.INTERNET'],[{'name':''}],[{'name':4}]):
            with self.subTest(permissions=permissions):
                p.write_text(json.dumps({'module':{'type':'entry','requestPermissions':permissions}}))
                self.assert_all_modes_fail()

    def test_missing_signing_material_still_fails_all_modes(self):
        self.module();self.data['app']['signingConfigs']=[{'name':'test','material':{'storeFile':'absent.p12'}}];self.save()
        self.assert_all_modes_fail()

    def test_bad_module_list_still_fails_all_modes(self):
        self.data['modules']={};self.save()
        self.assert_all_modes_fail()

    def fake_tools(self):
        sdk=self.root/'controlled tool fixtures'
        tools={'tools/hvigor/bin/hvigorw':'6.26.8','tools/ohpm/bin/ohpm':'26.0.0.630',
               'jbr/bin/java':'openjdk version "25.0.2"','tools/node/bin/node':'v24.14.1',
               'sdk/default/openharmony/toolchains/hdc':''}
        for rel,output in tools.items():
            p=sdk/rel;p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text('#!/bin/sh\nprintf \'%s\\n\' \''+output+'\'\n');p.chmod(0o755)
        p=self.root/'.migbot/config.json';p.parent.mkdir()
        p.write_text(json.dumps({'source_platform':'ios','deveco':str(sdk),'hdc':str(sdk/'sdk/default/openharmony/toolchains/hdc')}))

    def cli(self,*args):
        env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
        env.pop('DEVECO_SDK_HOME',None)
        return subprocess.run([sys.executable,'-B',str(ROOT/'skills/hmos-env-doctor/scripts/env_doctor.py'),'--project',str(self.root),*args],
                              cwd=self.root,capture_output=True,text=True,timeout=30,env=env)

    def test_public_cli_modes_exit_codes_and_read_only(self):
        self.module();self.fake_tools()
        before={str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        for args,code,mode,source in [([],0,'unknown','default'),(['--network-mode','required'],1,'required','cli'),
                                     (['--network-mode','not-required'],0,'not-required','cli')]:
            result=self.cli(*args,'--json')
            self.assertEqual(result.returncode,code,result.stdout+result.stderr)
            data=json.loads(result.stdout)
            self.assertEqual(data['network_mode'],mode)
            self.assertEqual(data['network_mode_source'],source)
            self.assertFalse(data['behavior_verified'])
            self.assertEqual(result.stderr,'')
        after={str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before,after)

    def test_public_cli_markdown_and_invalid_mode(self):
        self.module();self.fake_tools()
        md=self.root/'report.md';result=self.cli('--network-mode','not-required','--markdown',str(md))
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('网络权限',md.read_text())
        self.assertEqual(self.cli('--network-mode','invalid').returncode,2)

    def test_mode_without_project_records_scope_without_external_probe(self):
        with patch.object(doctor,'installation',return_value=({},doctor.check('deveco','fixture','PASS','controlled'))), \
             patch.object(doctor,'inspect_tools',return_value=doctor.check('toolchain','fixture','PASS','controlled')), \
             patch.object(doctor,'devices',return_value=doctor.check('devices','fixture','WARN','controlled')):
            out=StringIO()
            with redirect_stdout(out):code=doctor.main(['--network-mode','not-required','--json'])
            self.assertEqual(code,0)
            self.assertEqual(json.loads(out.getvalue())['network_mode'],'not-required')


if __name__=='__main__':unittest.main()
