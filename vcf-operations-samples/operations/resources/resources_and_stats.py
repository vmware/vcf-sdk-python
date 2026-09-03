# Copyright (c) 2025-2026 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import time
import random
from datetime import datetime, timezone

from vcf.operations.model_client import (Resource, ResourceKey, ResourceIdentifier, StatContents, StatContent,
                                  PropertyContents, PropertyContent, ResourceIdentifierType)

from vcf.operations.api.resources_client import Adapterkinds, Stats, Properties, Maintained
from vcf.operations.api_client import Resources

from operations.sample_base import SampleBase
from operations.config.resources.resource_config import ResourceConfig
from operations.helpers.arg_parser import get_args
from vmware.vapi.bindings.error import VapiError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ResourcesAndStats(SampleBase):
    """
    Example that illustrates the use of API client bindings for creating resources
    and pushing in Stats and Properties.
    """

    def __init__(self, client_config, sample_config):
        super().__init__(client_config)

        with open(sample_config, "r") as f:
            data = json.load(f)

        self.resource_config = ResourceConfig(**data)
        self.stat_and_property_config = self.resource_config.statAndPropertyConfig
        self.number_of_stats_to_push = self.stat_and_property_config.numberOfStatAndPropertyToPush

        self.create_resource_client = Adapterkinds(self.ops_client.stub_config)
        self.maintain_client = Maintained(self.ops_client.stub_config)
        self.stat_client = Stats(self.ops_client.stub_config)
        self.properties_client = Properties(self.ops_client.stub_config)
        self.resources_client = Resources(self.ops_client.stub_config)

    def run(self):
        try:
            logger.info("Creating a Resource...")
            resource = self.create_resource()
            logger.info("Resource created successfully !!!")

            self.push_data(resource)

            logger.info("Sleep for 2 mins for data to get stored.")
            time.sleep(2 * 60)

            logger.info("Moving a resource to maintained state and ending the maintained state")
            self.move_resource_maintained_state(resource.identifier)

            logger.info("Deleting previously created resource")
            self.delete_resource(resource.identifier)
        except VapiError as vapi_error:
            raise vapi_error
        except Exception as ex:
            logger.error("Resources and stats management sample failed", ex)
            raise ex

    def push_data(self, resource):
        data = [0.0] * self.number_of_stats_to_push
        timestamps = [0] * self.number_of_stats_to_push
        values = [""] * self.number_of_stats_to_push
        
        current_time = int(datetime.now(timezone.utc).timestamp() * 1000)
        
        for i in range(self.number_of_stats_to_push):
            last_data_point = random.random() * 100
            data[i] = last_data_point
            timestamps[i] = current_time - ((i + 1) * 300000)  # 5 minutes intervals
            values[i] = "CONNECTED" if i % 2 == 0 else "DISCONNECTED"

        for i in range(self.number_of_stats_to_push):
            logger.info("Pushing Numeric Stats data...")
            self.add_stats(resource.identifier, self.stat_and_property_config.statKey, timestamps, data, None, False)

            logger.info("Pushing String Properties data...")
            self.add_properties(resource.identifier, self.stat_and_property_config.propertyKey, timestamps, None,
                                values)

    def create_resource(self):
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
            return self.create_resource_client.create_resource_using_adapter_kind(self.resource_config.pushAdapterKindKey,
                                                                                  resource)
        except VapiError as vapi_error:
            logger.error(f"Failed to create a resource: {vapi_error.get_error_value()}")
            raise vapi_error

    def add_stats(self, resource_uuid, stat_key, timestamps, data, values, store_only):
        """
        Push stat data for the specified Stat Keys

        :param resource_uuid: VMware Cloud Foundation Operations UUID of the Resource
        :param stat_key: Name of the Stat Key
        :param timestamps: Array of long values as timestamps
        :param data: Array of double values as data
        :param values: Array of string values
        :param store_only: true if we want to store the data only, false if we want
                    analytics processing to be performed
        """
        logger.info(f"Pushing some data for stat key: '{stat_key}' ...")
        contents = StatContents()
        content = StatContent()
        content.stat_key = stat_key
        content.data = data
        content.values = values
        content.timestamps = timestamps
        contents.stat_content = [content]
        try:
            self.stat_client.add_stats(resource_uuid, contents, True)
        except VapiError as vapi_error:
            logger.error(f"Failed to pushing stats: {vapi_error.get_error_value()}")
            raise vapi_error

    def add_properties(self, resource_uuid, property_key, timestamps, data, values):
        """
        Push property data for the specified Property Keys

        :param resource_uuid: VMware Cloud Foundation Operations UUID of the Resource
        :param property_key: Name of the Property Key
        :param timestamps: Array of long values as timestamps
        :param data: Array of double values as data
        :param values: Array of string values
        """
        logger.info(f"Pushing some data for property: '{property_key}' ...")
        contents = PropertyContents()
        content = PropertyContent()
        content.stat_key = property_key
        content.data = data
        content.values = values
        content.timestamps = timestamps
        contents.property_content = [content]
        try:
            self.properties_client.add_properties(resource_uuid, contents)
        except VapiError as vapi_error:
            logger.error(f"Failed to pushing properties: {vapi_error.get_error_value()}")
            raise vapi_error

    def move_resource_maintained_state(self, resource_id):
        duration = 1
        end_time = int(time.time() * 1000) + (5 * 60 * 1000)  # 5 minutes from now

        try:
            # will move the resource to maintained state for the 'duration' time period
            self.maintain_client.mark_resources_as_being_maintained([resource_id], duration, 0)

            # will move the resource to maintained state till the end time
            self.maintain_client.mark_resources_as_being_maintained([resource_id], 0, end_time)

            # will move the resource to maintained state till the end time (duration is not considered)
            self.maintain_client.mark_resources_as_being_maintained([resource_id], duration, end_time)

            # will move the resource to maintained_manual state until 'unmark_resources_as_being_maintained' method is
            # called
            self.maintain_client.mark_resources_as_being_maintained([resource_id], 0, 0)

            # will move the resource to back to started state
            self.maintain_client.unmark_resources_as_being_maintained([resource_id])
        except VapiError as vapi_error:
            logger.error(f"Failed to move resource maintained state: {vapi_error.get_error_value()}")
            raise vapi_error

    def delete_resource(self, resource_id):
        """Delete a resource"""
        try:
            self.resources_client.delete_resource(resource_id)
        except VapiError as vapi_error:
            logger.error(f"Failed to delete a resource: {vapi_error.get_error_value()}")
            raise vapi_error


if __name__ == "__main__":
    args = get_args()
    
    resource_and_stats = ResourcesAndStats(args.client_config, args.sample_config)
    resource_and_stats.run()
