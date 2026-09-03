# Copyright (c) 2025-2026 Broadcom Inc. and/or its subsidiaries. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

class SymptomDefinitionConfig:
    def __init__(self, name="Symptom-Definition-1", adapterKindKey="VMWARE", resourceKindKey="VirtualMachine",
                 waitCycle=5, cancelCycle=5, severity="CRITICAL", key="cpu|demandmhz",
                 operator="GT_EQ", value="95", instance=False):
        """
        Configuration for symptom definition
        
        :param name: Symptom name
        :param adapterKindKey: Adapter kind key
        :param resourceKindKey: Resource kind key
        :param waitCycle: Wait cycles
        :param cancelCycle: Cancel cycles
        :param severity: Severity level
        :param key: Condition key
        :param operator: Operator
        :param value: Condition value
        :param instance: Instance flag
        """
        self.name = name
        self.adapterKindKey = adapterKindKey
        self.resourceKindKey = resourceKindKey
        self.waitCycle = waitCycle
        self.cancelCycle = cancelCycle
        self.severity = severity
        self.key = key
        self.operator = operator
        self.value = value
        self.instance = instance or False


class AlertDefinitionConfig:
    def __init__(self, name="My-Alert-Definition-1", description="Alert for CPU demand exceeding 95% on VirtualMachine",
                 adapterKindKey="VMWARE", resourceKindKey="VirtualMachine", type=18, subType=19, waitCycle=1,
                 cancelCycle=1, severity="CRITICAL", impactType="BADGE", detail="health",
                 relation="SELF", aggregation="ALL", symptomDefinitionConfig=None):
        """
        Configuration for alert definition
        
        :param name: Alert name
        :param description: Alert description
        :param adapterKindKey: Adapter kind key
        :param resourceKindKey: Resource kind key
        :param type: Alert type
        :param subType: Alert sub-type
        :param waitCycle: Wait cycles
        :param cancelCycle: Cancel cycles
        :param severity: Severity level
        :param impactType: Impact type
        :param detail: Impact detail
        :param relation: Relationship type
        :param aggregation: Aggregation type
        :param symptomDefinitionConfig: SymptomDefinitionConfig object
        """
        self.name = name
        self.description = description
        self.adapterKindKey = adapterKindKey
        self.resourceKindKey = resourceKindKey
        self.type = type
        self.subType = subType
        self.waitCycle = waitCycle
        self.cancelCycle = cancelCycle
        self.severity = severity
        self.impactType = impactType
        self.detail = detail
        self.relation = relation
        self.aggregation = aggregation
        self.symptomDefinitionConfig = SymptomDefinitionConfig(**(symptomDefinitionConfig or {}))
