from __future__ import annotations
import copy, json, sys
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'machine/reference'))
import seed_reference as api
EX=ROOT/'machine/examples'
D=lambda c:'sha256:'+c*64

def load(cid:str)->dict[str,Any]:
 for sub in ('positive','negative'):
  p=EX/sub/f'{cid}.json'
  if p.exists(): return json.loads(p.read_text())
 raise KeyError(cid)

def replay(cid:str,count:int|None=None):
 case=load(cid); state=api.initialize_state(copy.deepcopy(case['initial_genesis']))
 seq=case.get('setup',[]) if count is None else case.get('setup',[])[:count]
 for tx in seq:
  r=api.apply_transition(state,copy.deepcopy(tx))
  if not (r['accepted'] and r['state_changed']): raise AssertionError((cid,tx['kind'],r['code']))
  state=r['state']
 return state,copy.deepcopy(case['candidate'])

def fresh(state,kind,context,signer,payload):
 tx={'schema_version':api.VERSION,'transition_id':'tx:'+'0'*64,'trust_space_id':state['trust_space_id'],
  'context_id':context,'kind':kind,'parent_state_root':state['current_state_root'],
  'expected_local_ordinal':state['contexts'][context]['local_ordinal']+1,'constitution_epoch':state['constitution']['epoch'],
  'causal_parents':[],'authn':{'signer_principal_id':signer,'proof_digest':D('d')},'payload':copy.deepcopy(payload)}
 tx['causal_parents']=api._required_causal_parents(state,tx); tx['transition_id']=api.compute_transition_id(tx); return tx

def apply(state,tx): return api.apply_transition(state,copy.deepcopy(tx))
def view(r): return {k:r[k] for k in ('accepted','code','state_changed')}
results=[]
def check(i,name,passed,**detail):
 results.append({'id':f'BB-{i:02d}-{name}','pass':bool(passed),**detail})
 if not passed: print('FAIL',results[-1])

# 01 unknown policy.
state,_=replay('POS-009',6); ver=copy.deepcopy(load('POS-009')['setup'][6]); ver['payload']['policy_digest']=D('9'); ver=fresh(state,'VERIFICATION',ver['context_id'],ver['authn']['signer_principal_id'],ver['payload']); r=apply(state,ver)
check(1,'UNRECOGNIZED_POLICY',not r['accepted'] and r['code']=='VERIFICATION_POLICY_UNRECOGNIZED',observed=view(r))
# 02 recognized but not Permit-bound policy.
state,_=replay('POS-009',6); ver=copy.deepcopy(load('POS-009')['setup'][6]); other=state['constitution']['body']['rules']['rule:permit']; ver['payload']['policy_digest']=other; ver=fresh(state,'VERIFICATION',ver['context_id'],ver['authn']['signer_principal_id'],ver['payload']); r=apply(state,ver)
check(2,'POLICY_PERMIT_BINDING',not r['accepted'] and r['code']=='VERIFICATION_POLICY_PERMIT_MISMATCH',observed=view(r))
# 03 Outcome cannot be corrected.
state,cand=replay('POS-009'); out=apply(state,cand); assert out['accepted']; state=out['state']; oid=out['artifacts'][0]
cor=fresh(state,'CORRECTION',state['outcomes'][oid]['context_id'],'principal:validator',{'target_type':'OUTCOME','target_ref':oid,'replacement_ref':None,'reason_digest':D('8')}); r=apply(state,cor)
check(3,'OUTCOME_IMMUTABLE',not r['accepted'] and r['code']=='TRANSITION_SCHEMA_INVALID',observed=view(r))
# 04 withdrawn Context cannot act.
state,cand=replay('POS-023'); wr=apply(state,cand); assert wr['accepted']; after=wr['state']; old=cand['context_id']
dec=fresh(after,'DECISION',old,'principal:a',{'decision_kind':'READINESS_EXECUTE','subject_principal_id':'principal:a','scope':['x'],'conditions_digest':D('7'),'related_ref':None}); r=apply(after,dec)
check(4,'WITHDRAWN_CONTEXT_INACTIVE',not r['accepted'] and r['code']=='CONTEXT_NOT_ACTIVE',observed=view(r))

