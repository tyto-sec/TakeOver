FROM python:3.11-slim
ENV DEBIAN_FRONTEND=noninteractive

# Configure DNS and network
RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf && \
    echo "nameserver 8.8.4.4" >> /etc/resolv.conf

ENV GOPATH=/root/go
ENV GOROOT=/usr/local/go
ENV PATH=/usr/local/go/bin:/root/go/bin:$PATH

RUN mkdir -p /root/go /root/go/bin

# Copy install script early for caching purposes
COPY install.sh /usr/local/bin/install.sh
RUN chmod +x /usr/local/bin/install.sh && \
    /usr/local/bin/install.sh && \
    echo "=== Docker build layer complete ===" && \
    ls -lh /usr/local/bin/{httpx,subfinder,dnsx,nuclei,chaos,anew} 2>/dev/null || echo "Binaries copied successfully"

WORKDIR /app

COPY src /app/src
COPY main.py /app/main.py
COPY setup.py /app/setup.py
COPY requirements.txt /app/requirements.txt
COPY .env /app/.env
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN chmod +x /usr/local/bin/docker-entrypoint.sh \
    && pip3 install --no-cache-dir -r /app/requirements.txt \
    && pip3 install --no-cache-dir /app

ENV DOMAINS_FILE=/app/input/domains.txt
ENV OUTPUT_DIR=/app/output
ENV NUCLEI_TEMPLATE_DIR=/root/nuclei-templates/http/takeovers
ENV MAX_THREADS=8
ENV PYTHONUNBUFFERED=1

VOLUME ["/app/output"]

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
