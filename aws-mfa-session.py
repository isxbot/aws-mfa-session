#!/usr/bin/env python3

import argparse
import getpass
import json
import os
import subprocess

def run_cmd(cmd):
    # Run a shell command and return its output.
    result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
    return result.stdout.strip()

def main():
    # Arguments
    parser = argparse.ArgumentParser(description="Get AWS session token using MFA")
    parser.add_argument("--output", choices=["json"], help="Output as JSON")
    args = parser.parse_args()

    # Cleanup old values
    ID = 'AWS_ACCESS_KEY_ID'
    KEY = 'AWS_SECRET_ACCESS_KEY'
    TOKEN = 'AWS_SESSION_TOKEN'

    if ID in os.environ:
        del os.environ[ID]
    if KEY in os.environ:
        del os.environ[KEY]
    if TOKEN in os.environ:
        del os.environ[TOKEN]

    # Prompt user for MFA code
    mfa_code = getpass.getpass("Enter MFA code: ").strip()

    # Get MFA device ARN
    try:
        mfa_devices_json = run_cmd("aws iam list-mfa-devices --output json")
        mfa_devices = json.loads(mfa_devices_json)
        mfa_arn = mfa_devices["MFADevices"][0]["SerialNumber"]
    except (KeyError, IndexError):
        print("Error: Could not retrieve MFA device serial number.")
        return

    if not mfa_arn:
        print("Error: Could not retrieve MFA ARN.")
        return

    # Get temporary session token
    cmd = (
        f"aws sts get-session-token "
        f"--serial-number {mfa_arn} "
        f"--token-code {mfa_code} "
        f"--duration-seconds 43200 "
        f"--output json"
    )
    session_json = run_cmd(cmd)
    session_data = json.loads(session_json)

    # Extract credentials
    creds = session_data.get("Credentials", {})
    if not creds:
        print("Error: Could not retrieve session credentials.")
        return

    if args.output == "json":
        print(json.dumps({
            "AWS_ACCESS_KEY_ID": creds["AccessKeyId"],
            "AWS_SECRET_ACCESS_KEY": creds["SecretAccessKey"],
            "AWS_SESSION_TOKEN": creds["SessionToken"],
        }, indent=2))
    else:
        print("\nMFA session credentials:")
        print(f'export AWS_ACCESS_KEY_ID="{creds["AccessKeyId"]}"')
        print(f'export AWS_SECRET_ACCESS_KEY="{creds["SecretAccessKey"]}"')
        print(f'export AWS_SESSION_TOKEN="{creds["SessionToken"]}"')
        print("\nRun the above commands in your shell to set the session environment.")

if __name__ == "__main__":
    main()
