"""Synthetic protocol regressions; these are not device or visual evidence."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from hmigbot_ios.core import MigrationError, read_json
from hmigbot_ios152 import native_visual as V
from hmigbot_ios152 import xcode_ui as X
from evaluations.test_native_verify38 import FixtureObserver, source_tree
from evaluations import test_xcode_ui as protocol


class ScopedObserver(FixtureObserver):
    def __init__(self):super().__init__();self.captures=[];self.actions=[]
    def capture(self,directory,**kwargs):
        self.captures.append((str(directory),dict(kwargs)))
        raw=super().capture(directory);scope=kwargs.get('scope','app')
        raw['observation']['scope']=scope
        if scope=='springboard':raw['observation']['bundle_id']='com.apple.springboard'
        return raw
    def command(self,operation,arguments):
        self.actions.append((operation,copy.deepcopy(arguments)))
        return super().command(operation,arguments)


class ObserverBudget45(unittest.TestCase):
    def test_queued_budgets_and_explicit_override(self):
        cases=[('launch',None,None,180),('tap',{'scope':'springboard'},None,180),
               ('tap',{},None,60),('long_press',{'scope':'springboard'},None,120),
               ('find',{'scope':'springboard'},None,60),('launch',{},7,7),
               ('tap',{'scope':'springboard'},9,9)]
        for operation,arguments,explicit,expected in cases:
            with self.subTest(operation=operation,arguments=arguments,explicit=explicit),tempfile.TemporaryDirectory() as tmp:
                session,queue=protocol.ObserverProtocolTests().session(Path(tmp));requests=[]
                original=X._atomic_json
                def respond(path,value):
                    original(path,value)
                    if Path(path).parent==queue/'commands':
                        requests.append(value)
                        original(queue/'results'/Path(path).name,{'id':value['id'],'session':value['session'],
                                                               'ok':True,'result':{}})
                with patch.object(X,'_atomic_json',side_effect=respond):
                    self.assertTrue(session.command(operation,arguments,timeout=explicit)['ok'])
                self.assertEqual(expected,requests[0]['timeout_seconds'])
                self.assertEqual(arguments or {},requests[0]['arguments'])


class SweepScope45(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory(prefix='native-scope45-test-');self.addCleanup(temp.cleanup)
        self.root=Path(temp.name);self.tree=source_tree();self.page=self.tree['pages'][0]
        self.plan={'checks':{}}
        # Use the indexed contract so duplicate original names retain both indices.
        self.plan={'functional_checks_sha256':V.functional_snapshot(self.page),'checks':[
            {'check_idx':i,'feature_path':c['feature_path'],'check_name':c['name'],
             'actions':[{'operation':'tap','arguments':{'selector':{'identifier':key}},'safety':'normal'}]}
            for i,(c,key) in enumerate(zip(self.page['functional_checks'],('A','B')))]}
    def run_sweep(self,observer):
        output=self.root/'out'
        result=V.sweep(observer,self.tree,'Neutral',self.plan,output,project=self.root)
        return result,read_json(output/'run_meta.json')
    def test_app_default_retains_public_arguments_paths_indices_and_result(self):
        observer=ScopedObserver();result,meta=self.run_sweep(observer)
        self.assertEqual([{}, {}, {}, {}, {}],[kw for _,kw in observer.captures])
        self.assertEqual(['before','check-before-0','check-0','check-before-1','check-1'],
                         [Path(p).name for p,_ in observer.captures])
        self.assertEqual([('tap',{'selector':{'identifier':'A'}}),('tap',{'selector':{'identifier':'B'}})],
                         [(op,args) for op,args in observer.actions if op=='tap'])
        self.assertEqual([(0,'Form>A','ok'),(1,'Form>B','ok')],
                         [(c['idx'],c['feature_path'],c['status']) for c in meta['checks']])
        self.assertFalse(result['escaped']);self.assertTrue(all('scope' not in c['before_capture'] for c in meta['checks']))
    def test_system_scope_is_inherited_for_all_captures_and_actions(self):
        self.page['native_identity']['scope']='springboard'
        observer=ScopedObserver();result,meta=self.run_sweep(observer)
        self.assertTrue(all(kw=={'scope':'springboard'} for _,kw in observer.captures))
        self.assertTrue(all(args['scope']=='springboard' for _,args in observer.actions))
        self.assertTrue(all(c['after_capture']['scope']=='springboard' for c in meta['checks']))
        self.assertFalse(result['judged']);self.assertFalse(result['escaped'])
    def test_explicit_after_scope_observes_destination_without_assuming_arrival(self):
        self.page['native_identity']['scope']='springboard'
        self.plan['checks'][0]['after_scope']='app'
        observer=ScopedObserver();result,meta=self.run_sweep(observer)
        self.assertEqual([{'scope':'springboard'},{'scope':'springboard'},{}],[kw for _,kw in observer.captures])
        self.assertTrue(result['escaped']);self.assertFalse(meta['checks'][0]['after_identity']['arrived'])
        self.assertEqual('deferred_outcome',meta['checks'][1]['status'])
        self.assertFalse(meta['checks'][0]['judged'])
    def test_explicit_action_scope_overrides_inheritance(self):
        self.page['native_identity']['scope']='springboard'
        self.plan['checks'][0]['actions'][0]['arguments']['scope']='app'
        observer=ScopedObserver();self.run_sweep(observer)
        taps=[args for op,args in observer.actions if op=='tap']
        self.assertEqual(['app','springboard'],[args['scope'] for args in taps])
    def test_invalid_scope_fails_before_any_capture_or_action(self):
        for location in ('page','after','action'):
            with self.subTest(location=location):
                tree=copy.deepcopy(self.tree);plan=copy.deepcopy(self.plan)
                if location=='page':tree['pages'][0]['native_identity']['scope']='unknown'
                elif location=='after':plan['checks'][0]['after_scope']='unknown'
                else:plan['checks'][0]['actions'][0]['arguments']['scope']='unknown'
                observer=ScopedObserver()
                with self.assertRaisesRegex(MigrationError,'scope must'):
                    V.sweep(observer,tree,'Neutral',plan,self.root/location,project=self.root)
                self.assertEqual([],observer.captures);self.assertEqual([],observer.actions)


if __name__=='__main__':unittest.main()
