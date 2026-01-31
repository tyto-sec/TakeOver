import logging
import os
import argparse
from src.tasks import run

def main():
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="[%(asctime)s] %(levelname)s: %(message)s",
    )

    banner = """
        88888888888       888                .d88888b.                            
            888           888               d88P" "Y88b                           
            888           888               888     888                           
            888   8888b.  888  888  .d88b.  888     888 888  888  .d88b.  888d888 
            888      "88b 888 .88P d8P  Y8b 888     888 888  888 d8P  Y8b 888P"   
            888  .d888888 888888K  88888888 888     888 Y88  88P 88888888 888     
            888  888  888 888 "88b Y8b.     Y88b. .d88P  Y8bd8P  Y8b.     888     
            888  "Y888888 888  888  "Y8888   "Y88888P"    Y88P    "Y8888  888 2.0.0     

    """
    print(banner)
    import sys
    sys.stdout.flush()
    
    parser = argparse.ArgumentParser(
        description="TakeOver Scanner: Automated subdomain takeover and permissive email configurations detection tool.",
        prog='TakeOver',
        epilog="""
EXAMPLES:
  TakeOver --input domains.txt --output ./results
  TakeOver --input /path/to/domains.txt --output /path/to/output --max-threads 16

OUTPUT FILES:
  - YYYYMMDD.chaos.subdomains.txt          - Subdomains from Chaos enumeration
  - YYYYMMDD.subfinder.subdomains.txt      - Subdomains from Subfinder enumeration
  - YYYYMMDD.combined_subdomains.txt       - Combined unique subdomains
  - YYYYMMDD.dns_records.txt               - DNS records (A, CNAME, TXT)
  - YYYYMMDD.cname_hosts_pairs.json        - CNAME hostname to target mappings
  - YYYYMMDD.grepped_cname_hosts_pairs.json - Filtered CNAME pairs matching fingerprints
  - YYYYMMDD.grepped_cname_hosts.txt       - List of vulnerable CNAME hosts
  - YYYYMMDD.hosts_with_protocol.txt       - Hosts with HTTPS protocol prefix
  - YYYYMMDD.online_candidates.txt         - Live hosts responding to probes
  - YYYYMMDD.spf_permissive_hosts.json     - Hosts with permissive SPF records
  - final_results_YYYYMMDD.csv             - Final vulnerability assessment report

For more info, visit: https://github.com/tyto-sec/TakeOver
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
        )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 2.0.0'
    )

    parser.add_argument(
        '--input',
        type=str,
        required=True,
        metavar='FILE',
        help='Text file containing list of domains to scan (one domain per line)'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='../output',
        metavar='PATH',
        help='Output directory where extracted assets will be saved (default: ../output)'
    )

    parser.add_argument(
        '--nuclei-template-dir',
        type=str,
        default=os.path.expanduser('~/nuclei-templates/http/takeovers'),
        metavar='PATH',
        help='Path to nuclei templates directory (default: ~/nuclei-templates/http/takeovers)'
    )

    parser.add_argument(
        '--max-threads',
        type=int,
        default=8,
        metavar='N',
        help='Maximum number of parallel threads to use (default: 8)'
    )

    args = parser.parse_args()
    
    run(
        domains_file=args.input,
        output_dir=args.output,
        nuclei_template_dir=args.nuclei_template_dir,
        max_threads=args.max_threads
    )


if __name__ == '__main__':
    main()