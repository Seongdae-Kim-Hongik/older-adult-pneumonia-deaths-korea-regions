# check_jgms.py — 14호 폐렴 사망 Journals of Gerontology: Medical Sciences 원고 검사기(2026-11-20; 규정 논문폴더 114_노인폐렴사망지리_JGMS/00_저널가이드/JGMS_가이드_요점_261120.md).
#  저널 규정 > 플레이북(3선 표·검은 네모·지문·그림) > 문체·수치. sanitize 뒤에 돌린다. FAIL 0이면 PASS(Zenodo PENDING은 경고).
import os, re, subprocess, zipfile
from docx import Document
from docx.oxml.ns import qn
from PIL import Image
import content_jgms as C
from build_jgms import read_draft, abstract_paras, abs_words, TITLE, ORCID, KEYS, FUNDING, COMPETING, KEYWORDS, ZENODO, GITHUB, REPO, OLD_REPOS, JOURNAL, TOK, ALT
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out")
N = C.N; R = []
def ok(c, m): R.append(("ok  " if c else "FAIL") + " " + m)
W = dict(l.split("=") for l in open(os.path.join(OUT, "wordcount.txt")).read().split())
D = read_draft(); AB = abstract_paras(D); ab = " ".join(t for _, t in AB)
MSF, SUPF, CLF = "Manuscript.docx", "Supplement.docx", "Cover_Letter.docx"
for f in (MSF, SUPF, CLF, "Manuscript.pdf", "Supplement.pdf", "Cover_Letter.pdf", "Figures/Fig1.tif", "Figures/Fig2.tif"): ok(os.path.exists(os.path.join(OUT, f)), f"파일 {f}")
supt = "\n".join(p.text for p in Document(os.path.join(OUT, SUPF)).paragraphs)
ok("eAppendix. STROBE checklist" in supt, "STROBE = Supplement eAppendix")
ok(all(t in supt[:2500] for t in ("Supplement", "Contents", "eTable 1.", "eTable 5.", "eFigure 1.", "eMethods.", "eAppendix.", TITLE)), "Supplement 첫 쪽 요소 번호·제목 목록(JGMS)")
ok(not re.search(r"Table S\d|Fig\. S\d|Appendix S\d", supt), "보충 옛 번호(S·Online Resource) 없음")
# 1. JGMS 규정
aw = abs_words(D); ok(aw <= 250, f"초록 {aw}단어 ≤250(소제목 포함)")
ok([h for h, _ in AB] == ["Background", "Methods", "Results", "Conclusions"], "구조 초록 Background/Methods/Results/Conclusions")
ok(not re.search(r"\[@", ab), "초록 인용 없음")
_abbr = set(re.findall(r"\b[A-Z]{2,}\b", ab)) - {"MRR", "MRRs"}; ok(not _abbr and "mortality rate ratios (MRRs)" in ab, f"초록 약어는 정의 후만 {_abbr}")
ok(all(v in ab for k, v in TOK.items() if k not in ("asr_rise_pct",)), f"초록 수치 = 결과 CSV(토큰) {[(k, v) for k, v in TOK.items() if v not in ab]}")
OLD = [t.lower() for t in C.OLD_TITLES]
ok(":" not in TITLE and "229" not in TITLE and "standardi" not in TITLE.lower() and TITLE.lower() not in OLD and not re.search(r"\b[A-Z]{2,}\b", TITLE), f"새 제목 {len(TITLE.split())}단어, 쌍점·약어·시리즈 틀·이전 제목 없음")
ok(int(W["refs"]) == len(KEYS) <= 50, f"참고문헌 {len(KEYS)}(≤50)"); ok(int(W["total_words"]) <= 5200, f"제목면+초록+본문 {W['total_words']}단어(≤5200)"); ok(int(W["tables"]) + int(W["figures"]) <= 5, "자료 요소 ≤5")
KW = [k.strip() for k in KEYWORDS.split(";")]; ok(3 <= len(KW) <= 5 and not any(w.lower() in TITLE.lower() for k in KW for w in k.split()) and "older adults" not in KEYWORDS.lower(), f"키워드 {len(KW)}개(3-5, 제목에 없는 말)")
d = Document(os.path.join(OUT, MSF)); _ps = [p.text.strip() for p in d.paragraphs]; _dx = "\n".join(_ps); tp = _dx[:_dx.find("\nAbstract\n")]
for t in (TITLE, "Seongdae Kim, PhD", "kimsd@hongik.ac.kr", ORCID, "Hongik University", "Seoul", "Republic of Korea", "Address correspondence to", f"Word count: {int(W['total_words']):,}", f"main text {int(W['body_words']):,}", "Number of data elements: 4"): ok(t in tp, f"제목면 '{t[:40]}'")
_ord = ["Abstract", "Introduction", "Method", "Results", "Discussion", "Funding", "Conflict of Interest", "Acknowledgments", "Author Contributions", "Data Availability", "References", "Figure Captions"]
pos = [_ps.index(k) if k in _ps else -1 for k in _ord]; ok(all(p >= 0 for p in pos) and pos == sorted(pos), f"절 순서 {' → '.join(_ord)}")
iT1 = next(i for i, p in enumerate(_ps) if p.startswith("Table 1. ")); iT2 = next(i for i, p in enumerate(_ps) if p.startswith("Table 2. ")); ok(pos[_ord.index("References")] < iT1 < iT2 < pos[_ord.index("Figure Captions")], "표는 참고문헌 뒤, 캡션 맨 끝")
ok(all(any(c.text.strip().startswith("Note. ") for r in t.rows for c in r.cells) for t in d.tables), "표 주석 'Note.'로 시작(AMA 11판)")
ok(FUNDING in _dx and COMPETING in _dx and "7002340-202511-HR-012" in _dx and "7002340-202611-HR-040" in _dx and "Declaration of Helsinki" in _dx and "waived informed consent" in _dx, "연구비·이해충돌·윤리(IRB 번호·헬싱키·동의 면제)")
meth = _dx[_dx.find("\nMethod\n"):_dx.find("\nResults\n")]
ok("Claude (Anthropic) and ChatGPT (OpenAI) were used only for translation and English-language editing" in meth, "AI 사용 = Method에 번역·영문 교정만(JGMS 규정)")
das = _dx[_dx.find("\nData Availability\n"):_dx.find("\nReferences\n")]
ok(f"https://doi.org/{ZENODO}" in das and GITHUB in das and "Analysis code is openly available at Zenodo" in das, "Data Availability = Zenodo DOI + GitHub")
legs = _dx[_dx.find("\nFigure Captions\n"):]
ok(len(re.findall(r"\nFigure [12]\. ", legs)) == 2 and legs.count("\nAlt text: ") == 2 and all(ALT[k] in legs for k in ALT), "캡션 'Figure n.' + 바로 아래 Alt text")
x = zipfile.ZipFile(os.path.join(OUT, MSF)).read("word/document.xml").decode()
ok("<w:drawing" not in x, "원고에 그림 삽입 없음(별도 TIFF)")
ok("Times New Roman" in x and 'w:line="480"' in zipfile.ZipFile(os.path.join(OUT, MSF)).read("word/styles.xml").decode(), "Times New Roman·더블 스페이스")
ok("PAGE" in "".join(zipfile.ZipFile(os.path.join(OUT, MSF)).read(n).decode() for n in zipfile.ZipFile(os.path.join(OUT, MSF)).namelist() if n.startswith("word/footer")), "자동 쪽 번호")
for k in (1, 2):
    im = Image.open(os.path.join(OUT, "Figures", f"Fig{k}.tif")); w_mm = im.size[0] / im.info["dpi"][0] * 25.4
    ok(im.mode == "RGB" and round(im.info.get("dpi", (0, 0))[0]) >= 300 and w_mm <= 170.5, f"Fig{k}.tif RGB·{round(im.info['dpi'][0])} dpi·폭 {w_mm:.0f} mm(≤170)")
