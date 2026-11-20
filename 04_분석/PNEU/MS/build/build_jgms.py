# build_jgms.py — 14호 폐렴 사망 The Journals of Gerontology, Series A: Medical Sciences(OUP·GSA) Research Article 원고 조립(2026-11-20).
#  규정 요점: 논문폴더 114_노인폐렴사망지리_JGMS/00_저널가이드/JGMS_가이드_요점_261120.md — 제목면(제목·저자·학위·소속·교신 이메일·단어 수·자료 요소 수) → 구조 초록 Background/Methods/Results/Conclusions ≤250 + 키워드 3-5(제목에 없는 말)
#   → Introduction → Method → Results → Discussion → Funding → Conflict of Interest → Acknowledgments → Author Contributions → Data Availability → References(AMA, 괄호 번호, DOI) → 표(각 쪽, Note.) → 그림 캡션+Alt text. 제목면+초록+본문 ≤5200, 자료 요소 ≤5, 참고문헌 ≤50. 단일 익명. 그림 별도 TIFF 300 dpi 이상. 보충 = Supplement 단일 PDF. 미국식 철자. AI 사용은 Method.
#   (표 각 쪽, 캡션 'Figure n.' + Alt text)
import os, re, json, subprocess
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt, Cm
from jkms_engine import JKMS
import content_jgms as C
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out"); os.makedirs(OUT, exist_ok=True)
N = C.N; REFS = json.load(open(os.path.join(HERE, "refs_jgms.json"), encoding="utf-8"))
DRAFT = os.path.join(MS, "draft", "01_manuscript_jgms.md")
PAPER = os.path.expandvars("$ST_DATA_ROOT") + "/G.Downloads/논문_마스터자료/114_노인폐렴사망지리_JGMS"
_zf = os.path.join(PAPER, "06_GitHub_Zenodo", "zenodo_doi.txt")   # 부모가 Zenodo 게시 후 이 한 줄(10.5281/zenodo.NNNNNNNN)을 고치고 run_all.sh 재실행
ZENODO = open(_zf).read().strip() if os.path.exists(_zf) else "10.5281/zenodo.PENDING"
REPO = "older-adult-pneumonia-deaths-korea-regions"; GITHUB = f"https://github.com/Seongdae-Kim-Hongik/{REPO}"
OLD_REPOS = (); assert REPO not in OLD_REPOS
TITLE = C.TITLE; ORCID = "0000-0002-1525-0091"; JOURNAL = "The Journals of Gerontology, Series A: Medical Sciences"
AFFIL = "Department of Biohealth Convergence Open Sharing System, Hongik University, Seoul, Republic of Korea"
ADDRESS = "Department of Biohealth Convergence Open Sharing System, Hongik University, 94 Wausan-ro, Mapo-gu, Seoul 04066, Republic of Korea"
FUNDING = "This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors."
COMPETING = "None."
ETHICS = "This study was performed in line with the principles of the Declaration of Helsinki. The Institutional Review Board of Hongik University approved the study on November 4, 2025 (7002340-202511-HR-012) and its continuing review on November 3, 2026 (7002340-202611-HR-040)."
CONSENT = "The Institutional Review Board of Hongik University waived informed consent because only published aggregate statistics were used; no individual can be identified."
CONSENT_PUB = "Not applicable; the manuscript contains no individual person's data."
CONTRIB = "Seongdae Kim conceived and designed the study, curated the data, performed the formal analysis, wrote the code, prepared the figures and tables, wrote the original draft, and reviewed and edited the manuscript. The author read and approved the final manuscript."
ACK = "None."
def data_statement(): return f"All source data are publicly available aggregate statistics from the national sources cited in the Method section. The processed district-year analytic data are available from the author on reasonable request. Analysis code is openly available at Zenodo (https://doi.org/{ZENODO}) and GitHub ({GITHUB})."
def code_statement(): return f"The analysis code and the scripts that generate every number, table, and figure are openly available at Zenodo (https://doi.org/{ZENODO}) and GitHub ({GITHUB})."

