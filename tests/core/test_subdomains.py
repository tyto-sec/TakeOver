import os
import pytest
import logging
from unittest.mock import patch, MagicMock
from datetime import datetime as dt

from src.core.subdomains import subfinder_enum, chaos_enum, subdomain_enum


class TestSubfinderEnum:
    def test_subfinder_enum_success(self, tmp_path, monkeypatch, caplog):
        """Test successful subfinder enumeration"""
        domain = "example.com"
        output_dir = tmp_path / "subdomains"
        output_dir.mkdir()
        
        mock_subdomains = "sub1.example.com\nsub2.example.com\nsub3.example.com"
        
        def fake_run_cmd(cmd):
            assert "subfinder" in cmd
            assert domain in cmd
            assert "-silent" in cmd
            return mock_subdomains
        
        def fake_clean_domain(line):
            return line.strip()
        
        monkeypatch.setattr("src.core.subdomains.run_cmd", fake_run_cmd)
        monkeypatch.setattr("src.core.subdomains.clean_domain", fake_clean_domain)
        
        result = subfinder_enum(domain, str(output_dir))
        
        assert result.endswith(".subfinder.subdomains.txt")
        assert os.path.exists(result)
        
        with open(result, "r") as f:
            content = f.read()
            assert "sub1.example.com" in content
            assert "sub2.example.com" in content
            assert "sub3.example.com" in content
    
    def test_subfinder_enum_no_results(self, tmp_path, monkeypatch, caplog):
        """Test subfinder enumeration with no results"""
        domain = "example.com"
        output_dir = tmp_path / "subdomains"
        output_dir.mkdir()
        
        def fake_run_cmd(cmd):
            return ""
        
        def fake_clean_domain(line):
            return line
        
        monkeypatch.setattr("src.core.subdomains.run_cmd", fake_run_cmd)
        monkeypatch.setattr("src.core.subdomains.clean_domain", fake_clean_domain)
        
        result = subfinder_enum(domain, str(output_dir))
        
        assert result.endswith(".subfinder.subdomains.txt")
        # File should not be created if no results
        assert not os.path.exists(result)
    
    def test_subfinder_enum_command_format(self, tmp_path, monkeypatch):
        """Test that subfinder command is formatted correctly"""
        domain = "test.org"
        output_dir = tmp_path / "subdomains"
        output_dir.mkdir()
        
        captured_cmd = []
        
        def fake_run_cmd(cmd):
            captured_cmd.append(cmd)
            return "test1.test.org"
        
        def fake_clean_domain(line):
            return line
        
        monkeypatch.setattr("src.core.subdomains.run_cmd", fake_run_cmd)
        monkeypatch.setattr("src.core.subdomains.clean_domain", fake_clean_domain)
        
        subfinder_enum(domain, str(output_dir))
        
        assert len(captured_cmd) > 0
        assert "subfinder" in captured_cmd[0]
        assert f"-d {domain}" in captured_cmd[0]
        assert "-silent" in captured_cmd[0]


