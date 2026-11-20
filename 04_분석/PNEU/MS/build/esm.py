# esm.py — 14호 폐렴 사망 Supplemental Material(단일 PDF: Supplemental Methods·Tables S1-S5·Figure S1·Supplemental Appendix STROBE, 본문 첫 인용 순서)(2026-11-20). 수치는 결과 CSV에서만.
import os, re, json, subprocess, unicodedata, pandas as pd
from docx.shared import Cm
import content as C
from numbers_pneu import _UNK
from build_ms import LABEL, GROUPS, TX, TITLE as DTITLE, foot_row, read_draft, ADDRESS, JOURNAL
HERE = os.path.dirname(os.path.abspath(__file__)); MSD = os.path.dirname(HERE); OUT = os.path.join(MSD, "out"); B = os.path.dirname(MSD); RS = os.environ.get("PNEU_RS_DEBUG", os.path.join(B, "results_std3"))
N = C.N
f3 = lambda t: f"{t[0]:.3f} ({t[1]:.3f}-{t[2]:.3f})"
B1 = "Intervals with a bound shown as 1.000 were classified from unrounded values."
J = TX(cite="bracket")
def TF(title, header, rows, foot="", fs=8):
    J.page_break(); J.table_fit(title, header, rows, "", fs_max=fs, title_bold=True)
    if foot: foot_row(J, foot, 8, 12)
CONTENTS = ["Supplemental Methods. Supplementary methods, panel checks, and additional results",
            "Table S1. Source, unit, observed years, expected direction, and filled cells for each district characteristic, Korea, 2011-2024",
            "Table S2. Panel checks before modeling, with rules, thresholds, flags, and actions, Korea, 2011-2024",
            "Table S3. Mortality rate ratios per 1 standard deviation across alternative specifications and comparison outcomes, Korea, 2011-2024",
            "Table S4. Checks of the influenza vaccination association, opposite to the expected direction, Korea, 2011-2024",
            "Table S5. Region-specific mortality rate ratios per 1 standard deviation for the subset-stable characteristics, Korea, 2011-2024",
            "Figure S1. Persistence of the district pattern of pneumonia mortality, Korea, 2011-2024",
            "Supplemental Appendix. STROBE checklist for this ecological study"]
