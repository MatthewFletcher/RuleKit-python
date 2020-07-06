from typing import Union, List, Any
from jpype import JClass, JString, JObject, JArray, java
import numpy as np
import pandas as pd
from .params import Measures
from .rules import Rule


def get_rule_generator(expert: bool = False) -> Any:
    OperatorDocumentation = JClass('com.rapidminer.tools.documentation.OperatorDocumentation')
    OperatorDescription = JClass('com.rapidminer.operator.OperatorDescription')
    Mockito = JClass('org.mockito.Mockito')
    path = 'adaa.analytics.rules.operator.'
    if expert:
        path += 'ExpertRuleGenerator'
    else:
        path += 'RuleGenerator'
    RuleGenerator = JClass(path)
    documentation = Mockito.mock(OperatorDocumentation.class_)
    description = Mockito.mock(OperatorDescription.class_)
    Mockito.when(documentation.getShortName()).thenReturn(JString(''), None)
    Mockito.when(description.getOperatorDocumentation()).thenReturn(documentation, None)
    return RuleGenerator(description)


class RuleGeneratorConfigurator:

    def __init__(self, rule_generator):
        self.rule_generator = rule_generator
        self.LogRank = None

    def configure(self,
                  min_rule_covered: int = None,
                  induction_measure: Measures = None,
                  pruning_measure: Union[Measures, str] = None,
                  voting_measure: Measures = None,
                  max_growing: int = None,
                  enable_pruning: bool = None,
                  ignore_missing: bool = None,

                  extend_using_preferred: bool = None,
                  extend_using_automatic: bool = None,
                  induce_using_preferred: bool = None,
                  induce_using_automatic: bool = None,
                  consider_other_classes: bool = None,
                  preferred_attributes_per_rule: int = None,
                  preferred_conditions_per_rule: int = None) -> Any:
        self._configure_rule_generator(
            min_rule_covered=min_rule_covered,
            induction_measure=induction_measure,
            pruning_measure=pruning_measure,
            voting_measure=voting_measure,
            max_growing=max_growing,
            enable_pruning=enable_pruning,
            ignore_missing=ignore_missing,
            extend_using_preferred=extend_using_preferred,
            extend_using_automatic=extend_using_automatic,
            induce_using_preferred=induce_using_preferred,
            induce_using_automatic=induce_using_automatic,
            consider_other_classes=consider_other_classes,
            preferred_conditions_per_rule=preferred_conditions_per_rule,
            preferred_attributes_per_rule=preferred_attributes_per_rule
        )
        return self.rule_generator

    def configure_expert_parameter(self, param_name: str, param_value: Any):
        if param_value is None:
            return
        rules_list = java.util.ArrayList()
        if isinstance(param_value, list) and len(param_value) > 0:
            if isinstance(param_value[0], str):
                for index, rule in enumerate(param_value):
                    rule_name = f'{param_name[:-1]}-{index}'
                    rules_list.add(JObject([rule_name, rule], JArray('java.lang.String', 1)))
            elif isinstance(param_value[0], Rule):
                for index, rule in enumerate(param_value):
                    rule_name = f'{param_name[:-1]}-{index}'
                    rules_list.add(JObject([rule_name, str(rule)], JArray('java.lang.String', 1)))
            elif isinstance(param_value[0], tuple):
                for index, rule in enumerate(param_value):
                    rules_list.add(JObject([rule[0], rule[1]], JArray('java.lang.String', 1)))
        self.rule_generator.setListParameter(param_name, rules_list)

    def _configure_simple_parameter(self, param_name: str, param_value: Any):
        if param_value is not None:
            if isinstance(param_value, bool):
                param_value = (str(param_value)).lower()
            elif not isinstance(param_value, str):
                param_value = str(param_value)
            self.rule_generator.setParameter(param_name, param_value)

    def _configure_measure_parameter(self, param_name: str, param_value: Union[str, Measures]):
        if param_value is not None:
            if isinstance(param_value, Measures):
                if param_value == Measures.LogRank:
                    self.rule_generator.setInductionMeasure(self.LogRank())
                else:
                    self.rule_generator.setParameter(param_name, param_value.value)
            if isinstance(param_value, str):
                self.rule_generator.setParameter(param_name, 'UserDefined')
                self.rule_generator.setParameter(param_name, param_value)

    def _configure_rule_generator(
            self,
            min_rule_covered: int,
            induction_measure: Measures,
            pruning_measure: Measures,
            voting_measure: Measures,
            max_growing: int = None,
            enable_pruning: bool = None,
            ignore_missing: bool = None,

            extend_using_preferred: bool = None,
            extend_using_automatic: bool = None,
            induce_using_preferred: bool = None,
            induce_using_automatic: bool = None,
            consider_other_classes: bool = None,
            preferred_conditions_per_rule: int = None,
            preferred_attributes_per_rule: int = None):
        if induction_measure == Measures.LogRank or pruning_measure == Measures.LogRank or voting_measure == Measures.LogRank:
            self.LogRank = JClass('adaa.analytics.rules.logic.quality.LogRank')
        self._configure_simple_parameter('min_rule_covered', min_rule_covered)
        self._configure_simple_parameter('max_growing', max_growing)
        self._configure_simple_parameter('enable_pruning', enable_pruning)
        self._configure_simple_parameter('ignore_missing', ignore_missing)

        self._configure_simple_parameter('extend_using_preferred', extend_using_preferred)
        self._configure_simple_parameter('extend_using_automatic', extend_using_automatic)
        self._configure_simple_parameter('induce_using_preferred', induce_using_preferred)
        self._configure_simple_parameter('induce_using_automatic', induce_using_automatic)
        self._configure_simple_parameter('consider_other_classes', consider_other_classes)
        self._configure_simple_parameter('preferred_conditions_per_rule', preferred_conditions_per_rule)
        self._configure_simple_parameter('preferred_attributes_per_rule', preferred_attributes_per_rule)

        self._configure_measure_parameter('induction_measure', induction_measure)
        self._configure_measure_parameter('pruning_measure', pruning_measure)
        self._configure_measure_parameter('voting_measure', voting_measure)