# 05 cross-context Authority transfer laundering.
state,_=replay('POS-022',1); f=state['context_aliases']['/f']; responsible='principal:responsible'; new_holder='principal:child'
old_auth=next(a for a in state['authorities'].values() if a['context_id']==f and a['capability_kind']=='CREATE_MEMBER_CONTEXT' and a['status']=='ACTIVE')
child_payload={'parent_context_id':f,'member_principal_id':new_holder,'context_kind':'SUBJECT','context_genesis_nonce':'cross-child','local_alias':'child','initial_authorities':[
 {'capability_kind':'ISSUE_PERMIT','holder_principal_id':new_holder,'scope':['*']},{'capability_kind':'VERIFY','holder_principal_id':new_holder,'scope':['*']},{'capability_kind':'CONFIRM_OUTCOME','holder_principal_id':new_holder,'scope':['*']}], 'depends_on_context_ids':[]}
r=apply(state,fresh(state,'MEMBER_CONTEXT_GENESIS',f,responsible,child_payload)); assert r['accepted'],r; state=r['state']; child=r['artifacts'][0]
task=api._transfer_task_digest(old_auth['authority_id'],new_holder); policy=state['constitution']['body']['rules']['rule:verification']; scope=['authority:accept']; terms=api.permit_terms_digest(new_holder,task,scope,policy,1,1000,{})
r=apply(state,fresh(state,'DECISION',child,new_holder,{'decision_kind':'READINESS_ACCEPT_RESPONSIBILITY','subject_principal_id':new_holder,'scope':scope,'conditions_digest':terms,'related_ref':old_auth['authority_id']})); assert r['accepted']; state=r['state']; ready=r['artifacts'][0]
r=apply(state,fresh(state,'DECISION',child,new_holder,{'decision_kind':'ISSUE_PERMIT','subject_principal_id':new_holder,'scope':scope,'conditions_digest':terms,'related_ref':ready})); assert r['accepted']; state=r['state']; decision=r['artifacts'][0]
r=apply(state,fresh(state,'PERMIT_ISSUE',child,new_holder,{'decision_ref':decision,'readiness_ref':ready,'delegate_principal_id':new_holder,'task_digest':task,'scope':scope,'success_predicate_digest':policy,'max_attempts':1,'stop_on_positive':True,'validity_end_ordinal':1000,'caveats':{}})); assert r['accepted'],r; state=r['state']; permit=r['artifacts'][0]
r=apply(state,fresh(state,'PERMIT_USE',child,new_holder,{'permit_ref':permit,'submission_id':'submission:cross','candidate_digest':D('6')})); assert r['accepted']; state=r['state']; receipt=r['artifacts'][1]
r=apply(state,fresh(state,'OBSERVATION',child,new_holder,{'permit_ref':permit,'receipt_ref':receipt,'claim_digest':D('5'),'claim_subject_context_id':None,'evidence_refs':['evidence:cross']})); assert r['accepted']; state=r['state']; obs=r['artifacts'][0]
r=apply(state,fresh(state,'VERIFICATION',child,new_holder,{'permit_ref':permit,'receipt_ref':receipt,'observation_ref':obs,'policy_digest':policy,'evidence_refs':['evidence:cross'],'status':'PASS','result_class':'SUCCESS'})); assert r['accepted']; state=r['state']; ver=r['artifacts'][0]
r=apply(state,fresh(state,'OUTCOME',child,new_holder,{'permit_ref':permit,'verification_refs':[ver],'outcome_class':'POSITIVE'})); assert r['accepted']; state=r['state']; outcome=r['artifacts'][0]
r=apply(state,fresh(state,'AUTHORITY_TRANSFER',f,responsible,{'authority_ref':old_auth['authority_id'],'new_holder_principal_id':new_holder,'outcome_ref':outcome}))
check(5,'CROSS_CONTEXT_TRANSFER',not r['accepted'] and r['code']=='TRANSFER_ACTION_CONTEXT_MISMATCH',observed=view(r))

