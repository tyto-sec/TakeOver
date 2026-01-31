import os
import logging
import datetime as dt
import concurrent.futures

from src.core.subdomains import subfinder_enum, chaos_enum
from src.core.dns import dns_enum
from src.core.txtrecords import get_hosts_with_permissive_spf
from src.core.cnamerecords import get_hosts_with_cname, grep_cname_hosts
from src.core.probing import check_online_hosts
from src.core.nuclei import run_nuclei_scan
from src.constants import CNAME_FINGERPRINTS, TAKEOVER_MAP

from src.utils.txtfiles import (
    concatenate_files,
    read_lines
)

NUCLEI_TEMPLATE_DIR = os.path.expanduser("~/nuclei-templates/http/takeovers")
OUTPUT_DIR = "../output"

def process_single_domain(domain, output_dir, cname_fingerprints, takeover_map, nuclei_template_dir):
    domain_name_safe = domain.replace('.', '_')
    domain_output_dir = os.path.join(output_dir, domain_name_safe)
    
    os.makedirs(domain_output_dir, exist_ok=True)

    logging.info(f"Processing domain: {domain}")
    logging.info(f"Output directory: {domain_output_dir}")
    
    try:
        subfinder_file = subfinder_enum(domain, domain_output_dir)
        subfinder_file_abs = os.path.join(domain_output_dir, os.path.basename(subfinder_file))

        chaos_file = chaos_enum(domain, domain_output_dir)
        chaos_file_abs = os.path.join(domain_output_dir, os.path.basename(chaos_file))

        combined_subdomains_file = os.path.join(domain_output_dir, f"{dt.datetime.now().strftime('%Y%m%d')}.combined_subdomains.txt")
        subs_file = concatenate_files([subfinder_file_abs, chaos_file_abs], combined_subdomains_file)

        dns_file = dns_enum(subs_file, domain_output_dir)
        dns_file_abs = os.path.join(domain_output_dir, os.path.basename(dns_file))

        get_hosts_with_permissive_spf(dns_file_abs, domain_output_dir)
        
        cname_hosts_pairs_file = get_hosts_with_cname(dns_file_abs, domain_output_dir)
        cname_hosts_pairs_file_abs = os.path.join(domain_output_dir, os.path.basename(cname_hosts_pairs_file))

        grepped_cname_hosts_pairs_file = grep_cname_hosts(cname_hosts_pairs_file_abs, domain_output_dir, cname_fingerprints)
        grepped_cname_hosts_pairs_file_abs = os.path.join(domain_output_dir, os.path.basename(grepped_cname_hosts_pairs_file))

        online_file = check_online_hosts(grepped_cname_hosts_pairs_file_abs, domain_output_dir)
        online_file_abs = os.path.join(domain_output_dir, os.path.basename(online_file))
        
        run_nuclei_scan(online_file_abs, grepped_cname_hosts_pairs_file_abs, domain_output_dir, cname_fingerprints, takeover_map, nuclei_template_dir, output_dir)

        logging.info(f"Domain {domain} scan completed successfully.")
        
    except Exception as e:
        logging.error(f"Error processing domain {domain}: {e}")
    


def run(domains_file, output_dir=OUTPUT_DIR, cname_fingerprints=CNAME_FINGERPRINTS, takeover_map=TAKEOVER_MAP, nuclei_template_dir=NUCLEI_TEMPLATE_DIR, max_threads=8):
    logging.info("Starting automated TakeOver scanner...")

    os.makedirs(output_dir, exist_ok=True)

    domains_list = read_lines(domains_file)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        logging.info(f"Processing {len(domains_list)} domain with {max_threads} parallel threads.")

        futures = [
            executor.submit(
                process_single_domain,
                domain_item,
                output_dir,
                cname_fingerprints,
                takeover_map,
                nuclei_template_dir,
            )
            for domain_item in domains_list
        ]
        for future in concurrent.futures.as_completed(futures):
            future.result()

    logging.info("Process completed. Check the output directory for results.")
