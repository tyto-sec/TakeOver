#!/bin/sh
set -e

## Install Basic Utilities
apt-get update
apt-get install -y --no-install-recommends wget git unzip curl ca-certificates
rm -rf /var/lib/apt/lists/*

# Install Go 1.25.1
rm -rf /usr/local/go
wget https://go.dev/dl/go1.25.1.linux-amd64.tar.gz -O /tmp/go1.25.1.tar.gz
tar -C /usr/local -xzf /tmp/go1.25.1.tar.gz
rm /tmp/go1.25.1.tar.gz

# Configure Go environment variables
export GOROOT=/usr/local/go
export GOPATH=/root/go
export PATH=$PATH:$GOROOT/bin:$GOPATH/bin

# Add to profile for persistence
echo "export GOROOT=/usr/local/go" >> /etc/profile
echo "export GOPATH=/root/go" >> /etc/profile
echo "export PATH=\$PATH:\$GOROOT/bin:\$GOPATH/bin" >> /etc/profile

# Create GOPATH directory
mkdir -p $GOPATH

# Install Go binaries in parallel (faster)
echo "Installing Go tools (parallel)..."
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest &
PID1=$!
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest &
PID2=$!
go install -v github.com/projectdiscovery/chaos-client/cmd/chaos@latest &
PID3=$!
go install -v github.com/tomnomnom/anew@latest &
PID4=$!
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest &
PID5=$!
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest &
PID6=$!

echo "Waiting for builds: httpx($PID1) subfinder($PID2) chaos($PID3) anew($PID4) dnsx($PID5) nuclei($PID6)"
wait $PID1 $PID2 $PID3 $PID4 $PID5 $PID6
echo "All builds completed"

# Copy to /usr/local/bin
for bin in httpx subfinder chaos anew dnsx nuclei; do
    if [ -f /root/go/bin/$bin ]; then
        cp /root/go/bin/$bin /usr/local/bin/$bin
        echo " - Copied $bin"
    else
        echo " - NOT FOUND: /root/go/bin/$bin"
    fi
done

# Install nuclei templates after nuclei is available
echo "Installing nuclei templates..."
/usr/local/bin/nuclei -update-templates || echo "Warning: nuclei templates installation failed"

# Remove pip3 if conflict exists
pip3 uninstall -y 'httpx[cli]' 2>/dev/null || true

echo "Installation completed."
exit 0