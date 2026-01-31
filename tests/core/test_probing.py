import os
import logging

import pytest

from src.core.probing import check_online_hosts


def test_check_online_hosts_missing_file_logs_error(tmp_path, caplog):
	missing_file = tmp_path / "missing.json"
	output_dir = tmp_path / "out"
	output_dir.mkdir()

	with caplog.at_level(logging.ERROR):
		result = check_online_hosts(str(missing_file), str(output_dir))

	assert result is None
	assert "not found for online checking" in caplog.text


def test_check_online_hosts_writes_cleaned_output(tmp_path, monkeypatch):
	cname_pairs = tmp_path / "pairs.json"
	cname_pairs.write_text("{}")
	output_dir = tmp_path / "out"
	output_dir.mkdir()

	def fake_convert_json_keys_to_txt(src, dest):
		# create the grepped_cname_hosts.txt file
		with open(dest, "w") as f:
			f.write("example.com\n")

	def fake_add_protocol_to_hosts(src, dest):
		# create grepped_cname_hosts_with_protocol.txt file
		with open(dest, "w") as f:
			f.write("https://example.com\n")

	def fake_run_cmd(cmd):
		return "https://example.com [200]\nhttps://test.com [404]"

	monkeypatch.setattr("src.core.probing.convert_json_keys_to_txt", fake_convert_json_keys_to_txt)
	monkeypatch.setattr("src.core.probing.add_protocol_to_hosts", fake_add_protocol_to_hosts)
	monkeypatch.setattr("src.core.probing.run_cmd", fake_run_cmd)

	result = check_online_hosts(str(cname_pairs), str(output_dir))

	assert result is not None
	assert os.path.isfile(result)
	with open(result, "r") as f:
		lines = [line.strip() for line in f.readlines() if line.strip()]

	assert lines == ["https://example.com", "https://test.com"]


def test_check_online_hosts_no_output_writes_empty_file(tmp_path, monkeypatch, caplog):
	cname_pairs = tmp_path / "pairs.json"
	cname_pairs.write_text("{}")
	output_dir = tmp_path / "out"
	output_dir.mkdir()

	monkeypatch.setattr("src.core.probing.convert_json_keys_to_txt", lambda s, d: open(d, "w").close())
	monkeypatch.setattr("src.core.probing.add_protocol_to_hosts", lambda s, d: open(d, "w").close())
	monkeypatch.setattr("src.core.probing.run_cmd", lambda cmd: "")

	with caplog.at_level(logging.WARNING):
		result = check_online_hosts(str(cname_pairs), str(output_dir))

	assert result is not None
	assert os.path.isfile(result)
	with open(result, "r") as f:
		content = f.read()

	assert content == ""
	assert "httpx returned no results" in caplog.text