J.para("<b>Supplemental Material</b>"); J.para(f"Article title: {DTITLE}")   # 이중 익명: 저자·소속·저널 표기 없음
J.para("<b>Contents</b>")
for _c in CONTENTS: J.para(_c, double=False)
_LK = C._LK; _MT = pd.read_csv(os.path.join(B, "panel_META_PNEU_std3.csv"), encoding="utf-8-sig").set_index("variable")
_imp = lambda v: int(_MT.loc[v, "n_imputed_interp"] + _MT.loc[v, "n_imputed_sgg_mean"] + _MT.loc[v, "n_imputed_year_mean"])
assert int(_MT.loc["older_single_household_share", "obs_year_min"]) == 2015
gate = open(os.path.join(B, "data_gate_PNEU_std3_261116.txt"), encoding="utf-8").read(); nwarn = int(re.search(r"경고 (\d+)건", gate).group(1))
z_ltc, z_em, z_fac = (re.search(r"\[전 연도 0인 지역\] " + c + r"_raw: (\d+)곳", gate).group(1) for c in ("ltc_hospitals_per_100k_65", "em_specialists_per_100k", "factory_land_share"))
J.page_break(); J.head("Supplemental Methods. Supplementary methods, panel checks, and additional results", 2)
SM = [("Outcome.", "Annual deaths with pneumonia as the underlying cause (International Classification of Diseases, 10th revision, J12-J18) by district of residence came from the cause-of-death statistics of Statistics Korea (deaths by cause, sex, and district). Deaths are attributed to the district of the registered address at death. Influenza (J09-J11) and aspiration pneumonitis (J69) are separate causes and were not included."),
      ("Expected deaths.", f"National pneumonia deaths by 5-year age group (0-4 to 80-84 years and 85 years or older, both sexes combined) came from the national cause-of-death table by cause, sex, and age. Deaths with unknown age ({_UNK} in 14 years) were excluded from the age-specific rates. District age structures came from resident registration statistics. Expected deaths summed nationally to the observed national deaths each year. In the 2023 resident registration file, the age block of Changwon duplicated the 2022 block; the 2023 total was replaced with the official total (1,009,038). A coarser expected count with ten age groups (to 75 years or older) was used in one sensitivity analysis."),
      ("Covariates.", "Community Health Survey indicators are district age-standardized estimates from adults aged 19 years or older, except chewing difficulty, which refers to adults aged 65 years or older; influenza vaccination is the share vaccinated in the past year. Suspected diabetes is the share of adults attending the National Health Insurance Service general health screening with fasting glucose in the diabetes range among attendees not already classified as treated. Long-term care hospitals are counts of long-term care hospitals (care institutions registered under the Medical Service Act) divided by the resident population aged 65 years or older. Basic livelihood security recipients are the share of residents receiving benefits under the National Basic Livelihood Security Act. Emergency medicine specialists per 100,000 population and the factory land share of district area came from a harmonized public district panel; emergency medicine specialists in some district-years carry apportioned (non-integer) values. Values of basic livelihood recipients for 2021-2023 that were below 20% or above five times the mean of the same district in 2020 and 2024 (33 district-years in 11 cities: 30 in ten cities with sub-city wards, where the published figure covered only part of the city, and 3 in Changwon, where it was inflated) were set to missing and interpolated within the district. Pneumococcal vaccination coverage, district fine particulate matter, and long-term care facility (nursing home) capacity were not available as annual district series."),
      ("Panel checks before modeling.", f"An automated gate run on the analytic panel reported {nwarn} flags (Table S2). Most flagged standardized columns whose yearly means were near 0 (a ratio artifact) or the post-2020 indicator (constant by design); the sex ratio exceeds 100 by definition (men per 100 women). Districts with no long-term care hospital ({z_ltc}), no emergency medicine specialist ({z_em}), or no factory land ({z_fac}) in any year were true zeros and retained. No covariate had 100 or more cells filled with yearly national means; older adults living alone were first observed in 2015 and earlier years were filled with district means of later years ({_imp('older_single_household_share'):,} cells). Thirty-three implausible basic livelihood values (2021-2023) were set to missing and interpolated within districts (see Covariates), and four early long-term care hospital values (Yongin and Cheonan, 2011-2012) were interpolated."),
      ("Models.", f"Software: R 4.6.0 with R-INLA; Python 3.9 for data preparation and figures. The negative binomial likelihood was chosen because its widely applicable information criterion (WAIC) for the forced-controls model was lower than that of a Poisson likelihood ({_LK['nbinomial']:,.1f} vs {_LK['poisson']:,.1f}). The Besag-York-Mollié 2 district effect used penalized-complexity priors (P(σ>0.5)=0.01; P(φ<0.5)=2/3) on a 593-edge district adjacency graph with Jeju Island as a separate component. Knorr-Held interactions used Kronecker-product structures (type I: independent; II: random walk in time by independent districts; III: independent years by intrinsic conditional autoregressive districts; IV: random walk by intrinsic conditional autoregressive districts). The Spatial+-type method regressed each standardized covariate on the 23 lowest-frequency eigenvectors of the graph Laplacian. Between- and within-district components were the district mean and the deviation from district and year means. The death-certification check added the district share of all deaths with ill-defined causes (R00-R99), whose median rose from {N['illdef_med'][2011]:.1f}% in 2011 to {N['illdef_med'][2024]:.1f}% in 2024."),
      ("Post hoc checks of the association opposite to the expected direction.", "After the principal results were seen, influenza vaccination was fitted with the forced controls alone, and characteristics on the care and frailty (older adults living alone, long-term care hospitals), behavioral (smoking, high-risk drinking), and access (emergency medicine specialists, basic livelihood recipients) pathways were removed in turn. Space-time interaction, lag, decomposition, window, and comparison-outcome models were part of the standard sensitivity analyses. Results are in Table S4.")]
