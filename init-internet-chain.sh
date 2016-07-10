iptables -t mangle -A PREROUTING -d 52.90.158.81 -j ACCEPT
iptables -t mangle -A PREROUTING -d 192.168.42.1 -j ACCEPT
iptables -N internet -t mangle
iptables -t mangle -A PREROUTING -p tcp -j internet
