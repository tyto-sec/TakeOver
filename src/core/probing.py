import os
from utils.commands import run_cmd
import logging
import datetime as dt
import json
from utils.txtfiles import convert_json_keys_to_txt

def check_online_hosts(cname_hosts_pairs_file, domain_output_dir):
    if not os.path.isfile(cname_hosts_pairs_file):
        logging.error(f"Grepped CNAME hosts file {cname_hosts_pairs_file} not found for online checking.")
        return
    logging.info(f"Checking online hosts from {cname_hosts_pairs_file}.")
    online_file = os.path.join(domain_output_dir, f"{dt.datetime.now().strftime('%Y%m%d')}.online_candidates.txt")
    
    grepped_cname_hosts_file = os.path.join(domain_output_dir, f"{dt.datetime.now().strftime('%Y%m%d')}.grepped_cname_hosts.txt")
    convert_json_keys_to_txt(cname_hosts_pairs_file, grepped_cname_hosts_file)
    
    cmd = f"/root/go/bin/httpx -silent -l {grepped_cname_hosts_file}"
    output = run_cmd(cmd)

    if output:
        with open(online_file, "w") as f:
            f.write(output)
    
    logging.debug(f"Found {len(output.splitlines())} online hosts.")
    return online_file