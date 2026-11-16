import importlib.util,json,pathlib,unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('checker',ROOT/'cloud-check.py')
checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
class Recovery(unittest.TestCase):
 def test_ambiguous_numeric_source_is_not_silently_omitted(self):
  directory=[]
  with self.assertRaisesRegex(checker.SourceReviewRequired,'Unresolved numeric hospital cell on page 4: 2'):
   checker.extract_pdf(ROOT/'tests/fixtures/2026-11-17-ambiguous.pdf','2026-11-17',directory)
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
