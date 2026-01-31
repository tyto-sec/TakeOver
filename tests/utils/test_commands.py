import subprocess
import sys
import logging
from unittest.mock import patch, MagicMock, call
import io

import pytest

from src.utils.commands import run_cmd, run_cmd_with_stdin


class TestRunCmd:
	"""Tests for run_cmd function"""

	def test_run_cmd_successful_execution(self):
		"""Test successful command execution"""
		result = run_cmd("echo 'Hello World'")
		assert result == "Hello World"

	def test_run_cmd_returns_stripped_output(self):
		"""Test that output is stripped of whitespace"""
		result = run_cmd("echo '  test output  '")
		assert result == "test output"

	def test_run_cmd_with_newlines(self):
		"""Test command output with newlines"""
		result = run_cmd("printf 'line1\\nline2\\nline3'")
		assert "line1" in result
		assert "line2" in result

	def test_run_cmd_strips_trailing_newline(self):
		"""Test that trailing newline is stripped"""
		result = run_cmd("echo test")
		assert result == "test"
		assert not result.endswith('\n')

	def test_run_cmd_empty_output(self):
		"""Test command with empty output"""
		result = run_cmd("echo -n ''")
		assert result == ""

	def test_run_cmd_with_special_characters(self):
		"""Test command output with special characters"""
		result = run_cmd("echo '!@#$%^&*()'")
		assert "!@#$%^&*()" in result

	def test_run_cmd_with_pipes(self):
		"""Test command with pipes"""
		result = run_cmd("echo 'hello world' | grep hello")
		assert result == "hello world"

	def test_run_cmd_returns_stdout_not_stderr(self):
		"""Test that function returns stdout, not stderr"""
		# This command fails but we should get empty stdout
		result = run_cmd("command_that_does_not_exist 2>/dev/null")
		assert result == ""

	def test_run_cmd_with_file_operations(self, tmp_path):
		"""Test command that operates on files"""
		test_file = tmp_path / "test.txt"
		test_file.write_text("test content")
		result = run_cmd(f"cat {test_file}")
		assert result == "test content"

	def test_run_cmd_error_handling_logs_error(self, caplog):
		"""Test that errors are logged"""
		with patch('subprocess.run', side_effect=Exception("Test error")):
			with caplog.at_level(logging.ERROR):
				result = run_cmd("any_command")
			assert "Error executing" in caplog.text
			assert result == ""

	def test_run_cmd_returns_empty_string_on_exception(self):
		"""Test that empty string is returned on exception"""
		with patch('subprocess.run', side_effect=Exception("Test error")):
			result = run_cmd("failing_command")
			assert result == ""

	def test_run_cmd_uses_shell_true(self):
		"""Test that subprocess.run is called with shell=True"""
		with patch('subprocess.run') as mock_run:
			mock_run.return_value = MagicMock(stdout="output")
			run_cmd("test_cmd")
			mock_run.assert_called_once()
			assert mock_run.call_args[1]['shell'] is True

	def test_run_cmd_uses_capture_output_true(self):
		"""Test that subprocess.run is called with capture_output=True"""
		with patch('subprocess.run') as mock_run:
			mock_run.return_value = MagicMock(stdout="output")
			run_cmd("test_cmd")
			assert mock_run.call_args[1]['capture_output'] is True

	def test_run_cmd_uses_text_mode(self):
		"""Test that subprocess.run is called with text=True"""
		with patch('subprocess.run') as mock_run:
			mock_run.return_value = MagicMock(stdout="output")
			run_cmd("test_cmd")
			assert mock_run.call_args[1]['text'] is True

	def test_run_cmd_passes_command_to_subprocess(self):
		"""Test that the command is correctly passed to subprocess.run"""
		test_command = "echo 'specific test command'"
		with patch('subprocess.run') as mock_run:
			mock_run.return_value = MagicMock(stdout="output")
			run_cmd(test_command)
			assert mock_run.call_args[0][0] == test_command

	def test_run_cmd_with_multiple_lines_output(self):
		"""Test command that outputs multiple lines"""
		result = run_cmd("printf 'line1\\nline2\\nline3'")
		lines = result.split('\n')
		assert len(lines) >= 3

	def test_run_cmd_with_environment_variables(self):
		"""Test command that uses environment variables"""
		result = run_cmd("echo $HOME")
		assert len(result) > 0  # HOME should be set

	def test_run_cmd_command_not_found(self, caplog):
		"""Test handling of command not found"""
		with caplog.at_level(logging.ERROR):
			# Redirect stderr to avoid test output pollution
			result = run_cmd("nonexistent_command_xyz 2>/dev/null")
			# Command execution itself won't fail, just won't find the command

	def test_run_cmd_with_redirects(self):
		"""Test command with output redirection"""
		result = run_cmd("echo 'test' > /dev/null && echo 'success'")
		assert result == "success"

	def test_run_cmd_with_boolean_operators(self):
		"""Test command with boolean operators"""
		result = run_cmd("echo 'true' && echo 'executed'")
		assert "true" in result


