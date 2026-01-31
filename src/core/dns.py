import os
from src.utils.commands import run_cmd
import logging
import datetime as dt

def dns_enum(subdomains_file, domain_output_dir):
    if not os.path.isfile(subdomains_file):
        logging.error(f"Subdomains file {subdomains_file} not found for DNS enumeration.")
        return ""
    logging.info(f"Enumerating CNAMEs and TXTs DNS records for {subdomains_file}.")
    output_file = os.path.join(domain_output_dir, f"{dt.datetime.now().strftime('%Y%m%d')}.dns_records.txt")
    cmd = f"dnsx -cname -txt -silent -re -l {subdomains_file} -o {output_file}"
    run_cmd(cmd)
    return output_file