# Research datasets

Hand-compiled from public sources. Every row carries the page it came from and the date that page was read. A field that no source stated is left blank, and the gap is explained in `notes`; nothing is filled in by guesswork.

| File | Contents | Rows | Spot-check workbook |
|---|---|---|---|
| `dataset_A_india_space_ecosystem.csv` | Indian space companies across the value chain | 32 | `sources/dataset_A_verification.xlsx` |
| `dataset_B_satellite_missions.csv` | Satellites and missions relevant to the use case | 22 | `sources/dataset_B_verification.xlsx` |

## Dataset A: how to read it

**Categories.** Each company sits in one of the brief's seven value-chain categories: Launch, Satellites, Propulsion, Earth Observation, Components, Ground Systems and Space Data/Analytics. A company that spans several is placed by the evidence page's main subject, and `notes` names the other categories. Two rules decide the edge cases:
- Engines and thrusters count as Propulsion, whoever designed them.
- Companies whose business is not one of the seven are placed by what they build or sell: in-space servicing and orbital computing count as Satellites, and space surveillance data counts as Space Data/Analytics.

**Location.** The city is the one the evidence page gives. Where it names a facility rather than a headquarters, `notes` says so. The state is filled in from the city. Two rows leave the city blank: the HAL and L&T consortium, and KaleidEO, whose source gives no location of its own.

**Claims.** Press releases and funding announcements are company statements. `notes` flags these, along with old sources and anything not yet checked, such as whether a planned launch happened.

## Verification

- **Dataset B:** all 170 checks in its workbook were done on 25 Oct 2026, and 159 were confirmed. The rest, plus three items found on review, were re-checked on 26 Oct 2026. Eleven rows were corrected or given a better source. Details are in `sources/verification_log.md`.
- **Dataset A:** spot-check under way.

## Updating a row

Change the source and its date together: `evidence_url` and `date_accessed` in dataset A, `source_url` and `access_date` in dataset B. Use a dated and credible page. Record the change in `sources/verification_log.md`, and in `decision_log.md` too if it changes a conclusion.
