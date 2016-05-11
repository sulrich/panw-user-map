#!/bin/bash

# a script to scape the adjacencies for the routing device in use for the MAC
# addresses associated with a given users device.
#
# creates text files for the complementary user-id population script to do its
# thing. also assumes that the home network is dual-stack enabled though it
# should work just fine in an IPv4 only environment.
#
# one text file per MAC address is created to allow the user-id script to deal
# with stale entries and active entries as appropriate.
#
# dependencies:
# shyaml (https://github.com/0k/shyaml) - a nice tool to let shell scripts
# read YAML files for configuration info.
#
# also assumes that you've taken the necessary steps to secure the execution
# of commands on your routing device.


# $ROUTER - take the necessary precautions to secure access to this device
CONFIG="${HOME}/.config/users-panw.yaml"
USER="max"   # can be overriden with the -u argument
# router to glean arp/nd bindings from
ROUTER=$(cat ${CONFIG} | shyaml get-value router)

# XXX - add command line args to modify this
# XXX - specify a config file to reference other than the dfault.
# XXX - specify a user to check within the config
# while [[ $# > 0 ]]
# do
#   KEY="$1"
#
#   case "${KEY}" in
#     -c|--config)
#       shift
#       ;;
#     -u|--user)
#       shift
#       ;;
#     *)  # no options specified
#       ;;
#   esac
#   shift
# done



# wrap the MACLIST in an array.  shyaml doesn't deal with the nested values
# per se, so you need to scrub them a bit if you're not directly gettig the
# leaf value.  hence, the sed to strip
MACLIST=($(cat ${CONFIG} | shyaml get-value users.${USER} | sed 's/\-//g'))

# get the current bindings from router  for all address families
source "${HOME}/.keychain/${HOSTNAME}-sh"
for M in "${MACLIST[@]}";
do
  J="${M//\:/}-arpnd-cache" # generate filename sans colons
  DTS=$(date +"%Y%m%d-%H%M%S")
  # generate an arp/nd cache file per MAC address
  echo "dts: ${DTS}" > "/tmp/${J}" # largely optional but useful for debugging
  ssh "${ROUTER}" "ip neighbor show | grep ${M}" >> "/tmp/${J}"
done
