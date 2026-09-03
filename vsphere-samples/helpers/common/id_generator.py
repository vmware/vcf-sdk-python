#!/usr/bin/env python

# Copyright (c) 2013-2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0



import uuid
import string
import random


def generate_random_uuid():
    return str(uuid.uuid4())


def rand(value):
    return value + generate_random_string(5)


def generate_random_string(length):
    return ''.join(random.choice(string.ascii_uppercase) for _i in range(length))


def main():
    print(generate_random_uuid())
    print(generate_random_string(5))
    print(rand('Simple VM-'))


# Start program
if __name__ == "__main__":
    main()
