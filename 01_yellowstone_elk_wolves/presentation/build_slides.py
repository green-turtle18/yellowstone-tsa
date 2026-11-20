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
slide_charts={}
def add(title,subtitle,parts,notes,source):
 n=len(slides)+1
 shapes=box(2,title,.65,.45,12,1.05,32,DARK,True)+box(3,subtitle,.65,1.48,12,.65,19,GRAY)
 for j,part in enumerate(parts,4):
  if part[0]=='c':
   shapes+=chart_frame(j,*part[1:]);slide_charts[n]=part[1]
  elif part[0]=='t':shapes+=table(j,*part[1:])
  else:shapes+=box(j,*part[1:])
 shapes+=box(90,source,.65,6.93,11.2,.35,10,GRAY)+box(91,str(n),12.05,6.93,.45,.35,11,GRAY)
 slides.append((shapes,notes,title))
# Presentation narrative: equations and interpretation before numerical detail.
risk=read_csv(T/'q7_threshold_probabilities.csv')
risk10=[r for r in risk if int(r['horizon'])==10]
chart_specs.append(('bar',['Below 2,000','Below 4,000'],[('GBM continuous',[100*float(r['GBM_continuous']) for r in risk10]),('GBM annual monitoring',[100*float(r['GBM_annual_sim']) for r in risk10])],'10-year crossing probability (%)'))
comparison_dir=ROOT.parents[1]/'05_synthesis/reports/tables'
comparison={r['system']:r for r in read_csv(comparison_dir/'comparison_summary.csv') if r['scenario']=='common_1984_2015'}
matched_forecasts={r['system']:r for r in read_csv(comparison_dir/'matched_calendar_forecast_scores.csv') if r['scenario']=='common_1984_2015' and r['model']=='ARIMAX wolves'}
chart_specs.append(('bar',['Yellowstone','Isle Royale'],[('MAPE gain over drift',[float(matched_forecasts[name]['MAPE gain over drift %']) for name in ['Yellowstone','Isle Royale']])],'Forecast improvement over drift (%)'))
coefficients=read_csv(T/'q1_coefficients.csv')
wolf=next(r for r in coefficients if r['model']=='d_wolves' and r['term']=='d_wolves')
full=next(r for r in coefficients if r['model']=='full' and r['term']=='d_wolves')
granger=[r for r in read_csv(T/'q2_granger.csv') if r['model']=='VAR(1)']
def body(text,y,size=24,color=INK,bold=False):return ('b',text,.7,y,11.8,.9,size,color,bold)
def cue(text):return body(text,6.25,21,ACCENT,True)

add('Do wolves help explain elk population change?',
 'Part 1: northern Yellowstone, 1984–2025',[
 body('We separate three questions: association, prediction and future risk.',2.25,27,DARK,True),
 body('42 annual rows combine elk counts with wolves, hunting, bison,\nwinter severity, vegetation and climate.',3.4),
 body('Survey counts can change when animals change or when detection changes.\nEstimated entries remain flagged and sensitivity checks use alternative inputs.',4.65,22),
 cue('Main message: an uncertain wolf association and only a small forecast gain.')],
 'OPEN: We are testing whether wolves add information about elk changes, rather than assuming that every decline after reintroduction was caused by wolves.\nEXPLAIN: Annual observational data contain several competing influences. Surveys are counts, not complete censuses. The 42 rows do not mean 42 equally comparable direct observations.\nDATA CAVEAT: Whole-herd coverage in 2020–2021, some historical estimates, wolf/elk geography and climate metadata remain unresolved. Recovered wolf counts for 1996–2000 form a separate scenario.\nTRANSITION: First define the outcome and the competing models. Sources: reports/CONCLUSIONS.md and HANDOFF.md.',
 'Sources: CONCLUSIONS.md and HANDOFF.md')

