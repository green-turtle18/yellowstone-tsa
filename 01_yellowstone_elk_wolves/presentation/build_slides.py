"""Create an editable OOXML presentation without external authoring dependencies."""
from pathlib import Path
from xml.sax.saxutils import escape as E
import zipfile,json,csv,io
ROOT=Path(__file__).resolve().parent
NS='http://schemas.openxmlformats.org'
A=NS+'/drawingml/2006/main';P=NS+'/presentationml/2006/main';R=NS+'/officeDocument/2006/relationships'
W,H=12192000,6858000
DARK='193B32';INK='24352F';GRAY='58665F';BG='F7F7F2';ACCENT='9B572B'
def emu(x):return int(x*914400)
def para(text,size=22,color=INK,bold=False):
 return f'<a:p><a:pPr/><a:r><a:rPr lang="en-US" sz="{size*100}" b="{int(bold)}"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:latin typeface="Arial"/></a:rPr><a:t>{E(str(text))}</a:t></a:r><a:endParaRPr lang="en-US" sz="{size*100}"/></a:p>'
def box(i,text,x,y,w,h,size=22,color=INK,bold=False):
 return f'<p:sp><p:nvSpPr><p:cNvPr id="{i}" name="Text {i}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0"/><a:lstStyle/>'+''.join(para(t,size,color,bold) for t in text.split('\n'))+'</p:txBody></p:sp>'
def table(i,rows,widths,y,rowh=.64,size=20):
 xml=f'<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="{i}" name="Evidence table"/><p:cNvGraphicFramePr/><p:nvPr/></p:nvGraphicFramePr><p:xfrm><a:off x="{emu(.65)}" y="{emu(y)}"/><a:ext cx="{emu(sum(widths))}" cy="{emu(rowh*len(rows))}"/></p:xfrm><a:graphic><a:graphicData uri="{A}/table"><a:tbl><a:tblPr firstRow="1" bandRow="0"/><a:tblGrid>'+''.join(f'<a:gridCol w="{emu(w)}"/>' for w in widths)+'</a:tblGrid>'
 for n,row in enumerate(rows):
  xml+=f'<a:tr h="{emu(rowh)}">'
  for val in row:
   xml+='<a:tc><a:txBody><a:bodyPr/><a:lstStyle/>'+para(val,size,'FFFFFF' if n==0 else INK,n==0)+f'</a:txBody><a:tcPr marL="120000" marR="100000" marT="100000" marB="70000"><a:solidFill><a:srgbClr val="{DARK if n==0 else ("FFFFFF" if n%2 else "EDEFE8")}"/></a:solidFill></a:tcPr></a:tc>'
  xml+='</a:tr>'
 return xml+'</a:tbl></a:graphicData></a:graphic></p:graphicFrame>'
# Read plotted evidence directly from the current pipeline outputs.
def read_csv(path):
 with path.open(newline='') as f:return list(csv.DictReader(f))
T=ROOT.parent/'reports'/'tables'
forecast=read_csv(ROOT.parent/'supplements/gap_research/forecast_sensitivity.csv')
removals=read_csv(T/'q6_removals_comparison.csv')
models=['drift','wolves_only','full_conditional']
chart_specs=[
 ('bar',['Drift','Wolf-only','Full conditional'],[(label,[float(next(r['MAE'] for r in forecast if r['model']==m and r['scenario']==scenario)) for m in models]) for label,scenario in [('Primary','baseline'),('Recovered wolves','wolf_gap_candidate')]],'Mean absolute error (elk)'),
 ('line',[r['Year'] for r in removals],[(label,[float(r[col]) for r in removals]) for label,col in [('Estimated wolf kills','Estimated_wolf_kills'),('Published hunting / late hunt','Published_hunting_removals'),('Fall + late hunt','Harvest_Total')]],'Elk removed per winter')]
