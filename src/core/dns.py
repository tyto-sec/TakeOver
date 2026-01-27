import os
from utils.commands import run_cmd
import logging
import datetime as dt

def dns_enum(subdomains_file, domain_output_dir):
    if not os.path.isfile(subdomains_file):
        logging.error(f"[{dt.datetime.now()}] Subdomains file {subdomains_file} not found for DNS enumeration.")
        return ""
    logging.info(f"[{dt.datetime.now()}] Enumarating CNAMEs and TXTs DNS records for {subdomains_file}.")
    output_file = os.path.join(domain_output_dir, "dns_records.txt")
    cmd = f"dnsx -cname -txt -silent -re -l {subdomains_file} -o {output_file}"
    run_cmd(cmd)
    return output_file