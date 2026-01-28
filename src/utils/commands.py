import subprocess
import sys
import logging
import datetime as dt

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        logging.error(f"Error executing: {cmd}\n{e}")
        return ""


def run_cmd_with_stdin(cmd, stdin_data=None):
    try:
        if stdin_data is None:
            if not sys.stdin.isatty():
                stdin_data = sys.stdin.read()
            else:
                stdin_data = ""
        
        result = subprocess.run(
            cmd,
            shell=True,
            input=stdin_data,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except Exception as e:
        logging.error(f"Error executing: {cmd}\n{e}")
        return ""

