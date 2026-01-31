import json
import logging
import builtins

import pytest

from src.utils.txtfiles import (
	read_lines,
	concatenate_files,
	convert_json_keys_to_txt,
	add_protocol_to_hosts,
)


class TestReadLines:
	def test_read_lines_strips_and_skips_empty(self, tmp_path):
		file_path = tmp_path / "input.txt"
		file_path.write_text(" line1 \n\nline2\n   \nline3\n")

		result = read_lines(str(file_path))

		assert result == ["line1", "line2", "line3"]

	def test_read_lines_empty_file(self, tmp_path):
		file_path = tmp_path / "empty.txt"
		file_path.write_text("")

		result = read_lines(str(file_path))

		assert result == []


class TestConcatenateFiles:
	def test_concatenate_files_returns_sorted_unique_lines(self, tmp_path):
		file_a = tmp_path / "a.txt"
		file_b = tmp_path / "b.txt"
		file_a.write_text("b\na\n")
		file_b.write_text("a\nc\n")

		result = concatenate_files([str(file_a), str(file_b)])

		assert result == ["a", "b", "c"]

	def test_concatenate_files_ignores_blank_lines(self, tmp_path):
		file_a = tmp_path / "a.txt"
		file_b = tmp_path / "b.txt"
		file_a.write_text("a\n\n")
		file_b.write_text("\n\nb\n")

		result = concatenate_files([str(file_a), str(file_b)])

		assert result == ["a", "b"]

	def test_concatenate_files_missing_file_logs_error(self, tmp_path, caplog):
		file_a = tmp_path / "a.txt"
		file_a.write_text("a\n")
		missing = tmp_path / "missing.txt"

		with caplog.at_level(logging.ERROR):
			result = concatenate_files([str(file_a), str(missing)])

		assert result == ["a"]
		assert "File not found" in caplog.text

	def test_concatenate_files_writes_output_file(self, tmp_path, caplog):
		file_a = tmp_path / "a.txt"
		file_b = tmp_path / "b.txt"
		file_a.write_text("b\na\n")
		file_b.write_text("c\n")
		output_file = tmp_path / "out.txt"

		with caplog.at_level(logging.INFO):
			result = concatenate_files([str(file_a), str(file_b)], output_file=str(output_file))

		assert result == str(output_file)
		assert output_file.read_text() == "a\nb\nc\n"
		assert "Files concatenated and saved" in caplog.text

	def test_concatenate_files_output_file_returns_path_on_write_error(self, tmp_path, caplog):
		file_a = tmp_path / "a.txt"
		file_a.write_text("a\n")
		output_file = tmp_path / "out.txt"

		real_open = builtins.open

		def fake_open(path, mode='r', *args, **kwargs):
			if path == str(output_file) and 'w' in mode:
				raise IOError("write error")
			return real_open(path, mode, *args, **kwargs)

		with caplog.at_level(logging.ERROR):
			with pytest.MonkeyPatch().context() as mp:
				mp.setattr("builtins.open", fake_open)
				result = concatenate_files([str(file_a)], output_file=str(output_file))

		assert result == str(output_file)
		assert "Error saving file" in caplog.text


class TestConvertJsonKeysToTxt:
	def test_convert_json_keys_to_txt_writes_keys(self, tmp_path, caplog):
		json_file = tmp_path / "data.json"
		json_file.write_text(json.dumps({"b": 2, "a": 1}))
		output_file = tmp_path / "keys.txt"

		with caplog.at_level(logging.INFO):
			convert_json_keys_to_txt(str(json_file), str(output_file))

		lines = [line.strip() for line in output_file.read_text().splitlines()]
		assert set(lines) == {"a", "b"}
		assert "JSON keys saved" in caplog.text

	def test_convert_json_keys_to_txt_logs_error_on_invalid_json(self, tmp_path, caplog):
		json_file = tmp_path / "bad.json"
		json_file.write_text("{not-json}")
		output_file = tmp_path / "keys.txt"

		with caplog.at_level(logging.ERROR):
			convert_json_keys_to_txt(str(json_file), str(output_file))

		assert "Error converting JSON to TXT" in caplog.text


class TestAddProtocolToHosts:
	def test_add_protocol_to_hosts_adds_protocol(self, tmp_path, caplog):
		input_file = tmp_path / "hosts.txt"
		input_file.write_text("example.com\nhttp://already.com\nhttps://secure.com\n")
		output_file = tmp_path / "out.txt"

		with caplog.at_level(logging.INFO):
			count = add_protocol_to_hosts(str(input_file), str(output_file), protocol="https")

		assert count == 3
		lines = [line.strip() for line in output_file.read_text().splitlines()]
		assert lines == [
			"https://example.com",
			"http://already.com",
			"https://secure.com",
		]
		assert "Added https:// protocol" in caplog.text

	def test_add_protocol_to_hosts_uses_custom_protocol(self, tmp_path):
		input_file = tmp_path / "hosts.txt"
		input_file.write_text("example.com\n")
		output_file = tmp_path / "out.txt"

		count = add_protocol_to_hosts(str(input_file), str(output_file), protocol="http")

		assert count == 1
		assert output_file.read_text().strip() == "http://example.com"

	def test_add_protocol_to_hosts_warns_on_empty_input(self, tmp_path, caplog):
		input_file = tmp_path / "hosts.txt"
		input_file.write_text("")
		output_file = tmp_path / "out.txt"

		with caplog.at_level(logging.WARNING):
			count = add_protocol_to_hosts(str(input_file), str(output_file))

		assert count == 0
		assert "No hosts found" in caplog.text

	def test_add_protocol_to_hosts_returns_none_on_error(self, tmp_path, caplog, monkeypatch):
		input_file = tmp_path / "hosts.txt"
		input_file.write_text("example.com\n")
		output_file = tmp_path / "out.txt"

		def raise_error(*args, **kwargs):
			raise IOError("boom")

		monkeypatch.setattr("builtins.open", raise_error)

		with caplog.at_level(logging.ERROR):
			result = add_protocol_to_hosts(str(input_file), str(output_file))

		assert result is None
		assert "Error adding protocol to hosts" in caplog.text
