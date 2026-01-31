import csv
import json
import logging
import os

import pytest

from src.core.nuclei import run_nuclei_scan


def _write_json(path, data):
	with open(path, "w") as f:
		json.dump(data, f)


def _read_csv_rows(path):
	with open(path, "r", newline="") as f:
		reader = csv.reader(f)
		return list(reader)


def test_run_nuclei_scan_missing_online_hosts(tmp_path, caplog):
	online_hosts = tmp_path / "missing.txt"
	cname_pairs = tmp_path / "pairs.json"
	_write_json(cname_pairs, {})

	with caplog.at_level(logging.ERROR):
		run_nuclei_scan(
			str(online_hosts),
			str(cname_pairs),
			str(tmp_path),
			{},
			{},
			str(tmp_path),
			str(tmp_path),
		)

	assert "Online hosts file" in caplog.text


def test_run_nuclei_scan_missing_cname_pairs(tmp_path, caplog):
	online_hosts = tmp_path / "online.txt"
	online_hosts.write_text("https://example.com\n")
	cname_pairs = tmp_path / "missing.json"

	with caplog.at_level(logging.ERROR):
		run_nuclei_scan(
			str(online_hosts),
			str(cname_pairs),
			str(tmp_path),
			{},
			{},
			str(tmp_path),
			str(tmp_path),
		)

	assert "CNAME hosts pairs file" in caplog.text


def test_run_nuclei_scan_no_template_creates_csv(tmp_path, monkeypatch):
	online_hosts = tmp_path / "online.txt"
	online_hosts.write_text("https://app.example.com\n")

	cname_pairs = tmp_path / "pairs.json"
	_write_json(cname_pairs, {"app.example.com": "no-match.example.net"})

	monkeypatch.setattr("src.core.nuclei.run_cmd", lambda cmd: "")
	monkeypatch.setattr("src.core.nuclei.send_telegram_message", lambda msg: None)

	run_nuclei_scan(
		str(online_hosts),
		str(cname_pairs),
		str(tmp_path),
		{"aws": ["s3.amazonaws.com"]},
		{"aws": "templates/aws.yaml"},
		str(tmp_path),
		str(tmp_path),
	)

	csv_files = list(tmp_path.glob("final_results_*.csv"))
	assert len(csv_files) == 1
	rows = _read_csv_rows(csv_files[0])
	assert rows[0] == ["Subdomain", "CNAME Target", "Provider", "Nuclei Template", "Vulnerability Status"]
	assert rows[1][0] == "app.example.com"
	assert rows[1][1] == "no-match.example.net"
	assert rows[1][2] == "Unknown"
	assert rows[1][3] == "N/A"
	assert rows[1][4] == "Skipped (No Template)"


def test_run_nuclei_scan_vulnerable_flow(tmp_path, monkeypatch):
	online_hosts = tmp_path / "online.txt"
	online_hosts.write_text("https://vuln.example.com\n")

	cname_pairs = tmp_path / "pairs.json"
	_write_json(cname_pairs, {"vuln.example.com": "bucket.s3.amazonaws.com"})

	messages = []

	def fake_send(msg):
		messages.append(msg)

	def fake_run_cmd(cmd):
		return "{\"vulnerable\": true}"

	monkeypatch.setattr("src.core.nuclei.run_cmd", fake_run_cmd)
	monkeypatch.setattr("src.core.nuclei.send_telegram_message", fake_send)

	run_nuclei_scan(
		str(online_hosts),
		str(cname_pairs),
		str(tmp_path),
		{"aws": ["s3.amazonaws.com"]},
		{"aws": "takeovers/aws.yaml"},
		str(tmp_path),
		str(tmp_path),
	)

	csv_files = list(tmp_path.glob("final_results_*.csv"))
	assert len(csv_files) == 1
	rows = _read_csv_rows(csv_files[0])
	assert rows[1][0] == "vuln.example.com"
	assert rows[1][2] == "aws"
	assert "VULNERABLE" in rows[1][4]

	output_files = list(tmp_path.glob("vuln.example.com_vulnerable_aws.jsonl"))
	assert len(output_files) == 1
	assert messages


def test_run_nuclei_scan_handles_run_cmd_error(tmp_path, monkeypatch):
	online_hosts = tmp_path / "online.txt"
	online_hosts.write_text("https://err.example.com\n")

	cname_pairs = tmp_path / "pairs.json"
	_write_json(cname_pairs, {"err.example.com": "bucket.s3.amazonaws.com"})

	def fake_run_cmd(cmd):
		raise RuntimeError("boom")

	monkeypatch.setattr("src.core.nuclei.run_cmd", fake_run_cmd)
	monkeypatch.setattr("src.core.nuclei.send_telegram_message", lambda msg: None)

	run_nuclei_scan(
		str(online_hosts),
		str(cname_pairs),
		str(tmp_path),
		{"aws": ["s3.amazonaws.com"]},
		{"aws": "takeovers/aws.yaml"},
		str(tmp_path),
		str(tmp_path),
	)

	csv_files = list(tmp_path.glob("final_results_*.csv"))
	rows = _read_csv_rows(csv_files[0])
	assert rows[1][0] == "err.example.com"
	assert rows[1][2] == "aws"
	assert rows[1][4].startswith("Error:")
