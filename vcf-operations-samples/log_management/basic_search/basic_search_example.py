#!/usr/bin/env python

# Copyright (c) 2023-2026 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

"""
Comprehensive example demonstrating various search operations using the vRLI API.
Shows basic queries, filtering, sorting, and result handling.
"""

import json
import logging
import sys
from log_management.helpers.client import ApiClientUtil
from log_management.helpers.arg_parser import get_args
from log_management.helpers.client_config import ClientConfig
from vcf.log_mgmt import model_client
from vcf.log_mgmt.api import v2_client

__author__ = 'Broadcom, Inc.'
__docformat__ = 'restructuredtext en'

logger = logging.getLogger(__name__)


class BasicSearchExample:
    """Example class demonstrating basic search operations."""

    def __init__(self, client_config):
        """Initialize the basic search example."""
        with open(client_config, "r") as f:
            data = json.load(f)
        self.client_config = ClientConfig(**data)
        self.client_util = None
        self.search_service = None

    def initialize(self):
        """Initialize the client and search service."""
        logger.info("Initializing search example...")
        self.client_util = ApiClientUtil()

        self.client_util.initialize_client(self.client_config.opsHost, self.client_config.username,
                                           self.client_config.password, self.client_config.logsHost,
                                           self.client_config.logsPort)
        self.search_service = v2_client.Search(self.client_util.get_stub_config())
        logger.info("Search service initialized successfully")

    def run_all_search_examples(self):
        """Run all search examples."""
        try:
            # Basic search examples
            self.perform_match_all_query()
            self.perform_exists_query()
            #
            self.perform_boolean_query()

        except Exception as e:
            logger.error(f"Error running search examples")
            raise

    def perform_match_all_query(self):
        """Example 1: Simple match-all query to retrieve all logs."""
        logger.info("=== Match All Query Example ===")

        try:
            # Create a match-all query
            match_all_query = model_client.MatchAllQuery()

            query = model_client.Query()
            query.match_all = match_all_query

            # Build the search request
            request = model_client.QueryRequest(
                query=query,
                size=10,  # Limit to 10 results
                from_=0   # Start from first result
            )

            # Execute the search
            response = self.search_service.execute_log_search_query(request)

            logger.info("Match-all query executed successfully")
            total_hits = len(response.events.hits) if response and response.events and response.events.hits else 0
            logger.info(f"Total hits: {total_hits}")

            # Process results
            if response and response.events and response.events.hits:
                for hit in response.events.hits:
                    logger.info(f"Log entry: {hit}")

        except Exception as e:
            logger.error(f"Match-all query failed: {e}")
            raise

    def perform_exists_query(self):
        """Example 2: Exists query to find logs with a specific field."""
        logger.info("=== Exists Query Example ===")

        try:
            # Create an exists query
            exists_query = model_client.ExistsQuery()
            exists_query.field = "field1"

            query = model_client.Query()
            query.exists = exists_query

            # Build the search request
            request = model_client.QueryRequest(
                query=query,
                size=10,  # Limit to 10 results
                from_=0   # Start from first result
            )

            # Execute the search
            response = self.search_service.execute_log_search_query(request)

            logger.info("Exists query executed successfully")
            total_hits = len(response.events.hits) if response and response.events and response.events.hits else 0
            logger.info(f"Total hits: {total_hits}")

            # Process results
            if response and response.events and response.events.hits:
                for hit in response.events.hits:
                    logger.info(f"Log entry: {hit}")

        except Exception as e:
            logger.error(f"Exists query failed: {e}")
            raise

    def perform_boolean_query(self):
        """Example 3: Boolean query combining multiple conditions."""
        logger.info("=== Boolean Query Example ===")

        try:
            # Create a regexp query for the must condition
            must_query = model_client.QueryRegexp()
            must_query._set_extra_fields({"message": ".*error.*"})

            m_query = model_client.Query()
            m_query.regexp = must_query

            # Combine into boolean query
            bool_query = model_client.BoolQuery()
            bool_query.must = [m_query]

            query = model_client.Query()
            query.bool = bool_query

            # Build the search request
            request = model_client.QueryRequest(
                query=query,
                size=10,  # Limit to 10 results
                from_=0   # Start from first result
            )

            # Execute the search
            response = self.search_service.execute_log_search_query(request)

            logger.info("Boolean query executed successfully")
            total_hits = len(response.events.hits) if response and response.events and response.events.hits else 0
            logger.info(f"Found logs matching boolean conditions: {total_hits}")

        except Exception as e:
            logger.error(f"Boolean query failed: {e}")
            raise

    def cleanup(self):
        """Clean up resources."""
        if self.client_util:
            self.client_util.cleanup()


def main():
    """Main entry point for standalone execution."""
    args = get_args()
    example = BasicSearchExample(args.client_config)
    try:
        example.initialize()
        example.run_all_search_examples()
    except Exception as e:
        logger.error(f"Search example failed: {e}")
        sys.exit(1)
    finally:
        example.cleanup()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    main()
