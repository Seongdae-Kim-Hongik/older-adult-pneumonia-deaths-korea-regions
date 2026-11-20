#!/usr/bin/env python3
# 99m — 사망 2차 묶음 6개 사인 공간 선별 준비(2026-11-06, 9호 후보 선정). 99_screen_cancers_prep.py와 같은 산출 형식·같은 규칙.
#  사인(시군구 사망원인 DT_1B34E13 사망자수 = cases, 전국 DT_1B34E01 사인×5세 사망자수 = 연령 프로파일):
#    STRK 뇌혈관질환 I60-I69 · IHD 허혈성심장질환 I20-I25 · FALL 낙상 W00-W19 · SUIC 자살 X60-X84 · ALZ 알츠하이머 G30 · CLRD 만성하기도질환 J40-J47
#  연령 구간: 5세 18구간(0-4 … 80-84, 85+). 전국 원자료가 85세 이상까지 5세로 나뉘어 있어 진료 자료(75+)보다 세분(E_std 열 이름은 98·99와 맞춰 그대로 E_std).
#  rate[y,a] = 전국 사인별 사망자수(연령미상 제외) / Σ_d 시군구 연령별 인구(FBD_DATA_ZIP, ST_FBDZIP=창원 교정 사본) ;
#  E_std[d,y] = Σ_a pop[d,y,a] × rate[y,a], 연도별 ΣE_std = Σcases 재척도. crude E = 인구 × 전국 조율.
#  산출: 02_패널/<TAG>_Estd.csv, 04_분석/<TAG>/panel_<TAG>.csv(PERIO v1 공변량 + cases·E·offset), config_<TAG>.json, results/nb_<TAG>.graph
#  사용: ST_FBDZIP=<교정 인구 폴더> python3 99m_screen_mortality_prep.py
import os, sys, json, shutil, importlib.util, unicodedata
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); AN = os.path.join(ROOT, "04_분석")
def _load(nm, f):
    s = importlib.util.spec_from_file_location(nm, os.path.join(HERE, f)); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
m38 = _load("m38", "38_build_Estd_all.py"); cw = _load("cw", "40_region_crosswalk.py")
NFC = lambda s: unicodedata.normalize("NFC", str(s))
CAUSES = {"STRK": ("뇌혈관질환", "뇌혈관 질환 (I60-I69)"), "IHD": ("허혈성심장질환", "허혈성 심장 질환 (I20-I25)"), "FALL": ("낙상", "낙상(추락) (W00-W19)"),
          "SUIC": ("자살", "고의적 자해(자살) (X60-X84)"), "ALZ": ("알츠하이머", "알츠하이머병 (G30)"), "CLRD": ("만성하기도질환", "만성 하기도 질환 (J40-J47)")}
CHANGWON = dict(year=2023, fbd_region="경상남도창원시", population=1009038)
BANDS = [f"{lo}-{lo+4}" for lo in range(0, 85, 5)] + ["85+"]
assert os.environ.get("ST_FBDZIP"), "ST_FBDZIP(창원 2023 교정 인구 폴더)를 지정"

# ── 전국 사인×5세 사망자수 ──
N = pd.read_csv(os.path.join(ROOT, "00_원천", "D_사망_인구_암", "DT_1B34E01_national_long.csv"), encoding="utf-8-sig")
N = N[(N.sex == "계") & (N.item == "사망자수") & N.year.between(2011, 2024)]
def nat_band(a):
    a = a.replace(" ", "")
    if a in ("0세", "1-4세"): return "0-4"
    if a in ("85-89세", "90세이상"): return "85+"
    if a.endswith("세") and "-" in a:
        lo, hi = a[:-1].split("-")
        if int(hi) - int(lo) == 4 and int(lo) <= 80: return f"{lo}-{hi}"
    return None   # 계·15세 미만·15-64세·65세 이상·80세이상·연령미상
N["band"] = N.age.map(nat_band)
NB = N[N.band.notna()].groupby(["cause", "year", "band"]).value.sum()
for T, (_, nc) in CAUSES.items():
    tot = N[(N.cause == nc) & (N.age == "계")].set_index("year").value; unk = N[(N.cause == nc) & (N.age == "연령미상")].set_index("year").value.reindex(tot.index).fillna(0)
    s = NB.loc[nc].groupby("year").sum(); assert ((s + unk - tot).abs() <= 1).all(), (T, (s + unk - tot).to_dict())