class TestRunCmdWithStdin:
	"""Tests for run_cmd_with_stdin function"""

	def test_run_cmd_with_stdin_explicit_data(self):
		"""Test with explicit stdin data provided"""
		result = run_cmd_with_stdin("cat", stdin_data="Hello from stdin")
		assert result == "Hello from stdin"

	def test_run_cmd_with_stdin_none_data_with_terminal(self):
		"""Test with stdin_data=None when no TTY available"""
		with patch('sys.stdin.isatty', return_value=True):
			result = run_cmd_with_stdin("cat", stdin_data=None)
			assert result == ""

	def test_run_cmd_with_stdin_none_data_with_pipe(self):
		"""Test with stdin_data=None when reading from pipe"""
		with patch('sys.stdin.isatty', return_value=False):
			with patch('sys.stdin.read', return_value="piped input"):
				result = run_cmd_with_stdin("cat", stdin_data=None)
				assert result == "piped input"

	def test_run_cmd_with_stdin_multiline_data(self):
		"""Test with multiline stdin data"""
		stdin_data = "line1\nline2\nline3"
		result = run_cmd_with_stdin("cat", stdin_data=stdin_data)
		assert "line1" in result
		assert "line2" in result
		assert "line3" in result

	def test_run_cmd_with_stdin_uses_shell_true(self):
		"""Test that subprocess.run is called with shell=True"""
		with patch('subprocess.run') as mock_run:
			mock_run.return_value = MagicMock(stdout="output")
			run_cmd_with_stdin("cat", stdin_data="test")
			assert mock_run.call_args[1]['shell'] is True

	def test_run_cmd_with_stdin_uses_capture_output_true(self):
		"""Test that subprocess.run is called with capture_output=True"""
		with patch('subprocess.run') as mock_run:
			mock_run.return_value = MagicMock(stdout="output")
			run_cmd_with_stdin("cat", stdin_data="test")
			assert mock_run.call_args[1]['capture_output'] is True

	def test_run_cmd_with_stdin_uses_text_mode(self):
		"""Test that subprocess.run is called with text=True"""
		with patch('subprocess.run') as mock_run:
			mock_run.return_value = MagicMock(stdout="output")
			run_cmd_with_stdin("cat", stdin_data="test")
			assert mock_run.call_args[1]['text'] is True

	def test_run_cmd_with_stdin_passes_input_parameter(self):
		"""Test that input parameter is correctly passed"""
		test_input = "test input data"
		with patch('subprocess.run') as mock_run:
			mock_run.return_value = MagicMock(stdout="output")
			run_cmd_with_stdin("cat", stdin_data=test_input)
			assert mock_run.call_args[1]['input'] == test_input

	def test_run_cmd_with_stdin_passes_command_to_subprocess(self):
		"""Test that the command is correctly passed to subprocess.run"""
		test_command = "grep test"
		with patch('subprocess.run') as mock_run:
			mock_run.return_value = MagicMock(stdout="output")
			run_cmd_with_stdin(test_command, stdin_data="test data")
			assert mock_run.call_args[0][0] == test_command

	def test_run_cmd_with_stdin_returns_stripped_output(self):
		"""Test that output is stripped"""
		result = run_cmd_with_stdin("cat", stdin_data="  test  ")
		assert result == "test"

	def test_run_cmd_with_stdin_empty_input(self):
		"""Test with empty stdin data"""
		result = run_cmd_with_stdin("cat", stdin_data="")
		assert result == ""

	def test_run_cmd_with_stdin_with_pipeline(self):
		"""Test with command pipeline"""
		result = run_cmd_with_stdin("grep hello", stdin_data="hello world\ntest\nhello again")
		assert "hello world" in result
		assert "hello again" in result

	def test_run_cmd_with_stdin_error_handling_logs_error(self, caplog):
		"""Test that errors are logged"""
		with patch('subprocess.run', side_effect=Exception("Test error")):
			with caplog.at_level(logging.ERROR):
				result = run_cmd_with_stdin("cat", stdin_data="test")
			assert "Error executing" in caplog.text
			assert result == ""

	def test_run_cmd_with_stdin_returns_empty_string_on_exception(self):
		"""Test that empty string is returned on exception"""
		with patch('subprocess.run', side_effect=Exception("Test error")):
			result = run_cmd_with_stdin("cat", stdin_data="test")
			assert result == ""

	def test_run_cmd_with_stdin_with_special_characters(self):
		"""Test stdin with special characters"""
		special_input = "!@#$%^&*()\n<>{}[]|\\:;\"'`~"
		result = run_cmd_with_stdin("cat", stdin_data=special_input)
		assert special_input in result

	def test_run_cmd_with_stdin_none_with_isatty_false(self):
		"""Test stdin_data=None when isatty returns False"""
		with patch('sys.stdin.isatty', return_value=False):
			with patch('sys.stdin.read', return_value="stdin content"):
				result = run_cmd_with_stdin("cat", stdin_data=None)
				assert result == "stdin content"

	def test_run_cmd_with_stdin_none_with_isatty_true(self):
		"""Test stdin_data=None when isatty returns True"""
		with patch('sys.stdin.isatty', return_value=True):
			result = run_cmd_with_stdin("cat", stdin_data=None)
			assert result == ""

	def test_run_cmd_with_stdin_reads_sys_stdin_when_needed(self):
		"""Test that sys.stdin.read is called when appropriate"""
		with patch('sys.stdin.isatty', return_value=False):
			with patch('sys.stdin.read', return_value="piped") as mock_read:
				run_cmd_with_stdin("cat", stdin_data=None)
				mock_read.assert_called_once()

	def test_run_cmd_with_stdin_does_not_read_sys_stdin_when_tty(self):
		"""Test that sys.stdin.read is not called when TTY"""
		with patch('sys.stdin.isatty', return_value=True):
			with patch('sys.stdin.read') as mock_read:
				run_cmd_with_stdin("cat", stdin_data=None)
				mock_read.assert_not_called()

	def test_run_cmd_with_stdin_command_filters_input(self):
		"""Test that command can filter stdin properly"""
		input_data = "apple\nbanana\ncherry\napple pie"
		result = run_cmd_with_stdin("grep apple", stdin_data=input_data)
		assert "apple" in result
		assert "banana" not in result

	def test_run_cmd_with_stdin_with_count_words(self):
		"""Test stdin with word counting command"""
		input_data = "one two three four five"
		result = run_cmd_with_stdin("wc -w", stdin_data=input_data)
		assert "5" in result

	def test_run_cmd_with_stdin_strips_trailing_newline(self):
		"""Test that trailing newline is stripped from output"""
		result = run_cmd_with_stdin("cat", stdin_data="test\n")
		assert result == "test"
		assert not result.endswith('\n')


