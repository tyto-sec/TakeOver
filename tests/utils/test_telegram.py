import os
import logging
from unittest.mock import patch, MagicMock, call
import datetime as dt

import pytest
import requests

from src.utils.telegram import get_telegram_config, send_telegram_message


class TestGetTelegramConfig:
	"""Tests for get_telegram_config function"""

	def test_get_telegram_config_returns_tuple(self):
		"""Test that function returns a tuple"""
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'token123', 'TELEGRAM_CHAT_ID': '12345'}):
			result = get_telegram_config()
			assert isinstance(result, tuple)
			assert len(result) == 2

	def test_get_telegram_config_returns_correct_values(self):
		"""Test that function returns correct token and chat_id"""
		token = 'test_token_xyz'
		chat_id = 'test_chat_123'
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': token, 'TELEGRAM_CHAT_ID': chat_id}):
			bot_token, returned_chat_id = get_telegram_config()
			assert bot_token == token
			assert returned_chat_id == chat_id

	def test_get_telegram_config_missing_bot_token_raises_error(self):
		"""Test that missing TELEGRAM_BOT_TOKEN raises ValueError"""
		with patch.dict(os.environ, {'TELEGRAM_CHAT_ID': '12345'}, clear=True):
			with pytest.raises(ValueError) as exc_info:
				get_telegram_config()
			assert "TELEGRAM_BOT_TOKEN" in str(exc_info.value)

	def test_get_telegram_config_missing_chat_id_raises_error(self):
		"""Test that missing TELEGRAM_CHAT_ID raises ValueError"""
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'token'}, clear=True):
			with pytest.raises(ValueError) as exc_info:
				get_telegram_config()
			assert "TELEGRAM_CHAT_ID" in str(exc_info.value)

	def test_get_telegram_config_both_missing_raises_error(self):
		"""Test that missing both variables raises ValueError"""
		with patch.dict(os.environ, {}, clear=True):
			with pytest.raises(ValueError) as exc_info:
				get_telegram_config()
			assert "TELEGRAM_BOT_TOKEN" in str(exc_info.value) or "TELEGRAM_CHAT_ID" in str(exc_info.value)

	def test_get_telegram_config_empty_bot_token_raises_error(self):
		"""Test that empty TELEGRAM_BOT_TOKEN raises ValueError"""
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': '', 'TELEGRAM_CHAT_ID': '12345'}):
			with pytest.raises(ValueError):
				get_telegram_config()

	def test_get_telegram_config_empty_chat_id_raises_error(self):
		"""Test that empty TELEGRAM_CHAT_ID raises ValueError"""
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'token', 'TELEGRAM_CHAT_ID': ''}):
			with pytest.raises(ValueError):
				get_telegram_config()

	def test_get_telegram_config_with_special_characters(self):
		"""Test config with special characters in token and chat_id"""
		token = 'token_with-special.chars_123'
		chat_id = '-987654321'
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': token, 'TELEGRAM_CHAT_ID': chat_id}):
			bot_token, returned_chat_id = get_telegram_config()
			assert bot_token == token
			assert returned_chat_id == chat_id

	def test_get_telegram_config_with_whitespace(self):
		"""Test that config values with whitespace are returned as-is"""
		token = 'token with spaces'
		chat_id = '123 456'
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': token, 'TELEGRAM_CHAT_ID': chat_id}):
			bot_token, returned_chat_id = get_telegram_config()
			assert bot_token == token
			assert returned_chat_id == chat_id

	def test_get_telegram_config_error_message_mentions_both_vars(self):
		"""Test that error message mentions both required variables"""
		with patch.dict(os.environ, {}, clear=True):
			with pytest.raises(ValueError) as exc_info:
				get_telegram_config()
			error_msg = str(exc_info.value)
			assert "TELEGRAM_BOT_TOKEN" in error_msg
			assert "TELEGRAM_CHAT_ID" in error_msg


