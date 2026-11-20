# 88r(88g 머리 복제) — 공간 트랙 질환 공통 민감도 묶음(88c·88f 정신질환판 일반화, 2026-10-21 유방암 2호부터).
#  사용(01_스크립트/): TAG=BRCA ST_VER=std GROUP=1..6 [NCO=GCA,INFECT] [FOCAL=walking_practice_rate] [SMOOTH=sex_ratio] [DROPS='{"name":["v1","v2"]}'] Rscript 88g_sens_suite.R
#  입력 = 88g_sens_prep.py 산출 S41_panel_*. 산출 = results_<VER>/S41_part_<analysis>.csv(공변량별 IRR + 적합 요약), S41_hot_<analysis>.csv(핫스팟)
#  GROUP 1 = 우도·시간·평활·Spatial+·지연·극단·이동평균·비교결과 / 2 = 시도 빼기 / 3 = 연도 빼기·짝홀·2024 조건부 검증 / 4 = 대체 잡음 20회
#        5 = 같은 기간 비지연 비교 / 6 = 이원 분해(강건 집합)·변수 제외(DROPS)
suppressPackageStartupMessages({library(INLA);library(sf);library(spdep);library(jsonlite)})
TAG<-Sys.getenv("TAG");stopifnot(nzchar(TAG));VER<-Sys.getenv("ST_VER",unset="std");SUF<-if(nzchar(VER))paste0("_",VER) else ""
ROOT<-normalizePath(file.path(dirname(sub("--file=","",grep("--file=",commandArgs(),value=TRUE))),".."))
SHP<-Sys.getenv("ST_SHP",file.path(normalizePath(file.path(dirname(sub("--file=","",grep("--file=",commandArgs(),value=TRUE))),"..")),"data","boundary","final.shp"))
OUTD<-file.path(ROOT,"04_분석",TAG);RES<-file.path(OUTD,paste0("results",SUF))
inla.setOption(num.threads="1:1")
LOG<-function(...)cat(sprintf("[88g %s %s] ",TAG,format(Sys.time(),"%H:%M:%S")),sprintf(...),"\n",sep="")
S<-fromJSON(file.path(OUTD,sprintf("config_%s%s.json",TAG,SUF)),simplifyVector=TRUE)
INFO<-fromJSON(file.path(OUTD,sprintf("panel_INFO_%s%s.json",TAG,SUF)))
DD<-read.csv(file.path(OUTD,sprintf("panel_%s%s.csv",TAG,SUF)),fileEncoding="UTF-8-BOM",stringsAsFactors=FALSE);DD$fbd_region<-enc2utf8(DD$fbd_region)
HB<-readLines(file.path(OUTD,sprintf("HM_best_%s%s.txt",TAG,SUF)));kv<-function(k)sub(paste0("^",k,"="),"",grep(paste0("^",k,"="),HB,value=TRUE)[1])
MAINFAM<-kv("main_family");BEST<-kv("best_set");FORCED<-S$forced;SETS<-lapply(S$sets_after_vif,as.character);HYPV<-SETS[[BEST]];MAINV<-unique(c(HYPV,FORCED))
ROB<-read.csv(file.path(RES,"S7_multiverse_summary.csv"),stringsAsFactors=FALSE);ROBV<-ROB$cov[ROB$robust];NR<-length(ROBV)
M3<-read.csv(file.path(RES,"S3_main_IRR.csv"),stringsAsFactors=FALSE);msign<-setNames(sign(log(M3$IRR)),M3$cov)
FOCAL<-Sys.getenv("FOCAL",unset=if(NR)ROBV[1] else HYPV[1])
LOG("family %s, set %s (%d hyp + %d forced), robust %d (%s), focal %s",MAINFAM,BEST,length(HYPV),length(FORCED),NR,paste(ROBV,collapse=";"),FOCAL)

