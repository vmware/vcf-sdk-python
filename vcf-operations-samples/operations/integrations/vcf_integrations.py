# Copyright (c) 2025-2026 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import time

from vcf.operations.model_client import (VCFIntegration, VCFDomain, Credential, NameValue, Certificate)
from vcf.operations.api.integrations_client import Vcf
from vcf.operations.api.integrations.vcf_client import Register, Unregister, TestConnection, Domains
from vcf.operations.api.integrations.vcf import domains_client
from vcf.operations.api.adapters.monitoringstate_client import Start
from vcf.operations.api_client import Credentials

from operations.sample_base import SampleBase
from operations.config.integrations.vcf_integration_config import VCFIntegrationConfig
from operations.helpers.arg_parser import get_args
from vmware.vapi.bindings.error import VapiError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VCFIntegrations(SampleBase):
    """
    Example that illustrates the use of API client bindings for VCF integration management
    """

    def __init__(self, client_config, sample_config):
        super().__init__(client_config)

        logger.info("--- VCFIntegrationsExample Constructor Started ---")
        logger.info(f"Client configuration file: {client_config}")
        logger.info(f"Sample configuration client file: {sample_config}")

        with open(sample_config, "r") as f:
            data = json.load(f)

        self.vcf_integration_config = VCFIntegrationConfig(**data)
        self.credential_config = self.vcf_integration_config.credentialConfig

        self.vcf_integrations_client = Vcf(self.ops_client.stub_config)
        self.vcf_domain_client = Domains(self.ops_client.stub_config)
        self.test_integrations_client = TestConnection(self.ops_client.stub_config)
        self.test_domain_client = domains_client.TestConnection(self.ops_client.stub_config)
        self.register_client = Register(self.ops_client.stub_config)
        self.unregister_client = Unregister(self.ops_client.stub_config)
        self.start_adapter_instances_client = Start(self.ops_client.stub_config)
        self.credentials_client = Credentials(self.ops_client.stub_config)

        self.delete_resources = True
        self.delete_child_resources = True
        self.force_delete = False

    def run(self):
        try:
            logger.info("--- VCFIntegrationsExample Run Started ---")

            logger.info("Calling create_credential()...")
            credential_id = self.create_credential()
            logger.info(f"Finished. Credential created with ID: {credential_id}")

            logger.info("Calling test_and_create_vcf_integration(credential_id)...")
            created_vcf_integration_id = self.test_and_create_vcf_integration(credential_id)
            logger.info(f"Finished. VCF Integration created with ID: {created_vcf_integration_id}")

            logger.info("Calling get_vcf_integration_by_id(created_vcf_integration_id)...")
            vcf_integration_by_id = self.get_vcf_integration_by_id(created_vcf_integration_id)
            logger.info(f"Finished. Retrieved VCF Integration: {vcf_integration_by_id.name} (ID: {created_vcf_integration_id})")

            logger.info(f"Calling adapter_instances_client.start_monitoring_resources_of_adapter_instance({created_vcf_integration_id})...")
            # VCF integration will not start automatically, remember to start it via api call
            self.start_monitoring_resources_of_adapter_instance(created_vcf_integration_id)
            logger.info(f"Finished. Monitoring started for Adapter Instance ID: {created_vcf_integration_id}")

            logger.info(f"Calling update_vcf_integration({vcf_integration_by_id})...")

            vcf_integration_by_id.name = "Updated VCFIntegration name"
            vcf_integration_by_id.description = "Updated VCFIntegration description"
            vcf_integration_by_id.collector_group_id = None
            self.update_vcf_integration(vcf_integration_by_id)

            logger.info(f"Finished. VCF Integration {created_vcf_integration_id} updated.")

            logger.info(f"Calling get_list_of_vcf_integration_domains({created_vcf_integration_id})...")
            list_of_vcf_integration_domains = self.get_list_of_vcf_integration_domains(created_vcf_integration_id)

            if (list_of_vcf_integration_domains and list_of_vcf_integration_domains.configured_domains and
                    len(list_of_vcf_integration_domains.configured_domains) > 0 and
                    list_of_vcf_integration_domains.configured_domains[0].domain_id):

                domain_id = list_of_vcf_integration_domains.configured_domains[0].domain_id
                logger.info(f"Finished. Found at least one configured domain. Using the first one with ID: {domain_id}")

                logger.info(f"Calling get_vcf_integration_domain_by_ids({created_vcf_integration_id}, {domain_id})...")
                domain = self.get_vcf_integration_domain_by_ids(created_vcf_integration_id, domain_id)
                logger.info(f"Finished. Retrieved VCF Domain: (ID: {domain_id})")

                logger.info(f"Calling test_and_update_vcf_domain({domain}, {domain_id}, {created_vcf_integration_id})...")

                domain.vcf_domain_vcenter.collector_id = "1"
                domain.vcf_domain_vcenter.sdmp_config.enabled = True
                domain.vcf_domain_vcenter.collector_group_id = None
                self.test_and_update_vcf_domain(domain, domain_id, created_vcf_integration_id)

                logger.info(f"Finished. VCF Domain {domain_id} updated and tested.")

                logger.info(f"Calling delete_vcf_domain_by_ids({created_vcf_integration_id}, {domain_id})...")
                self.delete_vcf_domain_by_ids(created_vcf_integration_id, domain_id)
                logger.info(f"Finished. VCF Domain {domain_id} deleted.")
            else:
                logger.info(f"Finished. No configured VCF Domains found for integration {created_vcf_integration_id} to process steps 7-9.")

            logger.info(f"Calling delete_vcf_integration_by_id({created_vcf_integration_id})...")
            self.delete_vcf_integration_by_id(created_vcf_integration_id)
            logger.info(f"Finished. VCF Integration {created_vcf_integration_id} deleted.")

            logger.info("Sleep for 2 minutes to allow the VCF integration to be deleted")
            time.sleep(2 * 60)

            logger.info(f"Calling delete_credential_instance({credential_id})...")
            self.delete_credential_instance(credential_id)
            logger.info(f"Finished. Credential Instance {credential_id} deleted.")

            logger.info("--- VCFIntegrationsExample Run Complete ---")
        except VapiError as vapi_error:
            raise vapi_error
        except Exception as ex:
            logger.error("Vcenter integration management sample failed", ex)
            raise ex

    def delete_vcf_domain_by_ids(self, integration_id, domain_id):
        """We need both integration and domain id's for domain removal"""
        try:
            self.vcf_domain_client.delete_vcf_domain(integration_id, domain_id, True, False)
        except VapiError as vapi_error:
            logger.error(f"Failed to delete vcf integration domain by id: {vapi_error.get_error_value()}")
            raise vapi_error

    def delete_credential_instance(self, credential_id):
        try:
            self.credentials_client.delete_credential(credential_id)
        except VapiError as vapi_error:
            logger.error(f"Failed to delete credential instance: {vapi_error.get_error_value()}")
            raise vapi_error

    def test_and_update_vcf_domain(self, domain, domain_id, integration_id):
        """
        Certain fields, such as those in standalone vCenter integration, cannot be changed for vCenter and NSX domains. 
        However, identifiers and the collector can still be modified
        Additionally, vSAN and SDMP can also be enabled from here.
        """
        vcf_domain = VCFDomain(domain.nsxt_integration, domain.vcf_domain_vcenter)
        try:
            test_vcf_domain_response = self.test_domain_client.test_domain(integration_id, domain_id, vcf_domain)
            # Similar to VCF, if any certificate needs to be accepted for the connection,
            # it will be included in the error result and must be added in future requests.

            self.vcf_domain_client.update_domain_details(integration_id, domain_id, test_vcf_domain_response, False)
        except VapiError as vapi_error:
            logger.error(f"Failed to test and update vcf domain: {vapi_error.get_error_value()}")
            raise vapi_error

    def get_vcf_integration_domain_by_ids(self, integration_id, domain_id):
        """By this call we can get more detailed information about domain, by providing its id, and integrations id"""
        try:
            return self.vcf_domain_client.get_domain_details_by_id(integration_id, domain_id)
        except VapiError as vapi_error:
            logger.error(f"Failed to get vcf integration domain by id: {vapi_error.get_error_value()}")
            raise vapi_error

    def get_list_of_vcf_integration_domains(self, integration_id):
        """
        Returns a list of VCF integration domains, categorized into configured and unconfigured domains
        The result model for each domain will include only the id and url
        """
        try:
            return self.vcf_domain_client.get_domain_summary(integration_id)
        except VapiError as vapi_error:
            logger.error(f"Failed to list vcf integration domains: {vapi_error.get_error_value()}")
            raise vapi_error

    def delete_vcf_integration_by_id(self, integration_id):
        """Deleting created VCF integration by providing its id, and flags, that will indicate deletion of related
        and child resources """
        try:
            self.vcf_integrations_client.delete_vcf_integration(integration_id, True, True, False)
        except VapiError as vapi_error:
            logger.error(f"Failed to delete vcf integration: {vapi_error.get_error_value()}")
            raise vapi_error

    def update_vcf_integration(self, integration):
        """Updating name and description of our created VCF integration"""
        try:
            self.vcf_integrations_client.update_vcf_integration(integration, False)
        except VapiError as vapi_error:
            logger.error(f"Failed to update vcf integration: {vapi_error.get_error_value()}")
            raise vapi_error

    def get_vcf_integration_by_id(self, integration_id):
        try:
            return self.vcf_integrations_client.get_vcf_integration_by_id(integration_id)
        except VapiError as vapi_error:
            logger.error(f"Failed to get vcf integration by id: {vapi_error.get_error_value()}")
            raise vapi_error

    def test_and_create_vcf_integration(self, credential_id):
        """Constructing vcf integration creation request"""
        vcf_integration = VCFIntegration()
        vcf_integration.name = self.vcf_integration_config.name
        vcf_integration.description = self.vcf_integration_config.description
        vcf_integration.collector_id = self.vcf_integration_config.collectorId

        identifiers = []
        for key, value in self.vcf_integration_config.identifiers.items():
            identifier = NameValue(key, value)
            identifiers.append(identifier)

        vcf_integration.resource_identifiers = identifiers
        vcf_integration.credential_instance_id = credential_id

        try:
            # Testing constructed request body, to be sure everything is normal
            self.test_integrations_client.test_vcf_integration(vcf_integration)
        except Exception as client_side_exception:
            if client_side_exception.type == 'CertificatesError' and client_side_exception._extra_fields.get('certificates'):
                certificates = client_side_exception._extra_fields['certificates']._list_val

                if not vcf_integration.certificates:
                    vcf_integration.certificates = []

                for integration_certificates in certificates:
                    integration_certificates_detail = integration_certificates._fields['certificates']
                    integration_certificates_details = integration_certificates_detail._list_val

                    for item in integration_certificates_details:
                        cert_fields = item._fields

                        cert = Certificate(
                            thumbprint=cert_fields["thumbprint"].value,
                            issued_to=cert_fields["issuedTo"].value,
                            issued_by=cert_fields["issuedBy"].value,
                            expires=cert_fields["expires"].value,
                            certificate_details=cert_fields["certificateDetails"].value,
                        )

                        vcf_integration.certificates.append(cert)

        # In case if test_vcf_integration fails with no valid certificate's error, it will provide ones for
        # acceptance, which means that those certificates must be provided in the future creation request

        try:
            created_integration = self.vcf_integrations_client.create_vcf_integration(
                vcf_integration,
                self.vcf_integration_config.forceManagementOwnership,
                self.vcf_integration_config.force
            )
            return created_integration.id
        except VapiError as vapi_error:
            logger.error(f"Failed to create vcf integration: {vapi_error.get_error_value()}")
            raise vapi_error

    def create_credential(self):
        logger.info("Creating Credential...")
        credential_instance = Credential()
        credential_instance.name = self.credential_config.name
        credential_instance.credential_kind_key = self.credential_config.credentialKindKey
        credential_instance.adapter_kind_key = self.credential_config.adapterKindKey
        logger.info(f"Credential Name: {credential_instance.name}, Kind Key: {credential_instance.credential_kind_key}")

        fields = []
        for key, value in self.credential_config.fields.items():
            value_display = "********" if key.upper() == "PASSWORD" else value
            field = NameValue(key, value)
            fields.append(field)
            logger.info(f"Adding credential field: {key} = {value_display}")

        credential_instance.fields = fields
        try:
            created_credential = self.credentials_client.create_credential(credential_instance)
            logger.info(f"Credential created with ID: {created_credential.id}, Name: {created_credential.name}")
            return created_credential.id
        except VapiError as vapi_error:
            logger.error(f"Failed to create a credential: {vapi_error.get_error_value()}")
            raise vapi_error

    def start_monitoring_resources_of_adapter_instance(self, created_vcf_integration_id):
        try:
            self.start_adapter_instances_client.start_monitoring_resources_of_adapter_instance(created_vcf_integration_id)
        except VapiError as vapi_error:
            logger.error(f"Failed to start monitoring of resource: {vapi_error.get_error_value()}")
            raise vapi_error


if __name__ == "__main__":
    args = get_args()
    
    vcf_integrations = VCFIntegrations(args.client_config, args.sample_config)
    vcf_integrations.run()