ok("Map lines delineate study areas" in legs and "(A)" in legs, "지도 면책·패널 지칭 대문자(저자 규칙)")
ok(not re.search(r"\b(red|blue|green|orange|purple|colou?r)\b", legs, re.I), "그림 설명에 색 의존 표현 없음")
ok(not re.search(r"\b(elderly|seniors|the aged|elders)\b", _dx[:_dx.find("\nReferences\n")] + supt, re.I), "JGMS 용어(elderly·seniors·the aged 금지, 참고문헌 제목 제외)")
# 2. 표·문서 위생
for nm, f in (("원고", MSF), ("보충", SUPF), ("커버", CLF)):
    dd = Document(os.path.join(OUT, f))
    for i, t in enumerate(dd.tables):
        b = t._tbl.tblPr.find(qn("w:tblBorders"))
        ok(b is not None and all(b.find(qn(f"w:{s}")) is not None and b.find(qn(f"w:{s}")).get(qn("w:val")) == "nil" for s in ("insideV", "insideH", "left", "right")), f"{nm} 표{i+1} 3선(세로선·안쪽 가로선 없음)")
        bad = [r.text for j, row in enumerate(t.rows) if j > 0 for c in row.cells if len({id(x_._tc) for x_ in row.cells}) == len(row.cells) for p in c.paragraphs for r in p.runs if r.bold and r.text.strip()]
        ok(not bad, f"{nm} 표{i+1} 데이터 칸 볼드 없음 {bad[:2]}")
        ok(not [c.text for r in t.rows for c in r.cells if re.search(r"\d\*+", c.text)], f"{nm} 표{i+1} 유의성 별표 없음")
    xx = subprocess.run(["unzip", "-p", os.path.join(OUT, f), "word/*.xml"], capture_output=True, text=True).stdout
    ok(len(re.findall(r"<w:keepNext[ />]|<w:keepLines[ />]|<w:pageBreakBefore[ />]", xx)) == 0, f"{nm} Word 검은 네모 0건")
    zz = zipfile.ZipFile(os.path.join(OUT, f)); core = zz.read("docProps/core.xml").decode(); app = zz.read("docProps/app.xml").decode()
    ok("2013-12-23" not in core and not any(n.startswith("customXml/") for n in zz.namelist()) and "<Words>0<" not in app, f"{nm} python-docx 지문 없음(sanitize 후)")
    ok("<dc:creator>Seongdae Kim</dc:creator>" in core, f"{nm} 작성자 메타 = 저자(단일 익명)")
