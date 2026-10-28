"""Isolated native-host protocol fixtures; never live enrollment/upgrade evidence.

The log is generated fixture data in a TemporaryDirectory. No production project,
real host log, environment thread identity or installed runtime is modified.
"""
from pathlib import Path
import contextlib,copy,hashlib,io,json,os,shlex,shutil,sys,tempfile,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from hmigbot_ios152 import join_attempt as j,join_scope as scope,join_upgrade as u
ORIGIN=ROOT/'evaluations/fixtures/join-upgrade-origin'

# Small actual installer interface for protocol fixtures. Production delegates to
# its unchanged real manage_install.py; these fixtures avoid copying 2GB per case.
MINI_INSTALLER='''from pathlib import Path
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1]
def checksum(p):return hashlib.sha256(p.read_bytes() if isinstance(p,Path) else p).hexdigest()
def payload():
 files={}
 for folder in ['src','scripts','skills','.codex-plugin']:
  for path in (ROOT/folder).rglob('*'):
   if path.is_file() and '__pycache__' not in path.parts:files['.agents/hmigbot-runtime/'+path.relative_to(ROOT).as_posix()]=path
 return files
def manage(project,mode):
 project=Path(project);files=payload();files['.codex/config.toml']=b'[features]\\nmulti_agent = true\\n\\n[agents]\\nmax_threads = 4\\nmax_depth = 2\\n';oldpath=project/'.hmigbot-ios/install.json';old=json.loads(oldpath.read_text()) if oldpath.exists() else None
 for name,data in files.items():
  p=project/name;p.parent.mkdir(parents=True,exist_ok=True)
  if isinstance(data,Path):shutil.copy2(data,p)
  else:p.write_bytes(data)
 for name in set(old['files'] if old else {})-set(files):(project/name).unlink()
 agent=b'fixture-owned AGENTS\\n';(project/'AGENTS.md').write_bytes(agent)
 record={'schema_version':1,'owner':'hmigbot-ios','version':json.loads((ROOT/'.codex-plugin/plugin.json').read_text())['version'],'files':{n:checksum(d) for n,d in files.items()},'agent_installed_sha256':checksum(agent)}
 oldpath.parent.mkdir(parents=True,exist_ok=True);oldpath.write_text(json.dumps(record,ensure_ascii=False,indent=2))
 return {'status':'upgraded' if old else 'installed','version':record['version']}
'''

def put(path,data):path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data if isinstance(data,bytes) else data.encode())
def dump(path,value):put(path,u.encoded(value))
def row(payload,kind='response_item'):return json.dumps({'type':kind,'payload':payload},separators=(',',':')).encode()+b'\n'