# Governance baseline.
base,red_tx=replay('POS-017'); f=red_tx['context_id']; proposal=red_tx['payload']['proposal']; a=proposal['target_context_id']; affected=api.compute_affected_sibling_set(base,f,a)
# 06 exact redefinition preserves aliases and remaps dependencies.
r=apply(base,red_tx); ok=r['accepted']; after=r['state'] if ok else base
rec=next(iter(after['context_redefinitions'].values())) if ok else {'successor_map':{}}
map_=rec['successor_map']; aliases_ok=ok and all(after['contexts'][old]['alias']==after['contexts'][new]['alias'] for old,new in map_.items())
deps={(e['source_context_id'],e['target_context_id']) for e in after['normative_dependencies']}; old_b=next(x for x in affected if x!=a); remap_ok=(map_.get(old_b),map_.get(a)) in deps
check(6,'ATOMIC_REDEFINE_ACCEPTED',ok and aliases_ok and remap_ok,observed=view(r),affected=affected)
# 07 missing authorization.
p=copy.deepcopy(red_tx['payload']); p['withdrawal_authorizations'].pop(); tx=fresh(base,'CONTEXT_REDEFINE',f,'principal:admin',p); r=apply(base,tx)
check(7,'AUTHORIZATION_SET_EXACT',not r['accepted'] and r['code']=='REDEFINITION_AUTHORIZATION_SET_MISMATCH',observed=view(r))
# 08 missing replacement and rebound digest.
p=copy.deepcopy(red_tx['payload']); p['proposal']['replacements'].pop(); dg=api.context_redefinition_proposal_digest(p['proposal']); p['proposal_digest']=dg
for au in p['withdrawal_authorizations']: au['proposal_digest']=dg
tx=fresh(base,'CONTEXT_REDEFINE',f,'principal:admin',p); r=apply(base,tx)
check(8,'AFFECTED_SET_EXACT',not r['accepted'] and r['code']=='REDEFINITION_AFFECTED_SET_MISMATCH',observed=view(r))
# 09 member substitution.
p=copy.deepcopy(red_tx['payload']); p['withdrawal_authorizations'][0]['member_principal_id']='principal:parent'; tx=fresh(base,'CONTEXT_REDEFINE',f,'principal:admin',p); r=apply(base,tx)
check(9,'MEMBER_SIGNATURE',not r['accepted'] and r['code']=='REDEFINITION_MEMBER_MISMATCH',observed=view(r))
# 10 proposal digest tamper.
p=copy.deepcopy(red_tx['payload']); p['proposal_digest']=D('4'); tx=fresh(base,'CONTEXT_REDEFINE',f,'principal:admin',p); r=apply(base,tx)
check(10,'FULL_PROPOSAL_BINDING',not r['accepted'] and r['code']=='REDEFINITION_PROPOSAL_DIGEST_MISMATCH',observed=view(r))
# 11 unauthorized parent actor.
tx=fresh(base,'CONTEXT_REDEFINE',f,'principal:a',copy.deepcopy(red_tx['payload'])); r=apply(base,tx)
check(11,'PARENT_AUTHORITY',not r['accepted'] and r['code']=='AUTHORITY_MISSING',observed=view(r))
# 12 failed redefine is exactly atomic.
p=copy.deepcopy(red_tx['payload']); p['withdrawal_authorizations'].pop(); r=apply(base,fresh(base,'CONTEXT_REDEFINE',f,'principal:admin',p))
check(12,'FAILED_REDEFINE_NO_MUTATION',not r['accepted'] and r['state']==base and r['state']['current_state_root']==base['current_state_root'],observed=view(r))
# 13 voluntary exit releases alias.
state,wd_tx=replay('POS-023'); old_alias=state['contexts'][wd_tx['context_id']]['alias']; parent=state['contexts'][wd_tx['context_id']]['parent_context_id']; r=apply(state,wd_tx); assert r['accepted']; state=r['state']
check(13,'VOLUNTARY_EXIT',wd_tx['context_id'] not in state['context_aliases'].values() and old_alias not in state['context_aliases'],observed=view(r))
# 14 released alias can be reused by new Genesis.
local=old_alias.rsplit('/',1)[-1]; payload={'parent_context_id':parent,'member_principal_id':'principal:a2','context_kind':'SUBJECT','context_genesis_nonce':'a-rejoin','local_alias':local,'initial_authorities':[],'depends_on_context_ids':[]}
r=apply(state,fresh(state,'MEMBER_CONTEXT_GENESIS',parent,'principal:admin',payload))
check(14,'ALIAS_REUSE_AFTER_EXIT',r['accepted'] and r['state']['context_aliases'].get(old_alias)==r['artifacts'][0],observed=view(r))
# 15 root cannot withdraw.
root=base['root_context_id']; r=apply(base,fresh(base,'MEMBERSHIP_WITHDRAW',root,'principal:bootstrap',{'reason_digest':D('3')}))
check(15,'ROOT_WITHDRAWAL_FORBIDDEN',not r['accepted'] and r['code']=='ROOT_WITHDRAWAL_FORBIDDEN',observed=view(r))
# 16 transitive C->B->A closure rejects incomplete A+B.
state=copy.deepcopy(base); b=next(x for x in affected if x!=a)
c_payload={'parent_context_id':f,'member_principal_id':'principal:c','context_kind':'SUBJECT','context_genesis_nonce':'c-v1','local_alias':'c','initial_authorities':[],'depends_on_context_ids':[b]}
r=apply(state,fresh(state,'MEMBER_CONTEXT_GENESIS',f,'principal:admin',c_payload)); assert r['accepted']; state=r['state']; c=r['artifacts'][0]
p=copy.deepcopy(red_tx['payload']); p['proposal']['proposal_nonce']='transitive-incomplete'; dg=api.context_redefinition_proposal_digest(p['proposal']); p['proposal_digest']=dg
for au in p['withdrawal_authorizations']: au['proposal_digest']=dg
r=apply(state,fresh(state,'CONTEXT_REDEFINE',f,'principal:admin',p))
check(16,'TRANSITIVE_CLOSURE_REJECTS_PARTIAL',not r['accepted'] and r['code']=='REDEFINITION_AFFECTED_SET_MISMATCH' and api.compute_affected_sibling_set(state,f,a)==sorted([a,b,c]),observed=view(r))
# 17 exact A+B+C redefinition succeeds and remaps both edges.
p=copy.deepcopy(red_tx['payload']); p['proposal']['proposal_nonce']='transitive-complete'; p['proposal']['replacements'].append({'old_context_id':c,'context_genesis_nonce':'c-v2','initial_authorities':[],'depends_on_context_ids':[b]}); dg=api.context_redefinition_proposal_digest(p['proposal']); p['proposal_digest']=dg
for au in p['withdrawal_authorizations']: au['proposal_digest']=dg
p['withdrawal_authorizations'].append({'context_id':c,'member_principal_id':'principal:c','proposal_digest':dg,'proof_digest':D('2')})
r=apply(state,fresh(state,'CONTEXT_REDEFINE',f,'principal:admin',p)); ok=r['accepted']; after=r['state'] if ok else state; rec=next(reversed(after['context_redefinitions'].values())) if ok else {'successor_map':{}}; mp=rec['successor_map']; edges={(e['source_context_id'],e['target_context_id']) for e in after['normative_dependencies']}
check(17,'TRANSITIVE_REDEFINE_ACCEPTS_EXACT',ok and (mp[b],mp[a]) in edges and (mp[c],mp[b]) in edges,observed=view(r))
# 18 there is no destructive pending-consent transition.
raw=fresh(base,'MEMBERSHIP_WITHDRAW',a,'principal:a',{'reason_digest':D('1')}); raw['kind']='REDEFINITION_CONSENT'; raw['transition_id']=api.compute_transition_id(raw); r=apply(base,raw)
check(18,'NO_PENDING_CONSENT_STATE',not r['accepted'] and r['code']=='TRANSITION_SCHEMA_INVALID',observed=view(r))
# 19 root Constitution amendment is outside the transition language.
raw=fresh(base,'MEMBERSHIP_WITHDRAW',a,'principal:a',{'reason_digest':D('1')}); raw['kind']='AMENDMENT'; raw['transition_id']=api.compute_transition_id(raw); r=apply(base,raw)
check(19,'ROOT_CONSTITUTION_IMMUTABLE',not r['accepted'] and r['code']=='TRANSITION_SCHEMA_INVALID',observed=view(r))
# 20 foreign dependency target cannot be historical/inactive.
p=copy.deepcopy(red_tx['payload']); historical=load('POS-023')['candidate']['context_id']
# Use an actually inactive Context in a separate state: withdraw A, then propose a replacement for B depending on withdrawn A is impossible because target itself inactive; direct API should fail closed before mutation.
state2,wd=replay('POS-023'); rr=apply(state2,wd); state2=rr['state']; parent2=state2['contexts'][wd['context_id']]['parent_context_id'];
# New sibling X first, then target X depends on the historical old A through replacement proposal.
xpay={'parent_context_id':parent2,'member_principal_id':'principal:x','context_kind':'SUBJECT','context_genesis_nonce':'x-v1','local_alias':'x','initial_authorities':[],'depends_on_context_ids':[]}; rr=apply(state2,fresh(state2,'MEMBER_CONTEXT_GENESIS',parent2,'principal:admin',xpay)); assert rr['accepted']; state2=rr['state']; x=rr['artifacts'][0]
prop={'parent_context_id':parent2,'target_context_id':x,'proposal_nonce':'inactive-dep','replacements':[{'old_context_id':x,'context_genesis_nonce':'x-v2','initial_authorities':[],'depends_on_context_ids':[wd['context_id']]}]}; dg=api.context_redefinition_proposal_digest(prop); pp={'proposal':prop,'proposal_digest':dg,'withdrawal_authorizations':[{'context_id':x,'member_principal_id':'principal:x','proposal_digest':dg,'proof_digest':D('1')}]}; rr=apply(state2,fresh(state2,'CONTEXT_REDEFINE',parent2,'principal:admin',pp))
check(20,'HISTORICAL_DEPENDENCY_REJECTED',not rr['accepted'] and rr['code']=='DEPENDENCY_CONTEXT_INACTIVE',observed=view(rr))