# 3. 문체·인용
body = re.sub(r"\s+", " ", _dx[_dx.find("\nIntroduction\n"):_dx.find("\nFunding\n")])
ok(not re.search(r"\b(we|our|us|We|Our)\b", body), "1인칭 없음")
cov = subprocess.run(["pdftotext", os.path.join(OUT, CLF.replace(".docx", ".pdf")), "-"], capture_output=True, text=True).stdout
ok("Dr Siette" in cov and "Medical Sciences" in cov and TITLE.split()[0] in cov and "Seongdae Kim, PhD" in cov and "latest complete year" in cov, "커버 수신(편집장)·저널명·제목·서명자·10년 넘은 자료 근거")
ok("<w:drawing" in zipfile.ZipFile(os.path.join(OUT, CLF)).read("word/document.xml").decode(), "커버 서명 이미지")
ok(not re.search(r"(?i)reject|previous(ly)? submitted|resubmi|overlap|preprint", cov), "커버 이전 투고·중복 고지 없음")
alltxt = _dx + supt + cov
ok("—" not in alltxt and not re.search(r"[가-힣]", alltxt), "em-dash·한글 없음")
ok(not re.search(r"\bsignifican", _dx + supt, re.I), "'significant' 없음")
UK = r"\b(ischaemi\w*|haemorrh\w*|modelled|modelling|behaviour\w*|neighbour\w*|centre\w*|labelled|favour\w*|analys(e|ed|ing)|ageing|programme\w*|colour\w*)\b"
nonref = body + " " + supt + " " + cov + " " + legs
uk = sorted(set(m.group(0) for m in re.finditer(UK, nonref))); ok(not uk or uk == ["ageing"], f"미국식 철자(영국식 남음 없음) {uk}")
ok(not re.search(r"\[(@|web:)", _dx) and "{{" not in _dx, "미해결 인용 없음")
disc = _dx[_dx.find("\nDiscussion\n"):_dx.find("\nFunding\n")]; disc_nc = re.sub(r"\([\d, \-–]+\)", "", disc)
_dn = re.findall(r".{15}\d.{8}", disc_nc)[:3]; ok(not _dn, f"고찰·결론에 숫자 없음 {_dn}")
ok("Implications for geriatric care" in _ps and all(k in body for k in ("frail", "dysphagia", "long-term care hospitals", "living alone")), "노인의학 각도(노쇠·삼킴·요양병원·독거) 서론·고찰")
ok(f"{100*N['share75_2024']:.1f}% at 75 years or older" in body or f"{100*N['share75_2024']:.1f}%" in body, "고령(75세 이상) 사망 비중 본문 제시(최고령층 범위)")
ok(not any(":" in h for h, _ in C.METHODS + C.RESULTS) and not any(":" in p for p in D["Discussion"] if p.startswith("###")), "소제목 쌍점 없음")
refs = _dx[_dx.find("\nReferences\n"):_dx.find("\nTable 1. ")]; RL = [l for l in refs.split("\n") if re.match(r"^\d+\. ", l)]
ok(len(RL) == len(KEYS), f"참고문헌 목록 {len(RL)}개")
ok(not re.search(r"github|zenodo", refs, re.I), "참고문헌에 GitHub·Zenodo 없음")
ok(all(re.search(r"\. (19|20)\d{2}[;.]", l) or "Accessed" in l for l in RL), "AMA형(학술지. 연도;권:쪽) 형식")
ok(sum(" doi:10." in l for l in RL) >= len(RL) - 3, f"AMA doi: 표기 {sum(' doi:10.' in l for l in RL)}/{len(RL)}(웹 문헌 3개 제외)")
ok(not any(re.search(r"^\d+\. ([^.]+, ){6,}", l) for l in RL), "AMA 저자 7명 이상은 3명 + et al")
ok("Cheol Seong" not in refs, "뒤집힌 한국인 이름 없음")
nums = [int(n) for g in re.findall(r"\(([\d]+(?:[, \-–]+\d+)*)\)", body) for part in g.replace("–", "-").split(",") for n in (range(int(part.split("-")[0]), int(part.split("-")[1]) + 1) if "-" in part else [int(part)])]
first = []; [first.append(n) for n in nums if n not in first]; ok(first == list(range(1, len(KEYS) + 1)), "인용 번호 첫 등장 순서 1..n")
for k in C.SUP:
    lab = C.sup(k); ok(lab in _dx and C.sup(k, True) in supt, f"보충 '{lab}' 본문 인용·ESM 존재")
