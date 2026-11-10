"""Publish source metadata only after the independent checker has passed."""
import base64,datetime,json,pathlib,subprocess,sys

REPO='repos/ummayummaaa/ondutymap-updater/'
def api(path,body=None,method=None,missing=False):
 args=['gh','api',REPO+path]
 if method:args+=['--method',method]
 if body is not None:args+=['--input','-']
 result=subprocess.run(args,input=json.dumps(body)if body is not None else None,capture_output=True,text=True)
 if result.returncode:
  if missing and 'HTTP 404'in result.stderr:return None
  raise RuntimeError('Source manifest repository operation failed')
 return json.loads(result.stdout)

def main():
 content=pathlib.Path(sys.argv[1]).read_bytes();manifest=json.loads(content)
 age=(datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(manifest['checkedAt'].replace('Z','+00:00'))).total_seconds()
 if manifest.get('passed')is not True or manifest.get('method')!='independent-pdfplumber-v1' or not -60<=age<10800 or not 2<=len(manifest['days'])<=3:raise ValueError('Only fresh independently verified sources can be published')
 if not api('git/ref/heads/source-mirror',missing=True):
  head=api('git/ref/heads/main')['object']['sha']
  api('git/refs',{'ref':'refs/heads/source-mirror','sha':head},'POST')
 existing=api('contents/source-manifest.json?ref=source-mirror',missing=True)
 body={'message':'Publish independently verified original PDF references','branch':'source-mirror','content':base64.b64encode(content).decode()}
 if existing:
  prior=json.loads(base64.b64decode(existing['content']))
  if prior.get('checkedAt','')>manifest['checkedAt']:raise ValueError('Refusing source timestamp regression')
  body['sha']=existing['sha']
 result=api('contents/source-manifest.json',body,'PUT')
 print(json.dumps({'published':True,'sourceCheckedAt':manifest['checkedAt'],'commit':result['commit']['sha'],'dates':[d['date']for d in manifest['days']]}))

if __name__=='__main__':main()