add('Models considered: growth and its drivers',
 'N = elk count; W = northern wolf count; t = annual observation',[
 body('Outcome: gₜ = log(Nₜ / Nₜ₋₁)      Wolf change: xₜ = (Wₜ₋₁ − Wₜ₋₂) / 10',2.15,25,DARK,True),
 body('Drift benchmark: gₜ = α + εₜ\nWolf-only model: gₜ = α + βxₜ + uₜ',3.15,25),
 body('Full model: gₜ = α + βxₜ + γ′Zₜ + uₜ\nZ contains the other drivers, transformed and aligned to their time windows.',4.35,23),
 body('Headline regressions assume uncorrelated errors across years.',5.4,23),
 cue('We check stationarity, compare model fit and test what remains in the errors.')],
 'OPEN: We model proportional annual change, not just the raw number of elk.\nEXAMPLE: A fall from 10,000 to 9,000 gives log(0.9) = −0.1054, which is an exact 10% decline. A preceding increase of ten wolves makes x equal to one.\nMODELS: We compare drift, single-driver models and a full model. The full driver set includes lagged bison log change, NDVI, precipitation, PDSI, harvest rate and winter severity. Timing and transformation rules differ by variable.\nERROR MODELS: AR(p) uses previous values, MA(q) uses previous innovations, and ARMA combines both. In regression-with-ARMA-errors notation, u_t = sum(phi_i u_(t-i)) + epsilon_t + sum(theta_j epsilon_(t-j)). Primary driver estimates use white-noise errors, with dynamic-error robustness checks including MA(2). EDA compares candidate ARMA orders.\nCHECKS: ADF tests a unit-root null; KPSS tests stationarity. AIC/BIC penalise complexity. Ljung–Box checks residual autocorrelation and ARCH LM checks conditional variance patterns. Forecast transformations are learned within each training window. Source: scripts/analysis.py, q1_stationarity.csv and q1_diagnostics.csv.',
 'Sources: analysis.py, q1_stationarity.csv and q1_diagnostics.csv')

add('The wolf estimate is negative but uncertain',
 'Q1: H₀: wolf coefficient β = 0 in each model (no conditional linear association)',[
 body(f"Wolf-only estimate: β = {float(wolf['estimate']):.4f}     p = {float(wolf['p']):.3f}",2.2,29,DARK,True),
 body(f"95% interval: {float(wolf['ci_low']):.4f} to +{float(wolf['ci_high']):.4f}\nThe interval includes zero, negative effects and small positive effects.",3.25,24),
 body(f"Adding other drivers does not make the wolf association clear.\nFull-model wolf estimate: {float(full['estimate']):.4f}, p = {float(full['p']):.3f}.",4.6,24),
 cue('A non-significant result does not show that wolves have no biological effect.')],
 'OPEN: The point estimate is negative, but its uncertainty is central to the conclusion.\nEXAMPLE: For a ten-wolf increase in the preceding annual change, the model predicts 0.0305 lower log elk growth. exp(−0.0305) is about 0.970, a roughly 3% lower prediction relative to the same model without that predictor increment. This is not a count of animals killed.\nINTERPRET: The confidence interval crosses zero and p is 0.120. The full model also does not establish an independent wolf association. Small samples, survey noise and correlated drivers limit power.\nVIVA: A p-value is calculated under the null; it is not the probability that wolves have no effect. Seven single-driver screens also have Bonferroni adjustments.\nTRANSITION: Association is one question. The next asks whether past wolves improve prediction beyond elk history. Source: q1_coefficients.csv.',
 'Source: q1_coefficients.csv')

add('Granger causality: does wolf history help?',
 'Q2: VAR(1) tests predictive information in both directions',[
 body('gₜ = a + b gₜ₋₁ + c vₜ₋₁ + εₜ\nvₜ = d + e gₜ₋₁ + f vₜ₋₁ + ηₜ',2.1,28,DARK,True),
 body('gₜ = annual log elk growth; vₜ = (Wₜ − Wₜ₋₁) / 10.\nH₀: c = 0 (wolves → elk); H₀: e = 0 (elk → wolves).',3.45,22),
 body(f"Wolves → elk: p = {float(granger[0]['p']):.3f}     Elk → wolves: p = {float(granger[1]['p']):.3f}\nNeither direction provides clear evidence in the original Yellowstone model.",4.75,23),
 cue('“Granger-causes” means “adds predictive information”, not “proves causation”.')],
 'OPEN: We first predict elk growth from its own history. Then we ask whether adding wolf history helps.\nMODEL: v is contemporary scaled wolf change, and the VAR supplies the one-year lag. Thus v_(t−1) is the same preceding wolf-change predictor used in the driver model. In the first equation c tests wolves to elk; in the second e tests elk to wolves.\nRESULTS: VAR(1) p-values are 0.176 and 0.797. The prespecified one-lag model has 28 fitted observations. VAR(2) sensitivity also does not reject either direction at 5%. Both AIC and BIC prefer zero lags among those considered, which weakens support for a feedback interpretation.\nCAVEAT: Omitted weather, observation changes and limited power can affect these tests. This is predictive information, not a controlled ecological intervention.\nTRANSITION: The forecast test asks whether any of this improves actual held-out prediction. Sources: q2_granger.csv and q2_lag_selection.csv.',
 'Sources: q2_granger.csv and q2_lag_selection.csv')

