# Copyright (c) 2025-2026 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import time

from vcf.operations.model_client import Resource, ResourceKey, ResourceQuery, ResourceIdentifier, ResourceIdentifierType
from vcf.operations.api.resources_client import Adapterkinds, Query
from vcf.operations.api_client import Resources

from operations.sample_base import SampleBase
from operations.config.resources.resource_config import ResourceConfig
from operations.helpers.arg_parser import get_args
from vmware.vapi.bindings.error import VapiError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ResourcesCRUD(SampleBase):
    """
    Example that illustrates the use of API client bindings for resource
    CRUD operations
    """

    def __init__(self, client_config, sample_config):
        super().__init__(client_config)

        with open(sample_config, "r") as f:
            data = json.load(f)

        self.resource_config = ResourceConfig(**data)
        self.create_resource_client = Adapterkinds(self.ops_client.stub_config)
        self.resources_client = Resources(self.ops_client.stub_config)
        self.resources_query_client = Query(self.ops_client.stub_config)

    def run(self):
        try:
            logger.info("Creating a Resource...")
            resource = self.create_resource()
            resource_identifier = resource.identifier

            logger.info("Sleep for 20 seconds for resource to get created")
            time.sleep(20)

            resource_dto = self.get_resources_with_uuid(resource_identifier)
            if resource_dto and resource_dto.resource_key.name == self.resource_config.name:
                logger.info(f"Resource {self.resource_config.name} is indeed created.")
            else:
                logger.info(f"Resource {self.resource_config.name} is not created.")
                return

            logger.info("Updating a Resource")
            resource_key = resource.resource_key
            resource_key.name = "Bar"
            resource.resource_key = resource_key
            resource_dto = self.update_resource(resource)

            logger.info("Sleep for 20 seconds for resource to get updated")
            time.sleep(20)

            if resource_dto.resource_key.name == "Bar":
                logger.info(f"Resource {self.resource_config.name} is indeed updated to Bar.")
            else:
                logger.info(f"Resource {self.resource_config.name} is not updated to Bar.")

            logger.info("Deleting previously created resource")
            self.delete_resource(resource_identifier)
            logger.info("Sleep for 20 seconds for resource to get deleted")
            time.sleep(20)

            resource_dto = self.get_resources_with_uuid(resource.identifier)
            if resource_dto:
                logger.info("Resource is not deleted successfully.")
            else:
                logger.info("Resource is deleted successfully.")

            logger.info("Getting first 100 resources.")
            self.get_resources()

            logger.info("Getting resources by page.")
            self.get_resources_by_page()

            logger.info("Getting resources with name.")
            self.get_resources_with_name(["name-1", "name-2"])
        except VapiError as vapi_error:
            raise vapi_error
        except Exception as ex:
            logger.error("Resources CRUD sample failed", ex)
            raise ex

    def create_resource(self):
        """
        Creates a Dummy vSphere Virtual Machine corresponding Resource in VMware Cloud Foundation Operations.
        Assumes that the vSphere solution pack has already been installed.
        """
        resource = Resource()
        resource_key = ResourceKey()
        resource_key.name = self.resource_config.name
        resource.description = self.resource_config.description
        resource_key.adapter_kind_key = self.resource_config.adapterKindKey
        resource_key.resource_kind_key = self.resource_config.resourceKindKey

        resource_identifiers = []
        for key, value in self.resource_config.identifiers.items():
            resource_identifier_type = ResourceIdentifierType()
            resource_identifier_type.data_type = ResourceIdentifierType.DATA_TYPE_STRING
            resource_identifier_type.name = key
            resource_identifier_type.is_part_of_uniqueness = True

            identifier = ResourceIdentifier()
            identifier.identifier_type = resource_identifier_type
            identifier.value = value
            resource_identifiers.append(identifier)

        resource_key.resource_identifiers = resource_identifiers
        resource.resource_key = resource_key
        try:
            return self.create_resource_client.create_resource_using_adapter_kind(self.resource_config.pushAdapterKindKey, resource)
        except VapiError as vapi_error:
            logger.error(f"Failed to create a resource: {vapi_error.get_error_value()}")
            raise vapi_error

    def delete_resource(self, resource_id):
        """Delete a resource"""
        try:
            self.resources_client.delete_resource(resource_id)
        except VapiError as vapi_error:
            logger.error(f"Failed to delete a resource: {vapi_error.get_error_value()}")
            raise vapi_error

    def update_resource(self, resource):
        try:
            return self.resources_client.update_resource(resource)
        except VapiError as vapi_error:
            logger.error(f"Failed to update a resource: {vapi_error.get_error_value()}")
            raise vapi_error

    def get_resources_with_uuid(self, uuid):
        try:
            return self.resources_client.get_resource(uuid)
        except VapiError:
            logger.info(f"Failed to get a resource with uuid: {uuid}")
            return None

    def get_resources(self):
        page = 0
        page_size = 100
        try:
            resources = self.resources_query_client.get_matching_resources(ResourceQuery(), page, page_size)
            logger.info(resources.page_info.total_count)
            logger.info(resources.page_info.page_size)
            return resources
        except VapiError as vapi_error:
            logger.error(f"Failed to get resources: {vapi_error.get_error_value()}")
            raise vapi_error

    def get_resources_by_page(self):
        """Example code detailing the use of page and pageSize"""
        try:
            page_size = 1000
            page_map = {}
            rq = ResourceQuery()
            resources = self.resources_query_client.get_matching_resources(rq, None, page_size)
            total_count = resources.page_info.total_count

            for page in range(total_count // page_size):
                temp_resources = self.resources_query_client.get_matching_resources(rq, page, page_size)
                page_map[page] = temp_resources

            return page_map
        except VapiError as vapi_error:
            logger.error(f"Failed to get resources by page: {vapi_error.get_error_value()}")
            raise vapi_error

    def get_resources_with_name(self, names):
        rq = ResourceQuery()
        rq.name = names
        try:
            return self.resources_query_client.get_matching_resources(rq, None)
        except VapiError as vapi_error:
            logger.error(f"Failed to get resources with name: {vapi_error.get_error_value()}")
            raise vapi_error


if __name__ == "__main__":
    args = get_args()

    resource_crud = ResourcesCRUD(args.client_config, args.sample_config)
    resource_crud.run()