M_ = N["main"]; _o = M_[C.OLD]
TOK = {"cases_total": f"{N['cases_total']:,}", "share75_2024": f"{100*N['share75_2024']:.1f}", "asr_2011": f"{N['asr_2011']:.1f}", "asr_2024": f"{N['asr_2024']:.1f}",
       "asr_peak_year": str(max(N["asr"], key=N["asr"].get)), "asr_peak": f"{max(N['asr'].values()):.1f}", "asr_rise_pct": f"{100*(N['asr_ratio']-1):.0f}", "n_hot": str(N["n_hot"]), "hot_county": str(N["type_class"]["hotspot"]["county"]),
       "old_ci": f"{_o['IRR']:.3f}; 95% credible interval {_o['lo']:.3f} to {_o['hi']:.3f}"}
TOK["n_hot_noncap"] = str(N["n_hot"] - N["hot_capital"]); assert N["hot_capital"] <= 0.1 * N["n_hot"], "핫스팟 대부분이 비수도권일 때만 'outside the capital region' 문장"
def read_draft():
    md = open(DRAFT, encoding="utf-8").read(); md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    md = re.sub(r"«(\w+)»", lambda m: TOK[m.group(1)], md); S = {}; cur = None
    for line in md.split("\n"):
        m = re.match(r"^## (.+)$", line)
        if m: cur = m.group(1).strip(); S[cur] = []; continue
        if cur is not None: S[cur].append(line)
    return {k: [p.strip() for p in "\n".join(v).split("\n\n") if p.strip()] for k, v in S.items()}
def pandoc_cites(t): return re.sub(r"\s*\[(@[^\]]+)\]", lambda m: " {{" + ",".join(k.strip().lstrip("@") for k in m.group(1).split(";")) + "}}", t)
def all_keys():
    src = open(os.path.join(HERE, "content_jgms.py"), encoding="utf-8").read() + open(DRAFT, encoding="utf-8").read()
    src = re.sub(r"<!--.*?-->", "", src, flags=re.S); src = re.sub(r"(?m)^\s*#.*$", "", src)
    return sorted(k for k in {k.strip().lstrip("@") for g in re.findall(r"\[(@[^\]]+)\]", src) for k in g.split(";")} if re.fullmatch(r"(web:)?[a-z][a-z0-9]*", k))
KEYS = all_keys(); assert len(KEYS) <= 50, len(KEYS)

KEEP = {"Korea", "Korean", "South", "United", "States", "US", "USA", "UK", "England", "Japan", "Japanese", "Norwegian", "Italy", "Brazil", "Bayesian", "Laplace", "Gaussian", "Besag", "York", "Mollié", "Knorr-Held", "INLA", "BYM2", "COVID-19", "STROBE", "GBD", "ICD-10", "NHIS", "E-value", "Seoul", "Ontario", "Spatial+:", "Spatial+", "Northeast", "Lancet", "CAPNETZ", "COPD"}
def sent(t):   # 참고문헌 제목 문장형(첫 단어·고유명사·약어 유지)
    w = t.split(" "); caps = sum(1 for x in w[1:] if x[:1].isupper())
    if len(w) < 4 or caps < 0.5 * (len(w) - 1): return t
    out = [w[0]]
    for i, x in enumerate(w[1:], 1):
        core = x.strip("(),:;.?")
        keep = core in KEEP or core.isupper() or any(c.isdigit() for c in core) or out[-1].endswith((":", "?")) or (core.split("-")[0] in KEEP)
        if not keep: x = x[:1].lower() + x[1:]
        x = "-".join([x.split("-")[0]] + [y if (y in KEEP or y.isupper()) else y[:1].lower() + y[1:] for y in x.split("-")[1:]])
        out.append(x)
    t2 = " ".join(out)
    for ph in ("National Health Insurance Service", "Community Health Survey", "Global Burden of Disease Study", "Korean National Hospital Discharge In-depth Injury Survey"): t2 = re.sub(ph, ph, t2, flags=re.I)
    return t2.replace("(A JAGES", "(a JAGES").replace("Long-Term Care", "long-term care")