for h, t in SM: J.para(f"<b>{h}</b> {t}")
_tc = N["type_class"]; _eh = N["ehsa"]; HNM = {C.FLU: "influenza vaccination", C.ALC: "high-risk drinking", C.OLD: "older adults living alone", C.LTC: "long-term care hospitals"}
J.para("<b>Additional results.</b> " + f"Pneumonia accounted for {100*N['pneu_share'][2011]:.1f}% of all deaths in 2011 and {100*N['pneu_share'][2024]:.1f}% in 2024. Residual spatial rate ratios correlated with northing (Spearman's ρ {N['lat_rr']:.2f}) and easting (ρ {N['lon_rr']:.2f}) and with unadjusted smoothed ratios (ρ {N['rr_eb']:.2f}). Emerging hot spot analysis of smoothed ratios classified {_eh['Persistent cold']} districts, all but one in Seoul, as persistent cold spots and none as persistent hot spots; {_eh['Sporadic hot']} were sporadic hot spots and {_eh['No pattern']} showed no pattern (Figure S1). "
       f"Cold spots comprised {_tc['coldspot']['ward']} urban wards, {_tc['coldspot']['city']} cities, and {_tc['coldspot']['county']} counties. With stricter thresholds (posterior probability above 0.975 or 0.99), {N['hot_strict'][0.975][0]} and {N['hot_strict'][0.99][0]} districts were hot spots. Of the {N['n_hyp']} interactions of district characteristics with the post-2020 period, {N['covid_nint']} were credible, and the period had no credible main effect (MRR {N['covid_main'][0]:.3f}; 95% CrI {N['covid_main'][1]:.3f} to {N['covid_main'][2]:.3f}). E-values for the point estimates (and the interval limits closer to 1) were " + "; ".join(f"{HNM[v]} {N['evalue'][v]['E_point']:.2f} ({N['evalue'][v]['E_limit']:.2f})" for v in C.ROB) + f". The 2024 out-of-sample check covered {100*N['oos']['coverage95']:.1f}% of districts within 95% predictive intervals (Spearman ρ {N['oos']['spearman_obs_pred']:.2f} between observed and predicted deaths).")
# ── Table S1 ──
DIR = {"influenza_vaccination_rate": "−", "current_smoking_rate": "+", "high_risk_drinking_rate": "+", "screening_suspected_diabetes_share": "+", "chewing_discomfort_rate_65plus": "+",
       "walking_practice_rate": "−", "moderate_pa_rate": "−", "public_sports_facilities_per_100k": "−", "older_single_household_share": "+", "basic_livelihood_rate": "+",
       "ltc_hospitals_per_100k_65": "+", "em_specialists_per_100k": "−", "factory_land_share": "+"}   # sets_PNEU_std3.json expected_direction
SRC = {"kchs": "Survey", "chk": "Screening", "eloc": "KOSIS", "fac": "Registry", "vil": "Registry"}
EXT = {"ext__pop80_share": "Registry", "ext__basic_livelihood_rate": "Panel", "ext__em_specialists_per100k": "Panel", "ext__factory_land_share": "Panel", "ext__ltc_hospitals_per100k_65": "HIRA"}
UNIT = {"influenza_vaccination_rate": "%", "current_smoking_rate": "%", "high_risk_drinking_rate": "%", "screening_suspected_diabetes_share": "% screened", "chewing_discomfort_rate_65plus": "% aged 65+",
        "walking_practice_rate": "%", "moderate_pa_rate": "%", "public_sports_facilities_per_100k": "per 100,000", "older_single_household_share": "% households", "basic_livelihood_rate": "%",
        "ltc_hospitals_per_100k_65": "per 100,000 aged 65+", "em_specialists_per_100k": "per 100,000", "factory_land_share": "% area",
        "urban_population_share": "%", "physicians_per_1000": "per 1,000", "sex_ratio": "ratio", "fiscal_independence": "%", "pop80_share": "%"}
rows = []
for g, vs in GROUPS:
    rows.append(["__H__", g])
    for v in vs:
        m = _MT.loc[v]; sc = str(m.source_column); src = EXT.get(sc, SRC.get(sc.split("__")[0], sc.split("__")[0]))
        rows.append([f"  {LABEL[v].replace(chr(8225), '')}", UNIT[v], src, f"{int(m.obs_year_min)}-{int(m.obs_year_max)}", ("Forced" if m.role == "forced" else DIR[v]), f"{_imp(v):,}"])
TF("Table S1. Source, unit, observed years, expected direction, and filled cells for each district characteristic, Korea, 2011-2024", ["Characteristic", "Unit", "Source", "Years", "Direction", "Filled cells"], rows,
   "Survey, Community Health Survey (district age-standardized rates); screening, National Health Insurance Service general health screening; KOSIS, Korean Statistical Information Service; registry, resident registration or public sports facility registry; HIRA, Health Insurance Review and Assessment Service care institution statistics; panel, harmonized public district panel; ratio, men per 100 women; forced, in every model. Filled cells of 3,206 district-years (interpolation, district means, or yearly means); 33 implausible basic livelihood values were interpolated beforehand. Expected directions follow the literature cited in the main text.", fs=8)