class TestChaosEnum:
    def test_chaos_enum_with_api_key(self, tmp_path, monkeypatch, caplog):
        """Test chaos enumeration with PDCP_API_KEY present"""
        domain = "example.com"
        output_dir = tmp_path / "subdomains"
        output_dir.mkdir()
        
        mock_subdomains = "chaos1.example.com\nchaos2.example.com"
        api_key = "test-api-key-12345"
        
        monkeypatch.setenv("PDCP_API_KEY", api_key)
        
        def fake_run_cmd(cmd):
            assert "chaos" in cmd
            assert domain in cmd
            return mock_subdomains
        
        def fake_clean_domain(line):
            return line.strip()
        
        monkeypatch.setattr("src.core.subdomains.run_cmd", fake_run_cmd)
        monkeypatch.setattr("src.core.subdomains.clean_domain", fake_clean_domain)
        
        with caplog.at_level(logging.DEBUG):
            result = chaos_enum(domain, str(output_dir))
        
        assert result.endswith(".chaos.subdomains.txt")
        assert os.path.exists(result)
        assert "API_KEY exported for chaos" in caplog.text
    
    def test_chaos_enum_missing_api_key(self, tmp_path, monkeypatch, caplog):
        """Test chaos enumeration without PDCP_API_KEY"""
        domain = "example.com"
        output_dir = tmp_path / "subdomains"
        output_dir.mkdir()
        
        monkeypatch.delenv("PDCP_API_KEY", raising=False)
        
        def fake_run_cmd(cmd):
            return "test.example.com"
        
        def fake_clean_domain(line):
            return line
        
        monkeypatch.setattr("src.core.subdomains.run_cmd", fake_run_cmd)
        monkeypatch.setattr("src.core.subdomains.clean_domain", fake_clean_domain)
        
        with caplog.at_level(logging.WARNING):
            result = chaos_enum(domain, str(output_dir))
        
        assert "PDCP_API_KEY not found in .env" in caplog.text
    
    def test_chaos_enum_command_format(self, tmp_path, monkeypatch):
        """Test that chaos command is formatted correctly"""
        domain = "target.io"
        output_dir = tmp_path / "subdomains"
        output_dir.mkdir()
        
        captured_cmd = []
        
        def fake_run_cmd(cmd):
            captured_cmd.append(cmd)
            return "target1.target.io"
        
        def fake_clean_domain(line):
            return line
        
        monkeypatch.setattr("src.core.subdomains.run_cmd", fake_run_cmd)
        monkeypatch.setattr("src.core.subdomains.clean_domain", fake_clean_domain)
        monkeypatch.delenv("PDCP_API_KEY", raising=False)
        
        chaos_enum(domain, str(output_dir))
        
        assert len(captured_cmd) > 0
        assert "chaos" in captured_cmd[0]
        assert f"-d {domain}" in captured_cmd[0]
        assert "-silent" in captured_cmd[0]


