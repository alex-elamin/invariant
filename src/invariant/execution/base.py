from __future__ import annotations

from typing import Protocol

from invariant.core.models import AnalysisResult, AnalysisSpecification


class AnalysisExecutor(Protocol):
    def execute(self, specification: AnalysisSpecification) -> AnalysisResult:
        ...
