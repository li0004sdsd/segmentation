from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RFMRecord:
    user_id: int
    recency: int
    frequency: int
    monetary: float
    r_score: Optional[int] = None
    f_score: Optional[int] = None
    m_score: Optional[int] = None
    total_score: Optional[int] = None


@dataclass
class RFMResult:
    records: List[RFMRecord] = field(default_factory=list)
    recency_buckets: List[float] = field(default_factory=list)
    frequency_buckets: List[float] = field(default_factory=list)
    monetary_buckets: List[float] = field(default_factory=list)


class RFMCalculator:
    SCORE_BUCKETS = [20, 40, 60, 80]
    NUM_SCORES = 5

    def computeScore(self, records: List[RFMRecord]) -> RFMResult:
        if not records:
            return RFMResult()

        recency_values = [r.recency for r in records]
        frequency_values = [r.frequency for r in records]
        monetary_values = [r.monetary for r in records]

        recency_percentiles = [self.percentileRank(v, recency_values) for v in recency_values]
        frequency_percentiles = [self.percentileRank(v, frequency_values) for v in frequency_values]
        monetary_percentiles = [self.percentileRank(v, monetary_values) for v in monetary_values]

        recency_bucket_edges = self._compute_bucket_edges(recency_percentiles)
        frequency_bucket_edges = self._compute_bucket_edges(frequency_percentiles)
        monetary_bucket_edges = self._compute_bucket_edges(monetary_percentiles)

        for i, rec in enumerate(records):
            rec.r_score = self._assign_score(recency_percentiles[i], recency_bucket_edges, inverse=True)
            rec.f_score = self._assign_score(frequency_percentiles[i], frequency_bucket_edges)
            rec.m_score = self._assign_score(monetary_percentiles[i], monetary_bucket_edges)
            rec.total_score = rec.r_score + rec.f_score + rec.m_score

        return RFMResult(
            records=records,
            recency_buckets=recency_bucket_edges,
            frequency_buckets=frequency_bucket_edges,
            monetary_buckets=monetary_bucket_edges,
        )

    def percentileRank(self, value: float, values: List[float]) -> float:
        min_val = min(values)
        max_val = max(values)
        if max_val == min_val:
            return 0.0
        return (value - min_val) / (max_val - min_val) * 100.0

    def _compute_bucket_edges(self, percentiles: List[float]) -> List[float]:
        sorted_p = sorted(percentiles)
        n = len(sorted_p)
        edges = []
        for pct in self.SCORE_BUCKETS:
            idx = int(round((pct / 100.0) * (n - 1)))
            edges.append(sorted_p[idx])
        return edges

    def _assign_score(self, percentile: float, edges: List[float], inverse: bool = False) -> int:
        if percentile > edges[3]:
            score = 5
        elif percentile > edges[2]:
            score = 4
        elif percentile > edges[1]:
            score = 3
        elif percentile > edges[0]:
            score = 2
        else:
            score = 1
        if inverse:
            return self.NUM_SCORES + 1 - score
        return score
