from pathlib import Path
import hashlib,json,zipfile,stat,sys
root=Path(__file__).resolve().parents[1]
out=root.parent/(root.name+'.zip')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Remove transient files.
for p in list(root.rglob('__pycache__')):
 import shutil; shutil.rmtree(p)
for p in root.rglob('*.pyc'): p.unlink()
for p in [root/'MANIFEST.json',root/'SHA256SUMS.txt']:
 if p.exists():p.unlink()
files=sorted(p for p in root.rglob('*') if p.is_file())
manifest={'document_type':'aset-seed-release-manifest','version':'0.1-rc11','package_root':root.name,'file_count':len(files),'files':[{'path':str(p.relative_to(root)),'size':p.stat().st_size,'sha256':'sha256:'+sha(p)} for p in files]}
(root/'MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
checks=sorted([*files,root/'MANIFEST.json'])
(root/'SHA256SUMS.txt').write_text(''.join(f'{sha(p)}  {p.relative_to(root)}\n' for p in checks))
allfiles=sorted(p for p in root.rglob('*') if p.is_file())
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in allfiles:
  arc=f'{root.name}/{p.relative_to(root)}'
  info=zipfile.ZipInfo(arc,(2026,8,4,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=(stat.S_IFREG|0o644)<<16; info.create_system=3
  z.writestr(info,p.read_bytes())
print(json.dumps({'archive':str(out),'size':out.stat().st_size,'sha256':'sha256:'+sha(out),'file_count':len(allfiles)},indent=2))
