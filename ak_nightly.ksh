#!/bin/ksh

export PATH=$PATH:/usr/sbin
[[ "$0" == /* ]] && typeset -r PRG=$0 || typeset -r PRG=$PWD/$0

OPT_REL=
OPT_TYPE=nightly
CONF_NAME=nightly.conf

while getopts ':r:t:g' char ; do
        case $char in
                r)      OPT_REL=$OPTARG
                        ;;
                t)      OPT_TYPE=$OPTARG
                        ;;
                \?)     echo "Unknown option $OPTARG"
                        exit 1
                        ;;
        esac
done
