#!/usr/bin/env python

# Copyright (c) 2008-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

"""
Python program to authenticate and print
a friendly encouragement to joining the community!
"""

from pyVmomi import vmodl
from helpers import cli, service_instance


def main():
    """
    Simple command-line program for listing the virtual machines on a system.
    """

    parser = cli.Parser()
    args = parser.get_args()
    si = service_instance.connect(args)

    try:
        print("\nHello World!\n")
        print("If you got here, you authenticted into vCenter.")
        print("The server is {}!".format(args.host))
        # NOTE (hartsock): only a successfully authenticated session has a
        # session key aka session id.
        session_id = si.content.sessionManager.currentSession.key
        print("current session id: {}".format(session_id))
        print("Well done!")
        print("\n")
        print("Download, learn and contribute back:")
        print("https://github.com/vmware/pyvmomi-community-samples")
        print("\n\n")

    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return -1

    return 0


# Start program
if __name__ == "__main__":
    main()
