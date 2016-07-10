iptables -t mangle -A internet -j MARK --set-mark 99
iptables -t nat -A PREROUTING -m mark --mark 99 -p tcp --dport 80 -j DNAT --to-destination 52.90.158.81:80
