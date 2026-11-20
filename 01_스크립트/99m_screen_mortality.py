#!/usr/bin/env python3
# 99m — 사망 2차 묶음 6개 사인 공간 선별(std, 2026-11-06). 99_screen_cancers.py를 사인 목록·산출 파일명만 바꿔 생성(지표·분류 규칙 동일, 결과 전 고정).
#  입력: 99m_screen_mortality_prep.py 산출 + 98_fit_forced.R <TAG> std. 산출: 04_분석/00_공간선별_사망6종_261106.csv/.md
#  산출: 04_분석/00_공간선별_사망6종_261106.csv/.md
import os, sys, importlib.util, numpy as np, pandas as pd
from scipy.stats import spearmanr
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); AN = os.path.join(ROOT, "04_분석")
src = open(os.path.join(HERE, "98_screen_std.py"), encoding="utf-8").read(); src = src[:src.index("SCR = pd.read_csv")]
g = {"__file__": os.path.join(HERE, "98_screen_std.py")}; exec(compile(src, "98head", "exec"), g)
read_graph, clusters, moran, classify, failed = g["read_graph"], g["clusters"], g["moran"], g["classify"], g["failed"]
TAGS = ["STRK", "IHD", "FALL", "SUIC", "ALZ", "CLRD"]; KO = {"STRK": "뇌혈관질환 사망", "IHD": "허혈성심장질환 사망", "FALL": "낙상 사망", "SUIC": "자살", "ALZ": "알츠하이머 사망", "CLRD": "만성하기도질환 사망"}
rows = []
for T in TAGS:
    D = os.path.join(AN, T); rng = np.random.default_rng(20261019)
    pan = pd.read_csv(f"{D}/panel_{T}.csv", encoding="utf-8-sig", usecols=lambda c: c in ("year", "fbd_region", "cases", "E", "population", "area_m2", "urban_population_share_raw", "older_adult_share_raw"))
    es = pd.read_csv(os.path.join(ROOT, "02_패널", f"{T}_Estd.csv"), encoding="utf-8-sig")
    pan = pan.merge(es[["year", "fbd_region", "E_std"]], on=["year", "fbd_region"], how="left", validate="one_to_one"); assert pan.E_std.notna().all()
    nb = read_graph(f"{D}/results/nb_{T}.graph")
    rr = pd.read_csv(f"{D}/results_screen/forced_std_RR.csv"); hy = pd.read_csv(f"{D}/results_screen/forced_std_hyper.csv")
    g0 = pan.groupby("fbd_region").agg(cases=("cases", "sum"), E_std=("E_std", "sum"), pop=("population", "mean"), km2=("area_m2", lambda x: x.mean() / 1e6),
                                        urban=("urban_population_share_raw", "mean"), old=("older_adult_share_raw", "mean"))
    g0 = rr[["area", "fbd_region"]].merge(g0, left_on="fbd_region", right_index=True, how="inner").sort_values("area").dropna(subset=["urban", "pop", "km2"]); g0 = g0[g0.cases > 0]
    idx = {a: i for i, a in enumerate(g0.area.values)}; W = np.zeros((len(g0), len(g0)))
    for a, i in idx.items():
        nbs = [idx[b] for b in nb.get(a, []) if b in idx]
        if nbs: W[i, nbs] = 1 / len(nbs)
    dens = np.log(g0["pop"] / g0["km2"]).values; u = g0.urban.values; X = np.column_stack([np.ones(len(g0)), u, u ** 2, dens, dens ** 2])
    sir = (g0.cases / g0.E_std).values; y = np.log(sir)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None); res = y - X @ beta; r2 = 1 - res.var() / y.var()
    I_raw, _ = moran(y, W, rng); I_ur, p_ur = moran(res, W, rng)
    ratio = float(np.percentile(sir, 90) / np.percentile(sir, 10)); rho = float(spearmanr(sir, g0.old.values).correlation)
    imin = []
    for yr, d in pan.groupby("year"):
        d = d.set_index("fbd_region").reindex(g0.fbd_region); k = d.cases.notna().values & (d.E_std > 0).values
        Wk = W[np.ix_(k, k)].copy(); rs = Wk.sum(1); Wk[rs > 0] = Wk[rs > 0] / rs[rs > 0, None]
        imin.append(moran(np.log((d.cases.values[k] + 0.5) / d.E_std.values[k]), Wk)[0])
    e1 = pan[pan.year <= 2015].groupby("fbd_region")[["cases", "E_std"]].sum(); e2 = pan[pan.year >= 2020].groupby("fbd_region")[["cases", "E_std"]].sum()
    cm = e1.index.intersection(e2.index); pers = float(spearmanr((e1.cases / e1.E_std)[cm], (e2.cases / e2.E_std)[cm]).correlation)
    hot = rr.loc[rr["class"] == "hotspot", "area"].tolist(); cold = rr.loc[rr["class"] == "coldspot", "area"].tolist(); hc = clusters(hot, nb)
    phi = float(hy[hy.hyperpar.str.startswith("Phi")]["mean"].iloc[0]); rl = float(np.corrcoef(dens, y)[0, 1])
    big = rr.set_index("area").loc[hc[0], "fbd_region"].tolist() if hc else []
    rows.append(dict(TAG=T, 질환=KO[T], n_sgg=len(g0), cases_14y=int(pan.cases.sum()), rho_old_std=round(rho, 3), P90P10_std=round(ratio, 3), I_raw_std=round(I_raw, 3), I_min_year_std=round(min(imin), 3),
                     persistence_std=round(pers, 3), R2_UR_std=round(r2, 3), I_UR_std=round(I_ur, 3), P_UR_std=p_ur, r_logdens_std=round(rl, 3), phi_forced_std=round(phi, 3),
                     hot_std=len(hot), cold_std=len(cold), largest_hot_std=len(hc[0]) if hc else 0, hot_core_std="; ".join(big[:8]),
                     track_std=classify(I_raw, r2, I_ur, p_ur, phi, ratio), fail_std=failed(I_ur, p_ur, phi, ratio),
                     방향_std="도시 높음" if rl > 0.2 else "농촌 높음" if rl < -0.2 else "도농 차 작음"))