def chart_frame(i,index,x,y,w,h):
 return f'<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="{i}" name="Editable evidence chart"/><p:cNvGraphicFramePr/><p:nvPr/></p:nvGraphicFramePr><p:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></p:xfrm><a:graphic><a:graphicData uri="{NS}/drawingml/2006/chart"><c:chart xmlns:c="{NS}/drawingml/2006/chart" r:id="rIdChart{index}"/></a:graphicData></a:graphic></p:graphicFrame>'
slides=[]
def add(title,subtitle,parts,notes,source):
 n=len(slides)+1
 shapes=box(2,title,.65,.45,12,1.05,32,DARK,True)+box(3,subtitle,.65,1.48,12,.65,19,GRAY)
 for j,part in enumerate(parts,4):
  if part[0]=='c':shapes+=chart_frame(j,*part[1:])
  elif part[0]=='t':shapes+=table(j,*part[1:])
  else:shapes+=box(j,*part[1:])
 shapes+=box(90,source,.65,6.93,11.2,.35,10,GRAY)+box(91,str(n),12.05,6.93,.45,.35,11,GRAY)
 slides.append((shapes,notes,title))
add('Yellowstone elk and wolves','Person 1 findings • Annual time-series analysis, 1984–2025',[
 ('b','How much do wolves help explain and predict elk counts?',.65,2.35,11.8,1.1,32,DARK,True),
 ('b','The current models show an uncertain wolf association and only a small forecasting gain.',.65,3.7,11.5,1.1,26,INK,False),
 ('b','Scope: drivers and feedback, winter conditions, structural change, removals and viability scenarios.',.65,5.05,11.6,.9,21,GRAY,False),
 ('b','Current-data conclusions, including the Isle Royale comparison.',.65,6.15,11.6,.45,18,ACCENT,False)],
 'The primary dataset is the corrected, flagged Yellowstone master, with 42 annual rows. Numerical entries include estimates and are not 42 fully comparable observations. Model samples differ. Recovered wolf counts are a separate sensitivity scenario. Q0 data audit, Q1 drivers, Q2 feedback, Q3 predictions, Q4 winter, Q5 breaks, Q6 removals, Q7 viability and R observation error are covered. Source: reports/CONCLUSIONS.md and reports/RESULTS.md. Prepared 20 November 2026.','Source: reports/CONCLUSIONS.md • Current analysis, 20 November 2026')
add('Wolf effects and feedback remain uncertain','Q1–Q2: annual elk log growth and changes in northern wolf numbers',[
 ('t',[['Test','Estimate or result','p-value'],['Wolf-only model','−0.0305 per +10 wolves','0.120'],['Full driver model','−0.0273 per +10 wolves','0.408'],['Wolves predict elk, VAR(1)','No clear predictive feedback','0.176'],['Elk predict wolves, VAR(1)','No clear predictive feedback','0.797']],[4.35,5.25,2.3],2.35,.65,20),
 ('b','Wolf-only 95% CI: −0.0690 to +0.0080 (n = 40).\nAIC and BIC prefer zero lags within the tested range.',.65,5.85,11.8,.85,20,INK,False)],
 'The regressor is (wolves[t−1]−wolves[t−2])/10, and the outcome is log(elk[t])−log(elk[t−1]). A ten-wolf increase refers to the preceding annual change, not a level effect. The wolf-only interval includes negative and small positive associations. Full model includes the other covariates. Non-significance does not prove no biological effect. Granger tests concern predictive information, not causation. Both AIC and BIC prefer lag 0. Sources: reports/tables/q1_coefficients.csv, q2_granger.csv, q2_lag_selection.csv.','Sources: q1_coefficients.csv, q2_granger.csv, q2_lag_selection.csv')
