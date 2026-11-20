#!/usr/bin/env python3
# 39ms_pneu — 14호 폐렴 사망 성×연령 E(민감도 ssx, 2026-11-08 포바포 지적). 공유 원본 39ms_build_Esex_mort.py는 건드리지 않고 사인 표에 PNEU만 더해 실행.
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "39ms_build_Esex_mort.py"), encoding="utf-8").read()
a = 'TAG = sys.argv[1]; assert TAG in CAUSES, TAG; NC = CAUSES[TAG]'
assert src.count(a) == 1
src = src.replace(a, 'CAUSES["PNEU"] = "폐렴 (J12-J18)"\n' + a)
sys.argv = ["39ms_build_Esex_mort.py", "PNEU"]
exec(compile(src, os.path.join(HERE, "39ms_build_Esex_mort.py"), "exec"), {"__file__": os.path.join(HERE, "39ms_build_Esex_mort.py"), "__name__": "__main__"})
