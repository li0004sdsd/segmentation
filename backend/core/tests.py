from django.test import TestCase
from core.rfm import RFMCalculator, RFMRecord


class PercentileRankTests(TestCase):
    def setUp(self):
        self.calc = RFMCalculator()

    def test_all_zero_values_no_exception(self):
        result = self.calc.percentileRank(0, [0, 0, 0, 0, 0])
        self.assertEqual(result, 0.0)

    def test_all_same_nonzero_no_exception(self):
        result = self.calc.percentileRank(100, [100, 100, 100])
        self.assertEqual(result, 0.0)

    def test_single_value_no_exception(self):
        result = self.calc.percentileRank(50, [50])
        self.assertEqual(result, 0.0)

    def test_normal_values_correct(self):
        values = [10, 50, 100, 200, 500]
        self.assertAlmostEqual(self.calc.percentileRank(10, values), 0.0)
        self.assertAlmostEqual(self.calc.percentileRank(500, values), 100.0)
        self.assertAlmostEqual(self.calc.percentileRank(100, values), 18.367, places=2)

    def test_mixed_zero_and_positive(self):
        values = [0, 10, 50, 100]
        self.assertEqual(self.calc.percentileRank(0, values), 0.0)
        self.assertGreater(self.calc.percentileRank(10, values), 0.0)


class AssignScoreTests(TestCase):
    def setUp(self):
        self.calc = RFMCalculator()
        self.edges = [0.0, 25.0, 50.0, 75.0]

    def test_lowest_boundary_exactly_zero(self):
        score = self.calc._assign_score(0.0, self.edges)
        self.assertEqual(score, 1)

    def test_exactly_edges_0(self):
        score = self.calc._assign_score(self.edges[0], self.edges)
        self.assertEqual(score, 1)

    def test_above_edges_0(self):
        score = self.calc._assign_score(self.edges[0] + 1, self.edges)
        self.assertEqual(score, 2)

    def test_top_percentile(self):
        score = self.calc._assign_score(100.0, self.edges)
        self.assertEqual(score, 5)

    def test_inverse_lowest_becomes_5(self):
        score = self.calc._assign_score(0.0, self.edges, inverse=True)
        self.assertEqual(score, 5)

    def test_inverse_highest_becomes_1(self):
        score = self.calc._assign_score(100.0, self.edges, inverse=True)
        self.assertEqual(score, 1)

    def test_inverse_mid_values(self):
        for pct in [10.0, 35.0, 60.0, 90.0]:
            normal = self.calc._assign_score(pct, self.edges)
            inv = self.calc._assign_score(pct, self.edges, inverse=True)
            self.assertEqual(normal + inv, 6)


class ComputeScoreBatchTests(TestCase):
    def setUp(self):
        self.calc = RFMCalculator()

    def test_all_refund_batch_all_monetary_zero(self):
        records = [
            RFMRecord(user_id=1, recency=1, frequency=1, monetary=0),
            RFMRecord(user_id=2, recency=2, frequency=3, monetary=0),
            RFMRecord(user_id=3, recency=5, frequency=5, monetary=0),
        ]
        result = self.calc.computeScore(records)
        self.assertEqual(len(result.records), 3)
        for rec in result.records:
            self.assertIsNotNone(rec.m_score)
            self.assertIsNotNone(rec.total_score)
            self.assertEqual(rec.m_score, 1)
            self.assertTrue(1 <= rec.r_score <= 5)
            self.assertTrue(1 <= rec.f_score <= 5)

    def test_empty_batch(self):
        result = self.calc.computeScore([])
        self.assertEqual(len(result.records), 0)

    def test_mixed_zero_and_positive_monetary(self):
        records = [
            RFMRecord(user_id=1, recency=60, frequency=0, monetary=0),
            RFMRecord(user_id=2, recency=30, frequency=1, monetary=10),
            RFMRecord(user_id=3, recency=10, frequency=5, monetary=100),
            RFMRecord(user_id=4, recency=1,  frequency=9, monetary=500),
        ]
        result = self.calc.computeScore(records)
        for rec in result.records:
            self.assertIsNotNone(rec.m_score)
            self.assertTrue(1 <= rec.m_score <= 5)
        sorted_by_m = sorted(result.records, key=lambda r: r.monetary)
        for i in range(len(sorted_by_m) - 1):
            self.assertLessEqual(sorted_by_m[i].m_score, sorted_by_m[i + 1].m_score)

    def test_all_same_nonzero_scores(self):
        records = [
            RFMRecord(user_id=1, recency=1, frequency=1, monetary=100),
            RFMRecord(user_id=2, recency=2, frequency=2, monetary=100),
            RFMRecord(user_id=3, recency=3, frequency=3, monetary=100),
        ]
        result = self.calc.computeScore(records)
        for rec in result.records:
            self.assertEqual(rec.m_score, 1)
            self.assertIsNotNone(rec.total_score)


