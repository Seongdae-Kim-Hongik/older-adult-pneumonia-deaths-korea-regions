#!/usr/bin/env python3
# 39m_pneu — 14호 폐렴 사망(PNEU, J12-J18) 세분 간접표준화 E(2026-11-08). 공유 원본 39m_build_Estd_mort.py는 건드리지 않고(15호 병렬 세션 보호)
#  원문을 읽어 사인 표에 PNEU 한 줄만 더해 실행한다(연령 구간·분모·재척도·검증 규칙 동일). 사용: ST_FBDZIP=<창원 교정 인구> [ST_E2_PANEL_SUF=_std3] python3 39m_pneu.py
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "39m_build_Estd_mort.py"), encoding="utf-8").read()
a = 'TAG = sys.argv[1]; assert TAG in CAUSES, TAG; NC = CAUSES[TAG]'
assert src.count(a) == 1
src = src.replace(a, 'CAUSES["PNEU"] = "폐렴 (J12-J18)"\n' + a)
sys.argv = ["39m_build_Estd_mort.py", "PNEU"]
exec(compile(src, os.path.join(HERE, "39m_build_Estd_mort.py"), "exec"), {"__file__": os.path.join(HERE, "39m_build_Estd_mort.py"), "__name__": "__main__"})
