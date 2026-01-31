import pytest
import os
import json
import tempfile
from src.core.cnamerecords import (
    get_hosts_with_cname,
    search_for_hosts_with_cname,
    grep_cname_hosts
)


class TestSearchForHostsWithCname:
    """Tests for search_for_hosts_with_cname function"""
    
    def test_search_cname_basic(self):
        """Test basic CNAME record extraction"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("example.com CNAME example.s3.amazonaws.com\n")
            f.write("test.example.com CNAME cdn.cloudflare.net\n")
            f.write("api.example.com A 1.2.3.4\n")
            dns_file = f.name
        
        try:
            result = search_for_hosts_with_cname(dns_file)
            assert len(result) == 2
            assert result["example.com"] == "example.s3.amazonaws.com"
            assert result["test.example.com"] == "cdn.cloudflare.net"
        finally:
            os.unlink(dns_file)
    
    def test_search_cname_with_colors(self):
        """Test CNAME extraction with ANSI color codes"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            # Even with color codes, the function extracts what it can
            f.write("subdomain.example.com [[35mCNAME[0m] [[32mtarget.service.com[0m]\n")
            dns_file = f.name
        
        try:
            result = search_for_hosts_with_cname(dns_file)
            # The function will extract the host correctly
            assert "subdomain.example.com" in result
        finally:
            os.unlink(dns_file)
    
    def test_search_cname_empty_file(self):
        """Test with empty DNS file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            dns_file = f.name
        
        try:
            result = search_for_hosts_with_cname(dns_file)
            assert len(result) == 0
        finally:
            os.unlink(dns_file)
    
    def test_search_cname_no_cname_records(self):
        """Test with file containing no CNAME records"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("example.com A 1.2.3.4\n")
            f.write("test.example.com TXT some-txt-record\n")
            dns_file = f.name
        
        try:
            result = search_for_hosts_with_cname(dns_file)
            assert len(result) == 0
        finally:
            os.unlink(dns_file)
    
    def test_search_cname_malformed_records(self):
        """Test with malformed records (should be skipped)"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("valid.com CNAME valid.target.com\n")
            f.write("invalid CNAME\n")  # Missing target
            f.write("another.com CNAME\n")  # Missing target
            dns_file = f.name
        
        try:
            result = search_for_hosts_with_cname(dns_file)
            assert len(result) == 1
            assert "valid.com" in result
        finally:
            os.unlink(dns_file)
    
    def test_search_cname_nonexistent_file(self):
        """Test with nonexistent file"""
        result = search_for_hosts_with_cname("/nonexistent/file.txt")
        assert len(result) == 0


class TestGetHostsWithCname:
    """Tests for get_hosts_with_cname function"""
    
    def test_get_hosts_with_cname_success(self):
        """Test successful CNAME host extraction and JSON output"""
        with tempfile.TemporaryDirectory() as tmpdir:
            dns_file = os.path.join(tmpdir, "dns_records.txt")
            with open(dns_file, 'w') as f:
                f.write("app.example.com CNAME app.github.io\n")
                f.write("cdn.example.com CNAME cdn.s3.amazonaws.com\n")
            
            result = get_hosts_with_cname(dns_file, tmpdir)
            
            assert result is not None
            assert os.path.isfile(result)
            
            with open(result, 'r') as f:
                data = json.load(f)
            
            assert len(data) == 2
            assert data["app.example.com"] == "app.github.io"
            assert data["cdn.example.com"] == "cdn.s3.amazonaws.com"
    
    def test_get_hosts_with_cname_nonexistent_file(self):
        """Test with nonexistent DNS file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = get_hosts_with_cname("/nonexistent/dns.txt", tmpdir)
            assert result is None
    
    def test_get_hosts_with_cname_creates_json(self):
        """Test that JSON output file is created with correct format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            dns_file = os.path.join(tmpdir, "dns_records.txt")
            with open(dns_file, 'w') as f:
                f.write("test.example.com CNAME test.s3.amazonaws.com\n")
            
            result = get_hosts_with_cname(dns_file, tmpdir)
            
            assert result.endswith(".cname_hosts_pairs.json")
            assert os.path.isfile(result)


class TestGrepCnameHosts:
    """Tests for grep_cname_hosts function"""
    
    @pytest.fixture
    def sample_cname_fingerprints(self):
        """Sample CNAME fingerprints for testing"""
        return {
            "aws": ["s3.amazonaws.com", "elb.amazonaws.com", "cloudfront.net"],
            "github": ["github.io", "github.com"],
            "cloudflare": ["cdn.cloudflare.net", "workers.dev"],
        }
    
    def test_grep_cname_hosts_matching(self, sample_cname_fingerprints):
        """Test filtering CNAME hosts with matching fingerprints"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cname_file = os.path.join(tmpdir, "cname_pairs.json")
            cname_data = {
                "app.example.com": "app.github.io",
                "cdn.example.com": "cdn.s3.amazonaws.com",
                "blog.example.com": "blog.example.com",
                "api.example.com": "api.cdn.cloudflare.net",
            }
            
            with open(cname_file, 'w') as f:
                json.dump(cname_data, f)
            
            result = grep_cname_hosts(cname_file, tmpdir, sample_cname_fingerprints)
            
            assert result is not None
            with open(result, 'r') as f:
                grepped = json.load(f)
            
            assert len(grepped) == 3
            assert "app.example.com" in grepped
            assert "cdn.example.com" in grepped
            assert "api.example.com" in grepped
            assert "blog.example.com" not in grepped
    
    def test_grep_cname_hosts_no_matches(self, sample_cname_fingerprints):
        """Test filtering with no matching fingerprints"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cname_file = os.path.join(tmpdir, "cname_pairs.json")
            cname_data = {
                "internal.example.com": "internal.local",
                "db.example.com": "db.internal.local",
            }
            
            with open(cname_file, 'w') as f:
                json.dump(cname_data, f)
            
            result = grep_cname_hosts(cname_file, tmpdir, sample_cname_fingerprints)
            
            with open(result, 'r') as f:
                grepped = json.load(f)
            
            assert len(grepped) == 0
    
    def test_grep_cname_hosts_case_insensitive(self, sample_cname_fingerprints):
        """Test that matching is case-insensitive"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cname_file = os.path.join(tmpdir, "cname_pairs.json")
            cname_data = {
                "app.example.com": "app.GITHUB.IO",
                "cdn.example.com": "cdn.S3.AMAZONAWS.COM",
            }
            
            with open(cname_file, 'w') as f:
                json.dump(cname_data, f)
            
            result = grep_cname_hosts(cname_file, tmpdir, sample_cname_fingerprints)
            
            with open(result, 'r') as f:
                grepped = json.load(f)
            
            assert len(grepped) == 2
    
    def test_grep_cname_hosts_nonexistent_file(self, sample_cname_fingerprints):
        """Test with nonexistent CNAME pairs file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = grep_cname_hosts("/nonexistent/cname.json", tmpdir, sample_cname_fingerprints)
            assert result is None
    
    def test_grep_cname_hosts_creates_json(self, sample_cname_fingerprints):
        """Test that grepped JSON output is created correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cname_file = os.path.join(tmpdir, "cname_pairs.json")
            cname_data = {
                "test.example.com": "test.s3.amazonaws.com",
            }
            
            with open(cname_file, 'w') as f:
                json.dump(cname_data, f)
            
            result = grep_cname_hosts(cname_file, tmpdir, sample_cname_fingerprints)
            
            assert result.endswith(".grepped_cname_hosts_pairs.json")
            assert os.path.isfile(result)
    
    def test_grep_cname_hosts_multiple_patterns(self, sample_cname_fingerprints):
        """Test matching with multiple patterns"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cname_file = os.path.join(tmpdir, "cname_pairs.json")
            cname_data = {
                "multi1.example.com": "multi1.s3.amazonaws.com",  # matches 's3.amazonaws.com'
                "multi2.example.com": "multi2.cloudfront.net",    # matches 'cloudfront.net'
            }
            
            with open(cname_file, 'w') as f:
                json.dump(cname_data, f)
            
            result = grep_cname_hosts(cname_file, tmpdir, sample_cname_fingerprints)
            
            with open(result, 'r') as f:
                grepped = json.load(f)
            
            assert len(grepped) == 2


class TestIntegration:
    """Integration tests for the full CNAME processing workflow"""
    
    def test_full_workflow(self):
        """Test complete workflow: DNS file -> search -> grep"""
        sample_fingerprints = {
            "aws": ["s3.amazonaws.com", "elb.amazonaws.com"],
            "github": ["github.io"],
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create DNS records file (clean format without color codes)
            dns_file = os.path.join(tmpdir, "dns_records.txt")
            with open(dns_file, 'w') as f:
                f.write("app.example.com CNAME app.github.io\n")
                f.write("cdn.example.com CNAME cdn.s3.amazonaws.com\n")
                f.write("internal.example.com CNAME internal.local\n")
            
            # Step 1: Get CNAME hosts
            cname_pairs_file = get_hosts_with_cname(dns_file, tmpdir)
            assert cname_pairs_file is not None
            
            with open(cname_pairs_file, 'r') as f:
                cname_pairs = json.load(f)
            assert len(cname_pairs) == 3
            
            # Step 2: Grep CNAME hosts
            grepped_file = grep_cname_hosts(cname_pairs_file, tmpdir, sample_fingerprints)
            assert grepped_file is not None
            
            with open(grepped_file, 'r') as f:
                grepped = json.load(f)
            
            # Should only have the vulnerable ones
            assert len(grepped) == 2
            assert "app.example.com" in grepped
            assert "cdn.example.com" in grepped
            assert "internal.example.com" not in grepped
