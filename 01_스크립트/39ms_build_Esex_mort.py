#!/usr/bin/env python3
# 39ms — (2026-11-08 12호 IHD 추가) 39m의 성×연령판: 전국 사인×성×5세 사망률(DT_1B34E01 남자·여자)과 시군구 성별 5세 인구(FBD_DATA_ZIP 남자·여자 열)로 E_sexage를 만든다. 산출 02_패널/<TAG>_Esex.csv(민감도 전용). 39m 원본 불변.
# (원 39m 설명) 사망 종속변수용 세분 간접 연령표준화 E (39_build_Estd_fine.py 의 사망판, 2026-11-06 9호 CLRD부터). 39 원본은 건보 진료(298 매핑) 전용이라 건드리지 않는다.
#  사용: ST_FBDZIP=<창원 교정 인구 폴더> [ST_E2_PANEL_SUF=_std3] python3 39m_build_Estd_mort.py <TAG>
#  사인: 99m_screen_mortality_prep.CAUSES 와 같은 표(STRK·IHD·FALL·SUIC·ALZ·CLRD) — 전국 KOSIS DT_1B34E01 사인×5세 사망자수(연령미상 제외)
#  ① 주 E(E_std2): 5세 18구간 0-4 … 80-84, 85+ (전국 사망 원자료가 85세 이상까지 5세라 진료 자료 75+보다 세분)
#  ② 거친 E(E_std_c10): 진료 시리즈와 같은 10구간(0-9 … 60-64·65-69·70-74·75+) — 민감도 s8(구간 수 축소) 대응
#  ③ 시군구 5세 인구 = FBD_DATA_ZIP(39·99m 매칭 규칙 그대로), 분모 = 패널 offset × FBD 연령 비율(총인구 비 |비−1| ≤ 1% assert)
#  ④ rate[y,a] = 전국 사망자수 / Σ_d 분모 ; E = Σ_a 분모 × rate ; 연도별 ΣE = Σcases 재척도
#  산출: 02_패널/<TAG>_Estd2.csv (year, fbd_region, E_std2, E_std_c10, SIR_*, pop65/80/85_share_raw)
#        02_패널/<TAG>_national_agerates_mort.csv, 04_분석/<TAG>/results_std2/S00_Estd2_validation.csv
import os, sys, importlib.util, unicodedata
import numpy as np, pandas as pd
from scipy.stats import spearmanr
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
def _load(nm, f):
    s = importlib.util.spec_from_file_location(nm, os.path.join(HERE, f)); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
m38 = _load("m38", "38_build_Estd_all.py"); cw = _load("cw", "40_region_crosswalk.py")
NFC = lambda s: unicodedata.normalize("NFC", str(s))
CAUSES = {"STRK": "뇌혈관 질환 (I60-I69)", "IHD": "허혈성 심장 질환 (I20-I25)", "FALL": "낙상(추락) (W00-W19)",
          "SUIC": "고의적 자해(자살) (X60-X84)", "ALZ": "알츠하이머병 (G30)", "CLRD": "만성 하기도 질환 (J40-J47)"}   # 99m 과 같은 표
