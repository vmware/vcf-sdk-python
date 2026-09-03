#!/usr/bin/env python

# Copyright (c) 2023-2026 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

"""
Example demonstrating log forwarder management operations.
Shows how to create, configure, update, and manage log forwarders.
"""

import json
import logging
import sys
from log_management.helpers.client import ApiClientUtil
from log_management.helpers.arg_parser import get_args
from log_management.helpers.client_config import ClientConfig
from vcf.log_mgmt import model_client
from vcf.log_mgmt.api.v2 import logs_client

__author__ = 'Broadcom, Inc.'
__docformat__ = 'restructuredtext en'

logger = logging.getLogger(__name__)


class LogForwarderExample:
    """Example class demonstrating log forwarder management operations."""

    def __init__(self, client_config):
        """Initialize the log forwarder example."""
        with open(client_config, "r") as f:
            data = json.load(f)
        self.client_config = ClientConfig(**data)
        self.client_util = None
        self.forwarders_service = None

    def initialize(self):
        """Initialize the client and forwarders service."""
        logger.info("Initializing log forwarder example...")
        self.client_util = ApiClientUtil()

        self.client_util.initialize_client(self.client_config.opsHost, self.client_config.username,
                                           self.client_config.password, self.client_config.logsHost,
                                           self.client_config.logsPort)
        self.forwarders_service = logs_client.Forwarders(self.client_util.get_stub_config())
        logger.info("Forwarders service initialized successfully")

    def run_all_forwarder_examples(self):
        """Run all log forwarder examples."""
        try:
            # Basic forwarder operations
            forwarder_id = self.create_syslog_forwarder()
            self.get_all_forwarders()

            if forwarder_id:
                self.get_forwarder_by_id(forwarder_id)
                self.update_forwarder(forwarder_id)
                self.delete_forwarder(forwarder_id)

        except Exception as e:
            logger.error(f"Error running forwarder examples")
            raise

    def get_all_forwarders(self):
        """Example 1: Retrieve all log forwarders."""
        logger.info("=== Get All Log Forwarders Example ===")

        try:
            # Execute the request
            forwarders = self.forwarders_service.get_all_log_forwarders()

            logger.info(f"Retrieved {len(forwarders) if forwarders else 0} log forwarders")

            # Display forwarder information
            if forwarders:
                for forwarder in forwarders:
                    logger.info(f"Forwarder ID: {forwarder.id}")
                    logger.info(f"Forwarder Name: {forwarder.name}")
                    logger.info(f"Host: {forwarder.host}:{forwarder.port}")
                    logger.info(f"Protocol: {forwarder.protocol}")
                    logger.info(f"Transport: {forwarder.transport_protocol}")
                    logger.info(f"SSL Enabled: {forwarder.ssl_enabled}")
                    logger.info(f"Enabled: {forwarder.enabled}")
                    logger.info("---")

        except Exception as e:
            logger.error(f"Failed to retrieve all forwarders: {e}")
            raise

    def create_syslog_forwarder(self):
        """Example 2: Create a new forwarder."""
        logger.info("=== Create Forwarder Example ===")

        try:
            # Create a new syslog forwarder
            new_forwarder = model_client.LogForwarder()
            new_forwarder.name = "Log Forwarder"
            new_forwarder.host = "syslog.example.com"
            new_forwarder.port = 514
            new_forwarder.protocol = "SYSLOG"
            new_forwarder.transport_protocol = "TCP"
            new_forwarder.ssl_enabled = False
            new_forwarder.enabled = True
            new_forwarder.worker_count = 2
            new_forwarder.connection_refresh_interval = 300  # 5 minutes
            new_forwarder.forward_complementary_fields = True

            # Add tags
            tags = {
                "environment": "production",
                "team": "infrastructure",
                "purpose": "log-aggregation"
            }
            new_forwarder.tags = tags

            # Execute the creation request
            created_forwarder = self.forwarders_service.create_log_forwarder(new_forwarder)

            logger.info("Successfully created log forwarder:")
            logger.info(f"Forwarder ID: {created_forwarder.id}")
            logger.info(f"Forwarder Name: {created_forwarder.name}")
            logger.info(f"Host: {created_forwarder.host}:{created_forwarder.port}")
            logger.info(f"Protocol: {created_forwarder.protocol}")

            return created_forwarder.id

        except Exception as e:
            logger.error(f"Failed to create syslog forwarder: {e}")
            raise

    def get_forwarder_by_id(self, forwarder_id):
        """Example 3: Retrieve a specific forwarder by ID."""
        logger.info("=== Get Forwarder By ID Example ===")

        try:
            # Execute the request
            forwarder = self.forwarders_service.get_log_forwarder_by_id(forwarder_id)

            logger.info("Retrieved log forwarder:")
            logger.info(f"Forwarder ID: {forwarder.id}")
            logger.info(f"Name: {forwarder.name}")
            logger.info(f"Host: {forwarder.host}")
            logger.info(f"Port: {forwarder.port}")
            logger.info(f"Protocol: {forwarder.protocol}")
            logger.info(f"Transport Protocol: {forwarder.transport_protocol}")
            logger.info(f"SSL Enabled: {forwarder.ssl_enabled}")
            logger.info(f"Enabled: {forwarder.enabled}")
            logger.info(f"Worker Count: {forwarder.worker_count}")
            logger.info(f"Connection Refresh Interval: {forwarder.connection_refresh_interval}")
            logger.info(f"Forward Complementary Fields: {forwarder.forward_complementary_fields}")
            logger.info(f"Tags: {forwarder.tags}")

        except Exception as e:
            logger.error(f"Failed to retrieve forwarder by ID: {e}")
            raise

    def update_forwarder(self, forwarder_id):
        """Example 4: Update an existing forwarder."""
        logger.info("=== Update Forwarder Example ===")

        try:
            # First, get the existing forwarder
            existing_forwarder = self.forwarders_service.get_log_forwarder_by_id(forwarder_id)

            # Create update request based on existing forwarder
            update_request = model_client.LogForwarder()
            update_request.name = existing_forwarder.name
            update_request.host = existing_forwarder.host + " - Updated"
            update_request.port = existing_forwarder.port
            update_request.protocol = existing_forwarder.protocol
            update_request.transport_protocol = existing_forwarder.transport_protocol
            update_request.ssl_enabled = existing_forwarder.ssl_enabled
            update_request.enabled = existing_forwarder.enabled
            update_request.worker_count = existing_forwarder.worker_count + 1  # Increase worker count
            update_request.connection_refresh_interval = existing_forwarder.connection_refresh_interval
            update_request.forward_complementary_fields = existing_forwarder.forward_complementary_fields

            # Update tags
            updated_tags = dict(existing_forwarder.tags) if existing_forwarder.tags else {}
            updated_tags["updated"] = "true"
            updated_tags["update-time"] = str(sys.maxsize)
            update_request.tags = updated_tags

            # Execute the update request
            updated_forwarder = self.forwarders_service.update_log_forwarder(forwarder_id, update_request)

            logger.info("Successfully updated log forwarder:")
            logger.info(f"Forwarder ID: {updated_forwarder.id}")
            logger.info(f"Updated Name: {updated_forwarder.name}")
            logger.info(f"Updated Host: {updated_forwarder.host}")
            logger.info(f"Updated Worker Count: {updated_forwarder.worker_count}")
            logger.info(f"Updated Tags: {updated_forwarder.tags}")

        except Exception as e:
            logger.error(f"Failed to update forwarder: {e}")
            raise

    def delete_forwarder(self, forwarder_id):
        """Example 5: Delete a forwarder."""
        logger.info("=== Delete Forwarder Example ===")

        try:
            # Execute the delete request
            self.forwarders_service.delete_log_forwarder(forwarder_id)

            logger.info(f"Successfully deleted log forwarder with ID: {forwarder_id}")

            # Verify deletion by trying to retrieve the forwarder
            try:
                forwarder = self.forwarders_service.get_log_forwarder_by_id(forwarder_id)

                if forwarder is None:
                    logger.info("Confirmed: Forwarder has been deleted")
                else:
                    logger.warning("Forwarder still exists after deletion attempt")
            except Exception as verify_exception:
                # Expected if forwarder is truly deleted
                logger.info("Confirmed: Forwarder not found (expected after deletion)")

        except Exception as e:
            logger.error(f"Failed to delete forwarder: {e}")
            raise

    def cleanup(self):
        """Clean up resources."""
        if self.client_util:
            self.client_util.cleanup()


def main():
    """Main entry point for standalone execution."""
    args = get_args()
    example = LogForwarderExample(args.client_config)
    try:
        example.initialize()
        example.run_all_forwarder_examples()
    except Exception as e:
        logger.error(f"Log forwarder example failed: {e}")
        sys.exit(1)
    finally:
        example.cleanup()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    main()
