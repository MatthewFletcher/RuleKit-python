import unittest

from rulekit.main import RuleKit
from rulekit import survival

from .utils import get_test_cases, assert_rules_are_equals, assert_accuracy_is_greater


class TestDecisionTreeRegressor(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        RuleKit.init()

    def test_compare_with_java_results(self):
        test_cases = get_test_cases('SurvivalLogRankSnCTest')

        for test_case in test_cases:
            params = test_case.induction_params
            tree = survival.SurvivalLogRankTree(**params, survival_time_attr=test_case.survival_time)
            example_set = test_case.example_set
            tree.fit(example_set.values, example_set.labels)
            model = tree.model
            expected = test_case.reference_report.rules
            actual = list(map(lambda e: str(e), model.rules))
            assert_rules_are_equals(expected, actual)
            assert_accuracy_is_greater(tree.predict(example_set.values), example_set.labels, 0.7)


if __name__ == '__main__':
    unittest.main()