PAGES_FIX = {"kim2026living": "1366"}   # BMC Geriatr 논문번호(Crossref article-number)
JFIX = {"The Lancet. Infectious diseases": "Lancet Infect Dis", "Age and Ageing": "Age Ageing"}   # Index Medicus 약어
def vauthor(a): return a.strip().rstrip(".")
def ref(k):   # AMA 11판: 저자 6명 이하 전원, 7명 이상 3명 + et al. Title. J Abbr. Year;Vol:pages. doi:...
    r = REFS[k]
    if r["type"] == "web": return f"{r['authors']}. {r['title'].rstrip('.')}. Published {r['year']}. Accessed {r['accessed']}. {r['url']}"
    au = [vauthor(a) for a in r["authors"]]; a = ", ".join(au) if len(au) <= 6 else ", ".join(au[:3]) + ", et al"
    t = sent(r["title"].rstrip(".")); t = t + ("" if t.endswith(("?", "!")) else ".")
    j = JFIX.get(r["journal"], r["journal"]).replace(".", "")
    s_ = f"{a}. {t} {j}. {r['year']}"
    pg = str(r.get("pages") or PAGES_FIX.get(k, ""))
    if r.get("vol"): s_ += f";{r['vol']}" + (f":{pg}" if pg else "")
    elif pg: s_ += f":{pg}"
    return s_ + "." + (f" doi:{r['doi']}" if r.get("doi") else "")

class TX(JKMS):
    raw = False; table_bold = False   # 데이터 칸 무볼드(시리즈 규칙) — 헤더·카테고리 행 볼드는 booktabs가 처리
    def _emit(self, p, text, sz=12, bold=False, italic=False):
        if not self.raw: text = re.sub(r"(^|[\s(])-(?=\d)", "\\1\u2212", text)   # 음수는 U+2212
        return super()._emit(p, text, sz, bold, italic)
    def head(self, text, level=1):
        return super().head(text, level)

TAB1_COV = [("pop80_share", "Population aged 80 years or older, %"), ("urban_population_share", "Urban population share, %"), ("physicians_per_1000", "Physicians per 1,000"),
            ("influenza_vaccination_rate", "Influenza vaccination, %"), ("current_smoking_rate", "Current smoking, %"), ("walking_practice_rate", "Walking practice, %"),
            ("older_single_household_share", "Older adults living alone, % of households"), ("basic_livelihood_rate", "Basic livelihood security recipients, %"), ("ltc_hospitals_per_100k_65", "Long-term care hospitals per 100,000 aged 65+")]
def table1():
    T = N["T1"]; cols = ["W1_2011-15", "W2_2016-19", "W3_2020-24", "2011-2024"]
    rows = [["__H__", "Deaths"],
            ["  District-years, n"] + [f"{T[c]['n']:,}" for c in cols],
            ["  Deaths, n"] + [f"{T[c]['cases']:,}" for c in cols],
            ["  Person-years, million"] + [f"{T[c]['py']/1e6:.1f}" for c in cols],
            ["  Crude rate per 100,000"] + [f"{T[c]['crude']:.1f}" for c in cols],
            ["  Age-standardized rate per 100,000<sup>a</sup>"] + [f"{T[c]['asr']:.1f}" for c in cols],
            ["  District SMR, median<sup>b</sup>"] + [f"{T[c]['sir_med']:.2f}" for c in cols],
            ["  District SMR, 10th-90th percentile<sup>b</sup>"] + [f"{T[c]['sir_p10']:.2f}-{T[c]['sir_p90']:.2f}" for c in cols],
            ["__H__", "District characteristics, mean (standard deviation)"]]
    for v, lab in TAB1_COV:
        mx = max(abs(T[c]['cov'][v][0]) for c in cols); dp = 0 if mx >= 100 else (2 if mx < 1 else 1)
        rows.append([f"  {lab}"] + [f"{T[c]['cov'][v][0]:,.{dp}f} ({T[c]['cov'][v][1]:,.{dp}f})" for c in cols])
    foot = ("Note. Crude rates pool deaths and person-years over the window. Older adults living alone were first reported in 2015; earlier years were filled with district means of later years. Pneumonia, International Classification of Diseases, 10th revision, J12-J18. SMR = standardized mortality ratio. "
            f"<sup>a</sup>Direct standardization to the 2015 national population in eighteen 5-year age groups; window values are means of annual rates ({N['asr_2011']:.1f} in 2011 and {N['asr_2024']:.1f} in 2024). "
            "<sup>b</sup>Observed over indirectly age-standardized expected deaths summed over the window.")
    return ("Table 1. Pneumonia deaths and district characteristics by calendar window, 3,206 district-years in Korea, 2011-2024", ["Characteristic", "2011-2015", "2016-2019", "2020-2024", "2011-2024"], rows, foot)

