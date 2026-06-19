from django.db import transaction, IntegrityError
from core.models import SegmentRule, SegmentRuleCondition


PRIORITY_CONFLICT_CODE = 'PRIORITY_CONFLICT'
PRIORITY_CONFLICT_MESSAGE = 'A rule with this priority already exists.'


class SegmentRuleService:
    @staticmethod
    def saveRule(rule_data, conditions_data=None, rule_instance=None, user=None):
        conditions_data = conditions_data or []

        try:
            with transaction.atomic():
                if rule_instance:
                    rule_instance.rule_id = rule_data.get('rule_id', rule_instance.rule_id)
                    rule_instance.rule_name = rule_data.get('rule_name', rule_instance.rule_name)
                    rule_instance.conditions = rule_data.get('conditions', rule_instance.conditions)
                    rule_instance.priority = rule_data.get('priority', rule_instance.priority)
                    rule_instance.save()
                else:
                    rule_instance = SegmentRule.objects.create(
                        rule_id=rule_data['rule_id'],
                        rule_name=rule_data['rule_name'],
                        conditions=rule_data.get('conditions', {}),
                        priority=rule_data['priority'],
                        created_by=user,
                    )

                rule_instance.segment_rule_conditions.all().delete()

                condition_objects = []
                for cond in conditions_data:
                    condition_objects.append(SegmentRuleCondition(
                        rule=rule_instance,
                        field=cond['field'],
                        operator=cond['operator'],
                        value=cond.get('value', {}),
                        condition_type=cond.get('condition_type', 'custom'),
                    ))

                if condition_objects:
                    SegmentRuleCondition.objects.bulk_create(condition_objects)

                rule_instance.refresh_from_db()
                return rule_instance

        except IntegrityError as e:
            error_str = str(e).lower()
            if 'priority' in error_str or 'unique' in error_str:
                raise PriorityConflictError()
            raise
        except Exception:
            raise


class PriorityConflictError(Exception):
    def __init__(self):
        self.code = PRIORITY_CONFLICT_CODE
        self.message = PRIORITY_CONFLICT_MESSAGE
        super().__init__(self.message)
