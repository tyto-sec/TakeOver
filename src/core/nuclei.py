import os
import re
import csv
import json
import datetime as dt
import logging

from src.utils.commands import run_cmd
from src.utils.txtfiles import read_lines
from src.utils.telegram import send_telegram_message

def run_nuclei_scan(online_hosts_file, cname_hosts_pairs_file, domain_output_dir, cname_fingerprints, takeover_map, nuclei_template_dir, output_dir):
    if not os.path.isfile(online_hosts_file):
        logging.error(f"Online hosts file {online_hosts_file} not found for nuclei scanning.")
        return
    if not os.path.isfile(cname_hosts_pairs_file):
        logging.error(f"CNAME hosts pairs file {cname_hosts_pairs_file} not found for nuclei scanning.")
        return

    logging.info(f"Executing targeted nuclei scan for subdomain takeover detection.")
    
    csv_file = os.path.join(domain_output_dir, f"final_results_{dt.datetime.now().strftime('%Y%m%d')}.csv")
    results = []
    host_to_cname = {}
    
    try:
        with open(cname_hosts_pairs_file, 'r') as f:
            host_to_cname = json.load(f)
        logging.info(f"Loaded {len(host_to_cname)} host-CNAME pairs from JSON.")
    except Exception as e:
        logging.error(f"Erro ao carregar JSON com pares Host -> CNAME: {e}")
        return
    
    for host_url in read_lines(online_hosts_file):
        host = host_url.split('//')[-1].split('/')[0]
        cname_target = host_to_cname.get(host)
        nuclei_template = None
        provider_name = "Unknown"
        
        if cname_target:
            for provider, cnames in cname_fingerprints.items():
                for cname_regex in cnames:
                    if re.search(cname_regex, cname_target, re.IGNORECASE):
                        provider_name = provider
                        nuclei_template = takeover_map.get(provider_name)
                        break
                if nuclei_template:
                    break
        
        if nuclei_template:
            template_path = os.path.join(nuclei_template_dir, nuclei_template) 
            cmd = f"nuclei -u {host} -t {template_path} -silent -jsonl"
            logging.info(f"Testing {host} against {provider_name} template: {nuclei_template}")
            try:
                result = run_cmd(cmd)
                vulnerable = "NOT Vulnerable"

                if result:
                    vulnerable = f"VULNERABLE ({provider_name})"
                    output_path = os.path.join(output_dir, f"{host.split(':')[0]}_vulnerable_{provider_name}.jsonl")

                    send_telegram_message(f"VULNERABLE: {host} is vulnerable to {provider_name} takeover.")
                    send_telegram_message(result)

                    with open(output_path, "w") as out_f:
                        out_f.write(result)

                    logging.info(f"VULNERABLE! Result saved in: {output_path}")
                results.append([host, cname_target, provider_name, template_path, vulnerable])

            except Exception as e:
                logging.error(f"Error running nuclei for {host}: {e}")
                results.append([host, cname_target, provider_name, template_path, f"Error: {str(e)}"])

        else:
            logging.info(f"Skipped {host} (CNAME: {cname_target}) - No specific nuclei template found for provider: {provider_name}")
            results.append([host, cname_target if cname_target else "N/A", provider_name, "N/A", "Skipped (No Template)"])

    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Subdomain", "CNAME Target", "Provider", "Nuclei Template", "Vulnerability Status"])
        writer.writerows(results)

    logging.info(f"CSV report saved in: {csv_file}")