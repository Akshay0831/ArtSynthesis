from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum


class FeedbackType(Enum):
    QUALITY = "quality"
    STYLE = "style"
    ANATOMY = "anatomy"
    CONSISTENCY = "consistency"


@dataclass
class FeedbackConfig:
    enable_feedback: bool = True
    valid_types: list[str] = field(default_factory=lambda: ["quality", "style", "anatomy", "consistency"])
    min_quality_threshold: float = 6.0


class FeedbackIntegration:
    def __init__(self, config: FeedbackConfig = None):
        self.config = config or FeedbackConfig()
        self.feedback_scores: dict[str, list[int]] = {}
    
    def IsEnabled(self) -> bool:
        return self.config.enable_feedback
    
    def RecordScore(self, feedback_type: str, score: int) -> None:
        if feedback_type not in self.feedback_scores:
            self.feedback_scores[feedback_type] = []
        self.feedback_scores[feedback_type].append(score)
    
    def GetAverageScore(self, feedback_type: str) -> float:
        if feedback_type not in self.feedback_scores:
            return 0.0
        scores = self.feedback_scores[feedback_type]
        return sum(scores) / len(scores) if scores else 0.0
    
    def ApplyQualityThreshold(self, min_score: float = None) -> list[str]:
        threshold = min_score or self.config.min_quality_threshold
        
        passing = []
        for feedback_type, scores in self.feedback_scores.items():
            avg_score = self.GetAverageScore(feedback_type)
            if avg_score >= threshold:
                passing.append(feedback_type)
        
        return passing