# ── Table S2: 자료 점검(17 §6 A8·A9) ──
cnt = lambda tag: len(re.findall(r"\[" + re.escape(tag) + r"\]", gate)); two = re.findall(r"\[연도 간 평균 2배 이상 차이\] (\S+):", gate)
ext = json.load(open(os.path.join(RS, "S41_extreme_flags.json"))); impc = json.load(open(os.path.join(RS, "S41_imputed_cells.json")))
rows = [["Year with all districts zero or missing", "At least 98% of districts in a year", "1 (post-2020 indicator)", "None (by design)"],
        ["Constant within a year", "One distinct value in a year", "1 (same indicator)", "None (by design)"],
        ["Year explains most variance", "Year R-squared at least 0.80", "1 (same indicator)", "None (by design)"],
        ["Districts zero in every year", "At least 5 and under 60% of districts", f"3 covariates ({z_ltc}, {z_em}, {z_fac} districts)", "Retained (true zeros)"],
        ["Yearly means differ twofold or more", "Largest over smallest positive yearly mean at least 2", f"{len(two)} columns (means near 0)", "Checked against sources; retained"],
        ["Ratio-type column above 100", "Maximum above 100 for a rate or ratio", f"{cnt('비율형인데 100 초과')} (sex ratio, men per 100 women)", "Retained (definition)"],
        ["Extreme district-years", "Beyond 5 interquartile ranges of yearly quartiles", f"{sum(ext.values())} cells in {sum(1 for v in ext.values() if v)} covariates", "Refilled in one alternative specification"],
        ["Missing district-years", "No observation", f"{sum(impc.values()):,} cells across {len(impc)} covariates", "Filled within districts; perturbation check"],
        ["Implausible values", "Below 20% or above 5 times the 2020-2024 district mean", "33 (basic livelihood, 2021-2023)", "Set to missing and interpolated"],
        ["Missing early counts", "No record in a district-year", "4 (long-term care hospitals)", "Interpolated within districts"],
        ["Duplicated population block", "Age block identical to previous year", "1 district-year (Changwon, 2023)", "Replaced with official total"],
        ["Yearly-mean filling", "At least 100 cells filled with national yearly means", "0 covariates", "None needed"]]
assert nwarn == 3 + len(two) + cnt("비율형인데 100 초과") + cnt("전 연도 0인 지역"), nwarn
TF("Table S2. Panel checks before modeling, with rules, thresholds, flags, and actions, Korea, 2011-2024", ["Check", "Threshold", "Flags in this panel", "Action"], rows, f"Checks were run on the analytic panel of 3,206 district-years. Zero in every year: long-term care hospitals ({z_ltc} districts), emergency medicine specialists ({z_em}), factory land ({z_fac}). Implausible values: 11 cities, 2021-2023; missing early counts: Yongin and Cheonan 2011-2012.", fs=8)
# ── Table S2: 사양 ──
FLU, ALC, OLD, LTC, BLS = C.FLU, C.ALC, C.OLD, C.LTC, C.BLS
NAMES = [("principal", "Principal model"), ("KH_typeI", "Knorr-Held type I"), ("KH_typeII", "Knorr-Held type II"), ("KH_typeIII", "Knorr-Held type III"), ("KH_typeIV", "Knorr-Held type IV"),
         ("icar_besag", "Intrinsic autoregressive district effect"), ("iid_only", "Independent district effect"), ("no_spatial", "No district effect"), ("knn5", "5 nearest neighbors"),
         ("C1_poisson_lognormal", "Poisson, observation-level effect"), ("C2_rw2_year", "Second-order random-walk year effect"), ("C3_ar1_year", "First-order autoregressive year effect"), ("C4_sido_year_iid", "Province-by-year effect"), ("D1_spatial_plus", "Spatial+-type adjustment"), ("B3_smooth_forced", "Smoothed forced controls"), ("F3_extreme_R7", "Extreme values refilled"),
         ("E0_nolag_from2012", "No lag, years from 2012"), ("E0_nolag_from2013", "No lag, years from 2013"), ("E1_lag1", "Covariates lagged 1 year"), ("E2_lag2", "Covariates lagged 2 years"), ("G1_kchs_ma3", "Survey covariates, 3-year averages"), ("H4_odd_years", "Odd years only"), ("H4_even_years", "Even years only"),
         ("ssx", "Sex-and-age standardized expected deaths"), ("s8", "Ten age groups in expected deaths"), ("s2", "Share aged 80+ omitted"), ("s577", "Queen contiguity graph"), ("Z1_illdefined", "Ill-defined cause share added"), ("Z4_outside_care", "Outside-care share added"), ("parsimonious", "Parsimonious model"),
         ("H1_nco_GCA", "Comparison: stomach cancer care"), ("H1_nco_INFECT", "Comparison: infectious disease care")]
