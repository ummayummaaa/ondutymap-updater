import importlib.util,json,pathlib,unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('checker',ROOT/'cloud-check.py')
checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
class Recovery(unittest.TestCase):
 def test_approved_omission_is_scoped_to_exact_source_and_cell(self):
  args=['b1f3a687c6e1fcdd8f20de539ac95ca7d73c7ee4b209ad26637582954f75aac9','2026-11-17',4,'Μαιευτική',0,('08:00','14:30',False),'2']
  self.assertTrue(checker.approved_source_omission(*args))
  for i,value in [(0,'a'*64),(1,'2026-11-18'),(2,3),(3,'Γυναικολογική'),(4,1),(5,('08:00','16:00',False)),(6,'3'),(6,'2 ΤΖΑΝΕΙΟ')]:
   changed=args.copy();changed[i]=value;self.assertFalse(checker.approved_source_omission(*changed))
 def test_changed_original_numeric_cell_remains_blocked(self):
  import tempfile
  with tempfile.TemporaryDirectory()as tmp:
   path=pathlib.Path(tmp)/'changed.pdf'
   path.write_bytes((ROOT/'tests/fixtures/2026-11-17-ambiguous.pdf').read_bytes()+b'\n')
   with self.assertRaisesRegex(checker.SourceReviewRequired,'Unresolved numeric hospital cell on page 4: 2'):
    checker.extract_pdf(path,'2026-11-17',[])
 def test_future_failure_does_not_block_verified_current_sources(self):
  import datetime
  today=datetime.datetime.now(checker.ZoneInfo('Europe/Athens')).date()
  dates=[(today+datetime.timedelta(days=n)).isoformat()for n in [-1,0,1]]
  sources=[{'date':d,'sourceHash':'a'*64,'sourceUrl':'https://www.moh.gov.gr/?fdl='+str(n+1),'sourceLabel':d+'.pdf'}for n,d in enumerate(dates)]
  report={'method':'independent-pdfplumber-v1','runId':'test-run','sourceCheckedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'days':sources[:2],'sources':sources,'issues':[dates[2]+': SourceReviewRequired ambiguous cell']}
  result={'passed':False,'days':[{'date':d,'entries':1,'issues':[]}for d in dates[:2]]}
  checker.SOURCE_MIRROR_ALLOWED=False
  manifest=checker.verified_manifest(report,result)
  self.assertEqual(manifest['days'],sources[:2]);self.assertEqual(manifest['blockedDays'],sources[2:]);self.assertTrue(manifest['passed'])
  result['days'][0]['issues']=['record_mismatch']
  with self.assertRaises(ValueError):checker.verified_manifest(report,result)
  result['days'][0]['issues']=[];report['issues']=['Official publication index unavailable']
  with self.assertRaises(ValueError):checker.verified_manifest(report,result)
 def test_blocked_mirror_source_does_not_fall_back_to_inaccessible_network(self):
  checker.SOURCE_MIRROR_ALLOWED=True
  with patch.object(checker,'mirror_source_bytes',side_effect=checker.SourceReviewRequired('Official source requires review')),patch.object(checker.urllib.request,'urlopen')as network:
   with self.assertRaises(checker.SourceReviewRequired):checker.fetch_bytes(checker.SOURCE)
   network.assert_not_called()
  checker.SOURCE_MIRROR_ALLOWED=False

if __name__=='__main__':unittest.main()
