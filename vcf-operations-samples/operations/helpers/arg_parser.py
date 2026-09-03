# Copyright (c) 2025-2026 Broadcom Inc. and/or its subsidiaries. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import argparse


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--client_config", action="store", required=True, help="Server configuration json file")
    parser.add_argument("--sample_config", action="store", required=True, help="Sample specific json file")

    return parser.parse_args()
