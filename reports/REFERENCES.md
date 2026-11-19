# References and source decisions

Checked against primary publisher, author or NPS records on 19 November 2026. URLs for individual corrections are retained in `data/corrections/verified_overrides.csv`.

## Ecological interpretation

- MacNulty, D. R., Stahler, D. R., Wyman, C. T., Ruprecht, J., & Smith, D. W. (2016). *The Challenge of Understanding Northern Yellowstone Elk Dynamics after Wolf Reintroduction*. **Yellowstone Science 24(1)**, beginning p. 25. [NPS article](https://home.nps.gov/yell/learn/ys-24-1-the-challenge-of-understanding-northern-yellowstone-elk-dynamics-after-wolf-reintroduction.htm); [author PDF](https://qanr.usu.edu/wild/labs/macnulty-lab/files/macnulty-et-al-2016a.pdf). The brief's PLOS ONE attribution was incorrect. A plotted count history is not an exact machine-readable source for every legacy value.
- Ripple, W. J., & Beschta, R. L. (2012). *Trophic cascades in Yellowstone: The first 15 years after wolf reintroduction*. **Biological Conservation 145(1):205–213**. [Publisher](https://www.sciencedirect.com/science/article/pii/S0006320711004046).
- Vucetich, J. A., Smith, D. W., & Stahler, D. R. (2005). *Influence of harvest, climate and wolf predation on Yellowstone elk, 1961–2004*. **Oikos 111:259–270**. [DOI](https://doi.org/10.1111/j.0030-1299.2005.14180.x); [research-project PDF](https://www.isleroyalewolf.org/sites/default/files/tech_pubs_files/vucetich_etal_2005oikos.pdf).
- Brice, E. M., Larsen, E. J., & MacNulty, D. R. (2022). *Sampling bias exaggerates a textbook example of a trophic cascade*. **Ecology Letters 25:177–188**. [DOI](https://doi.org/10.1111/ele.13915).
- Hobbs, N. T., Johnston, D. B., Marshall, K. N., Wolf, E. C., & Cooper, D. J. (2024). *Does restoring apex predators to food webs restore ecosystems? Large carnivores in Yellowstone as a model system*. **Ecological Monographs 94, e1598**. [Publisher](https://esajournals.onlinelibrary.wiley.com/doi/10.1002/ecm.1598).
- Eberhardt, L. L., White, P. J., Garrott, R. A., & Houston, D. B. (2007). *A Seventy-Year History of Trends in Yellowstone's Northern Elk Herd*. **Journal of Wildlife Management 71:594–602**. [DOI](https://doi.org/10.2193/2005-770). Bibliography verified; full Table 1 not obtained (publisher returned 403). Wolf-kill transcription remains a handoff, not a fabricated series.
- Mech, L. D., Smith, D. W., Murphy, K. M., & MacNulty, D. R. (2001). *Winter severity and wolf predation on a formerly wolf-free elk herd*. **Journal of Wildlife Management 65(4):998–1003**. [USGS record](https://pubs.usgs.gov/publication/1001772); DOI 10.2307/3803048.

## Methods

- Dennis, B., Munholland, P. L., & Scott, J. M. (1991). *Estimation of Growth and Extinction Parameters for Endangered Species*. **Ecological Monographs**. [Publisher / DOI](https://esajournals.onlinelibrary.wiley.com/doi/10.2307/1943004).
- Dennis, B., Ponciano, J. M., Lele, S. R., Taper, M. L., & Staples, D. F. (2006). *Estimating density dependence, process noise, and observation error*. **Ecological Monographs 76(3):323–341**. [Author PDF](https://briandennis.org/reprints/Dennis_et_al_Ecol_Monogr_2006.pdf).
- Bai, J., & Perron, P. (2003). *Computation and analysis of multiple structural change models*. **Journal of Applied Econometrics 18(1):1–22**. [Author PDF](https://www.columbia.edu/~jb3064/papers/2003_Computation_and_analysis_of_multiple_structural_changes.pdf); DOI 10.1002/jae.659. Implemented here: an exact L2 segmentation objective, not their complete inferential procedure.
- [Statsmodels MLEModel documentation](https://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.mlemodel.MLEModel.html) and [UnobservedComponents documentation](https://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.structural.UnobservedComponents.html). These distinguish covariates in the observation equation from the growth-state equation implemented here.

## Data reconciliation

- [2019 northern Yellowstone classification survey, Table 4](https://bloximages.chicago2.vip.townnews.com/helenair.com/content/tncms/assets/v3/editorial/2/42/242aa89c-d731-5ca3-aab4-ba9f4d9334a7/5ca685e1acd0e.pdf.pdf): total herd vs HD313 columns, unreliable 2014 observation, and 2016/2019 method differences. Agency report hosted by a newspaper; not newspaper estimates.
- [NPS elk overview](https://www.nps.gov/yell/learn/nature/elk.htm): 2022 whole-herd count.
- [NPS 2023 wolf report, archived copy](https://npshistory.com/publications/yell/ycr/wolf-reports/2023.pdf), p. 12: winter 2023 fixed-wing survey in December 2022 and separate March classification count. Use the year of the winter, not blindly the calendar survey year.
- [NPS 2024 report](https://home.nps.gov/yell/learn/nature/upload/2024-YELL-Wolf-Cougar-and-Elk-Report.pdf) and [2025 report](https://home.nps.gov/yell/learn/upload/2025-YELL-Wolf-Cougar-Elk-Project-Annual-Report-508.pdf): explicit counts and a conflicting implied 2024 base. Do not back-calculate a replacement from the reported percentage.
- [2014 wolf report](https://www.nps.gov/yell/learn/nature/upload/2014-wolf-report.pdf) and [2022 wolf report](https://home.nps.gov/yell/learn/nature/upload/2022-Web-Wolf-Report.pdf): northern wolves. The historically tabulated 2014 northern value 42 replaces a numerical interpolation of the same value.
- [NPS October 2023 bison status report](https://www.buffalofieldcampaign.org/images/news-and-media/bfc-news/update-2023-2024/2023-11-29/Yellowstone-National-Park-Bison-Population-Status-Report-October-2023.pdf): Table A1 and narrative give different summer summaries. Retain the exact survey choice and sensitivity rather than mixing park totals with northern-herd totals.

The remaining climate geography, NDVI settings, early elk source transcription, and harvest geography/timing require the original export/survey metadata. Lemke (1998) is inherited harvest provenance, not independently certified here. Optional Diebold–Mariano testing was not used, so no claim depends on its reference.