SS = {**N["s43"], **N["s41"], **N["s45"]}; WA = {**N["s43_waic"], **N["s41_waic"], **N["s45_waic"]}
for v in ("s577", "s2", "s8", "ssx"): SS.update({(v, c): t for c, t in N["sens_main"][v].items()}); WA[v] = float(pd.read_csv(os.path.join(os.environ.get("PNEU_SENS_DEBUG_ROOT", B), f"results_{v}", "S3_main_fit.csv")).WAIC.iloc[0])
SS.update({("parsimonious", c): (r["IRR"], r["lo"], r["hi"], r["cred"]) for c, r in N["s50_pars"].items()}); WA["parsimonious"] = N["s50_moran"]["parsimonious"]["WAIC"]; WA["principal"] = N["waic_main"]
SS.update({("principal", c): (r["IRR"], r["lo"], r["hi"], r["cred"]) for c, r in N["main"].items()})
def cell(a, v): t = SS.get((a, v)); return "-" if t is None else f"{t[0]:.3f} ({t[1]:.3f}-{t[2]:.3f})"
HN = {FLU: "Influenza vaccination", ALC: "High-risk drinking", OLD: "Older adults living alone", LTC: "Long-term care hospitals", BLS: "Basic livelihood recipients"}
_ALTN = {"B3_smooth_forced": "smoothed forced controls", "C1_poisson_lognormal": "Poisson with observation-level effect", "C2_rw2_year": "second-order random-walk year effect", "C3_ar1_year": "first-order autoregressive year effect", "C4_sido_year_iid": "province-by-year effect", "D1_spatial_plus": "Spatial+-type adjustment", "E0_nolag_from2012": "no lag, from 2012", "E0_nolag_from2013": "no lag, from 2013", "E1_lag1": "1-year lag", "E2_lag2": "2-year lag", "F3_extreme_R7": "extreme values refilled", "G1_kchs_ma3": "3-year survey averages", "H4_even_years": "even years", "H4_odd_years": "odd years"}
_ALT14 = [_ALTN[a] for a in N["alt14"]]; assert len(_ALT14) == 14
FOOT2 = "WAIC, widely applicable information criterion; not comparable across outcomes, across models fitted to different years (lags, odd or even years), or with models that include an observation-level effect. Values are mortality rate ratios (95% credible intervals); '-' in rate ratio columns, not in the model. The parsimonious model kept the forced controls and the subset-stable characteristics. " + B1
MOR = {"principal": "principal", "parsimonious": "parsimonious", "no_spatial": "no_spatial", "iid_only": "iid_district", "icar_besag": "icar_district", "KH_typeI": "typeI_interaction"}
for part, cols in (("A", [OLD, LTC]), ("B", [ALC, FLU, BLS])):
    rows = [[lab] + ([f"{WA[a]:,.0f}" if a in WA and not a.startswith("H1_") else "-", f"{N['s50_moran'][MOR[a]]['resid_moran_I']:.2f}" if a in MOR else "-"] if part == "A" else []) + [cell(a, v) for v in cols] for a, lab in NAMES]
    TF(f"Table S3{part.lower()}. Mortality rate ratios per 1 standard deviation across alternative specifications and comparison outcomes, Korea, 2011-2024 (part {part})", ["Specification"] + (["WAIC", "Residual Moran's I"] if part == "A" else []) + [HN[v] for v in cols], rows, FOOT2 + (f" Residual Moran's I, district-mean Pearson residuals of each specification refitted for this column ('-', not computed; forced controls only, {N['s50_moran']['forced_only']['resid_moran_I']:.2f})." if part == "A" else " Basic livelihood recipients, not credible in the principal model, is shown because it became credible in the type IV model. The 14 alternative specifications counted in the main text are: " + "; ".join(_ALT14) + "."), fs=8)
