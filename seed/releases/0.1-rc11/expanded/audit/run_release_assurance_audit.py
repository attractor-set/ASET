from pathlib import Path
import copy, shutil, subprocess, tempfile, json
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def check(name, ok, detail): checks.append({'name':name,'pass':bool(ok),'detail':detail})
with tempfile.TemporaryDirectory(prefix='aset-seed-assurance-') as td:
    td=Path(td)
    # stale coverage mutation
    c1=td/'coverage'; shutil.copytree(ROOT,c1)
    p=c1/'machine/reference/seed_reference.py'; p.write_text(p.read_text()+'\n# assurance mutation\n')
    r=subprocess.run(['python',str(c1/'tools/validate_package.py')],cwd=c1,text=True,capture_output=True)
    check('stale_coverage_rejected',r.returncode!=0 and 'coverage binding' in r.stdout+r.stderr,(r.stdout+r.stderr).strip())
    # publication byte mutation
    c2=td/'publication'; shutil.copytree(ROOT,c2)
    p=c2/'docs/ASET_Seed_Specification_0.1-rc11.docx'; p.write_bytes(p.read_bytes()+b'ASET-TAMPER')
    r=subprocess.run(['python',str(c2/'tools/validate_package.py')],cwd=c2,text=True,capture_output=True)
    check('publication_tamper_rejected',r.returncode!=0 and 'publication binding docx' in r.stdout+r.stderr,(r.stdout+r.stderr).strip())
result={'document_type':'aset-seed-release-assurance-audit','version':'0.1-rc11','checks':checks,'checks_total':len(checks),'checks_passed':sum(x['pass'] for x in checks),'verdict':'PASS' if all(x['pass'] for x in checks) else 'FAIL'}
out=ROOT/'validation/release_assurance_results.json'; out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({'checks_total':result['checks_total'],'checks_passed':result['checks_passed'],'verdict':result['verdict']},indent=2))
raise SystemExit(0 if result['verdict']=='PASS' else 1)
