from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from schemas import PerformanceAnalysis


def build_analyzer():
    llm = ChatOllama(
        model="llama3.2:3b",
        temperature=0
    )

    structured_llm = llm.with_structured_output(PerformanceAnalysis)

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
You are a senior web performance engineer.

Your job is to analyze a website performance report and propose practical optimization actions.

Rules:
- Focus on web performance only.
- Prioritize actions by likely performance impact.
- Be specific and developer-friendly.
- Suggest real technical fixes for frontend/backend teams.
- Use High, Medium, or Low for priority.
- Use Easy, Medium, or Hard for difficulty.
- Base your suggestions only on the given report.
"""
        ),
        (
            "human",
            """
Analyze this website performance report summary:

Performance Score: {performance_score}

Metrics:
- First Contentful Paint: {fcp}
- Largest Contentful Paint: {lcp}
- Total Blocking Time: {tbt}
- Cumulative Layout Shift: {cls}
- Speed Index: {speed_index}

Opportunities:
{opportunities}

Diagnostics:
{diagnostics}

Return:
1. A short summary
2. Score interpretation
3. Top optimization actions in priority order
"""
        )
    ])

    chain = prompt | structured_llm
    return chain