O = pd.DataFrame(rows); O.to_csv(os.path.join(AN, "00_공간선별_사망6종_261106.csv"), index=False, encoding="utf-8-sig")
OLD = pd.read_csv(os.path.join(AN, "00_공간선별_std재판정_261019.csv"))
cols = ["질환", "track_std", "I_raw_std", "I_min_year_std", "persistence_std", "P90P10_std", "R2_UR_std", "I_UR_std", "phi_forced_std", "largest_hot_std", "방향_std"]
ALL = pd.concat([O[cols].assign(묶음="2차 사망 6종(신규)"), OLD[cols].assign(묶음="1차 9종(기존)")])
L = ["# 공간 선별 — 사망 2차 묶음 6개 사인, 5세 18구간 연령표준화 기준 (2026-11-06)", "",
     "스크립트 `01_스크립트/34_fetch_national_cause_age_deaths.py`(전국 사인×5세) · `99m_screen_mortality_prep.py`(E_std·패널) · `98_fit_forced.R`(강제통제 BYM2) · `99m_screen_mortality.py`(지표·분류). 지표·분류 규칙은 98과 같다(결과 전 고정).", "",
     "| 묶음 | 질환 | 트랙 | 원자료 Moran | 연도별 최소 | 순위 지속 | P90/P10 | 도농 R² | 보정 후 Moran | phi | 최대 핫스팟 덩어리 | 방향 |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
for r in ALL.itertuples():
    L.append(f"| {r.묶음} | {r.질환} | {r.track_std} | {r.I_raw_std:.2f} | {r.I_min_year_std:.2f} | {r.persistence_std:.2f} | {r.P90P10_std:.2f} | {r.R2_UR_std:.2f} | {r.I_UR_std:.2f} | {r.phi_forced_std:.2f} | {r.largest_hot_std} | {r.방향_std} |")
L += ["", "신규 6종 공간형 미충족 항목: " + "; ".join(f"{r.질환} {r.fail_std}" for r in O.itertuples()),
      "핫스팟 핵심 지역(최대 덩어리 앞 8곳): " + " / ".join(f"{r.질환}: {r.hot_core_std}" for r in O.itertuples())]
open(os.path.join(AN, "00_공간선별_사망6종_261106.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print(O[["질환", "track_std", "I_raw_std", "I_min_year_std", "persistence_std", "P90P10_std", "R2_UR_std", "I_UR_std", "phi_forced_std", "largest_hot_std", "fail_std", "방향_std"]].to_string())