add('Wolves add little forecasting accuracy','Q3: mean absolute error in elk, on the same nine eligible years',[
 ('c',1,.65,2.15,11.9,3.25),
 ('b','Wolf-only gain over drift: 1.7% in the primary analysis.\nReplacing five interpolated wolf counts barely changes that result.',.65,5.45,11.8,.9,22,INK,False),
 ('b','Small retrospective sample. Predictor release dates are unverified.',.65,6.4,11.8,.4,17,ACCENT,False)],
 'Evaluation years: 2011, 2012, 2013, 2017, 2018, 2019, 2023, 2024, 2025. Training transformations use training data only, and scoring excludes imputed targets/prior counts and unresolved coverage. Full-model predictors include information potentially after some surveys. These are conditional retrospective predictions. No statistical significance is asserted for MAE differences. Candidate northern counts for 1996–2000 are 19,32,42,35,65. Conflicting source values for other years remain unresolved. Sources: reports/tables/q3_scores.csv and supplements/gap_research/forecast_sensitivity.csv.','Sources: q3_scores.csv and gap_research/forecast_sensitivity.csv')
add('Winter and break tests give limited evidence','Q4–Q5 and R: different tests answer different questions',[
 ('t',[['Analysis','Finding'],['Wolf × winter interaction','p = 0.990'],['Breaks in mean annual log growth','BIC selects no breaks'],['Separate continuous trend-break search','Lowest residual error at 2014'],['State-space survey-error model','Process SD 0.112; observation SD 0.087']],[6.4,5.5],2.3,.72,19),
 ('b','The 2014 trend result does not identify a cause.\nSurvey-error modelling still cannot resolve unknown sightability bias.',.65,6.2,11.8,.65,19,INK,False)],
 'Winter interaction does not distinguish additive from compensatory mortality. Exposure windows are not fully aligned to survey dates. Growth-mean break selection and the trend-break search are different hypotheses. The selected trend date is not a formal causal attribution or a Bai–Perron confidence set. The growth-state model converges with 33 observed values on a 40-year model grid. SDs are on the fitted latent log-count/process and observation scale, not numbers of elk. Spatial mismatches remain. Sources: q4_interaction.csv, q5_mean_breaks.csv, q5_trend_breaks.csv, r_variance_components.csv.','Sources: q4_interaction.csv, q5_*breaks.csv, r_variance_components.csv')
add('The hunting definition changes the comparison','Q6: published estimated wolf kills and hunting removals, 1996–2004',[
 ('c',2,.65,2.05,8.5,3.65),
 ('b','1996–2004 totals\n12,512 wolf kills\n11,653 published hunt\n\nCrossover year\n2000: published hunt\n2001: fall + late hunt',9.45,2.4,3.25,3.1,18,INK,False),
 ('b','All nine published hunting figures match late hunt.\nThe broader total includes estimated fall harvest in 1998–2004.',.65,5.85,11.8,.75,20,INK,False),
 ('b','Different age profiles mean removal counts alone cannot rank demographic effects.',.65,6.55,11.8,.35,16,ACCENT,False)],
 'Eberhardt et al. (2007), A Seventy-Year History of Trends in Yellowstone’s Northern Elk Herd, J Wildlife Management 71:594–602, DOI 10.2193/2005-770. Table 1, PDF page 5 / printed p.598, user-provided paper. Total kills by year: 517,591,788,1182,1084,1773,1897,2069,2611. Hunting: 1400,2465,1313,1683,974,1259,1139,718,702. Winter-year labels match existing harvest seasons. The plotted fall-plus-late series includes estimated fall components for 1998–2004. No annual confidence intervals are available for the wolf estimates. Published 0.26 adjustment reflects prime-age classes and is retained separately, not used as total kills. No annual uncertainty intervals are supplied. The joint standardised regression has p=0.145 for wolves and p=0.907 for harvest, so it cannot establish a ranking either. Sources: supplements/q6_removals/README.md and reports/tables/q6_hunting_vs_wolves.csv.','Source: Eberhardt et al. (2007), Table 1, p.598 • DOI: 10.2193/2005-770')
