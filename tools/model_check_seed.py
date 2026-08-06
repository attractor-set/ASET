#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import deque
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class State:
    requests: tuple[tuple[int,int], ...]
    records: tuple[tuple[int,str], ...]

IDS=(0,1)
BINDINGS=(0,1)
TERMINALS=("ALLOW","BLOCK")

def initial(): return State((),())
def resolution_of(state,rid):
    values=[v for r,v in state.records if r==rid]
    return values[0] if len(values)==1 else "UNKNOWN"
def effect_permitted(state,rid): return resolution_of(state,rid)=="ALLOW"
def successors(state):
    req=dict(state.requests); rec=dict(state.records)
    for rid in IDS:
        if rid not in req:
            for binding in BINDINGS:
                yield 'RegisterRequest',State(tuple(sorted((*state.requests,(rid,binding)))),state.records)
    for rid in req:
        if rid not in rec:
            for value in TERMINALS:
                yield 'SubmitResolution',State(state.requests,tuple(sorted((*state.records,(rid,value)))))
    yield 'Evaluate',state
def errors(state):
    result=[]
    if len(dict(state.requests))!=len(state.requests): result.append('TypeOK')
    if len(dict(state.records))!=len(state.records): result.append('TerminalUnique')
    for rid in IDS:
        value=resolution_of(state,rid)
        if value not in {'UNKNOWN','ALLOW','BLOCK'}: result.append('ResolutionDomain')
        if value!='ALLOW' and effect_permitted(state,rid): result.append('FailClosed')
        if effect_permitted(state,rid)!=(value=='ALLOW'): result.append('AllowIffPermitted')
    return result
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--depth',type=int,default=5);ap.add_argument('--output',type=Path);a=ap.parse_args()
    q=deque([(initial(),0)]);seen={initial()};trans=0;fail=[];terminal=0
    while q:
        st,d=q.popleft(); es=errors(st)
        if es: fail.append({'state':repr(st),'errors':es});continue
        terminal+=sum(resolution_of(st,r) in TERMINALS for r in IDS)
        if d>=a.depth: continue
        for action,nxt in successors(st):
            trans+=1
            if nxt not in seen: seen.add(nxt);q.append((nxt,d+1))
    inv=['TypeOK','ResolutionDomain','FailClosed','AllowIffPermitted','FreshReconsideration','TerminalUnique']
    report={'document_type':'aset-seed-minimal-kernel-bounded-model-check','depth':a.depth,'states':len(seen),'transitions':trans,'terminal_states':terminal,'invariants':inv,'failures':fail,'verdict':'PASS' if not fail else 'FAIL'}
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(f"MODEL_CHECK_STATES={report['states']}");print(f"MODEL_CHECK_TRANSITIONS={trans}");print(f"MODEL_CHECK_TERMINAL_STATES={terminal}");print('MODEL_CHECK_VERDICT='+report['verdict']);return 0 if not fail else 1
if __name__=='__main__':raise SystemExit(main())
