This directory contains samples for cluster APIs:

Running the samples to add cluster to the domain

    $ python add_cluster.py --server <SDDC_MANAGER Server IP> --user <username> --password <password>

* Testbed Requirement:
   - at least 3 unassigned hosts
   - 1 existing domain 
   - add_cluster.json : sample parses this file for generating input payload
  

Running the samples to add host to the cluster

    $ python add_host_to_cluster.py --server <SDDC_MANAGER Server IP> --username <username> --password <password>

* Testbed Requirement:
   - at least 1 unassigned hosts
   - 1 existing domain 
   - add_host_to_cluster.json : sample parses this file for generating input payload