TAG = sys.argv[1]; assert TAG in CAUSES, TAG; NC = CAUSES[TAG]
assert os.environ.get("ST_FBDZIP"), "ST_FBDZIP(창원 2023 교정 인구 폴더)를 지정"
B18 = [f"{lo}-{lo+4}" for lo in range(0, 85, 5)] + ["85+"]
C10 = ["0-9", "10-19", "20-29", "30-39", "40-49", "50-59", "60-64", "65-69", "70-74", "75+"]
def to10(b):
    if b == "85+": return "75+"
    lo = int(b.split("-")[0])
    return C10[lo // 10] if lo < 60 else ("60-64" if lo < 65 else "65-69" if lo < 70 else "70-74" if lo < 75 else "75+")

# ── 전국 사인×5세 사망자수(99m 규칙) ──
N = pd.read_csv(os.path.join(ROOT, "00_원천", "D_사망_인구_암", "DT_1B34E01_national_long.csv"), encoding="utf-8-sig")
NALL = N[(N.item == "사망자수") & N.year.between(2011, 2024) & (N.cause == NC)]
N = NALL[NALL.sex == "계"]
def nat_band(a):
    a = a.replace(" ", "")
    if a in ("0세", "1-4세"): return "0-4"
    if a in ("85-89세", "90세이상"): return "85+"
    if a.endswith("세") and "-" in a:
        lo, hi = a[:-1].split("-")
        if int(hi) - int(lo) == 4 and int(lo) <= 80: return f"{lo}-{hi}"
    return None
N["band"] = N.age.map(nat_band)
NB = N[N.band.notna()].groupby(["year", "band"]).value.sum().unstack()[B18]
tot = N[N.age == "계"].set_index("year").value; unk = N[N.age == "연령미상"].set_index("year").value.reindex(tot.index).fillna(0)
assert ((NB.sum(axis=1) + unk - tot).abs() <= 1).all(), "전국 연령 합 ≠ 계"
print(f"[39m] {TAG} {NC}: 전국 14년 사망 {int(tot.sum()):,} (연령미상 {int(unk.sum())})")

# ── 시군구 5세 인구(FBD_DATA_ZIP) ──
PAN = os.path.join(ROOT, "04_분석", TAG, f"panel_{TAG}{os.environ.get('ST_E2_PANEL_SUF', '')}.csv")
P = pd.read_csv(PAN, encoding="utf-8-sig"); P["key"] = P.key.map(NFC); P["fbd_region"] = P.fbd_region.map(NFC); PKEYS = set(P.key)
SIDO_HDR = {k for k in cw.SIDO_STD if len(k) >= 3 and (k.endswith("시") or k.endswith("도"))}
FIVE = [f"{lo}-{lo+4}세" for lo in range(0, 85, 5)]; OLD85 = ["85-89세", "90-94세", "95-99세", "100세 이상"]
EXTRA = {("충청북도", "청원군"): "충청북도|청주시"}
def popframe(POPCOL):
  rows = []
  for y in range(2011, 2025):
      d = pd.read_csv(os.path.join(m38.FBDZIP, f"{y}.csv"), encoding="cp949", dtype=str)
      d["행정구역별"] = d["행정구역별"].map(NFC).str.strip(); d["연령별"] = d["연령별"].map(NFC).str.strip(); d["v"] = pd.to_numeric(d[POPCOL].str.replace(",", ""), errors="coerce")
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
          a = g.set_index("연령별")["v"]
          if POPCOL != "전체": a = a.fillna(0)   # 성별 열은 0명 칸이 빈칸(예 계룡시 100세+)
          t = a.get("계", np.nan)
          if pd.isna(t): continue
          f = a.reindex(FIVE); o = a.reindex(OLD85); assert f.notna().all() and o.notna().all(), (y, nm)
          r = {"year": y, "tot": t, **{b: f[b + "세"] for b in B18[:-1]}, "85+": t - f.sum()}
          assert abs(r["85+"] - o.sum()) < 0.5, (y, nm)
          r["p65"] = sum(r[b] for b in B18[13:]); r["p80"] = r["80-84"] + r["85+"]; r["p85"] = r["85+"]
          key = EXTRA.get((cw.sido_std(sido), sg), cw.make_key(sido, sg))
          if key not in PKEYS and key.endswith("군") and key[:-1] + "시" in PKEYS: key = key[:-1] + "시"
          r["key"] = NFC(key); rows.append(r)
  return pd.DataFrame(rows).groupby(["year", "key"], as_index=False)[["tot"] + B18 + ["p65", "p80", "p85"]].sum()
G = popframe("전체")
X = P[["year", "key", "fbd_region", "offset", "population", "cases"]].merge(G, on=["year", "key"], how="left", validate="one_to_one")
assert X.tot.notna().all(), X[X.tot.isna()][["year", "key"]]
X["pop_ratio"] = X.tot / X.population
print("[39m] 총인구 비(FBD 계 / 패널 population):", X.pop_ratio.describe()[["min", "50%", "max"]].round(4).to_dict())
assert ((X.pop_ratio - 1).abs() <= 0.01).all(), X[(X.pop_ratio - 1).abs() > 0.01][["year", "key", "population", "tot"]]
for c in ("p65", "p80", "p85"): X[c.replace("p", "pop") + "_share_raw"] = 100 * X[c] / X.tot


# ── 성×연령 E ──
def natband_sex(sx):
    M = NALL[NALL.sex == sx].copy(); M["band"] = M.age.map(nat_band)
    return M[M.band.notna()].groupby(["year", "band"]).value.sum().unstack()[B18]
E = np.zeros(len(X))
for sx, col in (("남자", "남자"), ("여자", "여자")):
    Gs_ = popframe(col); Xs = X[["year", "key", "offset", "tot"]].merge(Gs_, on=["year", "key"], how="left", suffixes=("_all", ""), validate="one_to_one"); assert Xs[B18].notna().all().all()
    DENs = pd.DataFrame({b: Xs.offset * Xs[b] / Xs.tot_all for b in B18}); DENs["year"] = Xs.year.values
    Rs = natband_sex(sx) / DENs.groupby("year")[B18].sum()
    E += (DENs[B18].values * Rs.loc[Xs.year.values].values).sum(axis=1)
    print(f"[39ms] {sx} 인구 비(성별 합/전체):", round(float((Xs.tot / Xs.tot_all).mean()), 4))
OUT = X[["year", "fbd_region", "cases"]].copy(); OUT["E_sexage"] = E * OUT.groupby("year").cases.transform("sum") / pd.Series(E, index=OUT.index).groupby(OUT.year).transform("sum")
old = pd.read_csv(os.path.join(ROOT, "02_패널", f"{TAG}_Estd2.csv"), encoding="utf-8-sig"); old["fbd_region"] = old.fbd_region.map(NFC)
OUT = OUT.merge(old[["year", "fbd_region", "E_std2", "pop80_share_raw"]], on=["year", "fbd_region"], how="left", validate="one_to_one")
print("[39ms] E_sexage / E_std2:", (OUT.E_sexage / OUT.E_std2).describe()[["min", "50%", "max"]].round(4).to_dict())
OUT[["year", "fbd_region", "E_sexage", "E_std2", "pop80_share_raw"]].sort_values(["year", "fbd_region"]).to_csv(os.path.join(ROOT, "02_패널", f"{TAG}_Esex.csv"), index=False, encoding="utf-8-sig")
print(f"[39ms] 저장 02_패널/{TAG}_Esex.csv")