risk=read_csv(T/'q7_threshold_probabilities.csv')
risk10=[r for r in risk if int(r['horizon'])==10]
chart_specs.append(('bar',['Below 2,000','Below 4,000'],[('GBM continuous',[100*float(r['GBM_continuous']) for r in risk10]),('GBM annual monitoring',[100*float(r['GBM_annual_sim']) for r in risk10])],'10-year crossing probability (%)'))
add('Viability estimates are uncertain scenarios','Q7: ten-year survey-count threshold crossings, starting at 7,226',[
 ('c',3,.65,2.15,8.1,3.7),
 ('b','Below 4,000\n38.7% continuous\nBootstrap interval\n6.9%–78.7%',9.15,2.65,3.5,2.25,23,ACCENT,True),
 ('b','27 eligible annual transitions. Drift −0.0157, volatility 0.1790.\nGompertz φ = 0.9973, bootstrap LR p = 0.986.',.65,5.95,11.8,.7,19,INK,False),
 ('b','Monitoring frequency changes the result. These are model scenarios, not extinction risks.',.65,6.65,11.8,.3,16,GRAY,False)],
 'Continuous first passage counts any crossing during ten years. Annual monitoring checks only at yearly intervals and can miss crossings between observations. The bootstrap interval covers parameter uncertainty conditional on GBM, not systematic survey bias or future ecological changes. Thresholds apply to a survey-count index. Source: reports/tables/q7_threshold_probabilities.csv and q7_parameters.csv. No management or extinction forecast is asserted.',
 'Sources: q7_parameters.csv and q7_threshold_probabilities.csv')
comparison_dir=ROOT.parents[1]/'05_synthesis/reports/tables'
comparison={r['system']:r for r in read_csv(comparison_dir/'comparison_summary.csv') if r['scenario']=='common_1984_2015'}
matched_forecasts={r['system']:r for r in read_csv(comparison_dir/'matched_calendar_forecast_scores.csv') if r['scenario']=='common_1984_2015' and r['model']=='ARIMAX wolves'}
chart_specs.append(('bar',['Yellowstone','Isle Royale'],[('MAPE gain over drift',[float(matched_forecasts[name]['MAPE gain over drift %']) for name in ['Yellowstone','Isle Royale']])],'Forecast improvement over drift (%)'))
add('Yellowstone and Isle Royale comparison','Shared 1984–2015 model window, forecasts scored on the same 22 years',[
 ('c',4,.65,2.15,7.0,3.55),
 ('b',f"Wolf-to-prey Granger p\nYellowstone: {float(comparison['Yellowstone']['granger_wolf_p']):.3f}\nIsle Royale: {float(comparison['Isle Royale']['granger_wolf_p']):.3f}\n\nDensity-adjusted wolf p\nYellowstone: {float(comparison['Yellowstone']['p']):.3f}\nIsle Royale: {float(comparison['Isle Royale']['p']):.3f}",8.1,2.35,4.55,3.2,20,INK,False),
 ('b','Clearer predictive evidence in Isle Royale under these models.\nThis does not establish a causal difference between ecosystems.',.65,5.85,11.8,.8,21,DARK,True),
 ('b','Survey differences, reconstructed counts and small sensitivity samples remain.',.65,6.65,11.8,.3,16,ACCENT,False)],
 'Source: 05_synthesis/report/COMPARISON.md and reports/tables in that folder. Both systems use Person 4 specification 1.3. Lagged wolf levels and density differ from the original Yellowstone change-in-wolves model. Full coefficients and 95% intervals are in comparison_summary.csv. Negative forecast gain means worse performance than drift. Shared 22-year forecasts include filled training inputs; strict observed-input sensitivity has only seven shared years. Differences in significance do not prove different ecological effects. Survey timing, source conflicts and missing Isle Royale kill rates remain documented.',
 'Sources: comparison_summary.csv and matched_calendar_forecast_scores.csv')
