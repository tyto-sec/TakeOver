import os
import re
import csv
from utils.commands import run_cmd
import json
import datetime as dt
import logging
from utils.txtfiles import read_lines
from utils.telegram import send_telegram_message

def run_nuclei_scan(online_hosts_file, cname_hosts_pairs_file, domain_output_dir, cname_fingerprints, takeover_map, nuclei_template_dir, output_dir):
    if not os.path.isfile(online_hosts_file):
        logging.error(f"[{dt.datetime.now()}] Online hosts file {online_hosts_file} not found for nuclei scanning.")
        return
    if not os.path.isfile(cname_hosts_pairs_file):
        logging.error(f"[{dt.datetime.now()}] CNAME hosts pairs file {cname_hosts_pairs_file} not found for nuclei scanning.")
        return

    logging.info(f"[{dt.datetime.now()}] Executing targeted nuclei scan for subdomain takeover detection.")
    
    csv_file = os.path.join(domain_output_dir, f"final_results_{dt.datetime.now().strftime('%Y%m%d')}.csv")
    results = []
    host_to_cname = {}
    
    try:
        with open(cname_hosts_pairs_file, 'r') as f:
            host_to_cname = json.load(f)
        logging.info(f"[{dt.datetime.now()}] Loaded {len(host_to_cname)} host-CNAME pairs from JSON.")
    except Exception as e:
        logging.error(f"[{dt.datetime.now()}] Erro ao carregar JSON com pares Host -> CNAME: {e}")
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
            cmd = f"nuclei -u {host} -t {template_path}"
            logging.info(f"[{dt.datetime.now()}] Testing {host} against {provider_name} template: {nuclei_template}")
            try:
                result = run_cmd(cmd)
                vulnerable = "NOT Vulnerable"
                if result:
                    vulnerable = f"VULNERABLE ({provider_name})"
                    output_path = os.path.join(output_dir, f"{host.split(':')[0]}_vulnerable_{provider_name}.txt")

                    send_telegram_message(f"VULNERABLE! {host} is vulnerable to {provider_name} takeover. Details saved in: {output_path}")

                    with open(output_path, "w") as f:
                        f.write(result)
                    logging.info(f"[{dt.datetime.now()}] VULNERABLE! Result saved in: {output_path}")
                results.append([host, cname_target, provider_name, template_path, vulnerable])

            except Exception as e:
                logging.error(f"[{dt.datetime.now()}] Error running nuclei for {host}: {e}")
                results.append([host, cname_target, provider_name, template_path, f"Error: {str(e)}"])

        else:
            logging.info(f"[{dt.datetime.now()}] Skipped {host} (CNAME: {cname_target}) - No specific nuclei template found for provider: {provider_name}")
            results.append([host, cname_target if cname_target else "N/A", provider_name, "N/A", "Skipped (No Template)"])

    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Subdomain", "CNAME Target", "Provider", "Nuclei Template", "Vulnerability Status"])
        writer.writerows(results)

    logging.info(f"[{dt.datetime.now()}] CSV report saved in: {csv_file}")