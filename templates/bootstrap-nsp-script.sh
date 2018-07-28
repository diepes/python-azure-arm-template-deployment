#!/bin/bash
set -x
exec 3>&1 4>&2
trap 'exec 2>&4 1>&3' 0 1 2 3 RETURN
exec 1>/var/log/bootstrap-$(date -I).log 2>&1

#bootstrap script Pieter Smit (c) 2018
#max size 256 KB
#base64 encoded into template  cat script.sh | gzip -9 | base 64 -w0
mkdir -p /etc/salt/pki
cat > /etc/salt/pki/minion.pem <<EOF
{salt_key_pem}
EOF

cat > /etc/salt/pki/minion.pub <<EOF
{salt_key_pub}
EOF


cat > /etc/salt/minion <<EOF
{salt_minion}
EOF

cat > /etc/salt/grains <<EOF
{salt_grains}
EOF

python -c 'import urllib; print urllib.urlopen("https://bootstrap.saltstack.com").read()' > bootstrap-salt.sh
sudo sh bootstrap-salt.sh stable 2017.7
#git v2018.3.2

#sh bootstrap-salt.sh -x python3

#apt-get update
#apt-get install -y -o DPkg::Options::=--force-confold salt-minion


#Setup swap file through azure agent.
cat > /etc/waagent.conf <<EOF
# Format if unformatted. If 'n', resource disk will not be mounted.
ResourceDisk.Format=y

# File system on the resource disk
# Typically ext3 or ext4. FreeBSD images should use 'ufs2' here.
ResourceDisk.Filesystem=ext4
ResourceDisk.MountPoint=/mnt/resource
ResourceDisk.MountOptions=None
ResourceDisk.EnableSwap=y
ResourceDisk.SwapSizeMB=12000
Provisioning.Enabled=y
Provisioning.UseCloudInit=n
Provisioning.DeleteRootPassword=y
Provisioning.RegenerateSshHostKeyPair=y
Provisioning.SshHostKeyPairType=rsa
Provisioning.MonitorHostName=y
Provisioning.DecodeCustomData=n
Provisioning.ExecuteCustomData=n
Provisioning.PasswordCryptId=6
Provisioning.PasswordCryptSaltLength=10
Logs.Verbose=n

# Allow fallback to HTTP if HTTPS is unavailable
# Note: Allowing HTTP (vs. HTTPS) may cause security risks
OS.AllowHTTP=n
OS.RootDeviceScsiTimeout=300
OS.EnableFIPS=n
OS.OpensslPath=None
OS.SshClientAliveInterval=180
OS.SshDir=/etc/ssh
HttpProxy.Host=None
HttpProxy.Port=None

# Detect Scvmm environment, default is n
# DetectScvmmEnv=n

# Enable RDMA management and set up, should only be used in HPC images
# OS.EnableRDMA=y

# Enable RDMA kernel update, this value is effective on Ubuntu
# OS.UpdateRdmaDriver=y

# Enable or disable goal state processing auto-update, default is enabled
# AutoUpdate.Enabled=y

# Determine the update family, this should not be changed
# AutoUpdate.GAFamily=Prod

# Determine if the overprovisioning feature is enabled. If yes, hold extension
# handling until inVMArtifactsProfile.OnHold is false.
# Default is disabled
# EnableOverProvisioning=n


# Add firewall rules to protect access to Azure host node services
# Note:
# - The default is false to protect the state of exising VMs
OS.EnableFirewall=n

EOF

#restart to enable new config and swap.
#add 5 min restart, 20sec not working probably the agent not deployed yet.
( sleep 300 ; service walinuxagent restart ) &


return & exit 0