GROUP='<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
def rels(items):return '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+''.join(f'<Relationship Id="{id}" Type="{R}/{typ}" Target="{target}"/>' for id,typ,target in items)+'</Relationships>'
def root(tag):return f'<{tag} xmlns:a="{A}" xmlns:r="{R}" xmlns:p="{P}">'
parts={}
parts['_rels/.rels']=rels([('rId1','officeDocument','ppt/presentation.xml')])
parts['ppt/presentation.xml']=root('p:presentation')+'<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst><p:sldIdLst>'+''.join(f'<p:sldId id="{255+i}" r:id="rId{i+1}"/>' for i in range(1,8))+f'</p:sldIdLst><p:sldSz cx="{W}" cy="{H}"/><p:notesSz cx="6858000" cy="9144000"/></p:presentation>'
parts['ppt/_rels/presentation.xml.rels']=rels([('rId1','slideMaster','slideMasters/slideMaster1.xml')]+[(f'rId{i+1}','slide',f'slides/slide{i}.xml') for i in range(1,8)])
parts['ppt/slideMasters/slideMaster1.xml']=root('p:sldMaster')+'<p:cSld><p:spTree>'+GROUP+'</p:spTree></p:cSld><p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="dk2"/><p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>'
parts['ppt/slideMasters/_rels/slideMaster1.xml.rels']=rels([('rId1','slideLayout','../slideLayouts/slideLayout1.xml'),('rId2','theme','../theme/theme1.xml')])
parts['ppt/slideLayouts/slideLayout1.xml']=root('p:sldLayout').replace('>',' type="blank" preserve="1">',1)+'<p:cSld name="Blank"><p:spTree>'+GROUP+'</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'
parts['ppt/slideLayouts/_rels/slideLayout1.xml.rels']=rels([('rId1','slideMaster','../slideMasters/slideMaster1.xml')])
colors={'dk1':INK,'lt1':'FFFFFF','dk2':DARK,'lt2':BG,'accent1':DARK,'accent2':ACCENT,'accent3':'829A7C','accent4':'BCC8B6','accent5':'E1C99E','accent6':'657A82','hlink':'0563C1','folHlink':'954F72'}
parts['ppt/theme/theme1.xml']=f'<a:theme xmlns:a="{A}" name="Yellowstone"><a:themeElements><a:clrScheme name="Forest">'+''.join(f'<a:{k}><a:srgbClr val="{v}"/></a:{k}>' for k,v in colors.items())+'</a:clrScheme><a:fontScheme name="Arial"><a:majorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme><a:fmtScheme name="Simple"><a:fillStyleLst>'+('<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'*3)+'</a:fillStyleLst><a:lnStyleLst>'+('<a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>'*3)+'</a:lnStyleLst><a:effectStyleLst>'+('<a:effectStyle><a:effectLst/></a:effectStyle>'*3)+'</a:effectStyleLst><a:bgFillStyleLst>'+('<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'*3)+'</a:bgFillStyleLst></a:fmtScheme></a:themeElements></a:theme>'
for i,(shapes,notes,title) in enumerate(slides,1):
 parts[f'ppt/slides/slide{i}.xml']=root('p:sld')+f'<p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="{BG}"/></a:solidFill><a:effectLst/></p:bgPr></p:bg><p:spTree>'+GROUP+shapes+'</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'
 parts[f'ppt/slides/_rels/slide{i}.xml.rels']=rels([('rId1','slideLayout','../slideLayouts/slideLayout1.xml'),('rId2','notesSlide',f'../notesSlides/notesSlide{i}.xml')]+([(f'rIdChart{ {3:1,5:2,6:3,7:4}[i]}','chart',f'../charts/chart{ {3:1,5:2,6:3,7:4}[i]}.xml')] if i in (3,5,6,7) else []))
 note=box(2,notes,0,0,7,9,12).replace('<p:nvPr/>','<p:nvPr><p:ph type="body" idx="1"/></p:nvPr>')
 parts[f'ppt/notesSlides/notesSlide{i}.xml']=root('p:notes')+'<p:cSld><p:spTree>'+GROUP+note+'</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:notes>'
 parts[f'ppt/notesSlides/_rels/notesSlide{i}.xml.rels']=rels([('rId1','slide',f'../slides/slide{i}.xml')])
