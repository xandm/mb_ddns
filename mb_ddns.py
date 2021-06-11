#!/usr/bin/python3
#
# Simple dynamic DNS client for Mythic Beasts DNS API
# Xand Meaden, June 2021

import os
import re
import requests
import sys
import yaml

URLS = {
    "ipv4": "https://ipv4.api.mythic-beasts.com/dns/v2/dynamic/",
    "ipv6": "https://ipv6.api.mythic-beasts.com/dns/v2/dynamic/"
}

config_file = "/etc/mb_ddns.yaml"
if len(sys.argv) == 2 and os.path.exists(sys.argv[1]):
    config_file = sys.argv[1]

if os.stat(config_file).st_mode & 4:
    sys.stderr.write("Config file is world-readable; change its permissions and try again.\n")
    sys.exit(1)

try:
    with open(config_file) as fh:
        config = yaml.safe_load(fh)
except Exception as e:
    sys.stderr.write(f"Failed to load config from {config_file}: {e}\n")
    sys.exit(1)

if not re.match(r"(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])", config["domain"]):
    sys.stderr.write("Invalid domain in config\n")
    sys.exit(1)

exit_code = 0
for p in ["ipv4", "ipv6"]:
    if config[p]:
        url = URLS[p] + config["domain"]
        try:
            r = requests.post(url, auth=(config["key_id"], config["secret"]))
        except Exception as e:
            sys.stderr.write(f"[{p}] Failed updating address: {e}\n")
            exit_code = 1
            continue

        if r.status_code != 200:
            sys.stderr.write(f"[{p}] Error updating address, HTTP status {r.status_code}\n")
            exit_code = 1

        try:
            reply = r.json()
            if "message" in reply:
                print(f"[{p}] {reply['message']}")
            if "error" in reply:
                sys.stderr.write(f"[{p}] Error updating address: {reply['error']}\n")
                exit_code = 1
        except Exception as e:
            sys.stderr.write(f"[{p}] Failed decoding response: {e}\n")
            exit_code = 1

sys.exit(exit_code)