# ── Table S3: 역방향 사후 검정 ──
S44 = N["s44"]
R = [("Principal model", lambda v: (N["main"][v]["IRR"], N["main"][v]["lo"], N["main"][v]["hi"], N["main"][v]["cred"])),
     ("Knorr-Held type II", lambda v: N["s43"][("KH_typeII", v)]), ("Knorr-Held type IV (best fitting)", lambda v: N["s43"][("KH_typeIV", v)]), ("Province-by-year effect", lambda v: N["s41"][("C4_sido_year_iid", v)]),
     ("Covariates lagged 1 year", lambda v: N["s41"][("E1_lag1", v)]), ("Covariates lagged 2 years", lambda v: N["s41"][("E2_lag2", v)]),
     ("Window 2011-2015", lambda v: C.wt(v, C.WN[0])), ("Window 2016-2019", lambda v: C.wt(v, C.WN[1])), ("Window 2020-2024", lambda v: C.wt(v, C.WN[2])),
     ("Between-district component", lambda v: N["bw"][v + "__between"]), ("Within-district component", lambda v: N["bw"][v + "__within"]),
     ("Fitted alone with forced controls", lambda v: S44[(f"R4_single_{v}", v)]),
     ("Care and frailty characteristics removed", lambda v: S44[("R5_drop_care_frailty", v)]), ("Smoking and drinking removed", lambda v: S44[("R5_drop_behaviour", v)]), ("Access and deprivation removed", lambda v: S44[("R5_drop_access", v)]),
     ("Stomach cancer care (comparison)", lambda v: N["s41"][("H1_nco_GCA", v)]), ("Infectious disease care (comparison)", lambda v: N["s41"][("H1_nco_INFECT", v)])]
st = lambda t: f"{t[0]:.3f} ({t[1]:.3f}-{t[2]:.3f})"
rows = [[lab, st(f(FLU))] for lab, f in R]
def _b1rows():
    cr, nc = [], []
    for lab, f in R:
        t = f(FLU)
        if "1.000" in (f"{t[1]:.3f}", f"{t[2]:.3f}"): (cr if bool(t[3]) else nc).append("the " + lab[0].lower() + lab[1:])
    if not cr and not nc: return ""
    j = lambda l: ", ".join(l[:-1]) + " and " + l[-1] if len(l) > 1 else l[0]
    return "Of the rows with a bound shown as 1.000, " + "; ".join(x for x in ((j(cr) + (" was" if len(cr) == 1 else " were") + " credible") if cr else "", (j(nc) + (" was" if len(nc) == 1 else " were") + " not") if nc else "") if x) + ". "
TF("Table S4. Checks of the influenza vaccination association, opposite to the expected direction, Korea, 2011-2024", ["Analysis", "Influenza vaccination"], rows,
   "Mortality rate ratios per 1 standard deviation (95% credible intervals). Influenza vaccination was expected to lower mortality. The rows from 'Fitted alone' to 'Access and deprivation removed' were added after the principal results were seen; the other rows are standard sensitivity analyses. " + _b1rows() + B1, fs=9)
# ── Table S4: 권역 ──
REG = [("Capital", "Capital region"), ("Chungcheong", "Chungcheong"), ("Honam", "Honam"), ("Yeongnam", "Yeongnam"), ("Gangwon_Jeju", "Gangwon-Jeju")]
_rs = pd.read_csv(os.path.join(RS, "S50_region_slopes.csv")); _nd = _rs.groupby("region").n_district_years.first().to_dict()
RV = [v for v in (OLD, LTC, ALC, FLU) if (v, "Capital") in N["s50_region"]]; assert RV == [OLD, LTC, ALC, FLU], RV
RN = {OLD: "Older adults living alone", LTC: "Long-term care hospitals", ALC: "High-risk drinking", FLU: "Influenza vaccination"}
for part, cols in (("a", [OLD, LTC]), ("b", [ALC, FLU])):
    rows = [[lab, f"{_nd[r]:,}"] + [st(N["s50_region"][(v, r)]) for v in cols] for r, lab in REG]
    rows.append(["Difference in WAIC vs common slope", ""] + [f"{N['s50_region_dwaic'][v]:+.1f}" for v in cols])
    TF(f"Table S5{part}. Region-specific mortality rate ratios per 1 standard deviation for the subset-stable characteristics, Korea, 2011-2024 (part {part.upper()})", ["Region", "District-years"] + [RN[v] for v in cols], rows,
       "Principal model with each characteristic interacted with five regions (capital region: Seoul, Incheon, Gyeonggi; Chungcheong: Daejeon, Sejong, North and South Chungcheong; Honam: Gwangju, North and South Jeolla; Yeongnam: Busan, Daegu, Ulsan, North and South Gyeongsang; Gangwon-Jeju). Negative WAIC differences favor region-specific slopes. WAIC, widely applicable information criterion. " + B1, fs=9)
