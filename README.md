# panw-user-map


## overview

some quick and dirty scripts to parse local MAC to IPv(4|6) address binding information and use the PAN-OS XML API to log-in/out a user from a PAN-OS device.  useful for small scale environments (read, home networks) where there might be utility in selective policy enforcement for a few devices which are dual-stack enabled, and there may be churn in the IPV6 prefix-delegation, etc making hardcoding of IP addresses to user bindings, etc. problematic.

## dependencies
### utilities

- [shyaml](https://github.com/0k/shyaml) - used to parse configuration information for the shell script.

### python module(s)

- [PyYAML](https://pypi.python.org/pypi/PyYAML) - does the needful
- [pan-python](https://github.com/kevinsteves/pan-python) - kevin steve's very useful palo alto networks python API.


## configuration information
