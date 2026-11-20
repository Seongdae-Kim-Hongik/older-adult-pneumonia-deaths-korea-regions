# cover_jgms.py — 14호 폐렴 사망 Journals of Gerontology: Medical Sciences 커버레터(미국식 철자, 1쪽, 단독 저자 비인칭, 서명 이미지, 2026-11-20).
#  체육 시리즈 = 김성대 단독·교신 명의. 자료 중복·이전 투고 고지 금지. 추천·제외 심사자는 커버에 넣지 않음(포털 칸). 편집장 = Joyce Siette, PhD(Medical Sciences, 저널 About 2026-11-20). 10년 넘은 자료 근거 문장 필수(JGMS 범위 규정).
import os, re, datetime, subprocess
from docx import Document
from docx.shared import Pt, Cm
import content_jgms as C
from build_jgms import TITLE as DTITLE, GITHUB, ZENODO, ADDRESS, JOURNAL
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "out")
N = C.N; W = dict(l.split("=") for l in open(os.path.join(OUT, "wordcount.txt")).read().split()); M = N["main"]
assert N["asr_ratio"] > 1.5 and N["hot_capital"] <= 0.1 * N["n_hot"] and not any(N["s43"][("KH_typeIV", v)][3] for v in C.ROB) and not M[C.WALK]["cred"]
_d = datetime.date.today()
cl = [f"{_d:%B} {_d.day}, {_d.year}", "Joyce Siette, PhD", f"Editor-in-Chief, {JOURNAL}", "",
      "Dear Dr Siette,",
      f"Please find enclosed the manuscript entitled \"{DTITLE}\" by Seongdae Kim, for consideration as a Research Article in the Medical Sciences section of The Journals of Gerontology, Series A.",
      f"Pneumonia is above all a cause of death in late life: in Korea in 2024, {100*N['share75_2024']:.0f}% of pneumonia deaths occurred among adults aged 75 years or older. Using complete national death registration for all {N['n_districts']} districts, indirect standardization in eighteen age groups up to 85 years or older, and Bayesian spatiotemporal models, this study shows that the age-standardized pneumonia death rate rose by {100*(N['asr_ratio']-1):.0f}% between 2011 and 2024 and that residual excess mortality concentrated in districts outside the capital region, many of them rural counties. Thirteen district markers drawn from the epidemiology of pneumonia death in older adults, including living alone, long-term care hospitals, chewing difficulty, influenza vaccination, drinking, physical activity, and deprivation, explained little of this geography: the associations in the principal model moved toward the null once each district was allowed its own trend, and an association of influenza vaccination opposite to the expected direction is reported and examined.",
      "The study fits the journal's interest in environmental and social determinants of aging and in health outcomes among the oldest old. It identifies where pneumonia mortality among older adults remains high after age standardization and shows that district averages of the usual risk factors cannot account for it, pointing to swallowing function, frailty, care pathways in long-term care hospitals, and death certification in very old adults as questions for individual-level geriatric research.",
      f"The analysis uses data through 2024, the latest complete year of national death registration. Earlier years back to 2011 are included because the questions concern the trend of age-standardized mortality and the persistence of its geography, which a short recent window cannot answer; all district characteristics were harmonized over the same 14 years.",
      f"The manuscript contains {int(W['total_words']):,} words including the title page and abstract (main text {int(W['body_words']):,}), a structured abstract of {int(W['abstract_words'])} words, two tables, two figures, and {W['refs']} references; the Supplement contains supplementary methods, tables, a figure, and the STROBE checklist. All figures are original. The analysis code is openly available at Zenodo (https://doi.org/{ZENODO}) and GitHub ({GITHUB}).",
      "This manuscript has not been published previously and is not under consideration for publication elsewhere. The author declares no conflicts of interest and received no specific funding. Claude (Anthropic) and ChatGPT (OpenAI) were used only for translation and English-language editing; the author reviewed and edited all output and takes full responsibility for the content. The Institutional Review Board of Hongik University approved the study (7002340-202511-HR-012; continuing review 7002340-202611-HR-040) and waived informed consent because only published aggregate statistics were used.",
      "Thank you for considering this manuscript.", "", "Sincerely,", "[[SIG]]",
      "Seongdae Kim, PhD (corresponding author)", ADDRESS, "E-mail: kimsd@hongik.ac.kr; ORCID: 0000-0002-1525-0091"]
d = Document(); st = d.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11); st.paragraph_format.space_after = Pt(4); st.paragraph_format.line_spacing = 1.0
for s in d.sections: s.page_width, s.page_height = Cm(21), Cm(29.7); s.left_margin = s.right_margin = Cm(2.3); s.top_margin = s.bottom_margin = Cm(2.0)
gap = False
for t in cl:
    if t == "": gap = True; continue
    if t == "[[SIG]]":
        p = d.add_paragraph(); p.add_run().add_picture(os.path.join(HERE, "signature_kim.png"), height=Cm(1.3)); continue
    p = d.add_paragraph(t)
    if gap: p.paragraph_format.space_before = Pt(10); gap = False
d.core_properties.author = "Seongdae Kim"; d.core_properties.last_modified_by = "Seongdae Kim"; d.core_properties.title = "Cover Letter"; d.core_properties.comments = ""
fp = os.path.join(OUT, "Cover_Letter.docx"); d.save(fp)
subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_pneu_jgms_cl", "--convert-to", "pdf", "--outdir", OUT, fp], capture_output=True)
txt = subprocess.run(["pdftotext", fp.replace(".docx", ".pdf"), "-"], capture_output=True, text=True).stdout
assert not re.search(r"\b(we|our|us|I)\b", txt) and "—" not in txt and "7002340-202611-HR-040" in txt, "문체·IRB"
assert not re.search(r"(?i)reject|previous(ly)? submitted|resubmi|overlap|preprint", txt), "이전 투고·중복 고지 금지"
pages = subprocess.run(["pdfinfo", fp.replace(".docx", ".pdf")], capture_output=True, text=True).stdout.split("Pages:")[1].split()[0]
assert pages == "1", pages; print("cover pages", pages)
