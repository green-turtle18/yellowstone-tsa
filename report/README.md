# Final report source

`final_report.tex` is the LaTeX source of [`../Final_Report.pdf`](../Final_Report.pdf); `figures/` holds copies of the figures it uses, taken from each part's `reports/figures/` (and the comparison's).

To rebuild from this folder:

```sh
latexmk -pdf final_report.tex
```

then copy `final_report.pdf` to the repository root as `Final_Report.pdf`.
