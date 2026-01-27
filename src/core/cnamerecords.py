import os
import re
import logging
import datetime as dt

def get_hosts_with_cname(dns_file, domain_output_dir):
    if not os.path.isfile(dns_file):
        logging.error(f"[{dt.datetime.now()}] DNS records file {dns_file} not found for CNAME filtering.")
        return ""
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