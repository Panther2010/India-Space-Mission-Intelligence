# Report, one-pager and demo

| File | What it is |
|---|---|
| `report.pdf` | The technical and product report, 10 pages: the brief's deliverable 6. Interim until the 2026 forecast is scored after 30 Nov 2026. |
| `report.md` | Its source, readable here on GitHub. |
| `one_pager.pdf`, `one_pager.png` | The product one-pager (deliverable 7): Problem → User → Satellite data → Analysis → Insight → Decision. Its source is `one_pager.html`. |
| `demo_script.md` | The three-minute demo (deliverable 8): the story page, then the live dashboard. |
| `findings.md`, `mission_tradeoff.md`, `ml_classifier.md`, `limitations.md` | The working drafts behind sections 6–8 of the report, with more detail than it has room for. |
| `findings_numbers.py` | Prints every number in `findings.md` and in sections 3 and 6 of the report, from the committed outputs. |
| `compare_classifiers.py` | Runs six other classifiers against the Random Forest and the burn rule, and writes `data/processed/ml_model_comparison_sangrur_2025.csv`. |
| `build_report.py`, `report.css` | Build the two PDFs and the PNG. |

## The report's sections

1. **Summary:** the answer and the headline numbers.
2. **Problem and user:** from `methodology/problem_statement.md`.
3. **The Indian space ecosystem:** what dataset A shows about who could build, supply or buy this product.
4. **Data:** the missions used and why, and the source register.
5. **Method:** fire counts, burnt-area mapping, validation, the missed share, the 2021 comparison, the classifier and the forecast.
6. **Findings:** burnt area, the missed share, timing, 2021 against 2025, and the forecast against what happened.
7. **Mission trade-off:** six data options on the brief's six factors.
8. **Limitations:** what the analysis cannot conclude, and which way each limit moves the findings.
9. **Product concept:** the brief's "If I were building a space startup" page.
10. **Next steps:** the next experiments.

Every statement is labelled as a reported fact, our own calculation or our recommendation.

## Rebuilding the PDFs

After editing `report.md` or `one_pager.html`, run from the project folder:

```
pip install --no-cache-dir markdown-it-py      (once, into the project's environment)
python report/build_report.py
```

It also needs Playwright and Pillow, which `dashboard/take_screenshots.py` uses too. It prints with Microsoft Edge where it is installed, and with Playwright's own Chromium otherwise. `python report/build_report.py report` or `... one-pager` builds just one of them. The markers that shape the PDF without showing on GitHub are listed at the top of `build_report.py`.

## After the final forecast run (after 30 Nov 2026)

1. Run Notebook 04 and commit its outputs.
2. Run `python report/findings_numbers.py`, then update section 6.5 of `report.md` and section 5 of `findings.md` with the final score. Remove "interim" from the status line at the top of `report.md`.
3. Rebuild with `python report/build_report.py`, and retake screenshots 01, 08 and 09 with `dashboard/take_screenshots.py 01 08 09`.
