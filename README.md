# panw-user-map


## overview

some quick and dirty scripts to parse local MAC to IPv(4|6) address binding information and use the PAN-OS XML API to log-in/out a user from a PAN-OS device.  useful for small scale environments (read, home networks) where there might be utility in selective policy enforcement for a few devices which are dual-stack enabled, and there may be churn in the IPV6 prefix-delegation, etc making hardcoding of IP addresses to user bindings, etc. problematic.

## dependencies
### utilities

- [shyaml](https://github.com/0k/shyaml) - used to parse configuration information for the shell script.

### python module(s)

- [PyYAML](https://pypi.python.org/pypi/PyYAML) - does the needful
- [pan-python](https://github.com/kevinsteves/pan-python) - kevin steves very useful palo alto networks python API.

## operation

## overview

there is a shell script which gleans the relevant L2 adjacency information off the router.  in this case it's just running the relevant linux `ip` commands to gather the IPv4 and IPv6 address bindings for the MAC addresses of the devices of interest.  since PANW firewalls don't provide matching on MAC address capabilities so matching across L3 address families is a bit of a pain.  one way to approach this would be to statically assign IP addresses but doing this w/IPv6 prefix delegation is another rats nest.

the shell script dumps the mappings into some files which are in turn processed by the python script and populate the user bindings inside the firewall using the XML API.

based on the bindings the user mappings updated (logged in / out appropriately) and the standard PAN-OS policy application takes place based on these updated user bindings.


### configuration

the configuration file (`config/users-panw.yml`) is shared across the shell script and the python script.  most of this is/was specific to my environment, but the process is pretty simple to modify to your ends.   this script uses the API tag facility that keven steves [pan-python](https://github.com/kevinsteves/pan-python) library exposes.  in brief, this provides you with the facility to authenticate to the firewall's XML API and store those credentials.  you can then use those credentials seamlessly when exercising the API. (details re: API key generation and use can be found here - [http://api-lab.paloaltonetworks.com/keygen.html](http://api-lab.paloaltonetworks.com/keygen.html))  you will need to set this up or adjust the script appropriately to authenticate and use the API.

### configuration fields
- **firewall** - hostname / IP address of the firewall with user-id policy.  
- **router** - hostname / IP address of the router which has the L2/L3 binding information.  this is only used by the   `get-arp-nd-cache.sh` shell script.  assumes that you have a process for securing these credentials appropriately.  
- **adj_cmd** - command used to clean the L2/L3 adj bindings off the router.  the `%%MACADDR%%` in example below is replaced with the MAC address of the user's device.  
- **cache_dir** - path to the directory for the arpnd-cache files to be placed.  
- **users** - a YAML collection with the user-id and a list of the associated MAC addresses of their devices which will be subject to the firewall policy.  

``` yaml
firewall: sulrich-pa200.botwerks.net
router: 10.0.0.1
adj_cmd: "ip neighbor show | grep %%MACADDR%%"
api_tag: test
cache_dir: /tmp
users:
  max:
    - 30:10:e4:70:5a:2a  # max ipad
    - 5C:97:F3:1D:01:6E  # max laptop
  bunbun:
    - 66:97:F3:1D:01:6E  # bunbun iphone
    - 66:8D:12:0F:E3:04  # bunbun laptop
    - 66:10:e4:70:5a:2a  # household ipad
```

### cron

the shell script to glean the entries from the routing device needs to be added to the crontab of the device running these scripts.

## administravia
**author:** steve ulrich \<[sulrich@botwerks.org](mailto:sulrich@botwerks.org)\>  
**license:** CC0 1.0 universal (see LICENSE.txt)
**source:** [https://github.com/sulrich/panw-user-map](https://github.com/sulrich/panw-user-map)  

