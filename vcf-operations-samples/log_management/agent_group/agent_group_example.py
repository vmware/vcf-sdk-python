#!/usr/bin/env python

# Copyright (c) 2023-2026 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

"""
Example demonstrating agent group management operations.
Shows how to create, configure, update, and manage agent groups for log collection.
"""

import json
import logging
import sys

from log_management.helpers.client import ApiClientUtil
from log_management.helpers.arg_parser import get_args
from log_management.helpers.client_config import ClientConfig
from vcf.log_mgmt import model_client
from vcf.log_mgmt.api.v2 import agent_client

__author__ = 'Broadcom, Inc.'
__docformat__ = 'restructuredtext en'

logger = logging.getLogger(__name__)


class AgentGroupExample:
    """Example class demonstrating agent group management operations."""

    def __init__(self, client_config):
        """Initialize the agent group example."""
        with open(client_config, "r") as f:
            data = json.load(f)
        self.client_config = ClientConfig(**data)
        self.client_util = None
        self.agent_groups_service = None

    def initialize(self):
        """Initialize the client and agent groups service."""
        logger.info("Initializing agent group example...")
        self.client_util = ApiClientUtil()

        self.client_util.initialize_client(self.client_config.opsHost, self.client_config.username,
                                           self.client_config.password, self.client_config.logsHost,
                                           self.client_config.logsPort)
        self.agent_groups_service = agent_client.Groups(self.client_util.get_stub_config())
        logger.info("Agent groups service initialized successfully")

    def run_all_agent_group_examples(self):
        """Run all agent group examples."""
        try:
            # Basic agent group operations
            group_id = self.create_agent_group()

            if group_id:
                self.get_agent_group_by_id(group_id)
                self.update_agent_group(group_id)
                self.patch_agent_group(group_id)
                self.delete_agent_group(group_id)

        except Exception as e:
            logger.error(f"Error running agent group examples")
            raise

    def create_agent_group(self):
        """Example 1: Create a basic agent group."""
        logger.info("=== Create Agent Group Example ===")

        try:
            # Create sample constraint
            sample_constraint = model_client.Query()
            sample_constraint.bool = model_client.BoolQuery()

            # Create agent group request
            new_group = model_client.AgentGroupRequest(
                name="Agent group",
                info="Agent group info",
                auto_update=True,
                constraints=sample_constraint,
                agent_config="[server]\n max_disk_buffer=100\n",
                mp_id="web-server-mp-001"
            )

            # Execute the creation request
            created_group = self.agent_groups_service.create_agent_group_config(new_group)

            logger.info("Successfully created agent group:")
            logger.info(f"Group ID: {created_group.id}")
            logger.info(f"Group Name: {created_group.name}")
            logger.info(f"Auto Update: {created_group.auto_update}")

            return created_group.id

        except Exception as e:
            logger.error(f"Failed to create agent group: {e}")
            raise

    def get_agent_group_by_id(self, group_id):
        """Example 2: Retrieve a specific agent group by ID."""
        logger.info("=== Get Agent Group By ID Example ===")

        try:
            # Execute the request
            group = self.agent_groups_service.get_agent_group_config_by_id(group_id)

            logger.info("Retrieved agent group:")
            logger.info(f"Group ID: {group.id}")
            logger.info(f"Name: {group.name}")
            logger.info(f"Info: {group.info}")
            logger.info(f"Auto Update: {group.auto_update}")
            logger.info(f"MP ID: {group.mp_id}")
            logger.info(f"Agent Config: {'Present' if group.agent_config else 'Not set'}")
            logger.info(f"Constraints: {group.constraints if group.constraints else 'None'}")

        except Exception as e:
            logger.error(f"Failed to retrieve agent group by ID: {e}")
            raise

    def update_agent_group(self, group_id):
        """Example 3: Update an existing agent group (full update)."""
        logger.info("=== Update Agent Group Example ===")

        try:
            # First, get the existing group
            existing_group = self.agent_groups_service.get_agent_group_config_by_id(group_id)

            # Create sample constraint
            sample_constraint = model_client.Query()
            sample_constraint.bool = model_client.BoolQuery()

            # Create update request
            update_request = model_client.AgentGroupRequest(
                name="Updated agent group",
                info="Updated agent group info",
                auto_update=True,
                constraints=sample_constraint,
                agent_config="[server]\n max_disk_buffer=100\n",
                mp_id=existing_group.mp_id
            )

            # Execute the update request
            updated_group = self.agent_groups_service.update_agent_group_config(group_id, update_request)

            logger.info("Successfully updated agent group:")
            logger.info(f"Group ID: {updated_group.id}")
            logger.info(f"Updated Name: {updated_group.name}")
            logger.info(f"Updated Info: {updated_group.info}")

        except Exception as e:
            logger.error(f"Failed to update agent group: {e}")
            raise

    def patch_agent_group(self, group_id):
        """Example 4: Patch an existing agent group (partial update)."""
        logger.info("=== Patch Agent Group Example ===")

        try:
            # Create a partial update request
            patch_request = model_client.AgentGroupPatchRequest()
            patch_request.info = "Patched info - optimized for high-performance logging"
            patch_request.auto_update = False  # Disable auto-update temporarily

            # Execute the patch request
            patched_group = self.agent_groups_service.patch_update_agent_group_config(group_id, patch_request)

            logger.info("Successfully patched agent group:")
            logger.info(f"Group ID: {patched_group.id}")
            logger.info(f"Name: {patched_group.name}")
            logger.info(f"Patched Info: {patched_group.info}")
            logger.info(f"Auto Update: {patched_group.auto_update}")

        except Exception as e:
            logger.error(f"Failed to patch agent group: {e}")
            raise

    def delete_agent_group(self, group_id):
        """Example 5: Delete an agent group."""
        logger.info("=== Delete Agent Group Example ===")

        try:
            # Execute the delete request
            self.agent_groups_service.delete_agent_group_config(group_id)

            logger.info(f"Successfully deleted agent group with ID: {group_id}")

            # Verify deletion by trying to retrieve the group
            try:
                group = self.agent_groups_service.get_config(group_id)

                if group is None:
                    logger.info("Confirmed: Agent group has been deleted")
                else:
                    logger.warning("Agent group still exists after deletion attempt")
            except Exception as verify_exception:
                # Expected if group is truly deleted
                logger.info("Confirmed: Agent group not found (expected after deletion)")

        except Exception as e:
            logger.error(f"Failed to delete agent group: {e}")
            raise

    def cleanup(self):
        """Clean up resources."""
        if self.client_util:
            self.client_util.cleanup()


def main():
    """Main entry point for standalone execution."""
    args = get_args()
    example = AgentGroupExample(args.client_config)
    try:
        example.initialize()
        example.run_all_agent_group_examples()
    except Exception as e:
        logger.error(f"Agent group example failed: {e}")
        sys.exit(1)
    finally:
        example.cleanup()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    main()
