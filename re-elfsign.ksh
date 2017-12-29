#! /bin/ksh

OPT_DEBUG=false
OPT_START=1

BLDSERVER=twilight.us.oracle.com

[ "$OPT_DEBUG" == 'true' ] && set -x

while getopts ':r:n:g' char ; do
        case $char in
                r)      OPT_REL=$OPTARG
                        ;;
		n)	OPT_START=$OPTARG
			;;
		g)	OPT_DEBUG=true
			;;
                \?)     echo "Unknown option $OPTARG"
                        exit 1
                        ;;
        esac
done

case $OPT_REL in
	s11.*)	REPOPATH=/export/repos/regression_test/$OPT_REL/builds
		if [ "$OPT_REL" == "s11.0" ] ; then
			ELFREL=s11.0
		else
			ELFREL=s11
		fi
		;;
	s12.*)	REPOPATH=/net/twilight.us.oracle.com/export/repos/regression_test/$OPT_REL/builds
		ELFREL=s12
		;;
	\?)	echo "ERROR - Unknown release $OPT_REL"
		exit 1
		;;
esac

set -x
if [[ "$OPT_REL" == s12* ]]; then
	PKGSEND="ssh releng@elliemae sudo /usr/bin/pkgsend"
	SENDHOST=/net/$reposys
else
	SENDHOST=
	PKGSEND=/usr/bin/pkgsend
fi
set +x

ElfsignPkg () {

	[ "$OPT_DEBUG" == 'true' ] && set -x
       
	# elfsign binaries from a C-team repo, publishing back to that repo

	FormatExceptions () {
		# translate hashed pathnames into real ones for pathnames
		# that are excluded from elfsigning
		elfout=$1
		pkgarea=$2
		elfpkg=$3
		#get list of files that are excluded
		hashexcepts=$(awk '/WARNING: exception/ {print $4}' $elfout)
		for hashexcept in $hashexcepts; do
			# extract hashed pathname from output
			hashpath=$(echo $hashexcept | awk -F/ '{print $5}' | \
			  sed "s/ .*//")
			# derive real pathname from pkg manifest file
			realpath=$(sed -n \
			  "s|file $hashpath .* path=\(.*\) pkg.csize.*|\1|p" \
			  $pkgarea/*/manifest)
			# make swap, adding pkg name to output
			sed -e "s|$hashpath|$realpath|" \
			  -e "s|, .*Z:|, $elfpkg:|" $elfout > $elfout.new
			  mv $elfout.new $elfout
		done

		# get list of full packages that are excluded
		pkgexcept=$(awk '/exception found in/ {print $2}' $elfout)
		if [ -n "$pkgexcept" ]; then
		  sed "s|$pkgexcept|$elfpkg|" $elfout > $elfout.new
		  mv $elfout.new $elfout
		fi

		# clean up by removing tmp pathname and adding slashes to pkg
		sed -e "s|/tmp/sgnpkg.[0-9][0-9]*.[0-9][0-9]*.[0-9][0-9]*/||" \
	 	  $elfout | sed -e "s|%2F|/|g" \
		  -e "s|%2C|,|" -e "s/:\./: /"> $elfout.new

		mv $elfout.new $elfout
	}

	RAWPKG=$1

#	ELFBIN=/net/pkgdock/export/RE/bin
#	ELFBIN=/net/ikura-re/export/PROXY/bin
	ELFBIN=/net/vulcan/export/PROXY/bin


	# Run elfsign
	# isolate package name
	baseraw=$(dirname $RAWPKG)
	pkgname=$(basename $baseraw)
	fmriname=$(basename $RAWPKG)
	mkdir $baseraw/elfsigned

	$ELFBIN/elfsign_pkg.ips -d $baseraw \
	  -t $baseraw/elfsigned -r $ELFREL $fmriname > \
	  $baseraw/elfsigned/elfout.tmp 2>&1
	elferr=$?

	# make signing exceptions output easier to read
	FormatExceptions $baseraw/elfsigned/elfout.tmp $baseraw $pkgname

	cat  $baseraw/elfsigned/elfout.tmp
	rm $baseraw/elfsigned/elfout.tmp
	if [ "$elferr" -ne 0 ]; then
		echo "Elfsigning failed"
		return 1
	fi

        # if package is not elfsigned, then elfsigned directory will be empty
	if ls $baseraw/elfsigned/* > /dev/null 2>&1 ; then
		rm -rf $RAWPKG
		mv $baseraw/elfsigned/* $RAWPKG
	fi
	rmdir $baseraw/elfsigned
}


[ "$OPT_DEBUG" == 'true' ] && set -x


if [ ! -d $REPOPATH ] ; then
	echo "ERROR - The repository $REPOPATH does not exist"
	exit 1
fi

pkgrepo -s $REPOPATH info > /dev/null || exit 1


mkdir $REPOPATH/original || exit 1
mv $REPOPATH/* $REPOPATH/original 2>/dev/null


typeset pkglist=$(pkgrepo -s $REPOPATH/original list -F tsv -H \* 2>/dev/null | awk '{print $NF}')

#typeset pkglist="pkg://solaris/x11/xconsole@1.0.4,5.11-0.175.1.0.0.24.1317:20120904T180121Z pkg://solaris/x11/xfd@1.1.1,5.11-0.175.1.0.0.24.1317:20120904T180122Z"

mkdir $REPOPATH/raw
mkdir $REPOPATH/new
pkgrepo -s $REPOPATH/new create

pkgrecv -s $REPOPATH/original -d $REPOPATH/raw --raw $pkglist

for pkg in $(echo $REPOPATH/raw/*/*) ; do
	ElfsignPkg $pkg || exit 1
	$PKGSEND -s $REPOPATH/new publish --fmri-in-manifest \
	  --no-catalog --no-index -d $pkg $pkg/manifest
done

#rmdir $REPOPATH/new
rm -rf $REPOPATH/raw
pkgrepo -s $REPOPATH/new rebuild

exit 0
