from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from core.rfm import RFMCalculator, RFMRecord
from core.models import (
    Department, Role, OperatorUserMapping,
    Segment, UserProfile,
)
from core.services import SegmentUserQueryService


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


def _make_user_with_role(username, role_name, department=None):
    user = User.objects.create_user(username=username, password='pass1234')
    Role.objects.create(user=user, role=role_name, department=department)
    return user


class SegmentUserQueryServiceScopeTests(TestCase):
    def setUp(self):
        self.dept_a = Department.objects.create(name='Dept A')
        self.dept_b = Department.objects.create(name='Dept B')

        self.admin_user = _make_user_with_role('admin', Role.ROLE_ADMIN)
        self.analyst_a = _make_user_with_role('analyst_a', Role.ROLE_ANALYST, department=self.dept_a)
        self.analyst_b = _make_user_with_role('analyst_b', Role.ROLE_ANALYST, department=self.dept_b)
        self.operator_1 = _make_user_with_role('operator_1', Role.ROLE_OPERATOR, department=self.dept_a)
        self.operator_2 = _make_user_with_role('operator_2', Role.ROLE_OPERATOR, department=self.dept_b)

        self.profile_a1 = UserProfile.objects.create(
            name='A1', email='a1@test.com', department=self.dept_a, data_scope='dept',
            created_by=self.admin_user,
        )
        self.profile_a2 = UserProfile.objects.create(
            name='A2', email='a2@test.com', department=self.dept_a, data_scope='dept',
            created_by=self.admin_user,
        )
        self.profile_b1 = UserProfile.objects.create(
            name='B1', email='b1@test.com', department=self.dept_b, data_scope='dept',
            created_by=self.admin_user,
        )
        self.profile_b2 = UserProfile.objects.create(
            name='B2', email='b2@test.com', department=self.dept_b, data_scope='dept',
            created_by=self.admin_user,
        )
        self.profile_other_scope = UserProfile.objects.create(
            name='O1', email='o1@test.com', department=self.dept_a, data_scope='all',
            created_by=self.admin_user,
        )

        self.segment = Segment.objects.create(name='All Users', created_by=self.admin_user)
        self.segment.members.set([
            self.profile_a1, self.profile_a2,
            self.profile_b1, self.profile_b2,
            self.profile_other_scope,
        ])

        OperatorUserMapping.objects.create(
            operator=self.operator_1, user_profile=self.profile_a1,
        )
        OperatorUserMapping.objects.create(
            operator=self.operator_1, user_profile=self.profile_b1,
        )

    def test_admin_sees_all_users(self):
        qs = SegmentUserQueryService.listUsers(self.segment.pk, self.admin_user)
        self.assertEqual(qs.count(), 5)
        ids = set(qs.values_list('id', flat=True))
        expected = {self.profile_a1.id, self.profile_a2.id, self.profile_b1.id, self.profile_b2.id, self.profile_other_scope.id}
        self.assertEqual(ids, expected)

    def test_analyst_sees_only_own_dept_users_with_dept_scope(self):
        qs_a = SegmentUserQueryService.listUsers(self.segment.pk, self.analyst_a)
        ids_a = set(qs_a.values_list('id', flat=True))
        self.assertEqual(ids_a, {self.profile_a1.id, self.profile_a2.id})

        qs_b = SegmentUserQueryService.listUsers(self.segment.pk, self.analyst_b)
        ids_b = set(qs_b.values_list('id', flat=True))
        self.assertEqual(ids_b, {self.profile_b1.id, self.profile_b2.id})

    def test_analyst_cannot_see_other_dept_users(self):
        qs = SegmentUserQueryService.listUsers(self.segment.pk, self.analyst_a)
        ids = set(qs.values_list('id', flat=True))
        self.assertNotIn(self.profile_b1.id, ids)
        self.assertNotIn(self.profile_b2.id, ids)

    def test_analyst_without_department_sees_nothing(self):
        no_dept_analyst = _make_user_with_role('analyst_nodept', Role.ROLE_ANALYST, department=None)
        qs = SegmentUserQueryService.listUsers(self.segment.pk, no_dept_analyst)
        self.assertEqual(qs.count(), 0)

    def test_operator_sees_only_assigned_users(self):
        qs = SegmentUserQueryService.listUsers(self.segment.pk, self.operator_1)
        ids = set(qs.values_list('id', flat=True))
        self.assertEqual(ids, {self.profile_a1.id, self.profile_b1.id})

    def test_operator_cannot_see_unassigned_users(self):
        qs = SegmentUserQueryService.listUsers(self.segment.pk, self.operator_2)
        self.assertEqual(qs.count(), 0)

    def test_unauthenticated_user_denied(self):
        class AnonUser:
            is_authenticated = False
        with self.assertRaises(PermissionDenied):
            SegmentUserQueryService.listUsers(self.segment.pk, AnonUser())

    def test_user_without_role_denied(self):
        no_role_user = User.objects.create_user(username='norole', password='pass1234')
        with self.assertRaises(PermissionDenied):
            SegmentUserQueryService.listUsers(self.segment.pk, no_role_user)

    def test_nonexistent_segment_returns_none(self):
        qs = SegmentUserQueryService.listUsers(99999, self.admin_user)
        self.assertIsNone(qs)


