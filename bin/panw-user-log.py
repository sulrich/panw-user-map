#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
import argparse
import pan.xapi
import re
import sys
from string import Template

# template string to be used for user-ip addr mappings and fed to the PAN-OS
# API
entry_txt = '<entry name="$user" ip="$ip_addr"/>\n'

# template string for the XML API submission.  entries for login/logout events
# are placed in the respective locations.
userid_block = """
<uid-message>
<type>update</type>
  <payload>
    <login>
$lin
    </login>
    <logout>
$lout
    </logout>
  </payload>
</uid-message>\n"""


def main(args):
    panw_user_config = os.environ['HOME'] + "/.config/users-panw.yaml"
    if args.config:
        panw_user_config = args.config

    try:
        with open(panw_user_config, 'r') as c:
            config = yaml.load(c)
    except Exception as e:
        print "ERROR: unable to open config file: ", panw_user_config
        print "exception: ", e

    cachedir = config["cache_dir"]

    login = []                 # list of entries to generate login events for
    logout = []                # ibid, but logout events

    if args.user:
        maclist = config["users"][args.user]
        (entry_login, entry_logout) = parse_addr_binding(args.user, maclist,
                                                         cachedir)
        if entry_login:
            login += entry_login                  # merge, don't append
        if entry_logout:
            logout += entry_logout
    else:
        for u in config["users"]:
            maclist = config["users"][u]
            (entry_login, entry_logout) = parse_addr_binding(u,
                                                             maclist, cachedir)
            if entry_login:
                login += entry_login
            if entry_logout:
                logout += entry_logout

    e_temp = Template(entry_txt)
    ublock = Template(userid_block)

    lin = generate_entries(login, e_temp)
    lout = generate_entries(logout, e_temp)

    e = {'lin': lin, 'lout': lout}
    ucmd = ublock.substitute(e)

    try:
        xapi = pan.xapi.PanXapi(tag=config["api_tag"])
    except pan.xapi.PanXapiError as msg:
        print "pan.xapi.PanXapi:", msg
        sys.exit(1)

    try:
        xapi.user_id(cmd=ucmd)
    except pan.xapi.PanXapiError as umesg:
        print "ERROR: user-id mod\n--\n%s\n--\n" % umesg


def generate_entries(elist, template):
    """ elist: list of entries to be put into the associated template for
    replacement

    template: a template object to do the associated replacement in

    returns: string with the associated replacements in place.

    """
    entries = ""
    for i in elist:
        d = {'user': i[0], 'ip_addr': i[1]}
        entries += template.substitute(d)

    return entries


def parse_addr_binding(user, maclist, cachedir):
    """user:
    maclist:
    cachedir:

    returns: list of strings with the entries for insertion into the user-id
    update process.  this list should be appended to the running collection of
    userid/mac addr bindings that will be processed to set the user binding on
    the firewall.

    """

    # for each mac address in the list parse the associated arp/nd cache file
    # and return the entries for the login and logout stanza. logout the STALE
    # entries, login the REACHABLE entries
    #
    # note: this assumes linux ip command output. needs to be adjusted for
    # other gleaning methods.

    maclogin = []
    maclogout = []

    # strip out the fields we're not interested in as well as link local IPv6
    # addresses
    skip_re = re.compile("^(dts|fe80)")
    ip_entry_re = re.compile("(.*) dev (.*) lladdr (.*) (.*)")

    for mac in maclist:
        fn = re.sub(':', '', mac)
        fn = cachedir + "/" + fn + "-arpnd-cache"

        try:
            with open(fn, 'r') as macfile:
                for l in macfile:
                    skip = re.match(skip_re, l)
                    if skip:
                        continue

                    entry = re.match(ip_entry_re, l)
                    if entry:
                        if entry.group(4) == "STALE":
                            maclogout.append([user, entry.group(1)])
                            # print "logout: %s" % [user, entry.group(1)]
                        else:
                            maclogin.append([user, entry.group(1)])
                            # print "login: %s" % [user, entry.group(1)]

        except Exception:
            print "ERROR: unable to open arp/nd cache file (%s)" % fn

    return(maclogin, maclogout)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', dest='config', required=False,
                        help="file to parse for for config info")
    parser.add_argument('--user', dest='user', required=False,
                        help="user to update bindings for")
    args = parser.parse_args()
    main(args)
