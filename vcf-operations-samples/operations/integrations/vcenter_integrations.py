# Copyright (c) 2025-2026 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import time
import uuid

from vcf.operations.model_client import (VcenterIntegration, VsanConfig, SdmpConfig, NameValue, Credential, Certificate)
from vcf.operations.api.integrations.vcenters_client import Register, Unregister, TestConnection
from vcf.operations.api.integrations_client import Vcenters
from vcf.operations.api.adapters.monitoringstate_client import Start
from vcf.operations.api_client import Credentials

from operations.sample_base import SampleBase
from operations.config.integrations.vcenter_integration_config import VcenterIntegrationConfig
from operations.helpers.arg_parser import get_args
from vmware.vapi.bindings.error import VapiError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VcenterIntegrations(SampleBase):
    """
    Example that illustrates the use of API client bindings for vCenter integration management
    """

    def __init__(self, client_config, sample_config):
        super().__init__(client_config)

        logger.info("Initializing VcenterIntegrationsExample...")
        logger.info(f"Loading sample config from: {sample_config}")

        with open(sample_config, "r") as f:
            data = json.load(f)

        self.vcenter_integration_config = VcenterIntegrationConfig(**data)
        self.credential_config = self.vcenter_integration_config.credentialConfig
        
        self.vcenter_integrations_client = Vcenters(self.ops_client.stub_config)
        self.test_integrations_client = TestConnection(self.ops_client.stub_config)
        self.register_client = Register(self.ops_client.stub_config)
        self.unregister_client = Unregister(self.ops_client.stub_config)
        self.start_adapter_instances_client = Start(self.ops_client.stub_config)
        self.credentials_client = Credentials(self.ops_client.stub_config)

        self.delete_resources = True
        self.delete_child_resources = True
        self.force_delete = False

        logger.info("Clients initialized successfully.")

    def run(self):
        try:
            logger.info("--- Starting VcenterIntegrationExample run() ---")
            credential_id = self.create_credential()
            logger.info(f"Created Credential with ID: {credential_id}")

            created_vcenter_integration_id = self.test_and_create_vcenter_integration(credential_id)
            logger.info(f"Created vCenter Integration with ID: {created_vcenter_integration_id}")

            vcenter_integration_by_id = self.get_vcenter_integration_by_id(created_vcenter_integration_id)
            logger.info(f"Retrieved vCenter Integration by ID. Name: {vcenter_integration_by_id.name}, ID: {vcenter_integration_by_id.id}")

            logger.info(f"Starting monitoring resources for Adapter Instance with ID: {created_vcenter_integration_id}")
            # vCenter integration will not start automatically, remember to start it via api call
            self.start_monitoring_resources_of_adapter_instance(created_vcenter_integration_id)
            logger.info("Monitoring started for vCenter Integration.")

            updated_vcenter_integration = self.update_vcenter_integration(vcenter_integration_by_id)
            logger.info(f"Updated vCenter Integration. New Name: {updated_vcenter_integration.name}, ID: {updated_vcenter_integration.id}")

            self.delete_vcenter_integration(updated_vcenter_integration.id)
            logger.info(f"Deleted vCenter Integration with ID: {updated_vcenter_integration.id}")

            logger.info("Sleep for 2 minutes to allow the vCenter integration to be deleted")
            time.sleep(2 * 60)

            self.delete_credential_instance(credential_id)
            logger.info(f"Deleted Credential with ID: {credential_id}")
            logger.info("--- VcenterIntegrationExample run() completed ---")
        except VapiError as vapi_error:
            raise vapi_error
        except Exception as ex:
            logger.error("Vcenter integration management sample failed", ex)
            raise ex

    def test_and_create_vcenter_integration(self, credential_id):
        logger.info("Entering test_and_create_vcenter_integration...")

        # Constructing request for vCenter integration creation
        request = VcenterIntegration()
        request.name = self.vcenter_integration_config.name
        request.description = self.vcenter_integration_config.description
        request.collector_id = self.vcenter_integration_config.collectorId
        logger.info(f"Constructing vCenter Integration request. Name: {request.name}")

        # Constructing and setting required identifiers
        identifiers_list = []
        for key, value in self.vcenter_integration_config.identifiers.items():
            identifier = NameValue()
            identifier.name = key
            identifier.value = value
            identifiers_list.append(identifier)
        
        request.resource_identifiers = identifiers_list
        request.credential_instance_id = credential_id
        logger.info(f"Set Resource Identifiers and Credential ID: {credential_id}")

        # Construction and setting vSAN and Service Discovery adapters info
        vsan_config = VsanConfig()
        vsan_config.enabled = self.vcenter_integration_config.enableVSAN
        vsan_config.smart_data_collection_enabled = self.vcenter_integration_config.smartDataCollection
        request.vsan_config = vsan_config
        logger.info(f"vSAN config enabled: {vsan_config.enabled}, SmartDataCollection: {vsan_config.smart_data_collection_enabled}")

        sdmp_config = SdmpConfig()
        sdmp_config.enabled = self.vcenter_integration_config.enableSDMP
        sdmp_config.application_discovery_enabled = self.vcenter_integration_config.enableAutoDiscovery
        request.sdmp_config = sdmp_config
        logger.info(f"SDMP config enabled: {sdmp_config.enabled}, ApplicationDiscovery: {sdmp_config.application_discovery_enabled}")

        try:
            # Testing vCenter integration request to be sure everything is normal
            logger.info("Testing vCenter integration request...")
            self.test_integrations_client.test_vcenter_integration(request)
            logger.info("vCenter Integration test successful.")
        except Exception as client_side_exception:
            if client_side_exception.type == 'CertificatesError' and client_side_exception._extra_fields.get('certificates'):
                certificates = client_side_exception._extra_fields['certificates']._list_val

                if not request.certificates:
                    request.certificates = []

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

                        request.certificates.append(cert)

        # In case if test_vcenter_integration fails with no valid certificate's error, it will provide ones for
        # acceptance, which means that those certificates must be provided in the future creation request
        logger.info("Creating vCenter integration...")
        try:
            result = self.vcenter_integrations_client.create_vcenter_integration(
                request,
                self.vcenter_integration_config.force,
                self.vcenter_integration_config.forceManagementOwnership
            )
            logger.info(f"vCenter Integration created with ID: {result.id}, Name: {result.name}")
            return result.id
        except VapiError as vapi_error:
            logger.error(f"Failed to create vcenter integration: {vapi_error.get_error_value()}")
            raise vapi_error

    def get_vcenter_integration_by_id(self, integration_id):
        logger.info(f"Getting vCenter Integration by ID: {integration_id}")
        try:
            integration = self.vcenter_integrations_client.get_vcenter_integration_by_id(integration_id)
            logger.info(f"Successfully retrieved vCenter Integration. Name: {integration.name}")
            return integration
        except VapiError as vapi_error:
            logger.error(f"Failed to retrieve vcenter integration: {vapi_error.get_error_value()}")
            raise vapi_error

    def update_vcenter_integration(self, vcenter_integration):
        logger.info(f"Updating vCenter Integration with ID: {vcenter_integration.id}")
        old_name = vcenter_integration.name
        new_name = f"UpdatedTestVcenterIntegration-{str(uuid.uuid4())}"  # Add a unique suffix for better identification
        
        # Updating name and description of our created vCenter integration
        vcenter_integration.name = new_name
        vcenter_integration.description = "Updated vCenter integration description"
        vcenter_integration.collector_group_id = None
        logger.info(f"Old Name: {old_name}, New Name: {vcenter_integration.name}")
        try:
            updated = self.vcenter_integrations_client.update_vcenter_integration(vcenter_integration, False)
            logger.info(f"vCenter Integration updated successfully. Updated Name: {updated.name}")
            return updated
        except VapiError as vapi_error:
            logger.error(f"Failed to update vcenter integration: {vapi_error.get_error_value()}")
            raise vapi_error

    def delete_vcenter_integration(self, integration_id):
        logger.info(f"Deleting vCenter Integration with ID: {integration_id}")
        # Deleting created vCenter integration by providing its id, and flags, that will indicate deletion of related
        # and child resources
        try:
            self.vcenter_integrations_client.delete_vcenter_integration(integration_id, self.delete_resources, self.delete_child_resources, self.force_delete)
            logger.info(f"vCenter Integration with ID {integration_id} deleted successfully.")
        except VapiError as vapi_error:
            logger.error(f"Failed to delete vcenter integration: {vapi_error.get_error_value()}")
            raise vapi_error

    def delete_credential_instance(self, credential_id):
        logger.info(f"Deleting Credential with ID: {credential_id}")
        try:
            self.credentials_client.delete_credential(credential_id)
            logger.info(f"Credential with ID {credential_id} deleted successfully.")
        except VapiError as vapi_error:
            logger.error(f"Failed to delete credential instance: {vapi_error.get_error_value()}")
            raise vapi_error

    def start_monitoring_resources_of_adapter_instance(self, created_vcenter_integration_id):
        try:
            self.start_adapter_instances_client.start_monitoring_resources_of_adapter_instance(created_vcenter_integration_id)
        except VapiError as vapi_error:
            logger.error(f"Failed to start monitoring of vcenter integration: {vapi_error.get_error_value()}")
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
            logger.error(f"Failed to create credential instance: {vapi_error.get_error_value()}")
            raise vapi_error


if __name__ == "__main__":
    args = get_args()
    
    vcenter_integrations = VcenterIntegrations(args.client_config, args.sample_config)
    vcenter_integrations.run()
