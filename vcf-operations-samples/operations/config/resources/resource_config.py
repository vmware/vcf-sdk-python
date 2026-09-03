# Copyright (c) 2025-2026 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

class StatAndPropertyConfig:
    def __init__(self, statKey=None, propertyKey=None, numberOfStatAndPropertyToPush=None):
        """
        Configuration for stats and properties
        
        :param statKey: Stat key name
        :param propertyKey: Property key name
        :param numberOfStatAndPropertyToPush: Number of stats/properties to push
        """

        missing = []
        if not statKey:
            missing.append("statKey")
        if not propertyKey:
            missing.append("propertyKey")

        if missing:
            raise ValueError(f"Invalid configuration for StatAndPropertyConfig: missing {', '.join(missing)}")

        self.statKey = statKey
        self.propertyKey = propertyKey
        self.numberOfStatAndPropertyToPush = numberOfStatAndPropertyToPush or 5


class ResourceConfig:
    def __init__(self, name="FooBar", description="Description", adapterKindKey=None,
                 resourceKindKey=None, identifiers=None, statAndPropertyConfig=None,
                 pushAdapterKindKey="SOME-PUSH-ADAPTER-KEY"):
        """
        Configuration for resource management examples
        
        :param name: Resource name
        :param description: Resource description
        :param adapterKindKey: Adapter kind key
        :param resourceKindKey: Resource kind key
        :param identifiers: Dictionary of resource identifiers
        :param statAndPropertyConfig: StatAndPropertyConfig object
        :param pushAdapterKindKey: Push adapter kind key
        """

        missing = []
        if not adapterKindKey:
            missing.append("adapterKindKey")
        if not resourceKindKey:
            missing.append("resourceKindKey")
        if not identifiers:
            missing.append("identifiers")

        if missing:
            raise ValueError(f"Invalid configuration for {self.__class__.__name__}: missing {', '.join(missing)}")

        self.name = name
        self.description = description
        self.adapterKindKey = adapterKindKey
        self.resourceKindKey = resourceKindKey
        self.identifiers = identifiers or {}
        self.pushAdapterKindKey = pushAdapterKindKey

        if statAndPropertyConfig is not None:
            self.statAndPropertyConfig = StatAndPropertyConfig(**statAndPropertyConfig)
        else:
            self.statAndPropertyConfig = None
