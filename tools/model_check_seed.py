#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from collections import deque
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class State:
 status:str
 enforcement:str
 authority_index:int
 chain:tuple[int,...]
 audit_length:int

AUTHORITIES=3

def initial()->State:
 return State('UNKNOWN','BLOCKED',0,(0,),1)

def successors(state:State):
 if state.status!='UNKNOWN': return
 yield 'ResolveAccept',State('ACCEPT','ALLOW',state.authority_index,state.chain,state.audit_length+1)
 yield 'ResolveDeny',State('DENY','BLOCKED',state.authority_index,state.chain,state.audit_length+1)
 for next_authority in range(AUTHORITIES):
  if next_authority not in state.chain:
   yield 'Escalate',State('UNKNOWN','BLOCKED',next_authority,state.chain+(next_authority,),state.audit_length+1)

def invariant_errors(state:State)->list[str]:
 errors=[]
 if state.status not in {'UNKNOWN','ACCEPT','DENY'}: errors.append('StatusDomain')
 if state.status=='UNKNOWN' and state.enforcement!='BLOCKED': errors.append('UnknownBlocked')
 if state.enforcement=='ALLOW' and state.status!='ACCEPT': errors.append('AllowOnlyAccept')
 if state.status=='DENY' and state.enforcement!='BLOCKED': errors.append('AllowOnlyAccept')
 if len(state.chain)!=len(set(state.chain)): errors.append('EscalationAuthorized')
 if state.authority_index!=state.chain[-1]: errors.append('EscalationAuthorized')
 if state.audit_length<1: errors.append('AuditMonotone')
 if state.status in {'ACCEPT','DENY'} and list(successors(state) or []): errors.append('TerminalImmutable')
 return errors

def main()->int:
 parser=argparse.ArgumentParser(); parser.add_argument('--depth',type=int,default=5); parser.add_argument('--output',type=Path); args=parser.parse_args()
 queue=deque([(initial(),0)]); visited={initial()}; transitions=0; failures=[]; terminal=0
 while queue:
  state,depth=queue.popleft(); errors=invariant_errors(state)
  if errors: failures.append({'state':repr(state),'errors':errors}); continue
  if state.status in {'ACCEPT','DENY'}: terminal+=1
  if depth>=args.depth: continue
  for action,candidate in successors(state) or []:
   transitions+=1
   if candidate not in visited:
    visited.add(candidate); queue.append((candidate,depth+1))
 report={'document_type':'aset-seed-resolution-bounded-model-check','depth':args.depth,'states':len(visited),'transitions':transitions,'terminal_states':terminal,'invariants':['StatusDomain','UnknownBlocked','AllowOnlyAccept','TerminalImmutable','EscalationAuthorized','AuditMonotone'],'failures':failures,'verdict':'PASS' if not failures else 'FAIL'}
 if args.output:
  args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf-8')
 print(f"MODEL_CHECK_STATES={report['states']}"); print(f"MODEL_CHECK_TRANSITIONS={report['transitions']}"); print(f"MODEL_CHECK_TERMINAL_STATES={report['terminal_states']}"); print('MODEL_CHECK_VERDICT='+report['verdict'])
 return 0 if not failures else 1
if __name__=='__main__': raise SystemExit(main())
