#!/usr/bin/env python

# Copyright (c) 2023-2026 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

"""
Advanced example demonstrating complex search operations and aggregations.
Shows sophisticated querying patterns, nested aggregations, and result analysis.
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


class AdvancedSearchExample:
    """Example class demonstrating advanced search operations and aggregations."""

    def __init__(self, client_config):
        """Initialize the advanced search example."""
        with open(client_config, "r") as f:
            data = json.load(f)
        self.client_config = ClientConfig(**data)
        self.client_util = None
        self.search_service = None

    def initialize(self):
        """Initialize the client and search services."""
        logger.info("Initializing advanced search example...")
        self.client_util = ApiClientUtil()

        self.client_util.initialize_client(self.client_config.opsHost, self.client_config.username,
                                           self.client_config.password, self.client_config.logsHost,
                                           self.client_config.logsPort)
        self.search_service = v2_client.Search(self.client_util.get_stub_config())
        logger.info("Search services initialized successfully")

    def run_all_advanced_search_examples(self):
        """Run all advanced search examples."""
        try:
            # Complex query examples
            self.perform_complex_boolean_query()

        except Exception as e:
            logger.error(f"Error running advanced search examples")
            raise

    def perform_complex_boolean_query(self):
        """Example 1: Complex boolean query with multiple conditions."""
        logger.info("=== Complex Boolean Query Example ===")

        try:
            # Build a complex boolean query
            # Should conditions (OR logic)
            should_queries = []

            # Error level query
            query_match_phrase1 = model_client.QueryMatchPhrase()
            query_match_phrase1._set_extra_fields({"level": "ERROR"})

            error_query = model_client.Query()
            error_query.match_phrase = query_match_phrase1
            should_queries.append(error_query)

            # Warning level query
            query_match_phrase2 = model_client.QueryMatchPhrase()
            query_match_phrase2._set_extra_fields({"level": "WARN"})

            warn_query = model_client.Query()
            warn_query.match_phrase = query_match_phrase2
            should_queries.append(warn_query)

            # Combine into boolean query
            bool_query = model_client.BoolQuery()
            bool_query.should = should_queries

            main_query = model_client.Query()
            main_query.bool = bool_query

            # Add aggregations for analysis
            aggregations = {}

            # Terms aggregation for log levels
            level_agg = model_client.MultiTermsAggregation()
            level_agg.terms = [model_client.MultiTermLookup(field="level")]
            level_agg.size = 10

            agg = model_client.Aggregation()
            agg.multi_terms = level_agg
            aggregations["log_levels"] = agg

            # Build the search request
            request = model_client.QueryRequest(
                query=main_query,
                size=50,
                aggregations=aggregations,
                track_total_hits=True
            )

            # Execute the search
            response = self.search_service.execute_log_search_query(request)

            logger.info("Complex boolean query executed successfully")
            total_hits = len(response.events.hits) if response and response.events and response.events.hits else 0
            logger.info(f"Total hits: {total_hits}")

            if response and response.aggregations:
                logger.info(f"Result: {response.aggregations}")

        except Exception as e:
            logger.error(f"Complex boolean query failed: {e}")
            raise

    def cleanup(self):
        """Clean up resources."""
        if self.client_util:
            self.client_util.cleanup()


def main():
    """Main entry point for standalone execution."""
    args = get_args()
    example = AdvancedSearchExample(args.client_config)
    try:
        example.initialize()
        example.run_all_advanced_search_examples()
    except Exception as e:
        logger.error(f"Advanced search example failed: {e}")
        sys.exit(1)
    finally:
        example.cleanup()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    main()
