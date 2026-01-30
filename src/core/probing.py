import os
from utils.commands import run_cmd
import logging
import datetime as dt
import json
import re
from utils.txtfiles import (
    convert_json_keys_to_txt,
    add_protocol_to_hosts
)

def check_online_hosts(cname_hosts_pairs_file, domain_output_dir):
    if not os.path.isfile(cname_hosts_pairs_file):
        logging.error(f"Grepped CNAME hosts file {cname_hosts_pairs_file} not found for online checking.")
        return
    logging.info(f"Checking online hosts from {cname_hosts_pairs_file}.")
    online_file = os.path.join(domain_output_dir, f"{dt.datetime.now().strftime('%Y%m%d')}.online_candidates.txt")
    
    grepped_cname_hosts_file = os.path.join(domain_output_dir, f"{dt.datetime.now().strftime('%Y%m%d')}.grepped_cname_hosts.txt")
    convert_json_keys_to_txt(cname_hosts_pairs_file, grepped_cname_hosts_file)
    
    hosts_with_protocol_file = os.path.join(domain_output_dir, f"{dt.datetime.now().strftime('%Y%m%d')}.grepped_cname_hosts_with_protocol.txt")
    add_protocol_to_hosts(grepped_cname_hosts_file, hosts_with_protocol_file)
    
    cmd = f"httpx -silent -l {hosts_with_protocol_file} -status-code -timeout 15 -retries 0 -threads 5 -delay 500ms"
    logging.info("Running httpx (5 threads, 500ms delay) to check online hosts.")
    output = run_cmd(cmd)
    
    if output:
        logging.info(f"Found {len(output.splitlines())} responses from httpx")
    else:
        logging.warning("httpx returned no results - hosts may be blocking requests")

    try:
        with open(online_file, "w") as f:
            if output:
                cleaned_lines = []
                for line in output.splitlines():
                    url = line.split()[0] if line.split() else ""
                    if url:
                        cleaned_lines.append(url)
                
                f.write('\n'.join(cleaned_lines) + '\n')
                logging.info(f"Saved {len(cleaned_lines)} online hosts to {online_file}")
            else:
                f.write("")
    except Exception as e:
        logging.error(f"Error writing online hosts file {online_file}: {e}")
        return
    
    return online_file