class BackwardCompatibilityTests(TestCase):
    def setUp(self):
        self.calc = RFMCalculator()

    def _old_percentile_rank(self, value, values):
        min_val = min(values)
        max_val = max(values)
        return (value - min_val) / (max_val - min_val) * 100.0

    def _old_assign_score(self, percentile, edges, inverse=False):
        score = 0
        if percentile > edges[3]:
            score = 5
        elif percentile > edges[2]:
            score = 4
        elif percentile > edges[1]:
            score = 3
        elif percentile > edges[0]:
            score = 2
        if inverse:
            return 6 - score if score > 0 else 0
        return score

    def _old_compute_edges(self, percentiles):
        sorted_p = sorted(percentiles)
        n = len(sorted_p)
        edges = []
        for pct in [20, 40, 60, 80]:
            idx = int(round((pct / 100.0) * (n - 1)))
            edges.append(sorted_p[idx])
        return edges

    def test_monetary_positive_users_unchanged(self):
        records = [
            RFMRecord(user_id=10, recency=30, frequency=1, monetary=10),
            RFMRecord(user_id=11, recency=20, frequency=3, monetary=50),
            RFMRecord(user_id=12, recency=10, frequency=5, monetary=100),
            RFMRecord(user_id=13, recency=5,  frequency=7, monetary=200),
            RFMRecord(user_id=14, recency=1,  frequency=9, monetary=500),
        ]
        m_values = [r.monetary for r in records]
        m_perc = [self._old_percentile_rank(v, m_values) for v in m_values]
        edges = self._old_compute_edges(m_perc)

        new_result = self.calc.computeScore(records)

        for i, rec in enumerate(records):
            old_score = self._old_assign_score(m_perc[i], edges)
            new_score = new_result.records[i].m_score
            if old_score == 0:
                self.assertEqual(new_score, 1,
                    f'User {rec.user_id}: old bug score was 0, '
                    f'expected new corrected score 1 for bucket 1')
            else:
                self.assertEqual(new_score, old_score,
                    f'User {rec.user_id} (monetary={rec.monetary}): '
                    f'score changed from {old_score} to {new_score}')

    def test_monetary_positive_users_higher_than_lowest_bucket_unchanged(self):
        records = [
            RFMRecord(user_id=1, recency=30, frequency=2, monetary=50),
            RFMRecord(user_id=2, recency=25, frequency=3, monetary=75),
            RFMRecord(user_id=3, recency=20, frequency=4, monetary=100),
            RFMRecord(user_id=4, recency=15, frequency=5, monetary=200),
            RFMRecord(user_id=5, recency=10, frequency=6, monetary=300),
            RFMRecord(user_id=6, recency=5,  frequency=7, monetary=400),
            RFMRecord(user_id=7, recency=1,  frequency=8, monetary=500),
        ]
        m_values = [r.monetary for r in records]
        m_perc = [self._old_percentile_rank(v, m_values) for v in m_values]
        edges = self._old_compute_edges(m_perc)

        new_result = self.calc.computeScore(records)

        for i, rec in enumerate(records):
            old_score = self._old_assign_score(m_perc[i], edges)
            new_score = new_result.records[i].m_score
            if m_perc[i] > edges[0]:
                self.assertEqual(new_score, old_score,
                    f'User {rec.user_id}: percentile > edges[0] should be unchanged')