GROUPS = [("Prevention and host susceptibility", ["influenza_vaccination_rate", "current_smoking_rate", "high_risk_drinking_rate", "screening_suspected_diabetes_share", "chewing_discomfort_rate_65plus"]),
          ("Physical activity", ["walking_practice_rate", "moderate_pa_rate", "public_sports_facilities_per_100k"]),
          ("Social, care, and environmental conditions", ["older_single_household_share", "basic_livelihood_rate", "ltc_hospitals_per_100k_65", "em_specialists_per_100k", "factory_land_share"]),
          ("Forced controls", ["urban_population_share", "physicians_per_1000", "sex_ratio", "fiscal_independence", "pop80_share"])]
LABEL = {"influenza_vaccination_rate": "Influenza vaccination", "current_smoking_rate": "Current smoking", "high_risk_drinking_rate": "High-risk drinking",
         "screening_suspected_diabetes_share": "Suspected diabetes (fasting glucose)", "chewing_discomfort_rate_65plus": "Chewing difficulty, aged 65 years or older",
         "walking_practice_rate": "Walking practice", "moderate_pa_rate": "Moderate-or-higher physical activity", "public_sports_facilities_per_100k": "Public sports facilities per 100,000",
         "older_single_household_share": "Older adults living alone", "basic_livelihood_rate": "Basic livelihood security recipients", "ltc_hospitals_per_100k_65": "Long-term care hospitals per 100,000 aged 65+",
         "em_specialists_per_100k": "Emergency medicine specialists per 100,000", "factory_land_share": "Factory land share of area",
         "urban_population_share": "Urban population share", "physicians_per_1000": "Physicians per 1,000", "sex_ratio": "Sex ratio", "fiscal_independence": "Fiscal autonomy", "pop80_share": "Population aged 80 years or older"}
BEST_KH = C.BEST
from decimal import Decimal, ROUND_HALF_UP
_pct = lambda f: str(int(Decimal(str(round(100 * f, 6))).quantize(Decimal("1"), rounding=ROUND_HALF_UP)))   # 반올림 전 값 기준 half-up(6.5→7)
def table2():
    rows = []; assert sum(len(v) for g, v in GROUPS[:-1]) == N["n_hyp"] and set(LABEL) == set(N["main"])
    for g, vs in GROUPS:
        rows.append(["__H__", g])
        for v in vs:
            m = N["main"][v]; mv = N["mv"].get(v); k = N["s43"][(BEST_KH, v)]
            rows.append([f"  {LABEL[v]}", f"{m['IRR']:.3f} ({m['lo']:.3f}-{m['hi']:.3f})", _pct(mv["cred_frac"]) if mv else "\u2013", f"{k[0]:.3f} ({k[1]:.3f}-{k[2]:.3f})"])
    foot = (f"Note. MRR = mortality rate ratio per 1 standard deviation; CrI = credible interval. Influenza vaccination had a credible association opposite to the expected direction; post hoc checks are in {C.sup('reverse')}. Principal model, negative binomial with a Besag-York-Molli\u00e9 2 district effect and random-walk and independent year effects (n={N['n_rows']:,} district-years); all 13 district characteristics and five forced controls are shown. Bounds shown as 1.000 were classified from unrounded values. "
            f"<sup>a</sup>Share of the 200 covariate-subset fits containing the characteristic in which the CrI excluded 1; \u2013, forced into every fit. "
            f"<sup>b</sup>Principal model plus a Knorr-Held type IV space-time interaction (structured district-by-year term allowing district-specific trends), the best-fitting interaction model (difference in widely applicable information criterion {C.dW(BEST_KH):,.0f}).")
    return ("Table 2. District characteristics and age-standardized pneumonia mortality in Korea, 2011-2024, in the principal and best-fitting space-time interaction models", ["Characteristic", "Principal MRR\n(95% CrI)", "Subsets\ncredible, %<sup>a</sup>", "Type IV MRR\n(95% CrI)<sup>b</sup>"], rows, foot)

