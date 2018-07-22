#!/bin/bash
#bootstrap script Pieter Smit (c) 2018
#max size 256 KB
#base64 encoded into template  cat script.sh | gzip -9 | base 64 -w0
mkdir -p /etc/salt/pki
echo '{{ vm['priv_key'] }}' > /etc/salt/pki/minion.pem
echo '{{ vm['pub_key'] }}' > /etc/salt/pki/minion.pub
cat > /etc/salt/minion <<EOF
{{minion}}
EOF

python -c 'import urllib; print urllib.urlopen(\"https://bootstrap.saltstack.com\").read()' > bootstrap-salt.sh ; sudo sh bootstrap-salt.sh git v2018.3.2

#sh bootstrap-salt.sh -x python3

apt-get update
apt-get install -y -o DPkg::Options::=--force-confold salt-minion