def chart_xml(kind,categories,series,axis_title,index):
 C=NS+'/drawingml/2006/chart'
 def cache(vals,string=False):
  tag='str' if string else 'num'
  return f'<c:{tag}Cache>'+('' if string else '<c:formatCode>0.0</c:formatCode>')+f'<c:ptCount val="{len(vals)}"/>'+''.join(f'<c:pt idx="{j}"><c:v>{E(str(v))}</c:v></c:pt>' for j,v in enumerate(vals))+f'</c:{tag}Cache>'
 tx='<c:txPr><a:bodyPr/><a:lstStyle/><a:p><a:pPr><a:defRPr sz="1400"><a:solidFill><a:srgbClr val="24352F"/></a:solidFill><a:latin typeface="Arial"/></a:defRPr></a:pPr><a:endParaRPr lang="en-US"/></a:p></c:txPr>'
 out=f'<c:chartSpace xmlns:c="{C}" xmlns:a="{A}" xmlns:r="{R}"><c:lang val="en-US"/><c:chart><c:autoTitleDeleted val="1"/><c:plotArea><c:layout/>'
 out+= '<c:barChart><c:barDir val="col"/><c:grouping val="clustered"/>' if kind=='bar' else '<c:lineChart><c:grouping val="standard"/>'
 for j,(label,vals) in enumerate(series):
  col=chr(66+j);color=[DARK,ACCENT,'657A82'][j]
  out+=f'<c:ser><c:idx val="{j}"/><c:order val="{j}"/><c:tx><c:strRef><c:f>Data!${col}$1</c:f>'+cache([label],True)+'</c:strRef></c:tx>'
  out+=f'<c:spPr><a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:ln w="28575"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'+('<a:prstDash val="dash"/>' if j==2 else '')+'</a:ln></c:spPr>'
  if kind=='line':out+='<c:marker><c:symbol val="circle"/><c:size val="5"/></c:marker>'
  out+='<c:cat><c:strRef><c:f>Data!$A$2:$A$'+str(len(categories)+1)+'</c:f>'+cache(categories,True)+'</c:strRef></c:cat>'
  out+=f'<c:val><c:numRef><c:f>Data!${col}$2:${col}${len(categories)+1}</c:f>'+cache(vals)+'</c:numRef></c:val>'
  if kind=='line':out+='<c:smooth val="0"/>'
  out+='</c:ser>'
 if kind=='bar':out+='<c:dLbls><c:numFmt formatCode="0.0" sourceLinked="0"/>'+tx+'<c:dLblPos val="outEnd"/><c:showLegendKey val="0"/><c:showVal val="1"/><c:showCatName val="0"/><c:showSerName val="0"/></c:dLbls><c:gapWidth val="90"/><c:overlap val="0"/>'
 out+='<c:axId val="100"/><c:axId val="200"/>'+('</c:barChart>' if kind=='bar' else '</c:lineChart>')
 out+='<c:catAx><c:axId val="100"/><c:scaling><c:orientation val="minMax"/></c:scaling><c:delete val="0"/><c:axPos val="b"/><c:tickLblPos val="nextTo"/>'+tx+'<c:crossAx val="200"/><c:crosses val="autoZero"/><c:auto val="1"/><c:lblAlgn val="ctr"/><c:lblOffset val="100"/></c:catAx>'
 title='<c:title><c:tx><c:rich><a:bodyPr/><a:lstStyle/>'+para(axis_title,14)+'</c:rich></c:tx><c:overlay val="0"/></c:title>'
 out+='<c:valAx><c:axId val="200"/><c:scaling><c:orientation val="minMax"/><c:min val="0"/></c:scaling><c:delete val="0"/><c:axPos val="l"/><c:majorGridlines/>'+title+'<c:numFmt formatCode="#,##0" sourceLinked="0"/><c:tickLblPos val="nextTo"/>'+tx+'<c:crossAx val="100"/><c:crosses val="autoZero"/><c:crossBetween val="between"/></c:valAx></c:plotArea><c:legend><c:legendPos val="b"/><c:overlay val="0"/>'+tx+'</c:legend><c:plotVisOnly val="1"/><c:dispBlanksAs val="gap"/></c:chart>'+tx+'<c:externalData r:id="rId1"><c:autoUpdate val="0"/></c:externalData></c:chartSpace>'
 if index==4:out=out.replace('<c:min val="0"/>','<c:min val="-10"/><c:max val="15"/>')
 return out

