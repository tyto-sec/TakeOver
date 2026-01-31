import os
import json
import logging
import datetime as dt
from unittest.mock import patch, mock_open, MagicMock

import pytest

from src.core.txtrecords import get_hosts_with_permissive_spf, search_for_permissive_spf_hosts


class TestSearchForPermissiveSPFHosts:
	"""Tests for search_for_permissive_spf_hosts function"""

	def test_search_for_permissive_spf_hosts_with_tilde_all(self, tmp_path):
		"""Test detection of SPF records with ~all (softfail)"""
		dns_file = tmp_path / "dns_records.txt"
		dns_file.write_text(
			"example.com. IN TXT v=spf1 include:_spf.google.com ~all\n"
		)

		result = search_for_permissive_spf_hosts(str(dns_file))

		assert "example.com." in result
		assert "v=spf1" in result["example.com."]
		assert "~all" in result["example.com."]

	def test_search_for_permissive_spf_hosts_with_question_all(self, tmp_path):
		"""Test detection of SPF records with ?all (neutral)"""
		dns_file = tmp_path / "dns_records.txt"
		dns_file.write_text(
			"test.org. IN TXT v=spf1 mx ?all\n"
		)

		result = search_for_permissive_spf_hosts(str(dns_file))

		assert "test.org." in result
		assert "?all" in result["test.org."]

	def test_search_for_permissive_spf_hosts_ignores_strict_spf(self, tmp_path):
		"""Test that strict SPF records (-all) are ignored"""
		dns_file = tmp_path / "dns_records.txt"
		dns_file.write_text(
			"strict.com. IN TXT v=spf1 mx -all\n"
		)

		result = search_for_permissive_spf_hosts(str(dns_file))

		assert result == {}

	def test_search_for_permissive_spf_hosts_case_insensitive(self, tmp_path):
		"""Test that SPF search is case-insensitive"""
		dns_file = tmp_path / "dns_records.txt"
		dns_file.write_text(
			"example.com. in txt V=SPF1 include:_spf.google.com ~ALL\n"
		)

		result = search_for_permissive_spf_hosts(str(dns_file))

		assert "example.com." in result

	def test_search_for_permissive_spf_hosts_multiple_records(self, tmp_path):
		"""Test detection of multiple permissive SPF records"""
		dns_file = tmp_path / "dns_records.txt"
		dns_file.write_text(
			"host1.com. IN TXT v=spf1 include:_spf.google.com ~all\n"
			"host2.com. IN TXT v=spf1 mx ?all\n"
			"host3.com. IN TXT v=spf1 mx -all\n"
		)

		result = search_for_permissive_spf_hosts(str(dns_file))

		assert len(result) == 2
		assert "host1.com." in result
		assert "host2.com." in result
		assert "host3.com." not in result

	def test_search_for_permissive_spf_hosts_with_ansi_codes(self, tmp_path):
		"""Test that ANSI color codes are stripped"""
		dns_file = tmp_path / "dns_records.txt"
		dns_file.write_text(
			"\x1b[32mexample.com.\x1b[0m IN TXT v=spf1 ~all\n"
		)

		result = search_for_permissive_spf_hosts(str(dns_file))

		assert "example.com." in result
		assert "\x1b" not in list(result.keys())[0]

	def test_search_for_permissive_spf_hosts_with_brackets(self, tmp_path):
		"""Test that brackets are removed from output"""
		dns_file = tmp_path / "dns_records.txt"
		dns_file.write_text(
			"[example.com.] IN TXT v=spf1 ~all\n"
		)

		result = search_for_permissive_spf_hosts(str(dns_file))

		assert "example.com." in result

	def test_search_for_permissive_spf_hosts_empty_file(self, tmp_path):
		"""Test behavior with empty DNS file"""
		dns_file = tmp_path / "dns_records.txt"
		dns_file.write_text("")

		result = search_for_permissive_spf_hosts(str(dns_file))

		assert result == {}

	def test_search_for_permissive_spf_hosts_no_txt_records(self, tmp_path):
		"""Test file with no TXT records"""
		dns_file = tmp_path / "dns_records.txt"
		dns_file.write_text(
			"example.com. IN A 192.0.2.1\n"
			"example.com. IN MX 10 mail.example.com.\n"
		)

		result = search_for_permissive_spf_hosts(str(dns_file))

		assert result == {}

	def test_search_for_permissive_spf_hosts_non_spf_txt_records(self, tmp_path):
		"""Test file with TXT records that are not SPF"""
		dns_file = tmp_path / "dns_records.txt"
		dns_file.write_text(
			"example.com. IN TXT v=DKIM1 k=rsa p=MIGfMA0...\n"
			"example.com. IN TXT google-site-verification=xyz\n"
		)

		result = search_for_permissive_spf_hosts(str(dns_file))

		assert result == {}

	def test_search_for_permissive_spf_hosts_malformed_lines(self, tmp_path):
		"""Test handling of malformed DNS lines"""
		dns_file = tmp_path / "dns_records.txt"
		dns_file.write_text(
			"malformed\n"
			"example.com. IN TXT v=spf1 ~all\n"
			"\n"
		)

		result = search_for_permissive_spf_hosts(str(dns_file))

		assert "example.com." in result
		assert len(result) == 1

	def test_search_for_permissive_spf_hosts_file_not_found(self, caplog):
		"""Test error handling when file doesn't exist"""
		with caplog.at_level(logging.ERROR):
			result = search_for_permissive_spf_hosts("/nonexistent/path/file.txt")

		assert result == {}
		assert "Error searching DNS file" in caplog.text

	def test_search_for_permissive_spf_hosts_complex_spf(self, tmp_path):
		"""Test complex SPF records with multiple mechanisms"""
		dns_file = tmp_path / "dns_records.txt"
		dns_file.write_text(
			"complex.com. IN TXT v=spf1 ip4:192.0.2.0/24 include:_spf.google.com "
			"include:sendgrid.net a mx ~all\n"
		)

		result = search_for_permissive_spf_hosts(str(dns_file))

		assert "complex.com." in result
		assert "~all" in result["complex.com."]


