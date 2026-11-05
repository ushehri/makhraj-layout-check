# makhraj-layout-check

Analysis code for: *Does a Classical Arabic Articulation Order Hold Up? An Evidence Check of a Tongue-to-Forearm Haptic Layout for L2 Pronunciation* (Alshehri & Newbury, manuscript for *Computers*, 2026).

This repository contains **code only**. No audio, KAPD files, L2-KSU tokens, derived learner matrices or per-pair counts are included. Each dataset must be obtained from its official source under its own license (see below). Scripts read local paths set by the environment variable `LMP_DATA` (defaults to `./data`).

## Manuscript tables and figures → scripts

| Manuscript item | Script | Output under `$LMP_DATA` |
|---|---|---|
| Table 2: letter positions and A0 distances | `code/matrices/export_matrices.py` | `results/matrices/sleeve_distance_current_dad_midpoint_6.25_primary.csv` |
| Table 3: evidence provenance | (manuscript only) | — |
| Table 4 and Figure 2: order vs evidence (Kendall τb) | `code/s5.1-rev/s51_rev.py`, `s51_rev_epg_table.py`; labels via `code/redirect/fig2_fig3_names.py` | `results/s5.1-rev/s51r_agreement.csv`, `s51r_epg_table.csv`; `figures/redirect/fig2_order_vs_evidence.png` |
| Table 5: learner tokens and errors per letter | `code/redirect/round2_stats_hci.py` (bootstrap intervals); counts from `code/s5.4-rev/s54_rev.py` | `results/redirect/round2_stats_hci.json`; `results/s5.4-rev/s54r_per_letter.csv` |
| Table 6: six confused pairs and A0 distances | `code/redirect/a2a3_rho.py` | `results/redirect/confused_pairs_distances.csv` |
| Table 7 and Figure 4: alternatives on ρ and CWS | `code/redirect/a2a3_rho.py`, `tradeoff_fig_names.py` | `results/redirect/a2a3_rho.csv`; `figures/redirect/fig_tradeoff_redirect.png` |
| Table 8: design implications | (manuscript only) | — |
| Figure 1: sleeve layout | `code/redirect/fig1_round2.py` | `figures/redirect/fig1_layout_600dpi.png` |
| Figure 3: confusion vs distance | `code/redirect/fig2_fig3_names.py` | `figures/redirect/fig3_confusion_vs_distance.png` |
| Section 4.1 EPG permutation baseline and A0 rank among 548 | `code/redirect/order_baseline_hci.py` | `results/redirect/order_baseline_hci.json` |
| Section 4.2–4.3 leave-one-out, bootstrap, exact Mantel | `code/redirect/round2_stats_hci.py` | `results/redirect/round2_stats_hci.json` |
| A2/A3 and the 548-layout search | `code/s5.5-rev/s55_rev.py`, `targets.py` | `results/s5.5-rev/s55r_pareto.csv`, `s55r_named_layouts.csv` |
| Supplementary Files S1/S2 and Figure S1 | `code/redirect/build_supplement_hci.py` | Word/Excel under the manuscript tree when run in the author workspace |

Supporting analysis folders keep their draft section names (`s5.1-rev`, `s5.4-rev`, `s5.5-rev`). Number-check and manuscript-build helpers used for the Computers HCI submission live in `code/redirect/` (`verify_numbers_hci.py`, `check_final_hci.py`, `build_round2_hci.py`, `make_final_hci.py`, `r2lib.py`).

## Provenance (as in the manuscript)
- KAPD place labels are the KAPD (KACST) team’s expert labels.
- EPG contact positions were computed by us from 108 KAPD EPG files (4 speakers, Kay Palatometer 6300); the palate orientation is inferred.
- A1–A3 are our own untested candidates; A2 and A3 come from a search that used the same L2-KSU confusion data that scores them (in-sample).
- L2-KSU is CC BY-NC-ND 4.0: only aggregates are reported; this repository does not redistribute L2-KSU or any derived per-token or full confusion matrix.

## Obtaining the datasets
- **KAPD**: https://sourceforge.net/projects/kapd/
- **Coretta and Sakr ultrasound compendium**: https://doi.org/10.5281/zenodo.15335918
- **L2-KSU** (LDC2024S11): https://catalog.ldc.upenn.edu/LDC2024S11 (CC BY-NC-ND 4.0; not redistributed here)

## Running
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export LMP_DATA=/path/to/local/data   # KAPD, L2-KSU, ultrasound under this root
# then run folders in dependency order: s5.1 → s5.1-rev → s5.4 → s5.4-rev → s5.5-rev → matrices → redirect
python code/redirect/order_baseline_hci.py
python code/redirect/round2_stats_hci.py
python code/redirect/a2a3_rho.py
python code/redirect/fig1_round2.py
python code/redirect/fig2_fig3_names.py
python code/redirect/tradeoff_fig_names.py
```

## License
MIT. See `LICENSE`. Cite this repository with `CITATION.cff`.
