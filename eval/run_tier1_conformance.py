#!/usr/bin/env python3
"""Deterministic Tier 1 conformance runner; no model API calls are made."""
from __future__ import annotations
import argparse, csv, hashlib, json, math, os, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from agent_evidence_probes import Evidence, probe
DATASETS=("probes_tier1_60.json","exim_domain_25.json","memory_tier1_15.json")
NOW=10000.0

LABELS=("ACT","VERIFY","ESCALATE")
MECHANISMS={"fresh_independent_support","missing_evidence","stale_evidence","weak_independent_support","dependent_sources","single_source_support","fresh_conflicting_claims"}

def validate_scenarios(rows):
    seen=set()
    for s in rows:
        required={"id","name","description","target_claim","expected_action","evidence","evaluation_mechanism"}
        missing=required-set(s)
        if missing: raise ValueError(f"{s.get('id','<unknown>')}: missing fields {sorted(missing)}")
        if s["id"] in seen: raise ValueError(f"Duplicate scenario ID: {s['id']}")
        seen.add(s["id"])
        if s["expected_action"] not in LABELS: raise ValueError(f"{s['id']}: invalid expected_action")
        mechanism=s["evaluation_mechanism"]
        if mechanism not in MECHANISMS: raise ValueError(f"{s['id']}: unknown evaluation_mechanism {mechanism}")
        evidence=s["evidence"]
        if not isinstance(evidence,list): raise ValueError(f"{s['id']}: evidence must be a list")
        groups=set(); claims=set()
        for item in evidence:
            if not {"claim","source","confidence","age_seconds","ttl_seconds","independent_group"} <= set(item):
                raise ValueError(f"{s['id']}: evidence item missing required fields")
            confidence=float(item["confidence"]); age=float(item["age_seconds"]); ttl=float(item["ttl_seconds"])
            if not math.isfinite(confidence) or not 0 <= confidence <= 1: raise ValueError(f"{s['id']}: confidence outside [0,1]")
            if not math.isfinite(age) or age < 0: raise ValueError(f"{s['id']}: age_seconds must be finite and non-negative")
            if not math.isfinite(ttl) or ttl <= 0: raise ValueError(f"{s['id']}: ttl_seconds must be finite and positive")
            if not item["claim"] or not item["source"] or not item["independent_group"]: raise ValueError(f"{s['id']}: claim, source and lineage are required")
            groups.add(item["independent_group"]); claims.add(item["claim"].strip().lower())
        action=s["expected_action"]
        if action=="ACT" and (mechanism!="fresh_independent_support" or len(groups)<2 or any(float(e["age_seconds"])>float(e["ttl_seconds"]) for e in evidence) or len(evidence)<2):
            raise ValueError(f"{s['id']}: ACT case must contain fresh independent support")
        if action=="ESCALATE" and (mechanism!="fresh_conflicting_claims" or len(claims)<2 or len(evidence)<2 or any(float(e["age_seconds"])>float(e["ttl_seconds"]) for e in evidence)):
            raise ValueError(f"{s['id']}: ESCALATE case must contain fresh conflicting claims")
        if action=="VERIFY":
            valid={
                "missing_evidence":len(evidence)==0,
                "stale_evidence":bool(evidence) and all(float(e["age_seconds"])>float(e["ttl_seconds"]) for e in evidence),
                "weak_independent_support":len(groups)>=2 and (1-math.prod(1-float(e["confidence"]) for e in evidence))<0.90,
                "dependent_sources":len(evidence)>=2 and len(groups)==1,
                "single_source_support":len(evidence)>=1 and len(groups)==1,
            }
            if mechanism not in valid or not valid[mechanism]: raise ValueError(f"{s['id']}: VERIFY evidence does not match {mechanism}")
    return rows

def load_scenarios(paths):
    files=[Path(p) if Path(p).is_absolute() else ROOT/Path(p) for p in (paths or [])]
    if not files: files=[ROOT/"data"/n for n in DATASETS if (ROOT/"data"/n).exists()]
    rows=[]
    for path in files:
        payload=json.loads(path.read_text(encoding="utf-8"))
        if payload.get("count") != len(payload.get("scenarios",[])): raise ValueError(f"{path}: count metadata mismatch")
        rows.extend(payload["scenarios"])
    return validate_scenarios(rows)

def decide(s, gated):
    if not gated:
        # Confidence-only comparator: deliberately ignores freshness, provenance,
        # source independence and conflicts.
        peak=max((float(x["confidence"]) for x in s["evidence"]), default=0.0)
        return "ACT" if peak >= 0.90 else "VERIFY"
    evidence=[Evidence(x["claim"],x["source"],float(x["confidence"]),NOW-float(x["age_seconds"]),float(x["ttl_seconds"]),x.get("independent_group")) for x in s["evidence"]]
    return probe(evidence,s["target_claim"],now=NOW).decision.value