def map_attributes_names(example_set, attributes_names: List[str]):
    for index, name in enumerate(attributes_names):
        example_set.getAttributes().get(f'att{index + 1}').setName(name)


def set_survival_time(example_set, survival_time_attribute: str) -> object:
    OperatorDocumentation = JClass('com.rapidminer.tools.documentation.OperatorDocumentation')
    OperatorDescription = JClass('com.rapidminer.operator.OperatorDescription')
    Mockito = JClass('org.mockito.Mockito')
    ChangeAttributeRole = JClass('com.rapidminer.operator.preprocessing.filter.ChangeAttributeRole')

    documentation = Mockito.mock(OperatorDocumentation.class_)
    description = Mockito.mock(OperatorDescription.class_)
    Mockito.when(documentation.getShortName()).thenReturn(JString(''), None)
    Mockito.when(description.getOperatorDocumentation()).thenReturn(documentation, None)
    role_setter = ChangeAttributeRole(description)
    role_setter.setParameter(ChangeAttributeRole.PARAMETER_NAME, survival_time_attribute);
    role_setter.setParameter(ChangeAttributeRole.PARAMETER_TARGET_ROLE, "survival_time");
    return role_setter.apply(example_set)


def create_example_set(values, labels=None, numeric_labels=False, survival_time_attribute: str = None) -> object:
    if labels is None:
        labels = ['' if not numeric_labels else 0] * len(values)
    attributes_names = None
    label_name = None
    if isinstance(values, pd.DataFrame):
        attributes_names = values.columns.values
        values = values.to_numpy()
    if isinstance(labels, pd.Series):
        label_name = labels.name
        labels = labels.to_numpy()
    values = JObject(values, JArray('java.lang.Object', 2))
    labels = JObject(labels, JArray('java.lang.Object', 1))
    ExampleSetFactory = JClass('com.rapidminer.example.ExampleSetFactory')
    example_set = ExampleSetFactory.createExampleSet(values, labels)
    if attributes_names is not None:
        map_attributes_names(example_set, attributes_names)
    if label_name is not None:
        example_set.getAttributes().get('label').setName(label_name)
    if survival_time_attribute is not None:
        if survival_time_attribute == '':
            survival_time_attribute = f'att{example_set.getAttributes().size()}'
        example_set = set_survival_time(example_set, survival_time_attribute)
    return example_set


class PredictionResultMapper:

    @staticmethod
    def map(predicted_example_set) -> np.ndarray:
        attribute = predicted_example_set.getAttributes().get('prediction')
        if attribute.isNominal():
            return PredictionResultMapper.map_to_nominal(predicted_example_set)
        else:
            return PredictionResultMapper.map_to_numerical(predicted_example_set)

    @staticmethod
    def map_to_nominal(predicted_example_set) -> np.ndarray:
        prediction = []
        row_reader = predicted_example_set.getExampleTable().getDataRowReader()
        attribute = predicted_example_set.getAttributes().get('prediction')
        while row_reader.hasNext():
            row = row_reader.next()
            value_index = row.get(attribute)
            value = attribute.getMapping().mapIndex(round(value_index))
            prediction.append(value)
        prediction = list(map(str, prediction))
        return np.array(prediction)

    @staticmethod
    def map_to_numerical(predicted_example_set) -> np.ndarray:
        prediction = []
        row_reader = predicted_example_set.getExampleTable().getDataRowReader()
        attribute = predicted_example_set.getAttributes().get('prediction')
        while row_reader.hasNext():
            row = row_reader.next()
            value = attribute.getValue(row)
            prediction.append(value)
        prediction = list(map(float, prediction))
        return np.array(prediction)
