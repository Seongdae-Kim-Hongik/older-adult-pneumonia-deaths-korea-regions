# Pneumonia deaths among older adults across Korean regions

Analysis code for the manuscript

> Kim S. *Against the global decline, late-life pneumonia mortality in Korea rose by 63% after age standardization* Manuscript under review.

Archived version: Zenodo, https://doi.org/10.5281/zenodo.24408662 (version 1.1.0)

## Contents

This repository contains code only. The processed district-year data (master table, analytic panel, expected deaths, result tables, adjacency graph and boundary file) are not included; they are available from the author on reasonable request. All source statistics are public (see Data sources).

| Path | What it is |
|---|---|
| `01_스크립트/` | Analysis scripts (below) |
| `04_분석/PNEU/sets_PNEU_std3.json`, `sets_PNEU_s577.json`, `sets_PNEU_s2.json`, `sets_PNEU_s8.json`, `sets_PNEU_ssx.json`, `config_PNEU_std3.json`, `run_std3_chain_fix.sh` | Covariates with expected directions, forced controls, comparison outcomes and model settings (principal model `std3`; sensitivity versions with the queen contiguity graph, without the share aged 80 or older, with ten-group expected deaths, and with sex-and-age standardized expected deaths) |
| `04_분석/PNEU/MS/` | Scripts that read the result tables and write every number, table and figure in the manuscript and supplementary material, including `content.py`, which generates the Methods and Results text (the draft source of the Introduction and Discussion is not included) |

Folder and some column names are in Korean because the source tables are Korean; each script has a header comment describing its inputs and outputs.

## Data sources

All inputs are public, aggregated statistics. No individual-level data are included.

- Deaths by underlying cause (pneumonia, ICD-10 J12-J18) by district of residence: Statistics Korea, cause-of-death statistics (KOSIS DT_1B34E13), 2011-2024. Comparison outcomes are people treated for stomach cancer and for infectious diseases (National Health Insurance Service regional statistics).
- National deaths by cause and 5-year age group (to 85 years or older): Statistics Korea (KOSIS DT_1B34E01), fetched by `34_fetch_national_cause_age_deaths.py` (requires a personal KOSIS API key in `~/.kosis_key`; the key is not included).
- Population by 5-year age group: Ministry of the Interior and Safety, resident registration statistics. The 2023 age block of Changwon duplicated the 2022 block and was corrected (`population_override` in the sets files).
- District covariates: Korean Statistical Information Service (KOSIS), the Community Health Survey, National Health Insurance Service general health screening statistics, Health Insurance Review and Assessment Service care institution statistics, the public sports facility registry, and a harmonized public district panel (basic livelihood security recipients, emergency medicine specialists, factory land).

## Pipeline

Run from the repository root (set `ST_DATA_ROOT` and `ST_FBDZIP_CORRECTED` to the local copies of the public source files). R jobs are wrapped in `rslot.sh`, which limits the number of concurrent R processes on a shared machine.

| Step | Script | Output |
|---|---|---|
| 0 | `34_fetch_national_cause_age_deaths.py`, `99m3_screen_mortality_prep.py`, `98_fit_forced.R`, `99m3_screen_mortality.py` | National cause-by-age deaths, screening panels and spatial screening of six causes of death |
| 1 | `99c_extra_canonical_pool_pneu.py` | Assistance, emergency-medicine, factory-land and long-term care hospital indicators and ill-defined cause shares joined by district code; basic livelihood values for 2021-2023 below 20% or above five times the district's 2020-2024 mean are set to missing and interpolated |
| 2 | `39m_pneu.py` (runs `39m_build_Estd_mort.py` for PNEU), `39ms_pneu.py` (runs `39ms_build_Esex_mort.py`) | Expected deaths by indirect standardization in eighteen 5-year age groups (ten groups and sex-by-age groups for sensitivity) |
| 3 | `80_build_disease_panel_v.py PNEU` (`ST_VER=std3`) | Analytic panel |
| 4 | `81_fit_inla.R PNEU` (`ST_VER=std3`, `ST_GRAPH=04_분석/PNEU/graph_593.graph`, `ST_THREADS=1`; see `04_분석/PNEU/run_std3_chain_fix.sh`) | Principal model, set comparison, 200-subset multiverse, window models |
| 5 | `85_window_maps.R`, `86_yearly_maps_ehsa.py`, `86b_ehsa_modified_mk.py`, `87_window_grid.py` | Maps and emerging hot spot analysis |
| 6 | `88g_sens_prep.py PNEU std3 INFECT,GCA`, `88g_sens_suite.R` (`GROUP=1..6`), `88h_ppc_varpart.R`, `88k_struct_kh.R` (nb, struct, kh, review) with `kh_constraints.R`, `88z_pneu_coding.R`, `89g_sens_combine.py` | Sensitivity analyses, comparison outcomes, Knorr-Held models, death-certification and access checks, review outputs |
| 6b | `88r_reverse_check.R` (`REV`, `AXIS` environment variables) | Post hoc checks of the association opposite to the expected direction |
| 7 | `04_분석/PNEU/MS/build/` (`run_all.sh`: `figs.py`, `build_ms.py`, `esm.py`, `post_esm.py`; `build_refs.py` refreshes the reference cache) | Manuscript (APA author-year references), Supplemental Material and figures |

The boundary file is found at `data/boundary/final.shp` by default; set `ST_SHP` to use another path.

## Software

R 4.6.0 with R-INLA 25.10.19, spdep and sf; Python 3.9 with pandas, geopandas, numpy, scipy, matplotlib and python-docx.

## Checks

Expected deaths and the model offset contain no added constants (no `E + 1`, `log(E + c)` or lower bounds on `E`); the only constant is a continuity correction of 0.5 on observed deaths in the descriptive yearly Moran's I of log ratios (`01_스크립트/81_fit_inla.R`), which does not enter any model.

## License

Code: MIT (see `LICENSE`). The source statistics remain under the terms of their providers.
