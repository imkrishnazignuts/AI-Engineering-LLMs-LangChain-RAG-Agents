from pydantic import BaseModel, Field
from typing import List

class OptimizationAction(BaseModel):
    issue: str = Field(description="Main performance issue")
    reason: str = Field(description="Why this issue hurts performance")
    action: str = Field(description="Recommended optimization action")
    priority: str = Field(description="High, Medium, or Low")
    estimated_impact: str = Field(description="Expected performance impact")
    difficulty: str = Field(description="Easy, Medium, or Hard")


class PerformanceAnalysis(BaseModel):
    summary: str = Field(description="Short summary of website performance")
    score_interpretation: str = Field(description="Interpretation of the performance score")
    top_actions: List[OptimizationAction] = Field(description="List of optimization actions")