class TestSendTelegramMessage:
	"""Tests for send_telegram_message function"""

	def test_send_telegram_message_success(self):
		"""Test successful message sending"""
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'token123', 'TELEGRAM_CHAT_ID': '12345'}):
			with patch('requests.post') as mock_post:
				mock_response = MagicMock()
				mock_response.raise_for_status = MagicMock()
				mock_post.return_value = mock_response

				result = send_telegram_message("Test message")

				assert result is True
				mock_post.assert_called_once()

	def test_send_telegram_message_logs_success(self, caplog):
		"""Test that success is logged"""
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'token123', 'TELEGRAM_CHAT_ID': '12345'}):
			with patch('requests.post') as mock_post:
				mock_response = MagicMock()
				mock_response.raise_for_status = MagicMock()
				mock_post.return_value = mock_response

				with caplog.at_level(logging.INFO):
					send_telegram_message("Test message")

				assert "Telegram message sent successfully" in caplog.text

	def test_send_telegram_message_constructs_correct_url(self):
		"""Test that correct API URL is constructed"""
		token = 'test_token'
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': token, 'TELEGRAM_CHAT_ID': '12345'}):
			with patch('requests.post') as mock_post:
				mock_response = MagicMock()
				mock_response.raise_for_status = MagicMock()
				mock_post.return_value = mock_response

				send_telegram_message("Test")

				expected_url = f"https://api.telegram.org/bot{token}/sendMessage"
				actual_url = mock_post.call_args[0][0]
				assert actual_url == expected_url

	def test_send_telegram_message_sends_correct_payload(self):
		"""Test that correct payload is sent"""
		chat_id = '98765'
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'token', 'TELEGRAM_CHAT_ID': chat_id}):
			with patch('requests.post') as mock_post:
				mock_response = MagicMock()
				mock_response.raise_for_status = MagicMock()
				mock_post.return_value = mock_response

				message = "Test message"
				send_telegram_message(message)

				payload = mock_post.call_args[1]['json']
				assert payload['chat_id'] == chat_id
				assert message in payload['text']

	def test_send_telegram_message_includes_timestamp(self):
		"""Test that timestamp is included in message"""
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'token', 'TELEGRAM_CHAT_ID': '12345'}):
			with patch('requests.post') as mock_post:
				mock_response = MagicMock()
				mock_response.raise_for_status = MagicMock()
				mock_post.return_value = mock_response

				send_telegram_message("Test")

				payload = mock_post.call_args[1]['json']
				text = payload['text']
				assert "[" in text
				assert "]" in text
				assert "TakeOver Alert:" in text

	def test_send_telegram_message_timestamp_format(self):
		"""Test that timestamp has correct format YYYY-MM-DD HH:MM:SS"""
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'token', 'TELEGRAM_CHAT_ID': '12345'}):
			with patch('requests.post') as mock_post:
				mock_response = MagicMock()
				mock_response.raise_for_status = MagicMock()
				mock_post.return_value = mock_response

				send_telegram_message("Test")

				payload = mock_post.call_args[1]['json']
				text = payload['text']
				# Check for timestamp pattern YYYY-MM-DD HH:MM:SS
				import re
				pattern = r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]'
				assert re.search(pattern, text) is not None

	def test_send_telegram_message_uses_timeout(self):
		"""Test that timeout is set to 10 seconds"""
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'token', 'TELEGRAM_CHAT_ID': '12345'}):
			with patch('requests.post') as mock_post:
				mock_response = MagicMock()
				mock_response.raise_for_status = MagicMock()
				mock_post.return_value = mock_response

				send_telegram_message("Test")

				assert mock_post.call_args[1]['timeout'] == 10

	def test_send_telegram_message_returns_false_on_value_error(self, caplog):
		"""Test that False is returned when config is missing"""
		with patch.dict(os.environ, {}, clear=True):
			with caplog.at_level(logging.ERROR):
				result = send_telegram_message("Test")

			assert result is False
			assert "TELEGRAM_BOT_TOKEN" in caplog.text or "TELEGRAM_CHAT_ID" in caplog.text

	def test_send_telegram_message_returns_false_on_http_error(self, caplog):
		"""Test that False is returned on HTTP error"""
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'token', 'TELEGRAM_CHAT_ID': '12345'}):
			with patch('requests.post') as mock_post:
				mock_response = MagicMock()
				mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
				mock_post.return_value = mock_response

				with caplog.at_level(logging.ERROR):
					result = send_telegram_message("Test")

				assert result is False
				assert "Error sending Telegram message" in caplog.text

	def test_send_telegram_message_returns_false_on_timeout(self, caplog):
		"""Test that False is returned on timeout"""
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'token', 'TELEGRAM_CHAT_ID': '12345'}):
			with patch('requests.post') as mock_post:
				mock_post.side_effect = requests.exceptions.Timeout("Request timed out")

				with caplog.at_level(logging.ERROR):
					result = send_telegram_message("Test")

				assert result is False
				assert "Error sending Telegram message" in caplog.text

	def test_send_telegram_message_returns_false_on_connection_error(self, caplog):
		"""Test that False is returned on connection error"""
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'token', 'TELEGRAM_CHAT_ID': '12345'}):
			with patch('requests.post') as mock_post:
				mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")

				with caplog.at_level(logging.ERROR):
					result = send_telegram_message("Test")

				assert result is False
				assert "Error sending Telegram message" in caplog.text

	def test_send_telegram_message_returns_false_on_generic_exception(self, caplog):
		"""Test that False is returned on generic exception"""
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'token', 'TELEGRAM_CHAT_ID': '12345'}):
			with patch('requests.post') as mock_post:
				mock_post.side_effect = Exception("Unexpected error")

				with caplog.at_level(logging.ERROR):
					result = send_telegram_message("Test")

				assert result is False
				assert "Error sending Telegram message" in caplog.text

	def test_send_telegram_message_with_empty_message(self):
		"""Test sending empty message"""
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'token', 'TELEGRAM_CHAT_ID': '12345'}):
			with patch('requests.post') as mock_post:
				mock_response = MagicMock()
				mock_response.raise_for_status = MagicMock()
				mock_post.return_value = mock_response

				result = send_telegram_message("")

				assert result is True
				payload = mock_post.call_args[1]['json']
				assert "TakeOver Alert:" in payload['text']

	def test_send_telegram_message_with_multiline_message(self):
		"""Test sending multiline message"""
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'token', 'TELEGRAM_CHAT_ID': '12345'}):
			with patch('requests.post') as mock_post:
				mock_response = MagicMock()
				mock_response.raise_for_status = MagicMock()
				mock_post.return_value = mock_response

				message = "Line 1\nLine 2\nLine 3"
				result = send_telegram_message(message)

				assert result is True
				payload = mock_post.call_args[1]['json']
				assert "Line 1" in payload['text']
				assert "Line 2" in payload['text']

	def test_send_telegram_message_with_special_characters(self):
		"""Test sending message with special characters"""
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'token', 'TELEGRAM_CHAT_ID': '12345'}):
			with patch('requests.post') as mock_post:
				mock_response = MagicMock()
				mock_response.raise_for_status = MagicMock()
				mock_post.return_value = mock_response

				message = "Test !@#$%^&*()[]{}|\\:;\"'`~"
				result = send_telegram_message(message)

				assert result is True
				payload = mock_post.call_args[1]['json']
				assert message in payload['text']

	def test_send_telegram_message_with_long_message(self):
		"""Test sending very long message"""
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'token', 'TELEGRAM_CHAT_ID': '12345'}):
			with patch('requests.post') as mock_post:
				mock_response = MagicMock()
				mock_response.raise_for_status = MagicMock()
				mock_post.return_value = mock_response

				long_message = "A" * 5000
				result = send_telegram_message(long_message)

				assert result is True
				payload = mock_post.call_args[1]['json']
				assert long_message in payload['text']

	def test_send_telegram_message_uses_json_parameter(self):
		"""Test that requests.post uses json parameter"""
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'token', 'TELEGRAM_CHAT_ID': '12345'}):
			with patch('requests.post') as mock_post:
				mock_response = MagicMock()
				mock_response.raise_for_status = MagicMock()
				mock_post.return_value = mock_response

				send_telegram_message("Test")

				# Verify json parameter is used
				assert 'json' in mock_post.call_args[1]
				assert mock_post.call_args[1]['json'] is not None

	def test_send_telegram_message_value_error_logs_error_message(self, caplog):
		"""Test that ValueError details are logged"""
		error_msg = "Custom error message"
		with patch.dict(os.environ, {}, clear=True):
			with patch('src.utils.telegram.get_telegram_config', side_effect=ValueError(error_msg)):
				with caplog.at_level(logging.ERROR):
					send_telegram_message("Test")
				assert error_msg in caplog.text

	def test_send_telegram_message_generic_exception_logs_details(self, caplog):
		"""Test that generic exception details are logged"""
		error_msg = "Connection failed"
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'token', 'TELEGRAM_CHAT_ID': '12345'}):
			with patch('requests.post', side_effect=Exception(error_msg)):
				with caplog.at_level(logging.ERROR):
					send_telegram_message("Test")
				assert error_msg in caplog.text

	def test_send_telegram_message_raise_for_status_called(self):
		"""Test that raise_for_status is called to check for errors"""
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'token', 'TELEGRAM_CHAT_ID': '12345'}):
			with patch('requests.post') as mock_post:
				mock_response = MagicMock()
				mock_post.return_value = mock_response

				send_telegram_message("Test")

				mock_response.raise_for_status.assert_called_once()

	def test_send_telegram_message_multiple_calls_independent(self):
		"""Test that multiple calls are independent"""
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'token', 'TELEGRAM_CHAT_ID': '12345'}):
			with patch('requests.post') as mock_post:
				mock_response = MagicMock()
				mock_response.raise_for_status = MagicMock()
				mock_post.return_value = mock_response

				result1 = send_telegram_message("Message 1")
				result2 = send_telegram_message("Message 2")

				assert result1 is True
				assert result2 is True
				assert mock_post.call_count == 2


class TestIntegration:
	"""Integration tests for telegram module"""

	def test_send_message_workflow(self):
		"""Test complete workflow from config to sending message"""
		token = 'integration_test_token'
		chat_id = '999888'
		with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': token, 'TELEGRAM_CHAT_ID': chat_id}):
			with patch('requests.post') as mock_post:
				mock_response = MagicMock()
				mock_response.raise_for_status = MagicMock()
				mock_post.return_value = mock_response

				# Get config
				bot_token, chat_id_result = get_telegram_config()
				assert bot_token == token

				# Send message
				result = send_telegram_message("Integration test message")
				assert result is True

	def test_config_error_prevents_message_sending(self):
		"""Test that missing config prevents message sending"""
		with patch.dict(os.environ, {}, clear=True):
			result = send_telegram_message("Test")
			assert result is False
