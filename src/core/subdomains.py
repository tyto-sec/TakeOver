from utils.commands import run_cmd
import os
import logging
import datetime as dt
from dotenv import load_dotenv
from utils.transformations import clean_domain

# Carregar variáveis do .env
load_dotenv()

def subfinder_enum(domain, domain_output_dir):
    cmd = "subfinder -d {domain} -silent"
    return subdomain_enum(cmd, "subfinder", domain, domain_output_dir)

def chaos_enum(domain, domain_output_dir):
    cmd = "chaos -d {domain} -silent"
    return subdomain_enum(cmd, "chaos", domain, domain_output_dir, use_pdcp_api=True)

def subdomain_enum(cmd, tool_name, domain, domain_output_dir, use_pdcp_api=False):
    logging.info(f" Enumerating subdomains of {domain} with {tool_name}.")
    output_file = os.path.join(domain_output_dir, f"{dt.datetime.now().strftime('%Y%m%d')}.{tool_name}.subdomains.txt")
    
    if use_pdcp_api:
        pdcp_api_key = os.getenv('PDCP_API_KEY')
        if pdcp_api_key:
            os.environ['PDCP_API_KEY'] = pdcp_api_key
            logging.debug(f"PDCP_API_KEY exported for chaos.")
        else:
            logging.warning(f"PDCP_API_KEY not found in .env")
    
    full_cmd = cmd.format(domain=domain) + " | anew"
    subs = run_cmd(full_cmd)
    
    for line in subs.splitlines():
        cleaned_domain_line = clean_domain(line)
        if cleaned_domain_line != line:
            subs = subs.replace(line, cleaned_domain_line)

    if subs:
        with open(output_file, "w") as f:
            f.write(subs)
    logging.debug(f"Found {len(subs.splitlines())} subdomains.")
    return output_file