class TestGetHostsWithPermissiveSPF:
	"""Tests for get_hosts_with_permissive_spf function"""

	def test_get_hosts_with_permissive_spf_creates_json_file(self, tmp_path):
		"""Test that JSON file is created with correct name"""
		dns_file = tmp_path / "dns_records.txt"
		dns_file.write_text("example.com. IN TXT v=spf1 ~all\n")
		output_dir = tmp_path / "output"
		output_dir.mkdir()

		result = get_hosts_with_permissive_spf(str(dns_file), str(output_dir))

		expected_filename = f"{dt.datetime.now().strftime('%Y%m%d')}.spf_permissive_hosts.json"
		expected_path = os.path.join(str(output_dir), expected_filename)

		assert result == expected_path
		assert os.path.isfile(expected_path)

	def test_get_hosts_with_permissive_spf_json_content(self, tmp_path):
		"""Test that JSON contains correct permissive SPF hosts"""
		dns_file = tmp_path / "dns_records.txt"
		dns_file.write_text(
			"host1.com. IN TXT v=spf1 ~all\n"
			"host2.com. IN TXT v=spf1 -all\n"
		)
		output_dir = tmp_path / "output"
		output_dir.mkdir()

		get_hosts_with_permissive_spf(str(dns_file), str(output_dir))

		json_file = list(output_dir.glob("*.spf_permissive_hosts.json"))[0]
		with open(json_file, 'r') as f:
			data = json.load(f)

		assert "host1.com." in data
		assert "host2.com." not in data
		assert "v=spf1" in data["host1.com."]

	def test_get_hosts_with_permissive_spf_missing_file_logs_error(self, tmp_path, caplog):
		"""Test error handling when DNS file doesn't exist"""
		dns_file = tmp_path / "missing.txt"
		output_dir = tmp_path / "output"
		output_dir.mkdir()

		with caplog.at_level(logging.ERROR):
			result = get_hosts_with_permissive_spf(str(dns_file), str(output_dir))

		assert result is None
		assert "DNS records file" in caplog.text
		assert "not found" in caplog.text

	def test_get_hosts_with_permissive_spf_logs_info_message(self, tmp_path, caplog):
		"""Test that info message is logged"""
		dns_file = tmp_path / "dns_records.txt"
		dns_file.write_text("example.com. IN TXT v=spf1 ~all\n")
		output_dir = tmp_path / "output"
		output_dir.mkdir()

		with caplog.at_level(logging.INFO):
			get_hosts_with_permissive_spf(str(dns_file), str(output_dir))

		assert "Filtering SPF permissive candidates" in caplog.text

	def test_get_hosts_with_permissive_spf_logs_success_message(self, tmp_path, caplog):
		"""Test that success message is logged"""
		dns_file = tmp_path / "dns_records.txt"
		dns_file.write_text("example.com. IN TXT v=spf1 ~all\n")
		output_dir = tmp_path / "output"
		output_dir.mkdir()

		with caplog.at_level(logging.INFO):
			get_hosts_with_permissive_spf(str(dns_file), str(output_dir))

		assert "Permissive SPF hosts saved" in caplog.text

	def test_get_hosts_with_permissive_spf_empty_results(self, tmp_path):
		"""Test handling of empty results (no permissive SPF hosts)"""
		dns_file = tmp_path / "dns_records.txt"
		dns_file.write_text("example.com. IN TXT v=spf1 -all\n")
		output_dir = tmp_path / "output"
		output_dir.mkdir()

		result = get_hosts_with_permissive_spf(str(dns_file), str(output_dir))

		json_file = result
		with open(json_file, 'r') as f:
			data = json.load(f)

		assert data == {}

	def test_get_hosts_with_permissive_spf_json_formatting(self, tmp_path):
		"""Test that JSON is properly formatted with indentation"""
		dns_file = tmp_path / "dns_records.txt"
		dns_file.write_text(
			"host1.com. IN TXT v=spf1 ~all\n"
			"host2.com. IN TXT v=spf1 ?all\n"
		)
		output_dir = tmp_path / "output"
		output_dir.mkdir()

		get_hosts_with_permissive_spf(str(dns_file), str(output_dir))

		json_file = list(output_dir.glob("*.spf_permissive_hosts.json"))[0]
		with open(json_file, 'r') as f:
			content = f.read()

		# Check for proper indentation (4 spaces)
		assert "    " in content  # JSON should have indentation

	@patch('src.core.txtrecords.open', side_effect=IOError("Permission denied"))
	def test_get_hosts_with_permissive_spf_file_write_error(self, mock_file, tmp_path, caplog):
		"""Test error handling when JSON file cannot be written"""
		dns_file = tmp_path / "dns_records.txt"
		dns_file.write_text("example.com. IN TXT v=spf1 ~all\n")
		output_dir = tmp_path / "output"
		output_dir.mkdir()

		with caplog.at_level(logging.ERROR):
			result = get_hosts_with_permissive_spf(str(dns_file), str(output_dir))

		assert "Error saving permissive SPF hosts" in caplog.text or result is None

	def test_get_hosts_with_permissive_spf_returns_correct_path_format(self, tmp_path):
		"""Test that returned path uses correct date format"""
		dns_file = tmp_path / "dns_records.txt"
		dns_file.write_text("example.com. IN TXT v=spf1 ~all\n")
		output_dir = tmp_path / "output"
		output_dir.mkdir()

		result = get_hosts_with_permissive_spf(str(dns_file), str(output_dir))

		# Path should contain YYYYMMDD format
		assert result is not None
		assert re.search(r'\d{8}\.spf_permissive_hosts\.json', result)

	def test_get_hosts_with_permissive_spf_multiple_calls_same_day(self, tmp_path):
		"""Test that multiple calls on same day overwrite the file"""
		dns_file = tmp_path / "dns_records.txt"
		dns_file.write_text("example.com. IN TXT v=spf1 ~all\n")
		output_dir = tmp_path / "output"
		output_dir.mkdir()

		result1 = get_hosts_with_permissive_spf(str(dns_file), str(output_dir))
		result2 = get_hosts_with_permissive_spf(str(dns_file), str(output_dir))

		assert result1 == result2
		# Check that only one file exists
		assert len(list(output_dir.glob("*.spf_permissive_hosts.json"))) == 1


import re