# 21 voluntary exit cannot silently strand active normative dependants.
state, red = replay('POS-017'); parent=red['context_id']; target=red['payload']['proposal']['target_context_id']
withdraw=fresh(state,'MEMBERSHIP_WITHDRAW',target,'principal:a',{'reason_digest':D('2')}); r=apply(state,withdraw)
check(21,'WITHDRAWAL_DEPENDANTS_REQUIRE_REDEFINITION',not r['accepted'] and r['code']=='WITHDRAWAL_REDEFINITION_REQUIRED',observed=view(r))

# 22 new Context cannot bind a normative dependency to a historical Context.
state, wd = replay('POS-023'); wr=apply(state,wd); assert wr['accepted']; state=wr['state']; old=wd['context_id']; parent=state['contexts'][old]['parent_context_id']
payload={'parent_context_id':parent,'member_principal_id':'principal:x2','context_kind':'SUBJECT','context_genesis_nonce':'x2-v1','local_alias':'x2','initial_authorities':[],'depends_on_context_ids':[old]}
r=apply(state,fresh(state,'MEMBER_CONTEXT_GENESIS',parent,'principal:admin',payload))
check(22,'GENESIS_INACTIVE_DEPENDENCY_REJECTED',not r['accepted'] and r['code']=='DEPENDENCY_CONTEXT_INACTIVE',observed=view(r))

