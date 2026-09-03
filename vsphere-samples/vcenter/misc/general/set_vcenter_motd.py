#!/usr/bin/env python

# Copyright (c) 2016-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

"""
William Lam
wwww.virtuallyghetto.com
"""

import requests
from helpers import cli, service_instance
# Snippet borrowed from Michael Rice
# https://gist.github.com/michaelrice/a6794a017e349fc65d01
requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning)


# Demonstrates configuring the Message of the Day (MOTD) on vCenter Server

# Example output:
# > logged in to vcsa
# > Setting vCenter Server MOTD to "Hello from virtuallyGhetto"
# > logout

parser = cli.Parser()
parser.add_required_arguments(cli.Argument.MESSAGE)
args = parser.get_args()
si = service_instance.connect(args)

print("logged in to %s" % args.host)

print("Setting vCenter Server MOTD to \"%s\"" % args.message)
si.content.sessionManager.UpdateServiceMessage(message=args.message)

print("logout")
si.content.sessionManager.Logout()
