import os
from utils.commands import run_cmd
import logging
import datetime as dt
import re


def get_hosts_with_permissive_spf(dns_file, domain_output_dir):
    if not os.path.isfile(dns_file):
        logging.error(f"[{dt.datetime.now()}] DNS records file {dns_file} not found for SPF filtering.")
        return ""
    logging.info(f"[{dt.datetime.now()}] Filtering SPF permissive candidates from DNS records in {dns_file}.")
    spf_hosts_file = os.path.join(domain_output_dir, "spf_permissive_hosts.json")
    
    permissive_hosts = search_for_permissive_spf_hosts(dns_file)

    try:
        import json
        with open(spf_hosts_file, 'w') as f:
            json.dump(permissive_hosts, f, indent=4)
        logging.info(f"[{dt.datetime.now()}] Permissive SPF hosts saved to {spf_hosts_file}.")
    except Exception as e:
        logging.error(f"[{dt.datetime.now()}] Error saving permissive SPF hosts: {e}")
    return spf_hosts_file

def search_for_permissive_spf_hosts(dns_file):
    permissive_hosts = {}
    try:
        with open(dns_file, 'r') as f:
            for line in f:
                if 'TXT' in line.upper() and 'V=SPF1' in line.upper():
                    clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
                    clean_line = re.sub(r'[\[\]]', '', clean_line)
                    
                    parts = clean_line.strip().split()
                    if len(parts) >= 3:
                        host = parts[0]
                        txt_record = ' '.join(parts[2:])
                        if any(term in txt_record.lower() for term in ['~all', '?all']):
                            permissive_hosts[host] = txt_record
    except Exception as e:
        logging.error(f"[{dt.datetime.now()}] Error searching DNS file {dns_file} for SPF hosts: {e}")
    return permissive_hosts