add('Forecast gains are small on held-out years',
 'Q3: expanding training windows; the same nine eligible test years',[
 ('c',1,.65,2.05,8.0,3.65),
 ('b','Train on the past.\nPredict the next year.\nCompare with drift.\n\nLower error is better.',9.05,2.6,3.5,2.4,24,INK,False),
 body('Wolf-only MAE is 986 elk versus 1,004 for drift: about 1.7% better.\nThe full conditional model performs worse; recovered wolves barely change the ranking.',5.8,21),
 ],
 'OPEN: A useful model should beat a simple forecast, not merely fit the historical record.\nEQUATIONS: Drift forecast Nhat_t = N_(t−1) exp(mean training log growth). MAE = mean(abs(actual − forecast)). Gain = 100 × (1 − model MAE / drift MAE).\nDESIGN: Train up to t−1 and predict t. Eligible years are 2011–2013, 2017–2019 and 2023–2025. Target and origin counts must meet the scoring rules. Avoid future interpolation and full-sample transformation selection.\nRESULT: Primary MAEs are 1003.8, 986.4 and 1402.1 for drift, wolf-only and full conditional. The recovered-wolf scenario gives 983.1 and 1302.1 for the two driver models.\nCAVEAT: Nine years are a small retrospective evaluation. Predictor publication dates are unverified, so do not claim established real-time forecast skill or statistically significant improvement. Sources: q3_scores.csv and forecast_sensitivity.csv.',
 'Sources: q3_scores.csv and forecast_sensitivity.csv')

add('Winter interactions and structural changes',
 'Q4–Q5: a changing association differs from a changing trend',[
 body('Interaction: gₜ = α + βxₜ + γsₜ + δxₜsₜ + uₜ\nsₜ is the transformed winter-severity predictor.',2.1,24,DARK,True),
 body('H₀: δ = 0 — the wolf slope does not vary with winter severity.\nThe fitted interaction gives p = 0.990: no clear evidence here.',3.4,24),
 body('Trend break: log(Nₜ) = a + bt + d max(0, t − τ) + uₜ\nSeparate tests select no growth-mean break, but the trend search favours 2014.',4.7,22),
 cue('The break date does not identify a cause; these tests ask different questions.')],
 'OPEN: Wolves could matter differently in severe winters. An interaction allows the wolf slope to vary with winter conditions.\nEQUATION: The wolf slope is β + δs. The displayed interaction equation is schematic; the fitted model includes its specified controls. p=0.990 gives no evidence of a changing slope in this specification. Winter exposure windows may extend beyond some surveys. This does not distinguish additive from compensatory mortality.\nBREAKS: The growth-mean search uses exact segmentation, minimum segment lengths, BIC and the zero-break option. It selects zero breaks. A separate continuous piecewise-linear trend search has lowest RSS at 2014. The hinge term changes slope without forcing a discontinuous jump.\nCAVEAT: This is not a formal Bai–Perron confidence set or causal attribution to an event. Sources: q4_interaction.csv, q5_mean_breaks.csv and q5_trend_breaks.csv.',
 'Sources: q4_interaction.csv and q5_*breaks.csv')

