# TakeOver Scanner

![TakeOver](./img/TakeOver.png)

<div align="center">

![last commit](https://img.shields.io/github/last-commit/tyto-sec/TakeOver) ![created](https://img.shields.io/github/created-at/tyto-sec/TakeOver) ![language](https://img.shields.io/github/languages/top/tyto-sec/TakeOver) ![workflow](https://img.shields.io/github/actions/workflow/status/tyto-sec/TakeOver/tests.yml) ![stars](https://img.shields.io/github/stars/tyto-sec/TakeOver) 

</div>

> **TakeOver** is an automated security tool for discovering subdomain takeover vulnerabilities and permissive SPF records through comprehensive DNS enumeration, CNAME analysis, and vulnerability scanning.

<br>

## Features

- **Multi-Source Subdomain Enumeration:** Integrates Chaos and Subfinder for comprehensive subdomain discovery
- **DNS Record Analysis:** Extracts A, CNAME, and TXT records with permissive SPF detection
- **CNAME Vulnerability Detection:** Identifies dangling CNAMEs pointing to takeover-prone services
- **Active Host Probing:** Uses httpx to detect live hosts before vulnerability scanning
- **Nuclei Integration:** Automated vulnerability scanning with customizable templates
- **Comprehensive Reporting:** Generates detailed CSV reports with vulnerability findings
- **Docker Support:** Fully containerized for easy deployment and consistent environments

<br>

## Dependencies

### Python Dependencies

The tool requires Python 3.7+ with the following packages (from `requirements.txt`):

```
certifi==2026.1.4
charset-normalizer==3.4.4
dotenv==0.9.9
idna==3.11
python-dotenv==1.2.1
requests==2.32.5
urllib3==2.6.3
```

### External Tools (Go-based)

TakeOver depends on the following external tools:

| Tool | Version | Purpose |
|------|---------|---------|
| **[httpx](https://github.com/projectdiscovery/httpx)** | latest | Fast HTTP probing and response analysis |
| **[subfinder](https://github.com/projectdiscovery/subfinder)** | v2 latest | Subdomain enumeration from multiple sources |
| **[chaos](https://github.com/projectdiscovery/chaos-client)** | latest | ProjectDiscovery Chaos dataset enumeration |
| **[dnsx](https://github.com/projectdiscovery/dnsx)** | latest | Fast DNS toolkit for DNS enumeration |
| **[nuclei](https://github.com/projectdiscovery/nuclei)** | v3 latest | Vulnerability scanner with template support |
| **[anew](https://github.com/tomnomnom/anew)** | latest | Append unique lines to files |

<br>

## Installation

### Option 1: Local Installation

#### Prerequisites

- Go 1.25.1 or higher
- Python 3.7+
- pip

#### Install Go Tools

```bash
# Install httpx
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

# Install subfinder
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# Install chaos
go install -v github.com/projectdiscovery/chaos-client/cmd/chaos@latest

# Install dnsx
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest

# Install nuclei
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
nuclei -update-templates

# Install anew
go install -v github.com/tomnomnom/anew@latest
```

#### Install TakeOver

```bash
pip install -r requirements.txt
pip install .
```

### Option 2: Docker Installation

Build the Docker image (includes all dependencies):

```bash
sudo docker build --no-cache --progress=plain -t takeover:latest .
```

<br>

## Usage

### Command Line

```bash
TakeOver --input domains.txt --output ./results
```

**Arguments:**

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--input` | FILE | **required** | Text file containing domains to scan (one per line) |
| `--output` | PATH | `../output` | Output directory for results |
| `--nuclei-template-dir` | PATH | `~/nuclei-templates/http/takeovers` | Path to nuclei templates |
| `--max-threads` | INT | `8` | Maximum parallel threads |
| `--version` | - | - | Show version information |
| `-h, --help` | - | - | Display help message |

**Example:**

```bash
TakeOver --input targets.txt --output ./scan_results --max-threads 16
```

### Docker Usage

Mount your domains file and output directory:

```bash
docker run --rm \
  -v $(pwd)/domains.txt:/app/input/domains.txt \
  -v $(pwd)/output:/app/output \
  takeover:latest
```

**Custom Configuration:**

```bash
docker run --rm \
  -v $(pwd)/domains.txt:/app/input/domains.txt \
  -v $(pwd)/output:/app/output \
  -e MAX_THREADS=16 \
  -e NUCLEI_TEMPLATE_DIR=/root/nuclei-templates/http/takeovers \
  takeover:latest
```

<br>

## Input Format

Create a text file with one domain per line:

```
example.com
test.org
subdomain.example.com
```

<br>

## Output Files

TakeOver generates timestamped files for each scanned domain:

| File | Description |
|------|-------------|
| `YYYYMMDD.chaos.subdomains.txt` | Subdomains discovered via Chaos |
| `YYYYMMDD.subfinder.subdomains.txt` | Subdomains discovered via Subfinder |
| `YYYYMMDD.combined_subdomains.txt` | Merged and deduplicated subdomains |
| `YYYYMMDD.dns_records.txt` | DNS records (A, CNAME, TXT) |
| `YYYYMMDD.cname_hosts_pairs.json` | CNAME hostname to target mappings |
| `YYYYMMDD.grepped_cname_hosts_pairs.json` | Filtered vulnerable CNAME pairs |
| `YYYYMMDD.grepped_cname_hosts.txt` | List of potentially vulnerable hosts |
| `YYYYMMDD.hosts_with_protocol.txt` | Hosts with HTTPS protocol prefix |
| `YYYYMMDD.online_candidates.txt` | Live hosts responding to probes |
| `YYYYMMDD.spf_permissive_hosts.json` | Hosts with permissive SPF records (~all, ?all) |
| `final_results_YYYYMMDD.csv` | Comprehensive vulnerability report |

<br>

## Testing

Run the comprehensive test suite:

```bash
pytest
```

**Test Coverage:**
- Core DNS enumeration functions
- CNAME record parsing and filtering
- TXT/SPF record analysis
- Subdomain collection and deduplication
- HTTP probing utilities
- File transformation utilities
- Command execution wrappers

Run with coverage report:

```bash
pytest --cov=src --cov-report=term-missing
```

<br>

## Environment Variables

Configure TakeOver behavior via environment variables on `.env` file with the variables below:

| Variable | Description |
|----------|-------------|
| `PDCP_API_KEY` |  Chaos API Key |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token for notifications |
| `TELEGRAM_CHAT_ID` | Telegram chat ID for notifications |

Take a look on `.env.example` for examples.

<br>

## Contributing

Contributions are welcome! Please ensure all tests pass before submitting pull requests:

```bash
pytest
```

<br>

## License

See [LICENSE](LICENSE) file for details.

<br>

## Disclaimer

This tool is intended for authorized security testing only. Always obtain proper authorization before scanning domains you don't own.



