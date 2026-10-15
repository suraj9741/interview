# A disposable Linux "network lab" for the namespace-based labs in this folder.
# Same OS and packages as the environment the labs were tested in
# (Ubuntu 24.04, iproute2 6.1, BIND 9.18, dnsmasq 2.91, curl 8.5, OpenSSL 3.0).
# This Dockerfile itself was NOT built during testing (no Docker daemon was available there).
#
# From the 13-hands-on-labs folder:
# Build:  docker build -t netlab files/netlab
# Run:    docker run --rm -it --privileged --hostname netlab -v "$PWD/files:/labs" netlab
#         (--privileged is needed to create network namespaces and firewall rules
#          inside the container; it affects only Docker's Linux VM, not your Mac.)
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        iproute2 iputils-ping iputils-tracepath traceroute mtr-tiny \
        tcpdump tshark \
        curl netcat-openbsd \
        dnsmasq-base isc-dhcp-client \
        bind9 bind9-dnsutils \
        openssl faketime ca-certificates \
        iptables nftables conntrack \
        iperf3 ipcalc ethtool procps \
        python3 less vim-tiny \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /labs
CMD ["bash"]
