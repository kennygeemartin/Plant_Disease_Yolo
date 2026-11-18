"""Recheck existing public proxy CSVs; DO NOT infer missing experiments or checkpoints.

Usage from repository root:
    python -m pip install pandas numpy scipy
    python tools/audit_results.py --input results --manifest data/manifest.csv
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import t, wilcoxon

METRICS=("precision","recall","f1","map50","map50_95")
QUESTIONABLE={"Apple leaf","Bell_pepper leaf","grape leaf","Tomato leaf",
              "Potato leaf","Bell_pepper leaf spot"}

def audit(folder,manifest_file,outdir):
    outdir.mkdir(parents=True,exist_ok=True)
    run=pd.read_csv(folder/"run_metrics.csv")
    summaries=pd.read_csv(folder/"summary_mean_sd_ci.csv")
    paired=pd.read_csv(folder/"paired_wilcoxon.csv")
    perclass=pd.read_csv(folder/"per_class_metrics.csv")
    manifest=pd.read_csv(manifest_file)
    errors=[]
    calculated=[]
    for (m,c,s),g in run.groupby(["method","test_condition","test_source"]):
        for metric in METRICS:
            values=g[metric].dropna().to_numpy(float)
            n=len(values)
            if n<2:continue
            mean=float(values.mean())
            sd=float(values.std(ddof=1))
            half=float(t.ppf(.975,n-1)*sd/math.sqrt(n))
            row={"method":m,"test_condition":c,"test_source":s,"metric":metric,
                 "n":n,"mean":mean,"sd":sd,"ci95_low":mean-half,"ci95_high":mean+half}
            calculated.append(row)
            ref=summaries[(summaries.method==m)&(summaries.test_condition==c)&
                          (summaries.test_source==s)&(summaries.metric==metric)]
            if len(ref)!=1:
                errors.append("Missing or duplicate summary "+str((m,c,s,metric)))
                continue
            for col in ("n","mean","sd","ci95_low","ci95_high"):
                if not np.isclose(row[col],float(ref.iloc[0][col]),rtol=0,atol=1e-7):
                    errors.append("Summary mismatch "+str((m,c,s,metric,col)))
    pd.DataFrame(calculated).to_csv(outdir/"recomputed_summary.csv",index=False)
    paired_checked=0
    for _,row in paired.iterrows():
        method=str(row.comparison).removesuffix(" vs baseline")
        a=run[(run.method==method)&(run.test_condition==row.condition)&
              (run.test_source==row.test_source)].set_index("seed")[row.metric]
        b=run[(run.method=="baseline")&(run.test_condition==row.condition)&
              (run.test_source==row.test_source)].set_index("seed")[row.metric]
        seeds=sorted(set(a.index).intersection(set(b.index)))
        if len(seeds)<2:
            errors.append("Insufficient paired seeds "+str(row.to_dict()))
            continue
        result=wilcoxon(a.loc[seeds],b.loc[seeds],method="exact",alternative="two-sided")
        paired_checked+=1
        if not np.isclose(float(result.pvalue),float(row.p_value_unadjusted),atol=1e-7):
            errors.append("Paired p-value mismatch "+str((method,row.condition,row.test_source,row.metric)))
    flagged=manifest[(manifest.source=="PlantDoc detection")&
                     (manifest.source_label.isin(QUESTIONABLE))].copy()
    flagged["review_status"]="expert_review_required; do not automatically relabel"
    flagged.to_csv(outdir/"annotation_review_queue.csv",index=False)
    perclass[(perclass.method=="combined")&(perclass.test_condition=="clear")&
             (perclass.test_source=="all")].groupby(["class_id","class"],as_index=False)[
                 ["precision","recall","ap50","ap50_95"]].mean().to_csv(
                     outdir/"recomputed_table7.csv",index=False)
    hashes={name:hashlib.sha256((folder/name).read_bytes()).hexdigest()
            for name in ("run_metrics.csv","summary_mean_sd_ci.csv",
                         "paired_wilcoxon.csv","per_class_metrics.csv","experiment_config.json")
            if (folder/name).is_file()}
    checkpoints=list(folder.rglob("best.pt"))
    report={
        "scope":"secondary audit of existing public-data proxy outputs, not new training",
        "evaluation_rows":len(run),"class_metric_rows":len(perclass),
        "summary_rows":len(summaries),"summary_rows_checked":len(calculated),
        "paired_comparisons":len(paired),"paired_comparisons_checked":paired_checked,
        "manifest_images":len(manifest),"questionable_primary_label_images":len(flagged),
        "best_pt_files_found":len(checkpoints),"checkpoint_integrity_verified":False,
        "issues":errors,"files_sha256":hashes,
        "interpretation":"Cannot demonstrate field reliability or lesion localisation; no missing outputs invented."
    }
    (outdir/"audit_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    if errors:raise RuntimeError(str(len(errors))+" evidence-check errors: see audit_report.json")
    return report

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,default=Path("results"))
    parser.add_argument("--manifest",type=Path,default=Path("data/manifest.csv"))
    parser.add_argument("--output",type=Path,default=Path("reviewer_audit"))
    a=parser.parse_args()
    print(json.dumps(audit(a.input,a.manifest,a.output),indent=2))
