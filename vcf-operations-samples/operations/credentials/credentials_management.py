# Copyright (c) 2025-2026 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import json
import logging

from vcf.operations.model_client import Credential, NameValue
from vcf.operations.api_client import Credentials, Credentialkinds

from operations.sample_base import SampleBase
from operations.config.credentials.credential_config import CredentialConfig
from operations.helpers.arg_parser import get_args
from vmware.vapi.bindings.error import VapiError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CredentialsManagement(SampleBase):
    """
    Example that illustrates the use of API client bindings to perform CRUD
    operations for Credential Management. Also, this example
    illustrates the ability to query the Credential Kinds (metadata)
    available in the system.
    """

    def __init__(self, client_config, sample_config):
        super().__init__(client_config)

        with open(sample_config, "r") as f:
            data = json.load(f)

        self.credential_config = CredentialConfig(**data)
        self.credentials_client = Credentials(self.ops_client.stub_config)
        self.credentials_kind_client = Credentialkinds(self.ops_client.stub_config)

    def run(self):
        try:
            logger.info("Get all the Credential Kinds in the system...")
            cred_kinds = self.credentials_kind_client.get_credential_kinds()

            for cred_type in cred_kinds.credential_types:
                logger.info(f"Credential Kind: {cred_type.id}")

            credential = self.create_credential_instance()

            credential.name = "Updated Name"
            # Propagating the password field since it was returned as null
            for name_value_pair in credential.fields:
                if name_value_pair.name == "PASSWORD":
                    name_value_pair.value = self.credential_config.fields.get("PASSWORD")

            self.modify_credential_instance(credential)

            logger.info("Listing all Credential Instances...")
            credential_instances = self.retrieve_credential_instance(None)
            logger.info(f"# Credential Instances = {len(credential_instances.credential_instances)}")

            uuid_list = [ci.id for ci in credential_instances.credential_instances]

            logger.info("Retrieving Credential Instances for the Container Adapter Kind...")
            self.retrieve_credential_instance(id=None, adapter_kind=["Container"])

            if uuid_list:
                logger.info("Retrieving Credential Instance for the specified ID")
                ci_list = self.retrieve_credential_instance(id=uuid_list, adapter_kind=None)
                logger.info(f"Credential = {ci_list.credential_instances[0]}")

            logger.info("Cleaning up...")
            self.delete_credential_instance(credential.id)
        except VapiError as vapi_error:
            raise vapi_error
        except Exception as ex:
            logger.error("Credential management sample failed", ex)
            raise ex

    def create_credential_instance(self):
        logger.info("Creating a Credential Instance...")
        ci = Credential()
        ci.name = self.credential_config.name
        ci.credential_kind_key = self.credential_config.credentialKindKey
        ci.adapter_kind_key = self.credential_config.adapterKindKey

        fields = []
        for key, value in self.credential_config.fields.items():
            field = NameValue()
            field.name = key
            field.value = value
            fields.append(field)
        ci.fields = fields
        try:
            return self.credentials_client.create_credential(ci)
        except VapiError as vapi_error:
            logger.error(f"Failed to create credential instance: {vapi_error.get_error_value()}")
            raise vapi_error

    def retrieve_credential_instance(self, id=None, adapter_kind=None):
        try:
            ci_list = self.credentials_client.get_credentials(id, adapter_kind)
            logger.info(f"# CredentialsClient = {len(ci_list.credential_instances)}")
            return ci_list
        except VapiError as vapi_error:
            logger.error(f"Failed to retrieve credential instance: {vapi_error.get_error_value()}")
            raise vapi_error

    def modify_credential_instance(self, credential_instance):
        logger.info("Modify credential instance...")
        try:
            return self.credentials_client.update_credential(credential_instance)
        except VapiError as vapi_error:
            logger.error(f"Failed to modify credential instance: {vapi_error.get_error_value()}")
            raise vapi_error

    def delete_credential_instance(self, id):
        logger.info(f"Delete credential instance with id: {id}")
        try:
            self.credentials_client.delete_credential(id)
            logger.info("Credential instance is deleted successfully")
        except VapiError as vapi_error:
            logger.error(f"Failed to delete credential instance: {vapi_error.get_error_value()}")
            raise vapi_error


if __name__ == "__main__":
    args = get_args()
    
    credential_management = CredentialsManagement(args.client_config, args.sample_config)
    credential_management.run()