FIGCAP = {
 1: "Residual geography and trend of pneumonia mortality in Korea, 2011-2024. (A) Residual spatial rate ratio by district, the posterior mean of the exponentiated Besag-York-Molli\u00e9 2 district effect from the principal model, that is, the district mortality ratio not explained by the covariates. Solid outlines, hot spots (posterior probability of a residual spatial rate ratio above 1 greater than 0.95); dashed outlines, cold spots (less than 0.05); thick lines, province boundaries; district boundaries as of 2024; the scale bar shows 100 km. (B) National crude (circles) and directly age-standardized (2015 population; squares) pneumonia death rates per 100,000 population. Map lines delineate study areas and do not necessarily depict accepted national boundaries.",
 2: "Mortality rate ratios per 1 standard deviation with 95% credible intervals for the four characteristics credible in the principal model, Korea, 2011-2024: principal model; principal model with Knorr-Held type II and type IV (best fitting) space-time interactions, which allow district-specific trends; principal model with province-by-year effects; and between-district (district mean) and within-district (two-way-centered deviation) components, each shown with its own marker shape. The dotted vertical line marks a ratio of 1.",
}
assert all(c.endswith(".") for c in FIGCAP.values())
ALT = {
 1: "Two panels. Panel A is a choropleth map of Korean districts colored by the residual spatial mortality ratio, with outlined hot-spot districts mostly outside the capital region and cold-spot districts concentrated in Seoul and Gyeonggi. Panel B is a line chart of national crude and age-standardized pneumonia death rates from 2011 to 2024, both rising, with the age-standardized rate peaking in 2018.",
 2: "Forest plot of mortality rate ratios with 95% credible intervals for four district characteristics (older adults living alone, long-term care hospitals, high-risk drinking, and influenza vaccination) across six model specifications; intervals in the principal model lie above 1, and intervals in the models allowing district-specific trends include 1.",
}   # JGMS: 캡션 바로 아래 'Alt text:' 줄
def foot_row(J, text, sz=9, ls=15):
    from docx.enum.text import WD_LINE_SPACING
    t = J.doc.tables[-1]; r = t.add_row(); m = r.cells[0].merge(r.cells[-1]); m.text = ""; p = m.paragraphs[0]
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY; p.paragraph_format.line_spacing = Pt(ls); p.paragraph_format.space_before = Pt(4)
    c = J.counting; J.counting = False; J._emit(p, text, sz); J.counting = c
def put_table(J, t, fs=9):
    c = J.counting; J.counting = False; J.table_fit(t[0], t[1], t[2], "", fs_max=fs, title_bold=True); foot_row(J, t[3], 8); J.counting = c

KEYWORDS = C.KEYWORDS; assert 3 <= len(KEYWORDS.split(";")) <= 5
ABS_HEADS = ("Background", "Methods", "Results", "Conclusions")
def _heads(D, sec, heads):
    out = []
    for p in D[sec]:
        m = re.match(r"^(\w+):\s*(.*)$", p, re.S); assert m and m.group(1) in heads, p[:40]; out.append((m.group(1), m.group(2)))
    assert [h for h, _ in out] == list(heads); return out
def abstract_paras(D): return _heads(D, "Abstract", ABS_HEADS)
def abs_words(D): return sum(len(t.split()) + 1 for _, t in abstract_paras(D))   # 소제목 포함
def build(bw=0, tw=0):   # 단일 익명: 제목면 포함 원고 1개
    D = read_draft(); J = TX(cite="paren")
    J.para(f"<b>{TITLE}</b>")
    J.para("Seongdae Kim, PhD", before=12)
    J.para(AFFIL, before=6)
    J.para(f"<b>Address correspondence to:</b> Seongdae Kim, PhD, {ADDRESS}. E-mail: kimsd@hongik.ac.kr. ORCID: {ORCID}", before=12)
    J.para(f"<b>Word count:</b> {tw:,} (title page, abstract, and main text); main text {bw:,}", before=6)
    J.para("<b>Number of data elements:</b> 4 (2 tables and 2 figures)", before=6)
    J.page_break(); J.head("Abstract", 1)
    for h, t in abstract_paras(D): J.para(f"<b>{h}:</b> {t}")
    J.para(f"<b>Keywords:</b> {KEYWORDS}", before=6)
    J.page_break(); J.counting = True
    J.head("Introduction", 1)
    for p in D["Introduction"]: J.para(pandoc_cites(p), indent=True)
    J.head("Method", 1)
    for h, p in C.METHODS: J.head(h, 2); J.para(pandoc_cites(p), indent=True)
    J.head("Results", 1)
    for h, p in C.RESULTS: J.head(h, 2); J.para(pandoc_cites(p), indent=True)
    J.head("Discussion", 1)
    for p in D["Discussion"]:
        if p.startswith("### "): J.head(p[4:].strip(), 2); continue
        J.para(pandoc_cites(p), indent=True)
    J.counting = False
    for h, t in (("Funding", FUNDING), ("Conflict of Interest", COMPETING), ("Acknowledgments", ACK), ("Author Contributions", CONTRIB), ("Data Availability", data_statement())):
        J.head(h, 1); J.para(t)
    assert sorted(J.cites) == KEYS, (set(J.cites) ^ set(KEYS))
    J.page_break(); J.head("References", 1); J.raw = True; rl = []
    for i, k in enumerate(J.cites, 1): s_ = f"{i}. " + ref(k); rl.append(s_); J.para(s_)
    J.raw = False
    for t in (table1(), table2()): J.page_break(); put_table(J, t)   # 표는 참고문헌 뒤, 각 쪽
    J.page_break(); J.head("Figure Captions", 1)
    for k in sorted(FIGCAP): J.para(f"<b>Figure {k}.</b> {FIGCAP[k]}", before=6); J.para(f"Alt text: {ALT[k]}")
    return J, rl, D

