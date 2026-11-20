"""Check slide package links and chart caches against current numerical outputs."""
from pathlib import Path
import csv,zipfile,posixpath,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
C={'c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
def read(p):
 with p.open() as f:return list(csv.DictReader(f))
forecast=read(ROOT/'supplements/gap_research/forecast_sensitivity.csv')
removals=read(ROOT/'reports/tables/q6_removals_comparison.csv')
risk=[r for r in read(ROOT/'reports/tables/q7_threshold_probabilities.csv') if int(r['horizon'])==10]
matched=read(ROOT.parent/'05_synthesis/reports/tables/matched_calendar_forecast_scores.csv')
expected=[
 [[float(next(r['MAE'] for r in forecast if r['model']==m and r['scenario']==sc)) for m in ['drift','wolves_only','full_conditional']] for sc in ['baseline','wolf_gap_candidate']],
 [[float(r[k]) for r in removals] for k in ['Estimated_wolf_kills','Published_hunting_removals','Harvest_Total']],
 [[100*float(r[k]) for r in risk] for k in ['GBM_continuous','GBM_annual_sim']],
 [[float(next(r['MAPE gain over drift %'] for r in matched if r['system']==name and r['scenario']=='common_1984_2015' and r['model']=='ARIMAX wolves')) for name in ['Yellowstone','Isle Royale']]]
]
with zipfile.ZipFile(ROOT/'presentation/Yellowstone_Findings.pptx') as z:
 names=z.namelist()
 for name in names:
  if name.endswith(('.xml','.rels')):ET.fromstring(z.read(name))
  if name.endswith('.rels'):
   for rel in ET.fromstring(z.read(name)):
    target=posixpath.normpath(posixpath.join(posixpath.dirname(posixpath.dirname(name)),rel.attrib['Target']))
    assert target in names,(name,target)
 for index,series in enumerate(expected,1):
  chart=ET.fromstring(z.read(f'ppt/charts/chart{index}.xml'))
  actual=[[float(v.text) for v in ser.findall('c:val/c:numRef/c:numCache/c:pt/c:v',C)] for ser in chart.findall('.//c:ser',C)]
  assert actual==series,(index,actual,series)
 assert float(ET.fromstring(z.read('ppt/charts/chart4.xml')).find('.//c:valAx/c:scaling/c:min',C).attrib['val'])<0
 assert len([n for n in names if n.startswith('ppt/slides/slide') and n.endswith('.xml')])==7
print('Presentation checks passed: seven slides, four charts, exact source values and valid package links.')
