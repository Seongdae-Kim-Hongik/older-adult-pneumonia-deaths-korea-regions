#!/bin/bash
# run_all.sh — Journals of Gerontology: Medical Sciences 원고 빌드(14호 폐렴 사망). 그림 → 원고 → Supplement → 커버 → sanitize → PDF → 검사기.
#  Zenodo DOI는 논문폴더 114_노인폐렴사망지리_JGMS/06_GitHub_Zenodo/zenodo_doi.txt 한 줄에서 읽는다(게시 전 10.5281/zenodo.PENDING). 참고문헌 캐시 갱신(네트워크)은 build_refs_jgms.py를 따로 실행.
set -e; cd "$(dirname "$0")"; O=../out
python3 figs_jgms.py 2>&1 | grep -v Warning || true
python3 build_jgms.py
python3 esm_jgms.py
python3 post_esm.py $O/Supplement.docx
python3 cover_jgms.py
python3 sanitize_docx.py --no-anon $O/Manuscript.docx $O/Supplement.docx $O/Cover_Letter.docx > /dev/null
for f in Manuscript Supplement Cover_Letter; do /opt/homebrew/bin/soffice --headless -env:UserInstallation=file:///tmp/lo_pneu_jgms_all --convert-to pdf --outdir $O $O/$f.docx > /dev/null 2>&1; done
python3 check_jgms.py
