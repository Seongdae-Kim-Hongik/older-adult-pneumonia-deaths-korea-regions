# 88z_pneu — 14호 폐렴 사망(PNEU) 사망진단·접근성 민감도(2026-11-08, sets_PNEU_std3.json note에 적합 전 고정). 88z_alz 복제, 넓은 결과(Z2·Z3)는 없음.
#  사용(01_스크립트/): TAG=ALZ ST_VER=std3 ST_THREADS=1 ST_GRAPH=<593> Rscript 88z_alz_coding.R
#  Z0 주모형 재적합 / Z1 주모형 + 불명확 사인(R00-R99) 비율 / Z4 주모형 + 관외 외래 비율(접근성). 산출: results_std3/S45_coding_<an>.csv
#  산출: results_std3/S45_coding_<an>.csv (공변량 IRR), S45_coding_area.csv (주모형·Z2 지역 공간 RR, 핫스팟 비교용)
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

summ<-function(an,item,m,note,vars){
  if(is.null(m)){LOG("%s FAILED",an);return(invisible())}
  r<-do.call(rbind,lapply(intersect(vars,rownames(m$summary.fixed)),function(v)irr(m,v)))
  out<-data.frame(analysis=an,item=item,r,WAIC=round(m$waic$waic,1),note=note,stringsAsFactors=FALSE)
  write.csv(out,file.path(RES,sprintf("S45_coding_%s.csv",an)),row.names=FALSE,fileEncoding="UTF-8")
  for(i in seq_len(nrow(out)))LOG("%-14s %-40s %.3f (%.3f-%.3f)%s",an,out$cov[i],out$IRR[i],out$lo[i],out$hi[i],if(out$cred[i])"*" else "")
  invisible(m)}
arear<-function(m,data){s<-m$summary.random$area[1:n,];data.frame(fbd_region=G$region,RR=exp(s$mean),P_gt1=sapply(m$marginals.random$area[1:n],function(x)1-inla.pmarginal(0,x)))}
ILL<-"ill_defined_death_share";OUTC<-"outside_care_share";stopifnot(ILL%in%names(DD),OUTC%in%names(DD))
LOG("main vars %d: %s",length(MAINV),paste(MAINV,collapse=";"))
m0<-fitX(MAINV,DD);summ("Z0_main_refit","reference",m0,"principal model refit (reference for area RR)",MAINV)
summ("Z1_illdefined","certification",fitX(c(MAINV,ILL),DD),"principal model + ill-defined cause share (R00-R99)",c(MAINV,ILL))
summ("Z4_outside_care","access",fitX(c(MAINV,OUTC),DD),"principal model + out-of-district outpatient share",c(MAINV,OUTC))
LOG("done")
