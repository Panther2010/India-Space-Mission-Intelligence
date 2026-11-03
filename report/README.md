# Report, one-pager and demo

## Technical and product report (8–12 pages, Week 4)

1. **Summary.** The answer and the headline number, on half a page.
2. **Problem and user.** Taken from `methodology/problem_statement.md`.
3. **Indian space ecosystem.** What dataset A shows about who could build or buy this product.
4. **Data.** The missions used and why (from dataset B), plus the source register.
5. **Method.** Fire counts, burnt-area mapping, validation, the ML classifier and the forecast. Why the classifier is a Random Forest, and how six other models compare with it, is drafted in `ml_classifier.md` (3 Nov 2026).
6. **Findings.** Burnt area, the missed share, timing, trends and the forecast against actuals. Drafted in `findings.md` (3 Nov 2026); `findings_numbers.py` prints every number in it from the committed files. The forecast part is updated after each weekly check, and is final after 30 Nov.
7. **Mission trade-off.** Sentinel-2, HLS, VIIRS, Sentinel-1, Resourcesat AWiFS and PlanetScope compared on the brief's six factors. Drafted in `mission_tradeoff.md` (31 Oct 2026).
8. **Limitations.** What the analysis cannot conclude, and which way each limit moves the findings. Drafted in `limitations.md` (3 Nov 2026).
9. **Product concept.** The MVP, risks, dependencies and validation needs.
10. **Next steps.** The next experiment.

Every section labels its statements as reported facts, our calculations or our recommendations.

## One-pager
Problem → User → Satellite data → Analysis → Insight → Decision.

## Three-minute demo
Problem (30 s) → prototype walkthrough (90 s) → strongest insight (30 s) → one limitation and the next step (30 s).
