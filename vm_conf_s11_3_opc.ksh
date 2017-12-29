#! /bin/ksh

echo "...Install ovm-guest-additions"
pkg set-publisher -G '*' -g http://solaris-re/support/sru-internal solaris
pkg install -q --no-backup-be ovm-guest-additions
pkg set-publisher -G '*' -g https://pkg.oracle.com/solaris/support --no-refresh solaris

echo "...Add opc group"
groupadd opc
usermod -g opc opc

echo "...Add ssh key service"
wget http://solaris-re/ova/opc/sshkeys.tar
tar xf sshkeys.tar
sh addkeys.sh
rm addkeys.sh inject-sshkeys.sh inject-sshkeys.xml opc-inject-sshkeys sshkeys.tar

echo "...Remove any core files"
find / /var /var/share /dev /devices -xdev -type f -a -name core | xargs -t rm

echo "...Remove root emails"
rm -f /var/mail/root

echo "...Remove MAC address setting and adding tty console in grub"
sudo bootadm change-entry -i 0 kargs='-B disable-e1000g=true -B console=ttya'

echo "...Setting MTU value"
dladm set-linkprop -p mtu=9000 net0

echo "...Set password rules"
passwd -N opc
passwd -f root

cp /net/pkgdock/export/RE/script/sysconfig_util.py /export/home/opc/sysconfig_util.py

# modify DHCP settings for Higgs framework and restart dhcpagent
sed "s/^# VERIFIED_LEASE_ONLY=yes/VERIFIED_LEASE_ONLY=yes/" \
/etc/default/dhcpagent > /etc/default/dhcpagent.new
mv /etc/default/dhcpagent.new /etc/default/dhcpagent
chgrp sys /etc/default/dhcpagent

echo "Restarting dhcpagent..."
pkill -9 dhcpagent
/sbin/dhcpagent

# for Solaris 12 this can be done with these commands:
# ipadm set-addrprop -p verified-lease-only=yes net0/dhcp
# ipadm disable-if net0
# ipadm enable-if -t net0

# create script to be run in single-user mode after unconfig

cat > /export/home/opc/vm_conf.s11.3.opc-post << EOF
rm -rf /etc/svc/profile/sysconfig/*
rm /var/svc/log/network-physical:default.log
rm /var/svc/log/system-identity:node.log
rm /var/svc/log/system-console-login*
rm /var/adm/messages* /var/log/install/messages
rm /var/adm/lastlog /var/adm/wtmpx
touch /var/adm/wtmpx
chown adm:adm /var/adm/wtmpx
sed "s/cadmium.us.oracle.com/solaris/" /etc/svc/profile/site/sc_profile.xml > /tmp/site2
cat /tmp/site2 > /etc/svc/profile/site/sc_profile.xml
rm /tmp/site2
sed "s/drought.us.oracle.com/solaris/" /boot/grub/grub.cfg > /tmp/grubedit
cat /tmp/grubedit > /boot/grub/grub.cfg
rm /tmp/grubedit
sed "s/cadmium.us.oracle.com/solaris/" /var/log/install/install_log > /tmp/log2
mv /tmp/log2 /var/log/install/install_log

# remove system keys
/lib/svc/method/sshd -u

# remove pkg history entries referencing RE's server
grep -l solaris-re /var/pkg/history/* | xargs rm

rm /export/home/opc/.bash_history /export/home/opc/.lesshst
echo > /var/log/syslog

rm /etc/iscsi/iscsi_v1.dbc
zpool set cachefile=none rpool

rm /var/audit/*cadmium*

rm /var/fm/fmd/*log*

/export/home/opc/sysconfig_util.py
rm /export/home/opc/*
echo "run \"history -c\" followed by \"init 5\"."

EOF
chmod +x /export/home/opc/vm_conf.s11.3.opc-post

echo "...Run sysconfig to remove local config info"
sysconfig unconfigure -g identity,keyboard,naming_services,location,support --destructive
set +x

exit 0