add('State-space model: counts contain survey noise',
 'R extension: separate latent population variation from measurement error',[
 body('Latent state: xₜ = xₜ₋₁ + μ + β′zₜ + ηₜ\nObserved log count: log(Cₜ) = xₜ + εₜ',2.1,27,DARK,True),
 body('ηₜ represents process variation; εₜ represents observation noise.\nThe Kalman filter balances model expectations with each new count.',3.5,23),
 body('A sudden count drop need not be entirely a population crash.\nEstimated process SD = 0.112; observation SD = 0.087, on the log scale.',4.75,23),
 cue('Random observation error is modelled; unknown detection bias remains unresolved.')],
 'OPEN: The observed count mixes animal dynamics with the survey process. A state-space model explicitly separates those sources of variation under its assumptions.\nNOTATION: x is the latent log abundance index, z is the aligned driver vector, eta is process noise and epsilon is observation noise. The symbol x here is not the wolf predictor on earlier slides.\nEXAMPLE: If a survey suddenly misses more elk, a model without observation error would force the full drop into population dynamics. This model can distribute it between process and observation variation.\nKALMAN: A noisy observation gets less weight than a precise one. Filtering uses information through that year. Smoothing uses later data too and is not a real-time forecast.\nLIMIT: Random-noise separation does not identify unknown sightability, changing area coverage or systematic measurement bias. The fitted state model uses 33 observed counts on a 40-year grid. Source: r_variance_components.csv and analysis.py.',
 'Sources: analysis.py and r_variance_components.csv')

add('Hunting definitions change the removals comparison',
 'Q6: published wolf-kill estimates and hunting removals, 1996–2004',[
 ('c',2,.65,2.05,8.1,3.65),
 ('b','Hunting association tests\nH₀: harvest coefficient = 0\n\nHunting-only: p = 0.324\nFull model: p = 0.501\nJoint wolf–hunt: p = 0.907\n\nAll inconclusive at 5%.',9.1,2.15,3.65,3.55,19,INK,False),
 body('Wolf-kill crossover: 2000 against late hunt; 2001 against fall + late hunt.\nInconclusive regression results do not mean hunting has no population effect.',5.85,21)],
 'OPEN: The graph compares elk removals; the adjacent tests ask whether hunting predicts annual elk growth. H₀ in each test: the harvest coefficient is zero conditional on the predictors in that model. Hunting-only p=0.324; full-model p=0.501; joint wolf–harvest p=0.907. These are different specifications, not repeated tests of an identical model. The first two estimates are negative; the joint estimate is slightly positive. None establishes no ecological effect. Totals are 12,512 estimated wolf kills and 11,653 published hunting removals. In the joint model the wolf coefficient has p=0.145, H₀: wolf coefficient=0.\nSOURCE: Eberhardt et al. (2007), Table 1, printed page 598, DOI 10.2193/2005-770. The published hunting values match late hunt in all nine years. The broader project harvest series adds fall hunting, including estimated fall components for 1998–2004.\nEXPLAIN: That definition changes the crossover from 2000 to 2001. Neither comparison supplies the age-specific reproductive impact of the removals.\nCAVEATS: Annual wolf-kill confidence intervals are unavailable in the source table. The separate 26% adjustment concerns prime adult classes and is not total kills. Additive mortality increases deaths; compensatory mortality partly replaces other deaths. These totals cannot settle that distinction. Source: q6_removals_comparison.csv.',
 'Sources: Eberhardt et al. (2007), Table 1; q1_coefficients.csv; q6_hunting_vs_wolves.csv')

