import os
import re
import logging
import datetime as dt
from utils.commands import run_cmd
import json

def get_hosts_with_cname(dns_file, domain_output_dir):
    if not os.path.isfile(dns_file):
        logging.error(f"[{dt.datetime.now()}] DNS records file {dns_file} not found for CNAME filtering.")
        return
    logging.info(f"[{dt.datetime.now()}] Filtering candidates from {dns_file} for CNAME records.")
    cname_hosts_pairs_file = os.path.join(domain_output_dir, f"{dt.datetime.now().strftime('%Y%m%d')}.cname_hosts_pairs.json")
    host_cname_pairs = search_for_hosts_with_cname(dns_file)

    try:
        import json
        with open(cname_hosts_pairs_file, 'w') as f:
            json.dump(host_cname_pairs, f, indent=4)
        logging.info(f"[{dt.datetime.now()}] CNAME host-cname pairs saved to {cname_hosts_pairs_file}.")
    except Exception as e:
        logging.error(f"[{dt.datetime.now()}] Error saving CNAME host-cname pairs: {e}")

    return cname_hosts_pairs_file

def search_for_hosts_with_cname(dns_file):
    host_cname_pairs = {}
    try:
        with open(dns_file, 'r') as f:
            for line in f:
                if 'CNAME' in line.upper():
                    clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
                    clean_line = re.sub(r'[\[\]]', '', clean_line)
                    
                    parts = clean_line.strip().split()
                    if len(parts) >= 3:
                        host = parts[0]
                        cname = parts[-1]
                        if host and cname and '.' in cname:
                            host_cname_pairs[host] = cname
    except Exception as e:
        logging.error(f"[{dt.datetime.now()}] Error searching DNS file {dns_file} for CNAME hosts: {e}")
    return host_cname_pairs

def grep_cname_hosts(cname_hosts_pairs_file, domain_output_dir, cname_fingerprints):
    if not os.path.isfile(cname_hosts_pairs_file):
        logging.error(f"[{dt.datetime.now()}] CNAME hosts pairs file {cname_hosts_pairs_file} not found for grepping.")
        return
    
    logging.info(f"[{dt.datetime.now()}] Performing filtering on CNAME targets based on subdomain takeover domains list.")
    grepped_cname_hosts_pairs_file = os.path.join(domain_output_dir, f"{dt.datetime.now().strftime('%Y%m%d')}.grepped_cname_hosts_pairs.json")
    
    all_cname_keywords = []
    for cname_list in cname_fingerprints.values():
        all_cname_keywords.extend(cname_list)
    
    unique_cname_keywords = set(all_cname_keywords)
    
    grepped_hosts = {}
    try:
        with open(cname_hosts_pairs_file, 'r') as f:
            host_cname_pairs = json.load(f)
        
        for host, cname in host_cname_pairs.items():
            for keyword in unique_cname_keywords:
                if keyword.lower() in cname.lower():
                    grepped_hosts[host] = cname
                    break
        
        with open(grepped_cname_hosts_pairs_file, 'w') as f:
            json.dump(grepped_hosts, f, indent=4)
        
        logging.info(f"[{dt.datetime.now()}] Found {len(grepped_hosts)} vulnerable CNAME hosts.")
    except Exception as e:
        logging.error(f"[{dt.datetime.now()}] Error processing CNAME file: {e}")
    
    return grepped_cname_hosts_pairs_file
