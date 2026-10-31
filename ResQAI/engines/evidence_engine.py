from datetime import datetime, timezone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SOURCE_AUTHORITY = {"Government":0.95,"Field Team":0.90,"Hospital":0.93,"Sensor":0.82,"Citizen":0.55,"Unknown":0.30}


def analyze_reports(reports, duplicate_threshold=0.55, freshness_hours=3):
    """Classify reports. Similarity is a flag, not proof that either report is true."""
    if not reports:
        return []
    texts = [str(r.get("description", "")) for r in reports]
    similarities = None
    if len(texts) > 1 and any(t.strip() for t in texts):
        try:
            matrix = TfidfVectorizer(stop_words="english").fit_transform(texts)
            similarities = cosine_similarity(matrix)
        except ValueError:
            similarities = None
    now = datetime.now()
    results = []
    for i, report in enumerate(reports):
        item = dict(report)
        duplicate_of = None
        if similarities is not None:
            candidates = [(similarities[i][j], reports[j].get("id")) for j in range(i) if similarities[i][j] >= duplicate_threshold]
            if candidates:
                duplicate_of = max(candidates)[1]
        stamp = report.get("timestamp")
        age_hours = None
        if isinstance(stamp, datetime):
            age_hours = max(0.0, (now - stamp.replace(tzinfo=None)).total_seconds()/3600)
        prior = report.get("status", "Unverified")
        if duplicate_of:
            status, reason = "Duplicate", f"Text similarity is high with {duplicate_of}; it is not counted as an independent confirmation."
        elif age_hours is not None and age_hours > freshness_hours:
            status, reason = "Outdated", f"Report is {age_hours:.1f} hours old (freshness threshold: {freshness_hours}h)."
        elif prior == "Conflicting":
            status, reason = "Conflicting", report.get("reason", "Claims disagree with another evidence item; field verification is required.")
        elif prior == "Verified":
            status, reason = "Verified", report.get("reason", "Previously verified by an identified operational source.")
        else:
            status, reason = "Unverified", f"{report.get('source','Unknown')} source; independent corroboration or field verification is pending."
        authority = SOURCE_AUTHORITY.get(report.get("source", "Unknown"), 0.30)
        freshness = 1.0 if age_hours is None else max(0.0, 1.0-age_hours/freshness_hours)
        verification = 1.0 if status == "Verified" else 0.0
        item.update({"status":status,"reason":reason,"duplicate_of":duplicate_of,"age_hours":age_hours,
                     "source_authority":authority,"freshness_score":freshness,"verification_score":verification,
                     "evidence_score":round(100*(0.40*authority+0.25*freshness+0.35*verification),1)})
        results.append(item)
    return results


def evidence_summary(reports):
    analyzed = analyze_reports(reports)
    return {"reports": analyzed, "verified":sum(r["status"]=="Verified" for r in analyzed),
            "unverified":sum(r["status"]=="Unverified" for r in analyzed),
            "duplicates":sum(r["status"]=="Duplicate" for r in analyzed),
            "conflicting":sum(r["status"]=="Conflicting" for r in analyzed),
            "outdated":sum(r["status"]=="Outdated" for r in analyzed)}