add('Viability models describe uncertain scenarios',
 'Q7: survey-count thresholds, starting from 7,226',[
 body('GBM: d log(Nₜ) = μ dt + σ dBₜ\nGompertz: log(Nₜ) = a + φ log(Nₜ₋₁) + εₜ',2.05,25,DARK,True),
 ('c',3,.65,3.25,7.6,2.95),
 ('b','Below 4,000 in ten years:\n38.7% continuous crossing.\nBootstrap interval: 6.9%–78.7%.\n\nGompertz is close to a random walk.',8.65,3.5,4.0,2.5,20,INK,False),
 cue('Crossing below a count threshold is different from extinction or the year-ten endpoint.')],
 'OPEN: These models ask what paths are possible if the fitted dynamics continue. They are scenarios, not management forecasts.\nGBM: μ is average log growth, σ is volatility, and B is Brownian motion. Estimates are μ=−0.0157 and σ=0.1790 from 27 eligible adjacent transitions. The population-scale drift would be μ + σ²/2.\nGOMPERTZ: Density dependence can make log abundance return toward an equilibrium when 0<φ<1. Here φ=0.9973 and bootstrap LR p=0.986 (H₀: φ=1, random walk with drift; no mean reversion) provide little support over a random walk.\nGRAPH: Annual checks miss crossings between years. A count may fall below 4,000 and recover before year ten, so first passage differs from endpoint probability. Brownian-bridge simulation checks the continuous result.\nUNCERTAINTY: The 6.9%–78.7% interval is parameter uncertainty conditional on GBM, not all ecological or survey uncertainty. Future interventions and systematic bias are omitted. Source: q7_parameters.csv and q7_threshold_probabilities.csv.',
 'Sources: q7_parameters.csv and q7_threshold_probabilities.csv')

add('Isle Royale provides a comparison, not a causal test',
 'Shared model: lagged wolf levels and prey density; common 1984–2015 window',[
 body('gₜ = α + β(Wₜ₋₁ / 10) + γ[log(Nₜ₋₁) − mean] + uₜ',2.05,25,DARK,True),
 ('c',4,.65,3.05,7.4,2.9),
 ('b',f"Same 22 forecast years.\nPositive gain means lower error.\n\nH₀: lagged wolf terms = 0.\nVAR wolves → prey p:\nYellowstone {float(comparison['Yellowstone']['granger_wolf_p']):.3f}; Isle Royale {float(comparison['Isle Royale']['granger_wolf_p']):.3f}.",8.55,3.3,4.1,2.4,21,INK,False),
 cue('Conclusion: clearer predictive evidence in Isle Royale, with important data limitations.')],
 'OPEN: We rerun both systems with the same shared specification, rather than comparing coefficients from different models.\nDIFFERENCE: This model uses lagged wolf levels and prey density. The original Yellowstone headline uses lagged wolf changes. The comparison VAR uses prey and wolf log growth, whereas the original Yellowstone VAR uses prey log growth and scaled wolf-number changes. Thus their p-values are not interchangeable.\nRESULT: On identical 22 test years, MAPE gain is −5.31% in Yellowstone and +8.21% in Isle Royale. H₀ for each Granger test: all lagged wolf-growth coefficients in the prey-growth equation equal zero. Common-window wolf-to-prey Granger p-values are 0.530 and 0.009. The strict observed-input sensitivity has only seven common forecast years.\nCLOSE: The Yellowstone data do not establish a clear independent wolf effect, and the forecast gain in the original specification is small. Isle Royale provides clearer predictive evidence under shared models. This neither disproves wolf biology in Yellowstone nor proves a causal difference between ecosystems.\nLIMITS: Reconstructed moose counts, survey timing, geography and ecological regimes differ. Remaining kill-rate observations are unavailable. The two systems’ viability probabilities refer to different events and should not be directly ranked. Sources: 05_synthesis/report/COMPARISON.md and its tables.',
 'Sources: comparison_summary.csv and matched_calendar_forecast_scores.csv')