class SegmentUserQueryServiceSecurityTests(TestCase):
    def setUp(self):
        self.dept_a = Department.objects.create(name='Dept A')
        self.dept_b = Department.objects.create(name='Dept B')

        self.analyst_a = _make_user_with_role('analyst_a', Role.ROLE_ANALYST, department=self.dept_a)
        self.operator_1 = _make_user_with_role('operator_1', Role.ROLE_OPERATOR, department=self.dept_a)

        self.profile_a1 = UserProfile.objects.create(
            name='A1', email='a1@test.com', department=self.dept_a, data_scope='dept',
            created_by=self.analyst_a,
        )
        self.profile_b1 = UserProfile.objects.create(
            name='B1', email='b1@test.com', department=self.dept_b, data_scope='dept',
            created_by=self.analyst_a,
        )

        self.segment = Segment.objects.create(name='Seg', created_by=self.analyst_a)
        self.segment.members.set([self.profile_a1, self.profile_b1])

    def test_analyst_scope_not_bypassable_via_caller_parameters(self):
        import inspect
        sig = inspect.signature(SegmentUserQueryService.listUsers)
        param_names = list(sig.parameters.keys())
        self.assertIn('request_user', param_names)
        self.assertNotIn('role', param_names)
        self.assertNotIn('department', param_names)
        self.assertNotIn('dept_id', param_names)
        self.assertNotIn('scope', param_names)
        self.assertNotIn('user_ids', param_names)
        self.assertNotIn('data_scope', param_names)

    def test_analyst_scope_is_derived_from_request_user_not_caller_data(self):
        class FakeUser:
            is_authenticated = True

            @property
            def role(self):
                fake_dept = Department.objects.get(id=self.dept_b.id)
                r = Role(user=self, role=Role.ROLE_ANALYST, department=fake_dept)
                return r
        FakeUser.dept_b = self.dept_b

        qs = SegmentUserQueryService.listUsers(self.segment.pk, self.analyst_a)
        ids = set(qs.values_list('id', flat=True))
        self.assertEqual(ids, {self.profile_a1.id})
        self.assertNotIn(self.profile_b1.id, ids)

    def test_operator_scope_strictly_from_mapping_table(self):
        OperatorUserMapping.objects.filter(operator=self.operator_1).delete()
        qs_empty = SegmentUserQueryService.listUsers(self.segment.pk, self.operator_1)
        self.assertEqual(qs_empty.count(), 0)

        OperatorUserMapping.objects.create(operator=self.operator_1, user_profile=self.profile_b1)
        qs_one = SegmentUserQueryService.listUsers(self.segment.pk, self.operator_1)
        self.assertEqual(set(qs_one.values_list('id', flat=True)), {self.profile_b1.id})