# 23 whole-state validation rejects an active normative edge to an inactive Context.
mut=copy.deepcopy(state); active=parent
mut['normative_dependencies'].append({'source_context_id':active,'target_context_id':old,'dependency_kind':'NORMATIVE'}); mut['current_state_root']=api.compute_state_root(mut)
try:
 api.validate_state(mut); rejected=False; code=''
except api.SeedError as exc:
 rejected=exc.code=='NORMATIVE_DEPENDENCY_CONTEXT_INACTIVE'; code=exc.code
check(23,'STATE_INACTIVE_DEPENDENCY_REJECTED',rejected,observed=code)

# 24 redefinition audit record is bound to the full canonical proposal.
state, red = replay('POS-017'); rr=apply(state,red); assert rr['accepted']; mut=copy.deepcopy(rr['state']); rid=next(iter(mut['context_redefinitions']))
mut['context_redefinitions'][rid]['proposal']['proposal_nonce']='tampered'; mut['current_state_root']=api.compute_state_root(mut)
try:
 api.validate_state(mut); rejected=False; code=''
except api.SeedError as exc:
 rejected=exc.code=='REDEFINITION_PROPOSAL_DIGEST_MISMATCH'; code=exc.code
check(24,'REDEFINITION_RECORD_PROPOSAL_BOUND',rejected,observed=code)

# 25 active Permit cannot survive in an inactive Context in a forged state snapshot.
state,_=replay('POS-009',4); permit_id=next(iter(state['permits'])); ctx=state['permits'][permit_id]['context_id']; mut=copy.deepcopy(state); mut['contexts'][ctx]['lifecycle']='WITHDRAWN'; mut['context_aliases'].pop(mut['contexts'][ctx]['alias'],None); mut['current_state_root']=api.compute_state_root(mut)
try:
 api.validate_state(mut); rejected=False; code=''
except api.SeedError as exc:
 rejected=exc.code in {'ACTIVE_AUTHORITY_IN_INACTIVE_CONTEXT','ACTIVE_PERMIT_IN_INACTIVE_CONTEXT'}; code=exc.code
check(25,'ACTIVE_PERMIT_INACTIVE_CONTEXT_REJECTED',rejected,observed=code)

summary={'suite':'independent public-API black-box','checks_total':len(results),'checks_passed':sum(x['pass'] for x in results),'failed':[x for x in results if not x['pass']],'results':results}
if '--no-write' not in sys.argv:
 (ROOT/'validation'/'blackbox_audit_results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
 (ROOT/'validation'/'blackbox_audit_run.txt').write_text(f"Black-box: {summary['checks_passed']}/{summary['checks_total']}\n")
print(json.dumps({k:summary[k] for k in ('checks_total','checks_passed')},indent=2))
raise SystemExit(0 if not summary['failed'] else 1)
