import json


def load_report(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def safe_audit_value(audits: dict, key: str, default="N/A"):
    audit = audits.get(key, {})
    return audit.get("displayValue") or audit.get("numericValue") or default


def extract_report_summary(report: dict) -> dict:
    categories = report.get("categories", {})
    audits = report.get("audits", {})

    performance_score = categories.get("performance", {}).get("score")
    if performance_score is not None:
        performance_score = int(performance_score * 100)

    opportunities = []
    diagnostics = []

    for audit_key, audit_data in audits.items():
        score = audit_data.get("score")
        details = audit_data.get("details", {})
        title = audit_data.get("title", "")
        description = audit_data.get("description", "")
        display_value = audit_data.get("displayValue", "")

        if score is not None and score < 0.9:
            item = {
                "audit_key": audit_key,
                "title": title,
                "description": description,
                "display_value": display_value,
                "score": score,
            }

            if details.get("type") in ["opportunity", "table"]:
                opportunities.append(item)
            else:
                diagnostics.append(item)

    return {
        "performance_score": performance_score,
        "metrics": {
            "first_contentful_paint": safe_audit_value(audits, "first-contentful-paint"),
            "largest_contentful_paint": safe_audit_value(audits, "largest-contentful-paint"),
            "total_blocking_time": safe_audit_value(audits, "total-blocking-time"),
            "cumulative_layout_shift": safe_audit_value(audits, "cumulative-layout-shift"),
            "speed_index": safe_audit_value(audits, "speed-index"),
        },
        "opportunities": opportunities[:10],
        "diagnostics": diagnostics[:10],
    }