G<-st_read(SHP,quiet=TRUE);G$region<-enc2utf8(G$region);n<-nrow(G)
g<-inla.read.graph(file.path(RES,sprintf("nb_%s.graph",TAG)));stopifnot(g$n==n)
DD<-DD[order(DD$year,match(DD$fbd_region,G$region)),];DD$area<-match(DD$fbd_region,G$region);Y0<-min(DD$year);DD$time<-DD$year-Y0+1;DD$yiid<-DD$time;DD$id<-seq_len(nrow(DD))
pc<-list(prec=list(prior="pc.prec",param=c(0.5,0.01)),phi=list(prior="pc",param=c(0.5,2/3)));pcp<-list(prec=list(prior="pc.prec",param=c(0.5,0.01)))
CF<-list(mean=0,prec=4,mean.intercept=0,prec.intercept=0.001)
SPf<-function(gr="g")sprintf("f(area,model='bym2',graph=%s,scale.model=TRUE,constr=TRUE,hyper=pc)",gr)
TI<-"f(time,model='rw1',scale.model=TRUE,hyper=pcp)";IT<-"f(yiid,model='iid',hyper=pcp)"
bt<-function(v)sprintf("`%s`",v)
irr<-function(m,v){r<-m$summary.fixed[v,,drop=FALSE];pg<-1-inla.pmarginal(0,m$marginals.fixed[[v]])
  data.frame(cov=v,IRR=round(exp(r$mean),3),lo=round(exp(r$`0.025quant`),3),hi=round(exp(r$`0.975quant`),3),P_gt1=round(pg,3),cred=(r$`0.025quant`>0|r$`0.975quant`<0),stringsAsFactors=FALSE)}
M6<-read.csv(file.path(RES,"S6_spatial_RR.csv"),stringsAsFactors=FALSE);hot0<-M6$fbd_region[M6$class=="hotspot"]
rdp<-function(f){x<-read.csv(file.path(RES,f),fileEncoding="UTF-8",stringsAsFactors=FALSE);x$fbd_region<-enc2utf8(x$fbd_region);x}
mrg<-function(d,X,cols){d<-d[,setdiff(names(d),cols)];d<-merge(d,X[,c("year","fbd_region",cols)],by=c("year","fbd_region"),all.x=TRUE,sort=FALSE);d[order(d$id),]}
fitX<-function(vars,data,fam=MAINFAM,ti=TI,extra=character(0),sp=SPf(),cfg=FALSE){
  rhs<-c("1",bt(vars),extra,sp,ti,IT);rhs<-rhs[nzchar(rhs)];form<-as.formula(paste("cases ~",paste(rhs,collapse="+")))
  m<-tryCatch(inla(form,family=fam,data=data,E=E,control.fixed=CF,control.compute=list(waic=TRUE,config=cfg),control.predictor=list(compute=TRUE,link=1),
    control.inla=list(control.vb=list(emergency=50)),verbose=FALSE),error=function(e){message("fail: ",conditionMessage(e));NULL})
  if(is.null(m))m<-tryCatch(inla(form,family=fam,data=data,E=E,control.fixed=CF,control.compute=list(waic=TRUE,config=cfg),control.predictor=list(compute=TRUE,link=1),
    control.inla=list(control.vb=list(emergency=50),int.strategy="eb",strategy="gaussian"),verbose=FALSE),error=function(e){message("robust fail: ",conditionMessage(e));NULL})
  m}

summ<-function(an,item,m,data,note="",vars=MAINV){
  if(is.null(m)){LOG("%s FAILED",an);return(invisible())}
  r<-do.call(rbind,lapply(intersect(vars,rownames(m$summary.fixed)),function(v)irr(m,v)))
  out<-data.frame(analysis=an,item=item,r,WAIC=round(m$waic$waic,1),note=note,stringsAsFactors=FALSE)
  write.csv(out,file.path(RES,sprintf("S44_reverse_%s.csv",an)),row.names=FALSE,fileEncoding="UTF-8")
  for(v in intersect(c(REV,MBP),out$cov)){w<-out[out$cov==v,];LOG("%-26s %-40s %.3f (%.3f-%.3f)%s WAIC %.1f",an,v,w$IRR,w$lo,w$hi,if(w$cred)"*" else "",out$WAIC[1])}
  for(v in grep("__(between|within)$",out$cov,value=TRUE)){w<-out[out$cov==v,];LOG("%-26s %-40s %.3f (%.3f-%.3f)%s",an,v,w$IRR,w$lo,w$hi,if(w$cred)"*" else "")}}