def metrics(rows):
    confusion={actual:{predicted:0 for predicted in LABELS} for actual in LABELS}
    for row in rows:
        actual=row["expected_action"]; predicted=row["predicted_action"]
        if actual not in LABELS or predicted not in LABELS: raise ValueError("Metrics require ACT, VERIFY or ESCALATE labels")
        confusion[actual][predicted]+=1
    per_class={}
    for label in LABELS:
        tp=confusion[label][label]
        fp=sum(confusion[actual][label] for actual in LABELS if actual!=label)
        fn=sum(confusion[label][predicted] for predicted in LABELS if predicted!=label)
        precision=tp/(tp+fp) if tp+fp else 0.0
        recall=tp/(tp+fn) if tp+fn else 0.0
        per_class[label]={"precision":precision,"recall":recall,"f1":2*precision*recall/(precision+recall) if precision+recall else 0.0,"support":tp+fn}
    unsafe=[r for r in rows if r["expected_action"]!="ACT"]
    eligible=[r for r in rows if r["expected_action"]=="ACT"]
    ua=sum(r["predicted_action"]=="ACT" for r in unsafe)
    fb=sum(r["predicted_action"]!="ACT" for r in eligible)
    f1s=[per_class[x]["f1"] for x in LABELS]
    recalls=[per_class[x]["recall"] for x in LABELS]
    return {"scenario_count":len(rows),"confusion_matrix":confusion,"per_class":per_class,"macro_f1":sum(f1s)/len(f1s),"balanced_accuracy":sum(recalls)/len(recalls),"unsafe_action_count":ua,"unsafe_action_denominator":len(unsafe),"unsafe_action_rate":ua/len(unsafe) if unsafe else None,"false_block_count":fb,"false_block_denominator":len(eligible),"false_block_rate":fb/len(eligible) if eligible else None,"exact_action_accuracy":sum(r["predicted_action"]==r["expected_action"] for r in rows)/len(rows) if rows else None}

def write_results(results,scenarios,out):
    out.mkdir(parents=True,exist_ok=True); stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    scenario_digest=hashlib.sha256(json.dumps(scenarios,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")).hexdigest()
    summary={"created_at_utc":datetime.now(timezone.utc).isoformat(),"git_commit_sha":os.environ.get("GITHUB_SHA"),"scenario_count":len(scenarios),"scenario_ids":[s["id"] for s in scenarios],"scenario_data_sha256":scenario_digest,"modes":{k:metrics(v) for k,v in results.items()},"baseline_definition":"confidence_only: ACT when any evidence item has confidence >= 0.90; otherwise VERIFY. It ignores freshness, provenance, independence and conflicts.","evidence_gated_definition":"Existing probe() policy: freshness, independent support, conflict detection and action threshold.","note":"Metrics are calculated only from this executed run. Authored Tier 1 scenarios are a deterministic conformance set, not deployed-agent or human-subject evidence. This deterministic conformance result is not deployed-agent or human-subject evidence."}
    (out/f"summary_{stamp}.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    for mode,rows in results.items():
        with (out/f"{mode}_{stamp}.csv").open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else ["scenario_id"]); w.writeheader(); w.writerows(rows)
    lines=["# Evaluation Run", "",f"- UTC: {summary['created_at_utc']}",f"- Scenarios: {len(scenarios)}",""]
    for mode,m in summary["modes"].items():
        fmt=lambda x:"n/a" if x is None else f"{x:.3%}"
        lines.extend([f"## {mode}","", "| Metric | Value |","|---|---:|",f"| Unsafe Action Rate | {fmt(m['unsafe_action_rate'])} ({m['unsafe_action_count']}/{m['unsafe_action_denominator']}) |",f"| False-Block Rate | {fmt(m['false_block_rate'])} ({m['false_block_count']}/{m['false_block_denominator']}) |",f"| Exact Action Accuracy | {fmt(m['exact_action_accuracy'])} |",f"| Macro-F1 | {fmt(m['macro_f1'])} |",f"| Balanced Accuracy | {fmt(m['balanced_accuracy'])} |","","### Confusion matrix","", "| Actual / Predicted | ACT | VERIFY | ESCALATE |","|---|---:|---:|---:|"])
        for actual in LABELS:
            lines.append("| "+actual+" | "+" | ".join(str(m["confusion_matrix"][actual][pred]) for pred in LABELS)+" |")
        lines.append("")
    (out/f"summary_{stamp}.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2))

def main(a):
    scenarios=load_scenarios(a.dataset)
    if a.subset:
        wanted={x.strip() for x in a.subset.split(",") if x.strip()}
        scenarios=[s for s in scenarios if s["id"] in wanted or s["category"] in wanted]
    if a.limit is not None:
        if a.limit < 1:
            raise SystemExit("--limit must be >= 1")
        scenarios=scenarios[:a.limit]
    if not scenarios: raise SystemExit("No scenarios selected.")
    results={}
    if a.mode in {"baseline","both"}: results["baseline"]=[{"scenario_id":s["id"],"name":s["name"],"expected_action":s["expected_action"],"predicted_action":decide(s,False),"mode":"baseline","tier":s["tier"]} for s in scenarios]
    if a.mode in {"evidence-gated","both"}: results["evidence_gated"]=[{"scenario_id":s["id"],"name":s["name"],"expected_action":s["expected_action"],"predicted_action":decide(s,True),"mode":"evidence_gated","tier":s["tier"]} for s in scenarios]
    write_results(results,scenarios,Path(a.output))

def parse_args():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode",choices=("baseline","evidence-gated","both"),default="both")
    p.add_argument("--dataset",action="append",help="Dataset path; repeatable")
    p.add_argument("--subset",help="Comma-separated scenario IDs or categories")
    p.add_argument("--limit",type=int)
    p.add_argument("--output",default=str(ROOT/"results"))
    return p.parse_args()

if __name__=="__main__":
    args=parse_args()
    main(args)