# ── Figure S1 ──
J.page_break(); _pp = J.para(""); _pp.add_run().add_picture(os.path.join(HERE, "figs", "PNEU_FigS1.png"), width=Cm(16))
J.para("<b>Figure S1. Persistence of the district pattern of pneumonia mortality, Korea, 2011-2024.</b> (A) Emerging hot spot analysis (Getis-Ord Gi* with Mann-Kendall trend) of empirical Bayes-smoothed standardized mortality ratios; numbers of districts in parentheses. (B) Number of calendar windows (2011-2015, 2016-2019, 2020-2024) in which each district was a residual hot or cold spot in the principal model refitted in each window. Map lines delineate study areas and do not necessarily depict accepted national boundaries.")
# ── STROBE ──
DS = [x[4:].strip() for x in read_draft()["Discussion"] if x.startswith("### ")]; MH = [h for h, _ in C.METHODS]; RH = [h for h, _ in C.RESULTS]
q = lambda sec, h: f"{sec}, '{h}'"
assert "Limitations" in DS and "Implications for geriatric care" in DS and "Principal findings" in DS
CK = [("Title and abstract", "1", "Title page; Abstract"), ("Background/rationale", "2", "Introduction"), ("Objectives", "3", "Introduction, final paragraph"), ("Study design", "4", q("Method", MH[0])), ("Setting", "5", q("Method", MH[0])),
      ("Participants", "6", q("Method", MH[0]) + " (district populations; ecological)"), ("Variables", "7", f"Method, '{MH[1]}' and '{MH[2]}'; Tables S1-S2"), ("Data sources/measurement", "8", "Method; Supplemental Methods"),
      ("Bias", "9", f"Method, '{MH[3]}' and '{MH[4]}'; Tables S3-S4"), ("Study size", "10", q("Method", MH[0]) + " (all 229 districts)"), ("Quantitative variables", "11", q("Method", MH[2])),
      ("Statistical methods", "12", f"Method, '{MH[3]}' and '{MH[4]}'"), ("Participants (flow)", "13", "Not applicable (aggregate district data; no exclusions)"), ("Descriptive data", "14", q("Results", RH[0]) + "; Table 1"), ("Outcome data", "15", q("Results", RH[0])),
      ("Main results", "16", q("Results", RH[1]) + "; Table 2; Figures 1-2"), ("Other analyses", "17", f"Results, '{RH[2]}' and '{RH[3]}'; Tables S3-S5"),
      ("Key results", "18", q("Discussion", "Principal findings")), ("Limitations", "19", q("Discussion", "Limitations")), ("Interpretation", "20", f"Discussion, '{DS[1]}' to '{DS[DS.index('Implications for geriatric care')-1]}'"), ("Generalizability", "21", f"Discussion, '{DS[DS.index('Implications for geriatric care')]}' and 'Limitations'"),
      ("Funding", "22", "Funding section")]
J.page_break()
J.table_fit("Supplemental Appendix. STROBE checklist for this ecological study", ["Item", "No.", "Where reported"], [[a, b, c] for a, b, c in CK], "", fs_max=9, title_bold=True)
foot_row(J, "STROBE, Strengthening the Reporting of Observational Studies in Epidemiology.", 8, 12)
ps = os.path.join(OUT, "Supplement.docx"); J.doc_title = "Supplement"; J.save(ps)
for f in (ps,): subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_pneu_ms_esm", "--convert-to", "pdf", "--outdir", OUT, f], check=True, capture_output=True)
print("saved", os.path.basename(ps))
