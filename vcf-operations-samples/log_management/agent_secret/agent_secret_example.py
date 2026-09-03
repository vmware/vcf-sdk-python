#!/usr/bin/env python

# Copyright (c) 2023-2026 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

"""
Example demonstrating agent secret management operations.
Shows how to create and exchange agent secrets for secure agent authentication.
"""

import json
import logging
import sys

from log_management.helpers.client import ApiClientUtil
from log_management.helpers.arg_parser import get_args
from log_management.helpers.client_config import ClientConfig
from vcf.log_mgmt import model_client
from vcf.log_mgmt.api.v2 import agent_client
from vcf.log_mgmt.api.v2.agent import secrets_client

__author__ = 'Broadcom, Inc.'
__docformat__ = 'restructuredtext en'

logger = logging.getLogger(__name__)


class AgentSecretExample:
    """Example class demonstrating agent secret management operations."""

    def __init__(self, client_config):
        """Initialize the agent secret example."""
        with open(client_config, "r") as f:
            data = json.load(f)
        self.client_config = ClientConfig(**data)
        self.client_util = None
        self.agent_secrets_service = None
        self.agent_secrets_exchange_service = None
        self.agent_secrets_revoke_service = None

    def initialize(self):
        """Initialize the client and agent secrets service."""
        logger.info("Initializing example...")
        self.client_util = ApiClientUtil()

        self.client_util.initialize_client(self.client_config.opsHost, self.client_config.username,
                                           self.client_config.password, self.client_config.logsHost,
                                           self.client_config.logsPort)

        self.agent_secrets_service = agent_client.Secrets(self.client_util.get_stub_config())
        self.agent_secrets_exchange_service = secrets_client.Exchange(self.client_util.get_stub_config())
        self.agent_secrets_revoke_service = secrets_client.Revoke(self.client_util.get_stub_config())

        logger.info("Agent secrets service initialized successfully")

    def run_all_agent_secret_examples(self):
        """Run all agent secret examples."""
        try:
            # Basic agent secret operations
            self.create_secret()
            self.exchange_secrets()
            self.revoke_secret()

        except Exception as e:
            logger.error(f"Error running agent secret examples")
            raise

    def create_secret(self):
        """Create a new agent secret."""
        logger.info("=== Create Secret Example ===")

        try:
            # Create agent secret request
            create_request = model_client.AgentSecretCreateRequest(
                # When the secret name is not set, it will be generated
                # name="Agent_Secret"
            )

            # Execute the request
            sec = self.agent_secrets_service.create_agent_secret(create_request)

            logger.info("Successfully acquired agent secret:")
            logger.info(f"Name: {sec.name}")
            logger.info(f"Secret: {sec.secret}")
            
            self.secret = sec.secret
            self.secretName = sec.name

        except Exception as e:
            logger.error(f"Failed to acquire secret: {e}")
            raise

    def exchange_secrets(self):
        """Exchange agent secret for authentication."""
        logger.info("=== Exchange Secret Example ===")

        try:
            # Create authentication request
            auth_request = model_client.AgentAuthenticationRequest(
                secret=self.secret
            )

            # Execute the request
            auth = self.agent_secrets_exchange_service.create_agent_session(auth_request)

            logger.info("Successfully exchanged agent secret:")
            logger.info(f"Name: {auth.name}")
            logger.info(f"New Secret: {auth.new_secret}")

        except Exception as e:
            logger.error(f"Failed to exchange secret: {e}")
            raise

    def revoke_secret(self):
        """Revoke agent secret."""
        logger.info("=== Delete Secret Example ===")

        try:

            # Execute the request
            sec = self.agent_secrets_revoke_service.revoke_agent_secret(self.secretName)

            logger.info("Successfully revoked agent secret:")
            logger.info(f"Name: {sec.name}")

        except Exception as e:
            logger.error(f"Failed to acquire secret: {e}")
            raise

    def cleanup(self):
        """Clean up resources."""
        if self.client_util:
            self.client_util.cleanup()


def main():
    """Main entry point for standalone execution."""
    args = get_args()
    example = AgentSecretExample(args.client_config)
    try:
        example.initialize()
        example.run_all_agent_secret_examples()
    except Exception as e:
        logger.error(f"Agent secret example failed: {e}")
        sys.exit(1)
    finally:
        example.cleanup()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    main()