_seen = []; [_seen.append(m.group(0)) for m in re.finditer(r"eTable \d+", body) if m.group(0) not in _seen]
ok(_seen == [f"eTable {i}" for i in range(1, 6)], f"보충 표 첫 인용 순서 eTable 1..5 {_seen}")
ok(not re.search(r"\[\d", body) and not re.search(r"\bFig\. \d", body), "본문 인용은 괄호 번호, 그림은 'Figure n'(AMA)")
TRACE = r"previous submission|prior submission|resubmi|version 1|\bv[12]\b"
_nr = alltxt.replace(refs, ""); ok(not re.search(TRACE, _nr, re.I), f"이전 투고·버전 흔적 없음 {re.findall(TRACE, _nr, re.I)[:3]}")
ok(REPO not in OLD_REPOS, f"새 저장소 이름 {REPO}")
pend = "PENDING" in ZENODO; R.append(("WARN" if pend else "ok  ") + f" Zenodo DOI {ZENODO}" + (" (부모 처리: 게시 후 zenodo_doi.txt 갱신·재빌드)" if pend else ""))
open(os.path.join(OUT, "check_jgms.txt"), "w").write("\n".join(R)); nf = sum(r.startswith("FAIL") for r in R)
print("\n".join(r for r in R if not r.startswith("ok")) or "", f"\n{len(R)} checks, FAIL {nf}", "PASS" if nf == 0 else "")
