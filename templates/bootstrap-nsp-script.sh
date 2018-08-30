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
echo "#!/bin/bash"                      >  /root/restart-walinuxagent.sh
echo "service walinuxagent restart"     >> /root/restart-walinuxagent.sh
echo "rm /root/restart-walinuxagent.sh" >> /root/restart-walinuxagent.sh
chmod +x /root/restart-walinuxagent.sh
at now +5 min -f /root/restart-walinuxagent.sh

#Add public key Shamera2018
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC6IH+RGAmPYC2DngPOPD3CzdONLbZBD9W1VK7xV/Lwq/a7tJ2uHCXxteUfvzw3n7LJjQT7lByjPtIKMq2q7ZuKTJHMN6qY5l5Wxn181RwN1spwz23+GjgJNc7OhdOF2st4onPwwi3v3eHxVfCXmnsGTR6i1k2jrGKzXdmnO+KInrCwEj1q7QOU0uSF5e9TaI3lrB80f1J9rQ01Jy/nnmluGXDrHcTOtdS7rohNKwJDV7XOKcZgzb3YNQumdvF+IQaRIv/84d4A2ZOpU+SawE3g/0LnREdHR3UWUkUncnhzU1ovV2rTmHQrh7whSROnqMp/pivn7v3u2nOqs8Gfpknh shamera.ranathunga@9spokes.com" >> /home/admin9sp/.ssh/authorized_keys
#Add public key Tom2018
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDkFhPQcjvbLdbJH6t3r4knPwJok0Tz7vqbTuvU/5bQcFb6wayGCKKx/Nzt5IaEnUK3lg/EcEYSW6x/v5pjyLOJMwC9Uhx0ieomrEtMQfABKyxM1p/zJllD3bIplxHIAfq0zWHzT/ECH4k3SmwP2Bd4PniRrdchupgAJNBTuBSNmFspA4EpS0LZx/zk03Ngus6x+NY9FJwAw2L02HlWNje+Cb4d9DaQRzMBFXyMFS+uAgNmi7wKaB8gZguBPAN81ZAyljoewQV10+y13NRCyxemPHOEo43okOyRaV7MIgw8O3Lq57jVJ1+00aS4+KGIk8Xzr8ln1DQZsvoeQiCBmTA3 tom.bosworth@9spokes.com" >> /home/admin9sp/.ssh/authorized_keys
#Add public key Mourad2018
echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEAgNgQY9+7fRJ554T4j+Dpk0QG82fvoThYeZrE6dp9VsckO/w/bCSKyqBRsXd0934pdKLTu3KfLOZVEbgHe9t1uoopzFKfvVsld0IiO1A+/cD6gzYuYGqP2NlRU6oQKp2c1ZKFYh1vR8GJQFWwmprEBBe29UJH2vbGMUmW2BwK+3x3mm7sGi4DzPMAghzBjn3LWyMHTQ7KZvcApDLaruesP1H0gS2bs7ammLZWgvzuNLJzeTYYVZRi+5jUAMiV0DqV41qTHrqwkNQLmvMSzVyw95onPPDFdmwvFQ40J3B9l12sPq1FBIhQ6+T0hdyaSbAwjoIpmWaaSfggRJ7Kgqf+EQ== " >> /home/admin9sp/.ssh/authorized_keys
#Add public key Pieter2018
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC4L7US4IKuxbzXl9Ewp8aquq30Caf52BcVkN/L/T0eFTpjCy6Q68QNQ4MDtfMcmKbysB4Pychy2dRpzixhp6aiO+Q3lxfMc7mH80XGfrB8ou7TPbGLAApzl7x/yTcsx2Kr5j6jSWVWYhFG3qxrMkmRcrZt08kfhdvH2Xpp1o840yo1d6bZ3xyzDvVXaWUi/YoWAC/a0H7Pd+zT+NdMfREVe5B8JfKI453Vr+vgwcqqTcYKGursJnsxgZW8KDZN7mZiHJRoGAOMF7EHhVo+MO/Ii2Ksl61T2DCMw/OstAeEQIEYfGjVRveVjs43cUkgqEPaJVVE4qjUtMLsVA1hmaBP pieter.smit@9spokes.com" >> /home/admin9sp/.ssh/authorized_keys


return & exit 0

