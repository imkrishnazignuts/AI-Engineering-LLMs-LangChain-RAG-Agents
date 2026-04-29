from report_parser import load_report, extract_report_summary
from analyzer import build_analyzer


def format_items(items):
    if not items:
        return "No major items found"

    lines = []
    for i, item in enumerate(items, start=1):
        lines.append(
            f"{i}. {item['title']} | value: {item['display_value']} | score: {item['score']}\n"
            f"   Description: {item['description']}"
        )
    return "\n".join(lines)


def main():
    report = load_report("sample_report.json")
    summary = extract_report_summary(report)

    chain = build_analyzer()

    result = chain.invoke({
        "performance_score": summary["performance_score"],
        "fcp": summary["metrics"]["first_contentful_paint"],
        "lcp": summary["metrics"]["largest_contentful_paint"],
        "tbt": summary["metrics"]["total_blocking_time"],
        "cls": summary["metrics"]["cumulative_layout_shift"],
        "speed_index": summary["metrics"]["speed_index"],
        "opportunities": format_items(summary["opportunities"]),
        "diagnostics": format_items(summary["diagnostics"]),
    })

    print("\n===== PERFORMANCE ANALYSIS =====\n")
    print("Summary:", result.summary)
    print("Score Interpretation:", result.score_interpretation)
    print("\nTop Actions:\n")

    for idx, action in enumerate(result.top_actions, start=1):
        print(f"{idx}. Issue: {action.issue}")
        print(f"   Reason: {action.reason}")
        print(f"   Action: {action.action}")
        print(f"   Priority: {action.priority}")
        print(f"   Estimated Impact: {action.estimated_impact}")
        print(f"   Difficulty: {action.difficulty}")
        print()


if __name__ == "__main__":
    main()