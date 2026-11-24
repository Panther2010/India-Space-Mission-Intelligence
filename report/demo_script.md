# Three-minute demo script

The brief's eighth deliverable: a short walkthrough of the problem, the prototype, the strongest insight, one limitation and the next step. It opens on the story page, moves to the live dashboard, and closes back on the story page's roadmap.

| Part | Time | Where |
|---|---|---|
| 1. The problem | 0:00–0:30 | Story page |
| 2. The prototype | 0:30–2:00 | Live dashboard |
| 3. The strongest insight | 2:00–2:30 | Dashboard, EO Analysis |
| 4. One limitation and the next step | 2:30–3:00 | Story page |

The spoken lines come to about 400 words: just under three minutes at a calm pace, leaving a few seconds for the clicks. Every number in them is from `report/report.md`.

## Before recording

- **Wake the dashboard** a few minutes early: open <https://india-space-mission-intelligence-dashboard.streamlit.app> and click through every page once, so nothing is loading on camera.
- **Two tabs, in this order:** the story page, scrolled to the top, then the dashboard on its Overview page.
- **Screen:** a browser window of about 1440 × 900 at 100% zoom, other tabs closed, notifications off.
- **Opportunity page:** leave its window slider on 30 Oct, where it starts.
- **If the dashboard won't load,** show the screenshots in `dashboard/screenshots/` (03, 04, 05, 06 and 11 cover this script) or the one-pager, and say the app is waking up.

## 1. The problem (0:00–0:30) · story page

**On screen:** the opening view, with Sangrur pinned on the Earth. At about 0:15, scroll to chapter 01, *The need*.

> Every autumn, Punjab's farmers clear paddy straw before sowing wheat, and much of it is burned. Burning is tracked by counting satellite fire alerts. But those satellites pass in the early afternoon and at night, and most large farm fires burn later in the afternoon. So the alerts can't say how much land burned, or which fields still hold straw that someone could use. I set out to measure the burning itself, in Sangrur district, from free satellite images.

## 2. The prototype (0:30–2:00) · live dashboard

**0:30, Overview.** Switch to the dashboard tab.

> This is the prototype: a dashboard built on free Sentinel-2 images and NASA's fire data. For the 2025 season it mapped every 20-metre pixel through eighteen five-day snapshots: green, then harvested, then burnt.

**0:45, EO Analysis → *Burnt-area map*.** Let the map settle; point at the red fields.

> About a fifth of the harvest burned: 63,400 hectares. I checked it at 240 reference points drawn at random, and where the label was clear it scores an F1 of 0.92.

**1:00, the *What fire counts missed* tab.**

> And here is the gap. For 90.6% of that burnt land, no fire alert fell within 375 metres around the time it burned. The peak weeks went largely unseen.

**1:15, Opportunity.** Point at the green squares and the list on the right; drag the slider from 25 Oct to 30 Oct, then on to 4 Nov.

> This is the product. The user is a straw buyer, such as the biogas plant at Lehragaga in Sangrur. Every five days the map shows fields harvested in the last ten days and not yet burnt, in green, with new burning as ember dots. At the peak, in the window from 30 October, that was about 185,000 hectares. The list ranks the squares to send balers to first. Fields that burn typically do so about ten days after harvest, so a five-day map gives a buyer time to act.

**1:45, Trade-offs.** Scroll the comparison once.

> Why Sentinel-2? Twenty-metre detail, the short-wave infrared bands that tell char from soil, and free. Fire alerts stay useful for same-day warnings, but never for measuring area.

## 3. The strongest insight (2:00–2:30) · dashboard

**On screen:** EO Analysis → the *2021 against 2025* tab.

> The strongest finding is this. From 2021 to 2025, the harvest barely changed and the burnt land halved. Over the same years, fire alerts fell 95%. Read from the alerts alone, burning has almost stopped. Measured as burnt land, a fifth of the harvest still burns, and most of it goes uncounted.

## 4. One limitation and the next step (2:30–3:00) · story page

**On screen:** switch back to the story page and scroll to chapter 04, *What comes next*.

> One limit matters most. My reference labels come from satellite images, not field visits, and 53 of the 240 points stayed doubtful. So the next step is on the ground: a pilot with one straw buyer in the 2027 harvest, measuring the tonnes collected from squares the map flagged before they burned. The report, data and code are all on GitHub.

## Numbers to have ready for questions

| Question | Answer | Source in the report |
|---|---|---|
| How accurate is the map? | Precision 0.87, recall 0.97, F1 0.92 at 187 labelled points; overall accuracy 0.96 | Section 6.1 |
| What if the doubtful points are counted? | F1 0.78–0.82; burnt area from the labels 52,700–141,200 ha | Section 6.1 |
| Didn't machine learning help? | A Random Forest tied the rule (F1 0.92), and six other models scored 0.89–0.94; none beat it beyond chance | Section 6.1 |
| How many detections were there? | 1,500 VIIRS detections in the district in 2025, 1,143 of them in the three busiest windows | Section 6.2 |
| What about clouds and smoke? | Sentinel-2 saw at least 99.9% of the district clearly in every window from 15 Oct except 25–29 Oct (71%); Sentinel-1 radar is the next test | Sections 6.3 and 7 |
| And the 2026 forecast? | For Punjab's first three weeks it was about a fifth too low, and the busiest week so far was right; Sangrur's forecast, made from 3 detections, failed as flagged. Final score after 30 Nov | Section 6.5 |
| Who else works on this in India? | 32 companies in dataset A; 9 in Earth observation and space data; SatSure, Satyukt and Cropin sell agri analytics; Blue Sky Analytics' Zuri (2019) used fire data | Section 3 |
