#!/bin/ksh

export PATH=$PATH:/usr/sbin
[[ "$0" == /* ]] && typeset -r PRG=$0 || typeset -r PRG=$PWD/$0

typeset OPT_REL=

while getopts ':r:g' char ; do
	case $char in
		r)	OPT_REL=$OPTARG
			;;
		\?)     echo "Unknown option $OPTARG"
			exit 1
			;;
	esac
done

if [ -z "$OPT_REL" ] ; then
	echo "ERROR: release name needed"
	exit 1
fi

typeset -r RELEASE=$OPT_REL
typeset -r DOCKREL=$(echo $RELEASE | sed "s/\./_/")
typeset -r MAJORREL=$(echo $DOCKREL | awk -F_ '{print $1}')
typeset -r DOCK=/net/ipsdock-re/export/integrate_dock/$MAJORREL/$DOCKREL
typeset -r ZIPDOCK=/net/pkgdock/export/zipped_dock/$MAJORREL/$DOCKREL
typeset -r CONF_FILE=$DOCK/config/nightly.conf
typeset -r RE_BIN=/net/pkgdock/export/RE/bin
typeset -r MAILTO_RE=$(cat $DOCK/config/email_addrs)
typeset -r MAILTO_RE_FILE=/tmp/mailtore$$
. $CONF_FILE

MAILSUBJECT="$RELEASE Nightly Build Failed"

dcstatus=Succeeded
# The trap will execute with any exit from the script
trap "cat $MAILTO_RE_FILE | /usr/bin/mailx -s \"$MAILSUBJECT\" $MAILTO_RE; rm $MAILTO_RE_FILE" 0 1 2 3 15

typeset -r BUILDAREA=/export/builds/$MAJORREL/$RELEASE
typeset -r LOGS=$BUILDAREA/nightly/logs
typeset -r CLOGS=$BUILDAREA/logs
typeset -r NTSTAMP=$(date +%y%m%d.%H%M)
typeset UPDATE_DC=false
typeset -i pkgcount=0

typeset NANA_REL_STRING=Solaris_$(echo ${RELEASE#s} | tr . _ | awk -F_ '{print$1}')

echo "Nightly start time: \c" | tee -a $MAILTO_RE_FILE
date | tee -a $MAILTO_RE_FILE

# create list of new C-teams to publish, since last publishing
# use md5 values to see what has changed and what is new
md5sum $DOCK/ips/* | awk '{print $2,$1}' | sed "s/.*\///" | 
    sort > $workdir/cteam-ips-new.md5
export RE_REPO_LIST=$(comm -13 $workdir/cteam-ips.md5 \
$workdir/cteam-ips-new.md5 | awk '{print $1}' | sed "s/.zip//")
mv $workdir/cteam-ips-new.md5 $workdir/cteam-ips.md5

echo "C-Team Repos for this build:" | tee -a $MAILTO_RE_FILE
echo $RE_REPO_LIST | tee -a  $MAILTO_RE_FILE

for cteamrepo in $RE_REPO_LIST; do
	if [ "$cteamrepo" == "osnet" ] ; then
		typeset UPDATE_DC=true
	fi

	sudo $RE_BIN/soltools -r $RELEASE PrepcteamIPS $cteamrepo
	sudo $RE_BIN/soltools -r $RELEASE ProcessCteamRepo $cteamrepo > \
	$CLOGS/process-$cteamrepo-$BUILDID-$NTSTAMP.out 2>&1 || {
		echo "Elfsigning failed for $cteamrepo" | tee -a  $MAILTO_RE_FILE 
		dcstatus=FAILED
	}
	pkgcount=pkgcount+$(grep -c "PUBLISHED" \
	$CLOGS/process-$cteamrepo-$BUILDID-$NTSTAMP.out)
	egrep -i -e "error|warning|failed" \
	/export/builds/$MAJORREL/$RELEASE/logs/process-$cteamrepo-$BUILDID-$NTSTAMP.out \
	>> $MAILTO_RE_FILE

done

echo "C-team Repo Processing:" | tee -a $MAILTO_RE_FILE
echo "$pkgcount packages published." | tee -a $MAILTO_RE_FILE
if [ ! -z $RE_REPO_LIST ] ; then
	sudo $RE_BIN/soltools -r $RELEASE -c $CONF_FILE PublishBycteamList \
	  >> $LOGS/PublishBycteamList-$BUILDID-$NTSTAMP.out 2>&1 || {
		echo "PublishByCTeamList Failed"
		echo "ERRORS in PublishBycteamList." >> $MAILTO_RE_FILE
		echo "See: $LOGS/PublishBycteamList-$BUILDID-$NTSTAMP.out"
		exit 1
	}
fi

# increment nightly build ID
export NITEID=$(expr $(cat $BUILDAREA/nightly/re-gate/build/NITEID) + 1)
echo $NITEID > $BUILDAREA/nightly/re-gate/build/NITEID

date

echo "Creating entire pkg"
sudo $RE_BIN/soltools -r $RELEASE -c $CONF_FILE MkEntire || {
	echo "Unable to create entire package"
	echo "ERRORS in MkEntire." >> $MAILTO_RE_FILE
	exit 1
} 

pkg list -nvHg /export/repos/${reposubdir} entire | tee -a $MAILTO_RE_FILE

date

# Restart the nightly repo
echo "Refreshing the catalog"
sudo pkgrepo -s file:///export/repos/${reposubdir} refresh --no-index


sudo svcadm restart ${DOCKREL}_nightly

# generate static list for version soak auditing
pkg list -afHg /export/repos/${reposubdir} pkg://solaris/*@latest | 
awk '{print $1"@"$2}' > /tmp/pkglist.$RELEASE
scp /tmp/pkglist.$RELEASE \
pkglintr@ipsdock-re:/export/pkglintr/$RELEASE/pkglist.$RELEASE

date

sleep 120

# make Distro Images

# We need to first update the build servers

typeset -r BENAME=${RELEASE}-${BUILDID}nightly-$(date +%y%m%d)

if [ "$UPDATE_DC" == "true" ] ; then
	ssh $DCSRVS sudo pkg set-publisher -G \'*\' -g http://solaris-re/$RELEASE/nightly solaris
	ssh $DCSRVS sudo pkg update --be-name $BENAME --accept
	if [ $? -eq 0 ]; then
		ssh $DCSRVS sudo /usr/sbin/reboot
	else
		echo >> $MAILTO_RE_FILE 
		echo "WARNING: $DCSRVS server nightly update FAILED!" >> $MAILTO_RE_FILE 
		echo >> $MAILTO_RE_FILE 
	fi
	ssh $DCSRVX sudo pkg set-publisher -G \'*\' -g http://solaris-re/$RELEASE/nightly solaris
	ssh $DCSRVX sudo pkg update --be-name $BENAME --accept
	if [ $? -eq 0 ]; then
		ssh $DCSRVX sudo /usr/sbin/reboot
	else
		echo >> $MAILTO_RE_FILE
		echo "WARNING: $DCSRVX server nightly update FAILED!" >> $MAILTO_RE_FILE
		echo >> $MAILTO_RE_FILE
	fi
	# allow time for reboot
	sleep 300
fi

# set DC build servers for nightly builds

# parallel process on $DCSRVS starts up SPARC build

echo "Building ISO images."

localdc=export/dc/$MAJORREL/$reposubdir


ssh $DCSRVX sudo $RE_BIN/soltools -r $RELEASE -c $CONF_FILE \
	DoDCbuild ai > $LOGS/dc_ai_x86_nite-$BUILDID-$NTSTAMP.out 2>&1 &
xpidai=$!

ssh $DCSRVS sudo $RE_BIN/soltools -r $RELEASE -c $CONF_FILE \
	DoDCbuild ai > $LOGS/dc_ai_sparc_nite-$BUILDID-$NTSTAMP.out 2>&1 &
spidai=$!

sleep 60
ssh $DCSRVX sudo $RE_BIN/soltools -r $RELEASE -c $CONF_FILE \
	DoDCbuild text > $LOGS/dc_text_x86_nite-$BUILDID-$NTSTAMP.out 2>&1 &
xpidtext=$!

ssh $DCSRVS sudo $RE_BIN/soltools -r $RELEASE -c $CONF_FILE \
	DoDCbuild text > $LOGS/dc_text_sparc_nite-$BUILDID-$NTSTAMP.out 2>&1 &
spidtext=$!

sleep 60
ssh $DCSRVX sudo $RE_BIN/soltools -r $RELEASE -c $CONF_FILE \
 DoDCbuild live > $LOGS/dc_live_x86_nite-$BUILDID-$NTSTAMP.out 2>&1 &
xpidlive=$!

ssh $DCSRVS sudo $RE_BIN/soltools -r $RELEASE -c $CONF_FILE \
	DoDCbuild boot > $LOGS/dc_boot_sparc_nite-$BUILDID-$NTSTAMP.out 2>&1 &
spidboot=$!

typeset -i dozecnt=1
while [ $dozecnt -lt 12 ]; do
	echo $dozecnt
	dozecnt=dozecnt+1
	# this would be a string of all DC PIDs
	ps $spidai || ps $xpidai || ps $spidtext || ps $xpidtext || ps $spidboot || ps $xpidlive || break   
	sleep 900 
done
if [ $dozecnt -eq 12 ]; then
	echo "Error: DC builds are hanging, jobs were killed" >> $MAILTO_RE_FILE
	kill  $spidai $xpidai $spidtext $xpidtext $spidboot $xpidlive
	exit 1
fi

wait

xcomp=/net/$DCSRVX/$localdc/.complete
scomp=/net/$DCSRVS/$localdc/.complete

typeset -r NANADIR=/net/nana/var/ftp/products/$NANA_REL_STRING
typeset -r IMAGEDIR=/net/$imgserver/export/images/$RELEASE

if [ ! -d $NANADIR/$RELEASE/.RE/nightly ] ; then
	sudo mkdir $NANADIR/$RELEASE/.RE/nightly
fi

sleep 300 

integer dc_ai_error=0
if [ -e ${xcomp}/successful.ai -a -e ${scomp}/successful.ai ] ; then
	sudo cp -p $IMAGEDIR/nightly/*ai* \
		$NANADIR/$RELEASE/.RE/nightly || dc_ai_error=3
elif [ -e ${xcomp}/failed.ai -a -e ${scomp}/failed.ai ] ; then
	echo "Error building AI on x86 and SPARC. See:" >> $MAILTO_RE_FILE
	echo "/net/$DCSRVX/$localdc/ai/logs and" >> $MAILTO_RE_FILE
	echo "/net/$DCSRVS/$localdc/ai/logs" >> $MAILTO_RE_FILE
	dc_ai_error=1
	dcstatus=FAILED
elif [ -e ${xcomp}/successful.ai -a -e ${scomp}/failed.ai ] ; then
	sudo cp -p $IMAGEDIR/nightly/*ai-x86* $NANADIR/$RELEASE/.RE/nightly
	echo "Error building AI on SPARC. See:" >> $MAILTO_RE_FILE
	echo "/net/$DCSRVS/$localdc/ai/logs" >> $MAILTO_RE_FILE
	dc_ai_error=1
	dcstatus=FAILED
elif [ -e ${xcomp}/failed.ai -a -e ${scomp}/successful.ai ] ; then
	dc_ai_error=1
	dcstatus=FAILED
	echo "Error building AI on X86. See:" >> $MAILTO_RE_FILE
	echo "/net/$DCSRVX/$localdc/ai/logs" >> $MAILTO_RE_FILE
	sudo cp -p $IMAGEDIR/nightly/*ai-sparc* $NANADIR/$RELEASE/.RE/nightly
fi


# Create solaris-auto-installer
if [ $dc_ai_error -eq 0 ] ; then
echo "Creating solaris-auto-installer ..."
	sudo pkgmerge -s arch=sparc,\
file:///net/$DCSRVS/export/dc/$MAJORREL/$RELEASE/nightly/ai/media/ai_image_repo \
        -s arch=i386,\
file:///net/$DCSRVX/export/dc/$MAJORREL/$RELEASE/nightly/ai/media/ai_image_repo \
	-d /export/repos/$RELEASE/nightly
	fi

echo "Refreshing the nightly repo in background..."
sudo pkgrepo -s file:///export/repos/${reposubdir} refresh --no-index &

echo "Update deployment pubdate and content"
sudo pkgrepo set -s file:///export/repos/${reposubdir} \
deployment/pubdate=`date -u '+%Y%m%dT%H%M%SZ'`


if [ -e ${xcomp}/successful.text -a -e ${scomp}/successful.text ] ; then
	sudo cp -p $IMAGEDIR/nightly/*text* $NANADIR/$RELEASE/.RE/nightly
elif [ -e ${xcomp}/successful.text -a -e ${scomp}/failed.text ] ; then
	dcstatus=FAILED
	sudo cp -p $IMAGEDIR/nightly/*text-x86* $NANADIR/$RELEASE/.RE/nightly
	echo "ERROR building text on SPARC. See:" >> $MAILTO_RE_FILE
	echo "/net/$DCSRVS/$localdc/text/logs." >> $MAILTO_RE_FILE
elif [ -e ${xcomp}/failed.text -a -e ${scomp}/successful.text ] ; then
	dcstatus=FAILED
	sudo cp -p $IMAGEDIR/nightly/*text-sparc* $NANADIR/$RELEASE/.RE/nightly
	echo "ERROR building text on X86. See:" >> $MAILTO_RE_FILE
	echo "/net/$DCSRVX/$localdc/text/logs." >> $MAILTO_RE_FILE
elif [ -e ${xcomp}/failed.text -a -e ${scomp}/failed.text ] ; then
	dcstatus=FAILED
	echo "ERROR building text on SPARC & X86. See:" >> $MAILTO_RE_FILE
	echo "/net/$DCSRVS/$localdc/text/logs." >> $MAILTO_RE_FILE
	echo "/net/$DCSRVX/$localdc/text/logs." >> $MAILTO_RE_FILE
fi


if [ -e ${xcomp}/successful.live ] ; then
	sudo cp -p $IMAGEDIR/nightly/*live* $NANADIR/$RELEASE/.RE/nightly
else
	dcstatus=FAILED
	echo "ERROR: X86 Live Media failed. See:" >> $MAILTO_RE_FILE
	echo "/net/$DCSRVX/$localdc/livecd/logs." >> $MAILTO_RE_FILE
fi

if [ ! -e ${scomp}/successful.boot ] ; then
	dcstatus=FAILED
	echo "ERROR: SPARC Boot Media failed. See:" >> $MAILTO_RE_FILE
	echo "/net/$DCSRVS/$localdc/boot/logs." >> $MAILTO_RE_FILE
fi

sudo mv $NANADIR/$RELEASE/.RE/nightly/*  $NANADIR/$RELEASE/nightly

sudo svcadm restart ${DOCKREL}_nightly

echo "Nana status" >> $MAILTO_RE_FILE
ls -lt $NANADIR/$RELEASE/nightly | tail +2 >> $MAILTO_RE_FILE

echo "Nightly end time: \c" | tee -a $MAILTO_RE_FILE
date | tee -a $MAILTO_RE_FILE

MAILSUBJECT="$RELEASE Nightly Build $dcstatus"

exit 0
