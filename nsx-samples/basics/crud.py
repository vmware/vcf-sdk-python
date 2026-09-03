#!/usr/bin/env python

# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

import argparse

from vcf.nsx.model_client import TransportZone
from vmware.vapi.bindings.struct import PrettyPrinter
from utils.client import create_nsx_client

"""
This example shows basic CRUD (create, read, update, delete) operations.
Using one of the simplest NSX resource types, a Transport Zone, we will
show how create, read, update, and delete operations are performed.

Sample prerequisites: NSX Manager instance.

APIs used:

List transport zones:
GET /api/v1/transport-zones

Create a transport zone:
POST /api/v1/transport-zones

Read a transport zone:
POST /api/v1/transport-zones/<zone-id>

Update a transport zone:
PUT /api/v1/transport-zones/<zone-id>

Delete a transport zone:
DELETE /api/v1/transport-zones/<zone-id>
"""

parser = argparse.ArgumentParser()

parser.add_argument("--server", required=True, help="NSX Host Name")

parser.add_argument("--username", required=True, help="NSX username")

parser.add_argument("--password", required=True, help="NSX password")

args = parser.parse_args()
server = args.server
username = args.username
password = args.password

pp = PrettyPrinter()

nsx_client = create_nsx_client(server, username, password)
transportZones = nsx_client.TransportZones

list_result = transportZones.list_transport_zones()
print(f"Initial list of transport zones - {list_result.result_count} zones")

transportZone = TransportZone(
    transport_type=TransportZone.TRANSPORT_TYPE_TRANSPORT_TYPE_OVERLAY,
    display_name="My Transport Zone",
    description="Transport zone for basic create/read/update/delete demo",
)
create_result = transportZones.create_transport_zone(transportZone)
print(f"Transport zone created. id is {create_result.id}")

transport_zone_id = create_result.id

read_result = transportZones.get_transport_zone(transport_zone_id)
print("Re-read the transport zone")
pp.pprint(read_result)

list_result = transportZones.list_transport_zones()
print(f"Updated list of transport zones - {list_result.result_count} zones")

read_result.description = "Updated description for transport zone"
update_result = transportZones.update_transport_zone(transport_zone_id, read_result)
print("After updating description")
pp.pprint(update_result)

# Update the transport zone again.
#
# Note that NSX insists that clients always operate on up-to-date
# data. To enforce this, every resource in NSX has a "revision"
# property that is automatically maintained by NSX and is
# incremented each time the resource is updated. If a client
# submits an update operation, and the revision property in the
# payload provided by the client does not match the revision
# stored on the server, another update must have happened since
# the client last read the resource, and the client's copy is
# therefore stale.  In this case, the server will return a 412
# Precondition Failed error. This is intended to prevent clients
# from clobbering each other's updates. To recover from this
# error, the client must re-read the resource, apply any desired
# updates, and perform another update operation.
update_result.description = "Updated description again for transport zone"
update_result = transportZones.update_transport_zone(transport_zone_id, update_result)
print("After updating description again")
pp.pprint(update_result)

transportZones.delete_transport_zone(transport_zone_id)
print("Transport zone deleted.")