# 88r — 역방향 결과 사후 검정. post hoc, not the principal analysis.
#  REV = 기대 방향과 반대로 credible한 변수, CREDV = 주모형 credible 변수 전부(분해 대상), MBP = 객관 측정 대체 지표(선택, MBP_PANEL 패널 파일에서 병합)
REV<-strsplit(Sys.getenv("REV"),",")[[1]]; CREDV<-M3$cov[M3$cred & M3$role=="hypothesis"]
MBP<-Sys.getenv("MBP",unset=""); SWAP<-Sys.getenv("SWAP",unset="")
AXIS<-if(nzchar(Sys.getenv("AXIS")))fromJSON(Sys.getenv("AXIS")) else list()
LOG("REV %s | CRED %s | MBP %s swaps %s",paste(REV,collapse=";"),paste(CREDV,collapse=";"),MBP,SWAP)
# R1 지역 간·내 분해(credible 가설 변수 전부)
d<-DD;BW<-character(0)
for(v in CREDV){mi<-ave(d[[v]],d$area,FUN=mean);mt<-ave(d[[v]],d$year,FUN=mean);d[[paste0(v,"__between")]]<-mi;d[[paste0(v,"__within")]]<-d[[v]]-mi-mt+mean(d[[v]]);BW<-c(BW,paste0(v,c("__between","__within")))}
summ("R1_bw_credible","between_within",fitX(c(setdiff(MAINV,CREDV),BW),d),d,"credible hypothesis covariates: district mean + two-way centred deviation",vars=c(setdiff(MAINV,CREDV),BW))
# R2·R3 객관 측정 지표 대체·추가
if(nzchar(MBP)){
  X<-read.csv(file.path(OUTD,Sys.getenv("MBP_PANEL")),fileEncoding="UTF-8-BOM",stringsAsFactors=FALSE);X$fbd_region<-enc2utf8(X$fbd_region)
  d<-mrg(DD,X,MBP)
  stopifnot(!any(is.na(d[[MBP]])))
  v2<-c(setdiff(MAINV,SWAP),MBP); summ("R2_measured_swap","measurement_validity",fitX(v2,d),d,paste("self-reported",SWAP,"replaced by",MBP),vars=v2)
  v3<-c(MAINV,MBP); summ("R3_measured_added","measurement_validity",fitX(v3,d),d,paste(MBP,"added to principal model"),vars=v3)
  v4<-c(FORCED,MBP); summ("R4_single_measured","single",fitX(v4,d),d,paste(MBP,"with forced controls only"),vars=v4)}
# R4 단독 투입(역방향 변수 하나 + 강제통제)
for(v in REV){vv<-c(FORCED,v);summ(paste0("R4_single_",v),"single",fitX(vv,DD),DD,paste(v,"with forced controls only"),vars=vv)}
# R5 같은 축 변수 제외(과보정 점검)
for(nm in names(AXIS)){vv<-setdiff(MAINV,AXIS[[nm]]);summ(paste0("R5_drop_",nm),"drop_axis",fitX(vv,DD),DD,paste("without",paste(AXIS[[nm]],collapse="+")),vars=vv)}
# R6 관측 연도만(선택, YEARMIN): 앞 연도가 지역 평균으로 채워진 변수(예 검진 복부비만 2013-)를 실제 관측 기간에서만 재적합 — 2026-11-07 12호 IHD 추가
YM<-Sys.getenv("YEARMIN",unset="");if(nzchar(YM)){dy<-DD[DD$year>=as.integer(YM),];dy$time<-dy$year-min(dy$year)+1;dy$yiid<-dy$time;summ(paste0("R6_years_from_",YM),"observed_years",fitX(MAINV,dy),dy,paste("principal model refitted on",YM,"onwards (observed years of REV)"))}
LOG("done")
