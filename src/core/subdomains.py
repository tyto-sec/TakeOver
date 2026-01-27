from utils.commands import run_cmd
import os
import logging
import datetime as dt

def subfinder_enum(domain, domain_output_dir):
    cmd = "subfinder -d {domain} -silent"
    return subdomain_enum(cmd, "subfinder", domain, domain_output_dir)

def chaos_enum(domain, domain_output_dir):
    cmd = "chaos -d {domain} -silent"
    return subdomain_enum(cmd, "chaos", domain, domain_output_dir)

def subdomain_enum(cmd, tool_name, domain, domain_output_dir):
    logging.info(f"[{dt.datetime.now()}] Enumarating subdomains of {domain} with {tool_name}.")
    output_file = os.path.join(domain_output_dir, f"{dt.datetime.now().strftime('%Y%m%d')}.{tool_name}.subdomains.txt")
    full_cmd = cmd.format(domain=domain) + " | anew"
    subs = run_cmd(full_cmd)
    if subs:
        with open(output_file, "w") as f:
            f.write(subs)
    logging.debug(f"[{dt.datetime.now()}] Found {len(subs.splitlines())} subdomains.")
    return output_file