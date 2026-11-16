"""Bounded recovery using the existing authenticated updater; never print credentials."""
import json,os,subprocess,sys,time
secret=os.environ.get('UPDATER_TOKEN')
if not secret:raise SystemExit('Updater credential is not configured')
payload=json.dumps({'site':'https://ondutymap.ioanniskotidism.workers.dev','updaterToken':secret})
for attempt in range(3):
 print('Official-source update attempt',attempt+1,flush=True)
 try:result=subprocess.run(['node','updater.mjs'],input=payload,text=True,timeout=300)
 except subprocess.TimeoutExpired:result=None
 if result and result.returncode==0:sys.exit(0)
 if attempt<2:time.sleep(20)
raise SystemExit(1)
