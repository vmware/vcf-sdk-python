# Copyright (c) 2025-2026 Broadcom Inc. and/or its subsidiaries. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import logging

from vcf.operations.model_client import (SymptomDefinition, SymptomState, HTCondition, AlertDefinition,
                                  AlertDefinitionState, AlertDefinitionImpact, SymptomSet)
from vcf.operations.api_client import Symptomdefinitions, Alertdefinitions, Policies
from vcf.operations.api import alertdefinitions_client

from operations.sample_base import SampleBase
from operations.config.symptomdefinitions.symptom_definition_config import AlertDefinitionConfig
from operations.helpers.arg_parser import get_args
from vmware.vapi.bindings.error import VapiError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SymptomsAndAlertDefinitions(SampleBase):
    """
    Example that illustrates the use of API client bindings to perform CRUD
    operations on Symptom Definitions and Alert Definitions
    """

    def __init__(self, client_config, sample_config):
        super().__init__(client_config)

        with open(sample_config, "r") as f:
            data = json.load(f)

        self.alert_definition_config = AlertDefinitionConfig(**data)
        self.symptom_definition_config = self.alert_definition_config.symptomDefinitionConfig

        self.alert_definitions_client = Alertdefinitions(self.ops_client.stub_config)
        self.enable_alert_definitions_client = alertdefinitions_client.Enable(self.ops_client.stub_config)
        self.disable_alert_definitions_client = alertdefinitions_client.Disable(self.ops_client.stub_config)
        self.symptom_definitions_client = Symptomdefinitions(self.ops_client.stub_config)
        self.policy_client = Policies(self.ops_client.stub_config)

    def run(self):
        try:
            logger.info("Starting Symptom and Alert Definitions Example...")

            # --- Symptom Definition CRUD Operations ---
            logger.info("--- Performing Symptom Definition CRUD operations ---")
            symptom_id = self.create_symptom()
            self.get_symptom_by_id(symptom_id)
            self.get_symptom_by_name(self.symptom_definition_config.name)
            self.update_symptom(symptom_id)

            # --- Alert Definition CRUD Operations ---
            logger.info("--- Performing Alert Definition CRUD operations ---")
            # Create an alert definition linked to symptom_id1
            alert_id = self.create_alert_definition(symptom_id)
            self.get_alert_definition_by_id(alert_id)
            self.update_alert_definition(alert_id)

            policy_id = self.get_default_policy_id()

            # --- Alert Definition Policy Operations ---
            logger.info("--- Demonstrating Alert Definition Policy Management ---")
            self.enable_alert_definition_in_policy(alert_id, policy_id)

            # --- Final Cleanup ---
            logger.info("--- Performing final cleanup ---")
            self.disable_alert_definition_in_policy(alert_id, policy_id)
            self.delete_alert_definition(alert_id)
            self.delete_symptom(symptom_id)

            logger.info("Example finished successfully.")
        except VapiError as vapi_error:
            raise vapi_error
        except Exception as ex:
            logger.error("Resources CRUD sample failed", ex)
            raise ex

    def enable_alert_definition_in_policy(self, alert_id, policy_id):
        logger.info(f"Enabling alert definition '{alert_id}' in policy '{policy_id}'")
        try:
            self.enable_alert_definitions_client.enable_alert_definition_in_policies(alert_id, [policy_id])
            logger.info("Alert definition enabled in policy successfully.")
        except VapiError as vapi_error:
            logger.error(f"Failed to enable alert definition in policy: {vapi_error.get_error_value()}")
            raise vapi_error

    def disable_alert_definition_in_policy(self, alert_id, policy_id):
        logger.info(f"Disabling alert definition '{alert_id}' in policy '{policy_id}'")
        try:
            self.disable_alert_definitions_client.disable_alert_definition_in_policies(alert_id, [policy_id])
            logger.info("Alert definition disabled in policy successfully.")
        except VapiError as vapi_error:
            logger.error(f"Failed to disable alert definition in policy: {vapi_error.get_error_value()}")
            raise vapi_error

    def create_symptom(self):
        logger.info(f"Creating a new symptom definition named: '{self.symptom_definition_config.name}'")
        symptom = SymptomDefinition()
        symptom.name = self.symptom_definition_config.name
        symptom.adapter_kind_key = self.symptom_definition_config.adapterKindKey
        symptom.resource_kind_key = self.symptom_definition_config.resourceKindKey
        symptom.wait_cycles = self.symptom_definition_config.waitCycle
        symptom.cancel_cycles = self.symptom_definition_config.cancelCycle

        symptom_state = SymptomState()
        symptom_state.severity = self.symptom_definition_config.severity

        condition = HTCondition()
        condition.key = self.symptom_definition_config.key
        condition.operator = "GT_EQ"
        condition.value = self.symptom_definition_config.value
        condition.instanced = self.symptom_definition_config.instance  # Applies to the resource itself, not specific instances

        symptom_state.condition = condition
        symptom.state = symptom_state

        try:
            created_symptom = self.symptom_definitions_client.create_symptom_definition(symptom)
            logger.info(f"Symptom definition created successfully with ID: {created_symptom.id}")
            return created_symptom.id
        except VapiError as vapi_error:
            logger.error(f"Failed to create a symptom: {vapi_error.get_error_value()}")
            raise vapi_error

    def update_symptom(self, symptom_id):
        logger.info(f"Updating symptom definition with ID: {symptom_id}")
        symptom = self.get_symptom_by_id(symptom_id)
        symptom.wait_cycles = 10  # Example update: change wait cycles
        try:
            self.symptom_definitions_client.update_symptom_definition(symptom)
            logger.info(f"Symptom definition '{symptom_id}' updated (WaitCycles changed to 10).")
        except VapiError as vapi_error:
            logger.error(f"Failed to update a symptom: {vapi_error.get_error_value()}")
            raise vapi_error

    def update_alert_definition(self, alert_id):
        logger.info(f"Updating alert definition with ID: {alert_id}")
        alert = self.get_alert_definition_by_id(alert_id)
        alert.wait_cycles = 10  # Example update: change wait cycles
        try:
            self.alert_definitions_client.update_alert_definition(alert)
            logger.info(f"Alert definition '{alert_id}' updated (WaitCycles changed to 10).")
        except VapiError as vapi_error:
            logger.error(f"Failed to update alert definition: {vapi_error.get_error_value()}")
            raise vapi_error

    def get_symptom_by_id(self, symptom_id):
        logger.info(f"Getting symptom definition by ID: {symptom_id}")
        try:
            symptom = self.symptom_definitions_client.get_symptom_definition_by_key(symptom_id)
            logger.info(f"Successfully looked up symptom definition with ID: {symptom.id} and name: {symptom.name}")
            return symptom
        except VapiError as vapi_error:
            logger.error(f"Failed to get a symptom: {vapi_error.get_error_value()}")
            raise vapi_error

    def get_symptom_by_name(self, name):
        logger.info(f"Querying symptom definitions by name: '{name}'")
        try:
            symptoms = self.symptom_definitions_client.get_symptom_definitions(name=name)
            logger.info(f"Number of symptoms found with name '{name}': {len(symptoms.symptom_definitions)}")
            if symptoms.symptom_definitions:
                for s in symptoms.symptom_definitions:
                    logger.info(f"  - Found symptom: {s.name} (ID: {s.id})")
            return symptoms
        except VapiError as vapi_error:
            logger.error(f"Failed to get symptom by name: {vapi_error.get_error_value()}")
            raise vapi_error

    def create_alert_definition(self, symptom_id):
        logger.info(f"Creating a new alert definition named '{self.alert_definition_config.name}' linked to symptom ID: {symptom_id}")
        alert_definition = AlertDefinition()
        alert_definition.name = self.alert_definition_config.name
        alert_definition.description = self.alert_definition_config.description
        alert_definition.adapter_kind_key = self.alert_definition_config.adapterKindKey
        alert_definition.resource_kind_key = self.alert_definition_config.resourceKindKey
        alert_definition.type = self.alert_definition_config.type  # Example type ID (e.g., 'Performance')
        alert_definition.sub_type = self.alert_definition_config.subType  # Example sub-type ID (e.g., 'CPU')
        alert_definition.wait_cycles = self.alert_definition_config.waitCycle
        alert_definition.cancel_cycles = self.alert_definition_config.cancelCycle

        problem_states = []
        alert_definition_state = AlertDefinitionState()

        impact = AlertDefinitionImpact()
        impact.impact_type = self.alert_definition_config.impactType
        impact.detail = self.alert_definition_config.detail  # Impacts the health badge

        alert_definition_state.impact = impact
        alert_definition_state.severity = self.alert_definition_config.severity  # Severity determined automatically

        symptom_set = SymptomSet()
        symptom_set.relation = self.alert_definition_config.relation  # Symptom on the same resource
        symptom_set.symptom_definition_ids = [symptom_id]
        symptom_set.aggregation = self.alert_definition_config.aggregation  # All symptoms in the set must be true

        alert_definition_state.base_symptom_set = symptom_set
        problem_states.append(alert_definition_state)
        alert_definition.states = problem_states

        try:
            created_alert_definition = self.alert_definitions_client.create_alert_definition(alert_definition)
            logger.info(f"Alert definition created successfully with ID: {created_alert_definition.id}")
            return created_alert_definition.id
        except VapiError as vapi_error:
            logger.error(f"Failed to create an alert definition: {vapi_error.get_error_value()}")
            raise vapi_error

    def get_alert_definition_by_id(self, alert_id):
        logger.info(f"Getting alert definition by ID: {alert_id}")
        try:
            alert = self.alert_definitions_client.get_alert_definition_by_id(alert_id)
            logger.info(f"Successfully looked up alert definition with ID: {alert.id} and name: {alert.name}")
            return alert
        except VapiError as vapi_error:
            logger.error(f"Failed to get alert definition by id: {vapi_error.get_error_value()}")
            raise vapi_error

    def delete_alert_definition(self, alert_id):
        logger.info(f"Deleting alert definition with ID: {alert_id}")
        try:
            self.alert_definitions_client.delete_alert_definition(alert_id)
            logger.info(f"Alert definition '{alert_id}' deleted successfully.")
        except VapiError as vapi_error:
            logger.error(f"Failed to delete an alert definition: {vapi_error.get_error_value()}")
            raise vapi_error

    def delete_symptom(self, symptom_id):
        logger.info(f"Deleting symptom definition with ID: {symptom_id}")
        try:
            self.symptom_definitions_client.delete_symptom_definition(symptom_id)
            logger.info(f"Symptom definition '{symptom_id}' deleted successfully.")
        except VapiError as vapi_error:
            logger.error(f"Failed to delete a symptom: {vapi_error.get_error_value()}")
            raise vapi_error

    def get_default_policy_id(self):
        policies = self.policy_client.get_policies(True)
        
        # Prefer the default policy
        default_policy = None
        for policy in policies.policy_summaries:
            if policy.default_policy:
                default_policy = policy
                break
        
        # Fallback to first if no default
        if not default_policy and policies.policy_summaries:
            default_policy = policies.policy_summaries[0]
        
        if not default_policy:
            raise RuntimeError("No policies found in the system")
        
        policy_id = default_policy.id
        logger.info(f"Using policy: '{default_policy.name}' (ID: {policy_id}) for alert definition operations.")
        return policy_id


if __name__ == "__main__":
    args = get_args()
    
    symptoms_and_alert_definitions = SymptomsAndAlertDefinitions(args.client_config, args.sample_config)
    symptoms_and_alert_definitions.run()
