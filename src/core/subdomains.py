from utils.commands import run_cmd
import os

def subfinder_enum(domain, domain_output_dir):
    cmd = "subfinder -d {domain}"
    return subdomain_enum(cmd, "subfinder", domain, domain_output_dir)

def subdomain_enum(cmd, tool_name, domain, domain_output_dir):
    print("[*] Subdomain enumeration...")
    output_file = os.path.join(domain_output_dir, f"{tool_name}.subdomains.txt")
    full_cmd = cmd.format(domain=domain) + " | anew"
    subs = run_cmd(full_cmd)
    if subs:
        with open(output_file, "w") as f:
            f.write(subs)
    print(f"[DEBUG] Found {len(subs.splitlines())} subdomains.")
    return output_file