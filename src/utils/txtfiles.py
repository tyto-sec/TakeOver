import logging
import datetime as dt
import json

def read_lines(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def concatenate_files(file_paths, output_file=None):
    unique_lines = set()
    
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line: 
                        unique_lines.add(line)
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
        except Exception as e:
            logging.error(f"Error reading {file_path}: {e}")
    

    sorted_lines = sorted(unique_lines)
    

    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(sorted_lines) + '\n')
            logging.info(f"Files concatenated and saved to {output_file}.")
        except Exception as e:
            logging.error(f"Error saving file: {e}")
        return output_file

    return sorted_lines

def convert_json_keys_to_txt(json_file_path, output_file):
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for key in json_data.keys():
                f.write(f"{key}\n")
        logging.info(f"JSON keys saved to {output_file}.")
    except Exception as e:
        logging.error(f"Error converting JSON to TXT: {e}")

def add_protocol_to_hosts(input_file, output_file, protocol='https'):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            hosts_list = [line.strip() for line in f.readlines() if line.strip()]
        
        if not hosts_list:
            logging.warning(f"No hosts found in {input_file}")
            return 0
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for host in hosts_list:
                if not host.startswith('http://') and not host.startswith('https://'):
                    f.write(f"{protocol}://{host}\n")
                else:
                    f.write(f"{host}\n")
        
        logging.info(f"Added {protocol}:// protocol to {len(hosts_list)} hosts, saved to {output_file}")
        return len(hosts_list)
    except Exception as e:
        logging.error(f"Error adding protocol to hosts: {e}")
        return None