# ── 시군구 5세 인구(FBD_DATA_ZIP, 39 매칭 규칙 그대로) ──
base = pd.read_csv(os.path.join(AN, "PERIO", "panel_PERIO.csv"), encoding="utf-8-sig"); base["fbd_region"] = base.fbd_region.map(NFC); base["key"] = base.key.map(NFC)
PKEYS = set(base.key); SIDO_HDR = {k for k in cw.SIDO_STD if len(k) >= 3 and (k.endswith("시") or k.endswith("도"))}
FIVE = [f"{lo}-{lo+4}세" for lo in range(0, 85, 5)]; OLD85 = ["85-89세", "90-94세", "95-99세", "100세 이상"]
EXTRA = {("충청북도", "청원군"): "충청북도|청주시"}; rows = []
for y in range(2011, 2025):
    d = pd.read_csv(os.path.join(m38.FBDZIP, f"{y}.csv"), encoding="cp949", dtype=str)
    d["행정구역별"] = d["행정구역별"].map(NFC).str.strip(); d["연령별"] = d["연령별"].map(NFC).str.strip(); d["v"] = pd.to_numeric(d["전체"].str.replace(",", ""), errors="coerce")
    sido = None; city = None; blocks = (d["행정구역별"] != d["행정구역별"].shift()).cumsum()
    for _, g in d.groupby(blocks, sort=False):
        nm = g["행정구역별"].iat[0]
        if nm == "전국": continue
        if nm in SIDO_HDR:
            sido = nm; city = None
            if nm != "세종특별자치시": continue
            g = g.drop_duplicates("연령별")
        sg = nm.split("-")[-1]
        if sg.endswith("시"): city = sg
        elif sg.endswith("구") and city is not None and cw.sido_std(sido) not in ("서울시", "부산시", "대구시", "인천시", "광주시", "대전시", "울산시"): continue
        else: city = None
        a = g.set_index("연령별")["v"]; tot = a.get("계", np.nan)
        if pd.isna(tot): continue
        f = a.reindex(FIVE); o = a.reindex(OLD85); assert f.notna().all() and o.notna().all(), (y, nm)
        r = {"year": y, "tot": tot, **{b: f[b + "세"] for b in BANDS[:-1]}, "85+": tot - f.sum()}
        assert abs(r["85+"] - o.sum()) < 0.5, (y, nm)
        key = EXTRA.get((cw.sido_std(sido), sg), cw.make_key(sido, sg))
        if key not in PKEYS and key.endswith("군") and key[:-1] + "시" in PKEYS: key = key[:-1] + "시"
        r["key"] = NFC(key); rows.append(r)
G = pd.DataFrame(rows).groupby(["year", "key"], as_index=False)[["tot"] + BANDS].sum()

MA = pd.read_parquet(os.path.join(ROOT, "02_패널", "MASTER_시군구_연도_wide.parquet"), columns=["year", "fbd_region", "population"] + [f"mort__{v[0]}_deaths" for v in CAUSES.values()])
MA["fbd_region"] = MA.fbd_region.map(NFC); MA = MA[MA.year.between(2011, 2024)]
m = (MA.year == CHANGWON["year"]) & (MA.fbd_region == NFC(CHANGWON["fbd_region"])); assert m.sum() == 1; MA.loc[m, "population"] = CHANGWON["population"]
SUM = []
for T, (ko, nc) in CAUSES.items():
    P = base.drop(columns=["cases", "E", "SIR", "offset"]).merge(MA[["year", "fbd_region", "population", f"mort__{ko}_deaths"]].rename(columns={f"mort__{ko}_deaths": "cases", "population": "pop_master"}),
                                                             on=["year", "fbd_region"], how="left", validate="one_to_one")
    assert P.cases.notna().all() and len(P) == 3206, (T, P.cases.isna().sum())
    P["population"] = P.pop_master; P = P.drop(columns=["pop_master"]); P["offset"] = P.population
    nat = P.groupby("year").apply(lambda d: d.cases.sum() / d.offset.sum(), include_groups=False); P["E"] = P.offset * P.year.map(nat); P["SIR"] = P.cases / P.E
    X = P[["year", "key", "fbd_region", "offset", "cases"]].merge(G, on=["year", "key"], how="left", validate="one_to_one"); assert X.tot.notna().all(), X[X.tot.isna()][["year", "key"]]
    ratio = X.tot / X.offset; assert ((ratio - 1).abs() <= 0.01).all(), X[(ratio - 1).abs() > 0.01][["year", "key"]]
    DEN = pd.DataFrame({b: X.offset * X[b] / X.tot for b in BANDS}); DEN["year"] = X.year.values
    rate = NB.loc[nc].unstack()[BANDS] / DEN.groupby("year")[BANDS].sum()
    e = (DEN[BANDS].values * rate.loc[X.year.values].values).sum(axis=1)
    X["E_std"] = e * X.groupby("year").cases.transform("sum") / pd.Series(e, index=X.index).groupby(X.year).transform("sum")
    P = P.merge(X[["year", "fbd_region", "E_std"]], on=["year", "fbd_region"], how="left", validate="one_to_one")
    out = P[["year", "fbd_region", "E_std"]].assign(SIR_crude=P.cases / P.E, SIR_std=P.cases / P.E_std)
    out.to_csv(os.path.join(ROOT, "02_패널", f"{T}_Estd.csv"), index=False, encoding="utf-8-sig")
    d = os.path.join(AN, T); os.makedirs(os.path.join(d, "results"), exist_ok=True)
    P.drop(columns=["E_std"]).to_csv(os.path.join(d, f"panel_{T}.csv"), index=False, encoding="utf-8-sig")
    shutil.copy2(os.path.join(AN, "PERIO", "config_PERIO.json"), os.path.join(d, f"config_{T}.json"))
    shutil.copy2(os.path.join(AN, "PERIO", "results", "nb_PERIO.graph"), os.path.join(d, "results", f"nb_{T}.graph"))
    SUM.append((T, ko, int(P.cases.sum()), int((P.cases == 0).sum()), round(float((P.E_std / P.E).min()), 3), round(float((P.E_std / P.E).max()), 3)))
    print(f"[99m] {T} {ko}: 14년 사망 {SUM[-1][2]:,} · 0건 칸 {SUM[-1][3]} · E_std/E {SUM[-1][4]}~{SUM[-1][5]} · 총인구 비 {ratio.min():.4f}~{ratio.max():.4f}")
print("[99m] 저장: 02_패널/<TAG>_Estd.csv, 04_분석/<TAG>/panel·config·graph (" + " ".join(CAUSES) + ")")