def docx_bw(path):
    from docx import Document
    t = "\n".join(x.text for x in Document(path).paragraphs)
    return len(t[t.find("\nIntroduction\n"):t.find("\nFunding\n")].split())
def docx_tw(path):   # JGMS 단어 수 = 제목면 + 초록 + 본문
    from docx import Document
    t = "\n".join(x.text for x in Document(path).paragraphs)
    return len(t[:t.find("\nFunding\n")].split())
def fix_orphans(path, heads, max_iter=8):
    from docx import Document
    fixed = set()
    for _ in range(max_iter):
        pdf = path.replace(".docx", ".pdf")
        subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_pneu_jgms", "--convert-to", "pdf", "--outdir", os.path.dirname(path), path], check=True, capture_output=True)
        pages = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout.split("\f"); orphan = None
        for pg in pages:
            ls = [re.sub(r"^\d+\s+", "", l.strip()) for l in pg.split("\n") if l.strip()]; ls = [l for l in ls if not re.fullmatch(r"\d+", l)]
            if ls and ls[-1] in heads:
                k = len(ls) - 1
                while k > 0 and ls[k - 1] in heads: k -= 1
                orphan = ls[k]; break
        if orphan is None: return
        if orphan in fixed: print("orphan persists, stop:", orphan); return
        fixed.add(orphan); d = Document(path)
        for p in d.paragraphs:
            if p.text.strip() == orphan:
                np_ = OxmlElement("w:p"); r = OxmlElement("w:r"); br = OxmlElement("w:br"); br.set(qn("w:type"), "page"); r.append(br); np_.append(r); p._p.addprevious(np_); break
        d.save(path); print("orphan fixed:", orphan)

if __name__ == "__main__":
    p = os.path.join(OUT, "Manuscript.docx")
    J, rl, D = build(); J.doc_title = "Manuscript"; J.save(p); bw = docx_bw(p); tw = docx_tw(p) + 6
    for _ in range(3):
        J, rl, D = build(bw, tw); J.doc_title = "Manuscript"; J.save(p)
        if docx_tw(p) == tw: break
        tw = docx_tw(p)
    assert docx_bw(p) == bw and docx_tw(p) == tw, (bw, tw, docx_tw(p))
    assert tw <= 5200, tw
    heads = {"Abstract", "Introduction", "Method", "Results", "Discussion", "References", "Figure Captions", "Funding", "Conflict of Interest", "Acknowledgments", "Author Contributions", "Data Availability"} | {h for h, _ in C.METHODS + C.RESULTS} | {x[4:].strip() for x in D["Discussion"] if x.startswith("### ")}
    fix_orphans(p, heads)
    aw = abs_words(D)
    open(os.path.join(OUT, "wordcount.txt"), "w").write(f"body_words={bw}\ntotal_words={tw}\nabstract_words={aw}\nrefs={len(KEYS)}\ntables=2\nfigures=2\ntitle_words={len(TITLE.split())}\n")
    print(f"body {bw} | total {tw} | abstract {aw} | refs {len(KEYS)} | title words {len(TITLE.split())}")