class TestSubdomainEnum:
    def test_subdomain_enum_creates_output_file(self, tmp_path, monkeypatch, caplog):
        """Test that subdomain enumeration creates properly named output file"""
        cmd = "subfinder -d {domain} -silent"
        tool_name = "subfinder"
        domain = "example.com"
        output_dir = tmp_path / "subdomains"
        output_dir.mkdir()
        
        mock_output = "sub1.example.com\nsub2.example.com"
        
        def fake_run_cmd(cmd):
            return mock_output
        
        def fake_clean_domain(line):
            return line.strip()
        
        monkeypatch.setattr("src.core.subdomains.run_cmd", fake_run_cmd)
        monkeypatch.setattr("src.core.subdomains.clean_domain", fake_clean_domain)
        
        result = subdomain_enum(cmd, tool_name, domain, str(output_dir))
        
        # Verify file naming format: YYYYMMDD.{tool_name}.subdomains.txt
        assert result.endswith(f".{tool_name}.subdomains.txt")
        assert os.path.exists(result)
        
        with open(result, "r") as f:
            content = f.read()
            assert mock_output in content
    
    def test_subdomain_enum_pdcp_api_key_handling(self, tmp_path, monkeypatch, caplog):
        """Test PDCP API key environment variable handling"""
        cmd = "chaos -d {domain} -silent"
        tool_name = "chaos"
        domain = "example.com"
        output_dir = tmp_path / "subdomains"
        output_dir.mkdir()
        
        api_key = "test-api-key-xyz"
        monkeypatch.setenv("PDCP_API_KEY", api_key)
        
        def fake_run_cmd(cmd):
            # Verify the API key is set in os.environ
            assert os.getenv("PDCP_API_KEY") == api_key
            return "test.example.com"
        
        def fake_clean_domain(line):
            return line
        
        monkeypatch.setattr("src.core.subdomains.run_cmd", fake_run_cmd)
        monkeypatch.setattr("src.core.subdomains.clean_domain", fake_clean_domain)
        
        with caplog.at_level(logging.DEBUG):
            subdomain_enum(cmd, tool_name, domain, str(output_dir), use_pdcp_api=True)
        
        assert "PDCP_API_KEY exported for chaos" in caplog.text
    
    def test_subdomain_enum_clean_domain_transformation(self, tmp_path, monkeypatch, caplog):
        """Test that clean_domain transformation is applied to subdomains"""
        cmd = "subfinder -d {domain} -silent"
        tool_name = "subfinder"
        domain = "example.com"
        output_dir = tmp_path / "subdomains"
        output_dir.mkdir()
        
        dirty_output = "sub1.example.com  \n  sub2.example.com\nsub3.example.com"
        clean_output = "sub1.example.com\nsub2.example.com\nsub3.example.com"
        
        clean_call_count = [0]
        
        def fake_run_cmd(cmd):
            return dirty_output
        
        def fake_clean_domain(line):
            clean_call_count[0] += 1
            return line.strip()
        
        monkeypatch.setattr("src.core.subdomains.run_cmd", fake_run_cmd)
        monkeypatch.setattr("src.core.subdomains.clean_domain", fake_clean_domain)
        
        result = subdomain_enum(cmd, tool_name, domain, str(output_dir))
        
        # clean_domain should be called for each line
        assert clean_call_count[0] > 0
        
        with open(result, "r") as f:
            content = f.read()
            lines = [l for l in content.split("\n") if l.strip()]
            assert len(lines) == 3
    
    def test_subdomain_enum_logs_count(self, tmp_path, monkeypatch, caplog):
        """Test that subdomain count is logged"""
        cmd = "subfinder -d {domain} -silent"
        tool_name = "subfinder"
        domain = "example.com"
        output_dir = tmp_path / "subdomains"
        output_dir.mkdir()
        
        mock_output = "sub1.example.com\nsub2.example.com\nsub3.example.com"
        
        def fake_run_cmd(cmd):
            return mock_output
        
        def fake_clean_domain(line):
            return line
        
        monkeypatch.setattr("src.core.subdomains.run_cmd", fake_run_cmd)
        monkeypatch.setattr("src.core.subdomains.clean_domain", fake_clean_domain)
        
        with caplog.at_level(logging.DEBUG):
            subdomain_enum(cmd, tool_name, domain, str(output_dir))
        
        assert "Found 3 subdomains" in caplog.text
    
    def test_subdomain_enum_command_substitution(self, tmp_path, monkeypatch):
        """Test that domain placeholder is correctly substituted in command"""
        cmd = "subfinder -d {domain} -silent"
        tool_name = "subfinder"
        domain = "test-domain.net"
        output_dir = tmp_path / "subdomains"
        output_dir.mkdir()
        
        captured_cmd = []
        
        def fake_run_cmd(cmd):
            captured_cmd.append(cmd)
            return ""
        
        def fake_clean_domain(line):
            return line
        
        monkeypatch.setattr("src.core.subdomains.run_cmd", fake_run_cmd)
        monkeypatch.setattr("src.core.subdomains.clean_domain", fake_clean_domain)
        
        subdomain_enum(cmd, tool_name, domain, str(output_dir))
        
        assert len(captured_cmd) > 0
        assert f"-d {domain}" in captured_cmd[0]
        assert "{domain}" not in captured_cmd[0]
    
    def test_subdomain_enum_logs_enumeration_start(self, tmp_path, monkeypatch, caplog):
        """Test that enumeration start is logged"""
        cmd = "subfinder -d {domain} -silent"
        tool_name = "subfinder"
        domain = "example.com"
        output_dir = tmp_path / "subdomains"
        output_dir.mkdir()
        
        def fake_run_cmd(cmd):
            return ""
        
        def fake_clean_domain(line):
            return line
        
        monkeypatch.setattr("src.core.subdomains.run_cmd", fake_run_cmd)
        monkeypatch.setattr("src.core.subdomains.clean_domain", fake_clean_domain)
        
        with caplog.at_level(logging.INFO):
            subdomain_enum(cmd, tool_name, domain, str(output_dir))
        
        assert f"Enumerating subdomains of {domain} with {tool_name}" in caplog.text
    
    def test_subdomain_enum_output_file_naming(self, tmp_path, monkeypatch):
        """Test output file naming includes date in YYYYMMDD format"""
        cmd = "test -d {domain}"
        tool_name = "testtool"
        domain = "example.com"
        output_dir = tmp_path / "subdomains"
        output_dir.mkdir()
        
        def fake_run_cmd(cmd):
            return "result"
        
        def fake_clean_domain(line):
            return line
        
        monkeypatch.setattr("src.core.subdomains.run_cmd", fake_run_cmd)
        monkeypatch.setattr("src.core.subdomains.clean_domain", fake_clean_domain)
        
        result = subdomain_enum(cmd, tool_name, domain, str(output_dir))
        
        today = dt.now().strftime('%Y%m%d')
        assert today in result
        assert f"{today}.{tool_name}.subdomains.txt" in result