class NeutralUpgrade(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='join-upgrade-fixture-');self.addCleanup(self.temp.cleanup);self.base=Path(self.temp.name).resolve();self.project=self.base/'project';self.project.mkdir();self.origin=self.package('origin','1.5.2-ios.27',True);self.candidate=self.package('candidate',j.__version__);self.intermediate=self.package('middle','1.5.2-ios.30');self.native=self.base/'fixture-only.jsonl';self.raw=b'';self.counter=0
  self.thread=os.environ.get('CODEX_THREAD_ID');self.assertTrue(self.thread,'tests require actual process thread identity without overrides')
  self.raw+=row({'id':self.thread,'agent_path':'/root'},'session_meta');self.idle()
  self.backup=self.base/'approved-empty';self.backup.mkdir();put(self.backup/'Shell.txt','original shell\n');put(self.project/'Shell.txt','original shell\n')
  self.pristine=self.base/'pristine.json';dump(self.pristine,{'workspace':str(self.project),'backup':str(self.backup),'files':j.files(self.backup)})
  self.archive=self.base/'previous-failed';self.archive.mkdir();put(self.archive/'retained-failure.txt','fixture failure remains\n');self.archive_manifest=self.base/'previous-failed.json';dump(self.archive_manifest,{'workspace':str(self.project),'archive':str(self.archive),'files':j.files(self.archive)})
  u.installer(self.origin).manage(self.project,'install');installed=u.installed(self.project)
  self.history=self.base/'origin.history.jsonl';self.history.write_bytes(self.raw)
  with contextlib.redirect_stdout(io.StringIO()):audit,code=scope.audit([scope.read_trace(self.native,raw=self.raw,history=True)])
  self.history_audit=self.base/'origin.history-audit.json';dump(self.history_audit,audit)
  self.receipt=self.base/'origin.receipt.json';self.rc={'schema':j.RECEIPT,'project':str(self.project),'tool_version':'1.5.2-ios.27','tool_sha256':u.package_inventory(self.origin)['tool_sha256'],'previous_attempt':None,'installed_manifest':installed['manifest'],'pristine_manifest':str(self.pristine),'pristine_manifest_sha256':j.digest(self.pristine),'archive_manifest':str(self.archive_manifest),'archive_manifest_sha256':j.digest(self.archive_manifest),'post_install_files':j.expected_tree(self.project,j.load(self.pristine),installed['manifest']),'thread_id':self.thread,'rollout':str(self.native),'history':{'snapshot':str(self.history),'sha256':j.sha(self.raw),'bytes':len(self.raw),'audit':str(self.history_audit),'audit_sha256':j.digest(self.history_audit),'exit_code':code}};dump(self.receipt,self.rc)
  script=self.project/j._SCRIPT_MEMBERS[1];token='a'*32;cid='fixture-begin';cmd=shlex.join(['python3','-B',str(script),'begin','--project',str(self.project),'--receipt',str(self.receipt),'--receipt-sha256',j.digest(self.receipt),'--enrollment',token]);self.call(cid,'exec_command',{'cmd':cmd,'yield_time_ms':30000,'max_output_tokens':6500,'tty':False})
  self.state={'schema':j.SCHEMA,'tool_version':self.rc['tool_version'],'tool_sha256':self.rc['tool_sha256'],'attempt_id':token,'project':str(self.project),'thread_id':self.thread,'rollout':str(self.native),'enrollment_call_id':cid,'start_bytes':len(self.raw),'prefix_sha256':j.sha(self.raw),'receipt':str(self.receipt),'receipt_sha256':j.digest(self.receipt),'failed_enrollments':[],'history_summary':{'exit_code':code,'unjoined':audit['totals']['unjoined'],'audit':str(self.history_audit),'audit_sha256':j.digest(self.history_audit)}};dump(self.project/j.STATE,self.state);self.state_bytes=(self.project/j.STATE).read_bytes();self.output(cid,{'exit_code':0,'output':json.dumps({'status':'created','attempt_id':token,'prefix_sha256':self.state['prefix_sha256']})})
  u.installer(self.intermediate).manage(self.project,'install');put(self.project/'spec/execution/keep.txt','existing execute product\n');self.idle()
  self.root_patch=patch.object(j,'__file__',str(self.candidate/'src/hmigbot_ios152/join_attempt.py'));self.root_patch.start();self.addCleanup(self.root_patch.stop)
  self.rollout_patch=patch.object(scope,'current_rollout',return_value=self.native);self.rollout_patch.start();self.addCleanup(self.rollout_patch.stop)
 def package(self,name,version,original=False):
  root=self.base/name
  source=ORIGIN if original else ROOT
  names=list(u.MEMBERS)+['src/hmigbot_ios/__init__.py','src/hmigbot_ios152/__init__.py']
  if not original:names.append('src/hmigbot_ios152/join_upgrade.py')
  for n in names:put(root/n,(source/n).read_bytes())
  put(root/'src/hmigbot_ios/__init__.py','__version__ = '+repr(version)+'\n');dump(root/'.codex-plugin/plugin.json',{'version':version});put(root/'scripts/manage_install.py',MINI_INSTALLER)
  return root
 def call(self,cid,name,args):self.raw+=row({'type':'function_call','name':name,'call_id':cid,'arguments':json.dumps(args)});self.native.write_bytes(self.raw)
 def output(self,cid,value):self.raw+=row({'type':'function_call_output','call_id':cid,'output':json.dumps(value)});self.native.write_bytes(self.raw)
 def idle(self,agents=None):
  self.counter+=1;cid='fixture-list-'+str(self.counter);self.call(cid,'list_agents',{});self.output(cid,{'agents':agents or []})
 def request(self,nonce=None,candidate=None):
  candidate=candidate or self.candidate;nonce=nonce or str(self.counter%9+1)*32;manifest=self.base/('package-'+nonce+'.json');dump(manifest,u.package_inventory(candidate));evidence=self.base/('upgrade-'+nonce);argv=['python3','-B',str(candidate/'scripts/join_attempt.py'),'upgrade','--project',str(self.project),'--origin-package',str(self.origin),'--package-manifest',str(manifest),'--package-sha256',u.digest(manifest),'--evidence-root',str(evidence),'--upgrade',nonce];cid='fixture-upgrade-'+nonce
  self.call(cid,'exec_command',{'cmd':shlex.join(argv),'yield_time_ms':30000,'max_output_tokens':6500,'tty':False});return cid,(self.project,self.origin,manifest,u.digest(manifest),str(evidence),nonce)
 def upgrade(self,nonce=None):
  cid,args=self.request(nonce);result=u.upgrade(*args);self.assertEqual((self.project/j.STATE).read_bytes(),self.state_bytes);return cid,result
 def finish(self,cid,result,exit=0):self.output(cid,{'exit_code':exit,'output':json.dumps(result)})
 def validate(self):return j.validate_state(self.project,self.native,self.raw,self.state)
 def test_complete_upgrade_keeps_origin_scope_and_can_remove_distribution(self):
  cid,result=self.upgrade();self.finish(cid,result);self.assertEqual(self.validate(),self.state)
  record=u.load(result['receipt']);self.assertIn('unobserved',record['past_intermediate_installation']);self.assertEqual(record['comparison']['no_original_handle_or_failure_lost'],True)
  self.assertEqual((self.project/'spec/execution/keep.txt').read_text(),'existing execute product\n')
  shutil.rmtree(self.candidate)
  with patch.object(j,'__file__',str(self.project/'.agents/hmigbot-runtime/src/hmigbot_ios152/join_attempt.py')):self.assertEqual(self.validate(),self.state)
 def test_original_unjoined_and_failed_observations_remain_blocking(self):
  self.call('fixture-spawn','spawn_agent',{'task_name':'worker'});self.output('fixture-spawn',{'task_name':'/root/worker','agent_id':'worker-id'})
  self.call('fixture-failed','spawn_agent',{'task_name':'failed_worker'});self.output('fixture-failed',{'error':'neutral failure'})
  self.idle([{'agent_name':'/root/worker','agent_status':'idle'}]);cid,result=self.upgrade();self.finish(cid,result);self.validate()
  trace=j.scoped_trace(self.project,self.native)
  self.assertEqual(trace.attempt['start_bytes'],self.state['start_bytes']);self.assertIn('/root/worker',trace.handles);self.assertEqual(len(trace.failed_spawns),1)
  with contextlib.redirect_stdout(io.StringIO()):code=scope.gate(trace,self.project,'neutral',True)
  self.assertEqual(code,1)
 def test_missing_or_nonzero_success_output_cannot_authorize_pointer(self):
  cid,result=self.upgrade()
  with self.assertRaisesRegex(ValueError,'actual successful'):self.validate()
  self.finish(cid,result,exit=3)
  with self.assertRaisesRegex(ValueError,'actual successful'):self.validate()
 def test_pending_second_upgrade_blocks_stage_gate(self):
  cid,result=self.upgrade('1'*32);self.finish(cid,result);self.request('2'*32)
  with self.assertRaisesRegex(ValueError,'unambiguous'):self.validate()
 def test_two_equal_payload_upgrades_cannot_roll_back_pointer(self):
  cid,result=self.upgrade('1'*32);self.finish(cid,result);first=(self.project/u.POINTER).read_bytes();self.idle()
  cid,result=self.upgrade('2'*32);self.finish(cid,result);self.validate();(self.project/u.POINTER).write_bytes(first)
  with self.assertRaisesRegex(ValueError,'rolled back'):self.validate()
 def test_stricter_preparation_keeps_saved_failure_and_accepts_more(self):
  old={'handles':{'/root/a':'UNJOINED'},'thread_id':'x','source_sha256':'a','interval_sha256':'b','start_bytes':1,'end_bytes':2,'failed_spawns':[],'unrecovered_spawns':[],'failed_enrollments':[],'foreign_enrollments':[],'issues':[]}
  stricter=copy.deepcopy(old);stricter['handles']['/root/b']='UNJOINED';stricter['issues']=['stricter new finding'];self.assertTrue(u.compare_audits(old,stricter))
  relaxed=copy.deepcopy(old);relaxed['handles']['/root/a']='joined'
  with self.assertRaisesRegex(ValueError,'unjoined'):u.compare_audits(old,relaxed)
 def test_second_upgrade_accepts_a_stricter_current_audit(self):
  cid,result=self.upgrade('1'*32);self.finish(cid,result);self.idle()
  newer=self.package('candidate-next','1.5.2-ios.34');self.candidate=newer
  actual=u.audit_summary
  def stricter(*args,**kwargs):
   value=actual(*args,**kwargs);value['issues'].append('additional stricter fixture classifier finding');value['exit_code']=1;return value
  with patch.object(j,'__file__',str(newer/'src/hmigbot_ios152/join_attempt.py')),patch.object(j,'__version__','1.5.2-ios.34'),patch.object(u,'audit_summary',side_effect=stricter):
   cid,result=self.upgrade('2'*32);self.finish(cid,result);self.validate()
   self.assertEqual(result['version'],'1.5.2-ios.34')
   self.assertIn('additional stricter fixture classifier finding',u.load(u.load(result['receipt'])['new_audit_file'])['issues'])
 def test_wrong_package_sha_fails_without_touching_state(self):
  cid,args=self.request();bad=list(args);bad[3]='0'*64
  with self.assertRaisesRegex(ValueError,'manifest SHA'):u.upgrade(*bad)
  self.assertEqual((self.project/j.STATE).read_bytes(),self.state_bytes);self.assertFalse((self.project/u.POINTER).exists())
 def test_current_thread_mismatch_rejected_before_evidence_read(self):
  changed={**self.state,'thread_id':'not-this-host'}
  with patch.object(u,'validate_binding',side_effect=AssertionError('must not read evidence')):
   with self.assertRaisesRegex(ValueError,'thread mismatch'):j.validate_state(self.project,self.native,self.raw,changed)
 def test_explicit_failed_later_upgrade_preserves_original_success(self):
  cid,result=self.upgrade('1'*32);self.finish(cid,result);cid,args=self.request('2'*32)
  self.output(cid,{'exit_code':3,'output':'neutral clearly failed upgrade, no upgraded state'})
  self.assertEqual(self.validate(),self.state)
 def test_owned_edit_and_wrong_package_sha_refuse_before_install(self):
  owned=self.project/'.agents/hmigbot-runtime/src/hmigbot_ios/__init__.py';owned.write_text('edited owned\n');cid,args=self.request()
  with self.assertRaisesRegex(ValueError,'owned bytes'):u.upgrade(*args)
  self.assertEqual((self.project/j.STATE).read_bytes(),self.state_bytes);self.assertFalse((self.project/u.POINTER).exists())
 def test_origin_package_missing_member_refuses(self):
  (self.origin/u.MEMBERS[1]).unlink();cid,args=self.request()
  with self.assertRaises((ValueError,OSError)):u.upgrade(*args)
  self.assertFalse((self.project/u.POINTER).exists())
 def test_install_then_error_restores_old_install_and_state(self):
  before=u.installed(self.project);real=u.installer
  def injected(root):
   module=real(root)
   if str(root)==str(self.candidate):
    manage=module.manage
    def fail(*args,**kwargs):manage(*args,**kwargs);raise ValueError('fixture after-install fault')
    module.manage=fail
   return module
  cid,args=self.request()
  with patch.object(u,'installer',side_effect=injected):
   with self.assertRaisesRegex(ValueError,'after-install fault'):u.upgrade(*args)
  self.assertEqual(u.installed(self.project),before);self.assertEqual((self.project/j.STATE).read_bytes(),self.state_bytes);self.assertFalse((self.project/u.POINTER).exists())
 def test_pointer_receipt_archive_and_frozen_origin_tamper_refuse(self):
  cid,result=self.upgrade();self.finish(cid,result);record=u.load(result['receipt']);paths=[Path(result['receipt']),Path(record['before']['archive'])/'metadata/AGENTS.md',Path(record['origin']['frozen_root'])/u.MEMBERS[1],self.project/u.POINTER]
  for path in paths:
   with self.subTest(path=path):
    saved=path.read_bytes();path.write_bytes(saved+b' ')
    try:
     with self.assertRaises((ValueError,OSError,KeyError)):self.validate()
    finally:path.write_bytes(saved)
 def test_new_begin_after_upgrade_is_rejected(self):
  cid,result=self.upgrade();self.finish(cid,result);self.call('fixture-extra','exec_command',{'cmd':shlex.join(['python3','-B',str(self.project/j._SCRIPT_MEMBERS[1]),'seal','--project',str(self.project)]),'yield_time_ms':30000,'max_output_tokens':6500})
  with self.assertRaisesRegex(ValueError,'enrollment/recovery'):self.validate()
 def test_active_child_or_unreturned_control_refuses_upgrade(self):
  self.call('pending-control','spawn_agent',{'task_name':'pending'});cid,args=self.request()
  with self.assertRaisesRegex(ValueError,'no original output'):u.upgrade(*args)
  self.assertFalse((self.project/u.POINTER).exists())
 def test_original_process_polling_joins_only_matching_session(self):
  cid,result=self.upgrade();text=json.dumps(result);middle=len(text)//2
  self.output(cid,{'session_id':87654,'output':text[:middle]})
  self.call('fixture-poll','write_stdin',{'session_id':87654,'chars':'','yield_time_ms':10000,'max_output_tokens':6500})
  self.output('fixture-poll',{'exit_code':0,'output':text[middle:]});self.assertEqual(self.validate(),self.state)
 def test_agent_work_during_upgrade_window_cannot_be_erased(self):
  cid,result=self.upgrade()
  self.call('fixture-parallel-spawn','spawn_agent',{'task_name':'parallel'})
  self.output('fixture-parallel-spawn',{'task_name':'/root/parallel','agent_id':'parallel-id'})
  self.finish(cid,result)
  with self.assertRaisesRegex(ValueError,'while the tool upgrade'):self.validate()
 def test_original_oracle_provenance_and_open_guards_are_reported(self):
  cid,result=self.upgrade();record=u.load(result['receipt']);old=u.load(record['original_audit_file']);provenance=old['provenance']
  self.assertEqual(provenance['derived_member'],j._SCRIPT_MEMBERS[1]);self.assertEqual(provenance['old_version'],'1.5.2-ios.27')
  self.assertTrue(all(Path(m['physical']).is_relative_to(record['origin']['frozen_root']) for m in provenance['modules'].values()))
  self.assertTrue(any(a['operation']=='open' and not a['project'] for a in provenance['project_accesses']))
  self.assertFalse(any(a['operation']=='open' and a['project'] for a in provenance['project_accesses']))
 def summary_pair(self):
  cid,result=self.upgrade();record=u.load(result['receipt']);old=u.load(record['original_audit_file'])['summary'];return old,copy.deepcopy(old)
 def test_old_only_invalid_listing_and_order_failure_cannot_disappear(self):
  old,new=self.summary_pair();old.update(exit_code=1,invalid_lists=[{'call_id':'fixture-invalid','reason':'bad list','output_bytes':100}],last_invalid_list_output=100,last_full_list_call=90)
  with self.assertRaisesRegex(ValueError,'nonzero'):u.compare_audits(old,new)
  new['exit_code']=1
  with self.assertRaisesRegex(ValueError,'invalid_lists'):u.compare_audits(old,new)
  new['invalid_lists']=copy.deepcopy(old['invalid_lists'])
  with self.assertRaisesRegex(ValueError,'ordering'):u.compare_audits(old,new)
 def test_old_only_fake_ledger_observation_cannot_disappear(self):
  old,new=self.summary_pair();self.assertFalse(old['ledger_checked']);self.assertEqual(old['ledger_fake'],[])
  # No production ledger input is required. This synthetic old-only result
  # exercises the non-relaxation comparison's optional audit finding contract.
  old.update(exit_code=1,ledger_fake=[['fixture-point','fixture-not-completed']])
  with self.assertRaisesRegex(ValueError,'nonzero'):u.compare_audits(old,new)
  new['exit_code']=1
  with self.assertRaisesRegex(ValueError,'ledger_fake'):u.compare_audits(old,new)
 def test_canonical_options_and_nonce_are_verified(self):
  cid,args=self.request();p=next(r['payload'] for r,_,_ in j.rows(self.raw) if r.get('payload',{}).get('call_id')==cid);u.command(p,self.candidate/'scripts/join_attempt.py');bad=copy.deepcopy(p);a=json.loads(bad['arguments']);a['cmd']+=' extra';bad['arguments']=json.dumps(a)
  with self.assertRaises(ValueError):u.command(bad,self.candidate/'scripts/join_attempt.py')
  bad=copy.deepcopy(p);a=json.loads(bad['arguments']);a['yield_time_ms']=1000;bad['arguments']=json.dumps(a)
  with self.assertRaises(ValueError):u.command(bad,self.candidate/'scripts/join_attempt.py')

if __name__=='__main__':unittest.main(verbosity=2)