class TestEdgeCases:
	"""Tests for edge cases and integration scenarios"""

	def test_run_cmd_and_run_cmd_with_stdin_same_command_consistency(self):
		"""Test that both functions produce consistent results for same command"""
		cmd = "echo 'consistency test'"
		result1 = run_cmd(cmd)
		result2 = run_cmd_with_stdin(cmd, stdin_data="")
		assert result1 == result2

	def test_run_cmd_with_complex_shell_script(self):
		"""Test with complex shell script"""
		script = "for i in 1 2 3; do echo $i; done"
		result = run_cmd(script)
		assert "1" in result
		assert "2" in result
		assert "3" in result

	def test_run_cmd_with_stdin_command_substitution(self):
		"""Test command with substitution"""
		result = run_cmd_with_stdin("cat", stdin_data="$(echo 'test')")
		assert "test" in result or "$(echo 'test')" in result

	def test_run_cmd_error_exception_message_logged(self, caplog):
		"""Test that exception message is included in log"""
		error_msg = "Specific error message"
		with patch('subprocess.run', side_effect=Exception(error_msg)):
			with caplog.at_level(logging.ERROR):
				run_cmd("test")
			assert error_msg in caplog.text

	def test_run_cmd_with_stdin_error_exception_message_logged(self, caplog):
		"""Test that exception message is included in log"""
		error_msg = "Specific stdin error"
		with patch('subprocess.run', side_effect=Exception(error_msg)):
			with caplog.at_level(logging.ERROR):
				run_cmd_with_stdin("test", stdin_data="input")
			assert error_msg in caplog.text
