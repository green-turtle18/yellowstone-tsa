# AI Usage Report — Part 3: Park Visitation

*MATH F428 Time Series Analysis and Forecasting · Yellowstone project · Part 3 (Person 3)*

## Tool used

| Tool | Version / access |
|---|---|
| Claude (Anthropic) | Claude Opus 5.5, through claude.ai (chat with a code workspace) |

No other generative AI tools were used for Part 3.

## What the AI did

Claude helped write the analysis code, ran it in a cloud workspace, and helped draft the written material. Specifically:

1. **Data cleaning.** Helped write `scripts/build_visitation_data.py`: reshaping the IRMA export to one row per month, gap and yearly-total checks, and the `Note` column. It read the IRMA comment and procedure-change PDFs and flagged the 1993 counting change and the Dec 1995–Jan 1996 shutdown, which the project brief did not mention.
2. **Analysis code.** Helped write both notebooks (`13_visitation_eda_sarima`, `14_visitation_interventions`) and `scripts/q4_rolling_forecasts.py`, following the methods in the Person 3 brief: STL, ADF/KPSS, SARIMA selection, intervention models, Mann–Kendall trends, temperature regression, counterfactual forecasts and decay models, rolling-origin evaluation with Diebold–Mariano tests, and break tests.
3. **Method choices beyond the brief**, each explained in the notebooks:
   - a 1993 counting-change control in every before/after-1995 comparison;
   - the North-gate vs wolf-count regression with a placebo test (Q1);
   - a second flood counterfactual with a pre-COVID baseline.
4. **Syllabus extensions**, suggested by Claude after comparing the work with the MATH F428 handout; I chose which to include. Claude helped write: AR/MA root checks, the ARCH-LM test, the over-differencing check (SARIMA with d = 0), ψ-weights and the eventual forecast function, forecast combination and encompassing tests, Granger causality / VAR with residual white-noise checks, and ETS counterfactuals.
5. **Interpretation and writing.** Helped draft the plain-English summaries in the notebooks, the Q1 answer paragraph, the folder `README.md` and the Part 3 report (`reports/part3_report.md`).

## How the output was checked

- Each notebook runs from start to finish with no errors from the `03_park_visitation/` folder.
- The yearly sums of the cleaned monthly data match NPS's official annual totals exactly.
- Every number quoted in the report was printed by the notebooks; the summaries are generated from the computed values rather than typed in.
- Results that depend on a modelling choice are reported as ranges (for example SARIMA vs ETS counterfactuals), and post-hoc choices are labelled as such (the 1997 step in Q5).
