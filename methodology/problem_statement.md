# Problem statement

**Status:** draft. The lead user is decided at Checkpoint 2 (22 Oct 2026).

Labels used below:
- **[Reported]** comes from a cited source.
- **[Ours]** is our own calculation.
- **[Recommendation]** is our judgement.

| Element | Draft |
|---|---|
| **User** | Proposed lead: the biomass procurement manager at a compressed-biogas plant in Punjab that runs on paddy straw. Such plants exist: Verbio's Lehragaga plant uses 100,000 t of agricultural residue a year [Reported, Verbio press release, 26 Oct 2022]. Second user: the district agriculture officer. [Recommendation] |
| **Decision to improve** | *Buyer:* where and when to send balers and collection teams during the harvest window, before straw is burnt. *Department:* where to target residue-management machinery and farmer outreach, and whether burning is really falling. |
| **Current pain point** | Fire counts come from satellites that pass around midday. iFOREST reports that most large Punjab farm fires in 2024 and 2025 occurred after 3 pm [Reported, via The Tribune, 9 Dec 2025]. Counts show where fire was seen at that moment. They don't show how much area burned, or which harvested fields are still unburnt. |
| **Data needed** | A Sentinel-2 L2A time series for burn and harvest status. VIIRS active fires from NASA FIRMS. A cropland mask from ESA WorldCover 2021. District boundaries from geoBoundaries. Later, field reference data. |
| **Expected output** | A district map, refreshed at every clear Sentinel-2 pass, showing burnt area and the date each area was first seen burnt. District and block totals. The share of burnt area that fire counts missed. *Next step, outside this prototype:* mapping harvested-but-unburnt areas, which is the straw buyer's collection opportunity. |
| **Success metric** | *Prototype:* precision and recall of the burnt-area map each at least 0.80 on held-out reference points [Recommendation: proposed target]. For context, a 2026 study reported burnt-area user's accuracy of 67–90% at three sites [Reported, Dwivedi et al. 2026]. The missed share is reported with its uncertainty. *Product, in a future pilot:* tonnes of straw collected from areas the map flagged before they burned. |
| **Key limitations** | Reference labels come from imagery, not field visits. Cloud and smoke hide some dates. Burn scars can be ploughed under between clear images. FIRMS points are pixel centres. Suomi NPP data ends on 1 Nov 2026. Buyers' willingness to pay is untested. Health effects are not measured. |

## Open questions for Checkpoint 2

1. Which user leads the story: the straw buyer (commercial) or the agriculture department (public sector)?
2. Is "harvested but not yet burnt" in the Week 4 product concept as the next experiment? Proposed: yes, as a concept only.