GROUP='<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
def rels(items):return '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+''.join(f'<Relationship Id="{id}" Type="{R}/{typ}" Target="{target}"/>' for id,typ,target in items)+'</Relationships>'
def root(tag):return f'<{tag} xmlns:a="{A}" xmlns:r="{R}" xmlns:p="{P}">'
parts={}
parts['_rels/.rels']=rels([('rId1','officeDocument','ppt/presentation.xml')])
parts['ppt/presentation.xml']=root('p:presentation')+'<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst><p:sldIdLst>'+''.join(f'<p:sldId id="{255+i}" r:id="rId{i+1}"/>' for i in range(1,len(slides)+1))+f'</p:sldIdLst><p:sldSz cx="{W}" cy="{H}"/><p:notesSz cx="6858000" cy="9144000"/></p:presentation>'
parts['ppt/_rels/presentation.xml.rels']=rels([('rId1','slideMaster','slideMasters/slideMaster1.xml')]+[(f'rId{i+1}','slide',f'slides/slide{i}.xml') for i in range(1,len(slides)+1)])
parts['ppt/slideMasters/slideMaster1.xml']=root('p:sldMaster')+'<p:cSld><p:spTree>'+GROUP+'</p:spTree></p:cSld><p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="dk2"/><p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>'
parts['ppt/slideMasters/_rels/slideMaster1.xml.rels']=rels([('rId1','slideLayout','../slideLayouts/slideLayout1.xml'),('rId2','theme','../theme/theme1.xml')])
parts['ppt/slideLayouts/slideLayout1.xml']=root('p:sldLayout').replace('>',' type="blank" preserve="1">',1)+'<p:cSld name="Blank"><p:spTree>'+GROUP+'</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'
parts['ppt/slideLayouts/_rels/slideLayout1.xml.rels']=rels([('rId1','slideMaster','../slideMasters/slideMaster1.xml')])
colors={'dk1':INK,'lt1':'FFFFFF','dk2':DARK,'lt2':BG,'accent1':DARK,'accent2':ACCENT,'accent3':'829A7C','accent4':'BCC8B6','accent5':'E1C99E','accent6':'657A82','hlink':'0563C1','folHlink':'954F72'}
parts['ppt/theme/theme1.xml']=f'<a:theme xmlns:a="{A}" name="Yellowstone"><a:themeElements><a:clrScheme name="Forest">'+''.join(f'<a:{k}><a:srgbClr val="{v}"/></a:{k}>' for k,v in colors.items())+'</a:clrScheme><a:fontScheme name="Arial"><a:majorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme><a:fmtScheme name="Simple"><a:fillStyleLst>'+('<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'*3)+'</a:fillStyleLst><a:lnStyleLst>'+('<a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>'*3)+'</a:lnStyleLst><a:effectStyleLst>'+('<a:effectStyle><a:effectLst/></a:effectStyle>'*3)+'</a:effectStyleLst><a:bgFillStyleLst>'+('<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'*3)+'</a:bgFillStyleLst></a:fmtScheme></a:themeElements></a:theme>'
for i,(shapes,notes,title) in enumerate(slides,1):
 parts[f'ppt/slides/slide{i}.xml']=root('p:sld')+f'<p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="{BG}"/></a:solidFill><a:effectLst/></p:bgPr></p:bg><p:spTree>'+GROUP+shapes+'</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'
 parts[f'ppt/slides/_rels/slide{i}.xml.rels']=rels([('rId1','slideLayout','../slideLayouts/slideLayout1.xml'),('rId2','notesSlide',f'../notesSlides/notesSlide{i}.xml')]+([(f'rIdChart{slide_charts[i]}','chart',f'../charts/chart{slide_charts[i]}.xml')] if i in slide_charts else []))
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
ct={'ppt/presentation.xml':'presentation.main','ppt/slideMasters/slideMaster1.xml':'slideMaster','ppt/slideLayouts/slideLayout1.xml':'slideLayout',**{f'ppt/slides/slide{i}.xml':'slide' for i in range(1,len(slides)+1)},**{f'ppt/notesSlides/notesSlide{i}.xml':'notesSlide' for i in range(1,len(slides)+1)}}
parts['[Content_Types].xml']='<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'+''.join(f'<Override PartName="/{k}" ContentType="application/vnd.openxmlformats-officedocument.presentationml.{v}+xml"/>' for k,v in ct.items())+'<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/></Types>'
parts['[Content_Types].xml']=parts['[Content_Types].xml'].replace('</Types>','<Default Extension="xlsx" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"/>'+''.join(f'<Override PartName="/ppt/charts/chart{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.drawingml.chart+xml"/>' for i in range(1,len(chart_specs)+1))+'</Types>')
with zipfile.ZipFile(ROOT/'Yellowstone_Findings.pptx','w',zipfile.ZIP_DEFLATED) as z:
 for name,value in parts.items():z.writestr(name,value if isinstance(value,bytes) else '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'+value)
(ROOT/'speaker_notes.md').write_text('\n\n'.join(f'## {i}. {title}\n\n{notes}' for i,(_,notes,title) in enumerate(slides,1)))
print('Created 10-slide editable deck with four data-linked native charts and speaker notes.')
