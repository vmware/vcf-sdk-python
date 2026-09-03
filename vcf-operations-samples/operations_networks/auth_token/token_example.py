# Copyright (c) 2025 Broadcom. All Rights Reserved.
# The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.
# SPDX-License-Identifier: Apache-2.0

"""
Simple example demonstrating how to use TokenService class to generate authentication token.
"""

import argparse
import requests
from .token_service import TokenService

def main():
    """
    Main function to fetch and print authentication token
    """
    parser = argparse.ArgumentParser(
        description='Fetch authentication token from VCF Operations for Networks')
    
    parser.add_argument(
        '--server',
        required=True,
        help='VCF Operations Networks Instance Host Name or IP')
    
    parser.add_argument(
        '--user',
        required=True,
        help='VCF Operations Networks username')
    
    parser.add_argument(
        '--password',
        required=True,
        help='VCF Operations Networks password')
    
    parser.add_argument(
        '--domain-type',
        required=False,
        default='LOCAL',
        help='Domain type for authentication (default: LOCAL)')
    
    parser.add_argument(
        '--domain-value',
        required=False,
        default='example.com',
        help='Domain value for authentication (default: example.com)')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("Fetching Authentication Token")
    print("=" * 80)
    print(f"\nServer: {args.server}")
    print(f"User: {args.user}")
    print(f"Domain Type: {args.domain_type}")
    print(f"Domain Value: {args.domain_value}")
    print("\n" + "-" * 80)
    
    # Create a session with SSL verification disabled
    session = requests.Session()
    session.verify = False
    requests.packages.urllib3.disable_warnings()
    
    # Create TokenService instance
    print("\nCreating TokenService instance...")
    token_service = TokenService(
        server=args.server,
        username=args.user,
        password=args.password,
        session=session,
        domain_type=args.domain_type,
        domain_value=args.domain_value)
    
    # Fetch token from server
    print("Fetching authentication token from server...\n")
    try:
        token = token_service.fetch_token()
        print("=" * 80)
        print("Token fetched successfully!")
        print("=" * 80)
        print(f"\nAuthentication Token:\n{token}")
        print(f"\nToken Length: {len(token)} characters")
        print("\n" + "=" * 80)
    except Exception as e:
        print("=" * 80)
        print("Error fetching token!")
        print("=" * 80)
        print(f"\nError: {e}\n")
        print("=" * 80)

if __name__ == "__main__":
    main()
