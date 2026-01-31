import os
import datetime as dt
import logging

import pytest

from src.core.dns import dns_enum


def test_dns_enum_missing_file_returns_empty_and_logs_error(tmp_path, caplog):
	missing_file = tmp_path / "missing.txt"
	output_dir = tmp_path / "out"
	output_dir.mkdir()

	with caplog.at_level(logging.ERROR):
		result = dns_enum(str(missing_file), str(output_dir))

	assert result == ""
	assert "not found for DNS enumeration" in caplog.text


def test_dns_enum_builds_command_and_returns_output_path(tmp_path, monkeypatch):
	subdomains_file = tmp_path / "subs.txt"
	subdomains_file.write_text("example.com\n")
	output_dir = tmp_path / "out"
	output_dir.mkdir()

	captured = {}

	def fake_run_cmd(cmd):
		captured["cmd"] = cmd

	monkeypatch.setattr("src.core.dns.run_cmd", fake_run_cmd)

	result = dns_enum(str(subdomains_file), str(output_dir))

	expected_filename = f"{dt.datetime.now().strftime('%Y%m%d')}.dns_records.txt"
	expected_output = os.path.join(str(output_dir), expected_filename)

	assert result == expected_output
	assert expected_output in captured["cmd"]
	assert f"-l {subdomains_file}" in captured["cmd"]
	assert "dnsx -cname -txt -silent -re" in captured["cmd"]


def test_dns_enum_logs_info(tmp_path, caplog, monkeypatch):
	subdomains_file = tmp_path / "subs.txt"
	subdomains_file.write_text("example.com\n")
	output_dir = tmp_path / "out"
	output_dir.mkdir()

	monkeypatch.setattr("src.core.dns.run_cmd", lambda cmd: None)

	with caplog.at_level(logging.INFO):
		dns_enum(str(subdomains_file), str(output_dir))

	assert "Enumerating CNAMEs and TXTs DNS records" in caplog.text