def workbook(categories,series):
 # Minimal embedded spreadsheet enables PowerPoint Edit Data.
 X=NS+'/spreadsheetml/2006/main'
 rows=[['Category']+[label for label,_ in series]]+[[cat]+[vals[i] for _,vals in series] for i,cat in enumerate(categories)]
 sheet=f'<worksheet xmlns="{X}"><sheetData>'
 for i,row in enumerate(rows,1):
  sheet+=f'<row r="{i}">'
  for j,v in enumerate(row):
   ref=f'{chr(65+j)}{i}'
   sheet+=(f'<c r="{ref}"><v>{v}</v></c>' if isinstance(v,(int,float)) else f'<c r="{ref}" t="inlineStr"><is><t>{E(str(v))}</t></is></c>')
  sheet+='</row>'
 sheet+='</sheetData></worksheet>'
 buf=io.BytesIO()
 with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
  z.writestr('_rels/.rels',rels([('rId1','officeDocument','xl/workbook.xml')]))
  z.writestr('xl/workbook.xml',f'<workbook xmlns="{X}" xmlns:r="{R}"><sheets><sheet name="Data" sheetId="1" r:id="rId1"/></sheets></workbook>')
  z.writestr('xl/_rels/workbook.xml.rels',rels([('rId1','worksheet','worksheets/sheet1.xml')]))
  z.writestr('xl/worksheets/sheet1.xml',sheet)
 return buf.getvalue()
for index,(kind,categories,series,axis_title) in enumerate(chart_specs,1):
 parts[f'ppt/charts/chart{index}.xml']=chart_xml(kind,categories,series,axis_title,index)
 parts[f'ppt/charts/_rels/chart{index}.xml.rels']=rels([('rId1','package',f'../embeddings/chart{index}.xlsx')])
 parts[f'ppt/embeddings/chart{index}.xlsx']=workbook(categories,series)
ct={'ppt/presentation.xml':'presentation.main','ppt/slideMasters/slideMaster1.xml':'slideMaster','ppt/slideLayouts/slideLayout1.xml':'slideLayout',**{f'ppt/slides/slide{i}.xml':'slide' for i in range(1,8)},**{f'ppt/notesSlides/notesSlide{i}.xml':'notesSlide' for i in range(1,8)}}
parts['[Content_Types].xml']='<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'+''.join(f'<Override PartName="/{k}" ContentType="application/vnd.openxmlformats-officedocument.presentationml.{v}+xml"/>' for k,v in ct.items())+'<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/></Types>'
parts['[Content_Types].xml']=parts['[Content_Types].xml'].replace('</Types>','<Default Extension="xlsx" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"/>'+''.join(f'<Override PartName="/ppt/charts/chart{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.drawingml.chart+xml"/>' for i in range(1,len(chart_specs)+1))+'</Types>')
with zipfile.ZipFile(ROOT/'Yellowstone_Findings.pptx','w',zipfile.ZIP_DEFLATED) as z:
 for name,value in parts.items():z.writestr(name,value if isinstance(value,bytes) else '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'+value)
(ROOT/'speaker_notes.md').write_text('\n\n'.join(f'## {i}. {title}\n\n{notes}' for i,(_,notes,title) in enumerate(slides,1)))
print('Created 7-slide editable deck with four data-linked native charts and speaker notes.')
