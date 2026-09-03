#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import os
import socket
import ssl
import hashlib

from utils.misc_util import parse_bool_or_str


def get_ssl_cert_thumbprint(fqdn, ca_certs=True):
    """
    Obtain an arbitrary server's SSL certificate thumbprint
    :param fqdn: resolvable host name
    :param ca_certs: By default uses built-in CA.
        To pass custom CA provide absolute path to the file/folder
        containing CA certs to use for SSL verifications.
        Pass False to disable SSL verifications (NOT RECOMMENDED)
    :return: sha-256 thumbprint in 00:00:... format
    """
    ca_certs = parse_bool_or_str(ca_certs)
    if not ca_certs:
        # obtain cert without any verification
        pem = ssl.get_server_certificate((fqdn, 443))
    else:
        pem = _get_valid_server_cert((fqdn, 443), ca_certs)

    der = ssl.PEM_cert_to_DER_cert(pem)
    sha = hashlib.sha256(der)
    return ":".join(["{:02X}".format(b) for b in sha.digest()])


def _get_valid_server_cert(addr, ca_certs):
    context = ssl.create_default_context()  # use default CA

    if isinstance(ca_certs, str):
        if os.path.isdir(ca_certs):
            # use CA certs dir
            context = ssl.create_default_context(capath=ca_certs)
        else:
            # use CA certs file
            context = ssl.create_default_context(cafile=ca_certs)

    host, port = addr
    with socket.create_connection(addr) as sock:
        with context.wrap_socket(sock, server_hostname=host) as ssock:
            ssock.do_handshake()
            return ssock.getpeercert()
