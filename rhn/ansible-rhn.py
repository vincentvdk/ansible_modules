#!/usr/bin/python

import xmlrpclib
from operator import itemgetter
import re

URL = "https://rhn.redhat.com/rpc/api"
user = ""
pswd = ""
host = ""

client = xmlrpclib.Server(URL, verbose=0)
session = client.auth.login(user, pswd)

#systems = client.system.listUserSystems(session)

# ------------------------------------------------------- #

def getSystemId():
    systems = client.system.listUserSystems(session)
    for system in systems:
        if system.get('name') == host:
            idres = system.get('id')
            idd = int(idres)
            return idd

# ------------------------------------------------------- #

def getLocalSystemId():
    f = open("/etc/sysconfig/rhn/systemid", "r")
    content = f.read()
    loc_id = re.search(r'\b(ID-)(\d{10})' ,content)
    return loc_id.group(2)

# ------------------------------------------------------- #

def subscribeChannels(channels):
    sys_id = getSystemId()
    c = baseChannels(host)
    c.append(channels)
    return client.channel.software.setSystemChannels(session, sys_id, c)

# ------------------------------------------------------- #

def unsubscribeChannels(channels):
    sys_id = getSystemId()
    c = baseChannels(host)
    c.remove(channels)
    return client.channel.software.setSystemChannels(session, sys_id, c)

# ------------------------------------------------------- #

def baseChannels(system):
    sys_id = getSystemId()
    basechan = client.channel.software.listSystemChannels(session, sys_id)
    chans = [item['channel_label'] for item in basechan]
    return chans

# ------------------------------------------------------- #


def main():
    module = AnsibleModule(
        argument_spec = dict(
            state     = dict(default='present', choices=['present', 'absent']),
            name      = dict(required=True),
        )
    )
    
    channelname = module.params['name']
    state = module.params['state']  

    chans = baseChannels(host)
    

    if state == 'present':
        if channelname in chans:
            module.exit_json(changed=False, msg="Channel %s already exists" % channelname)

        else:
            subscribeChannels(channelname)
            module.exit_json(changed=True, msg="Channel %s added" % channelname)

    if state == 'absent':
        unsubscribeChannels(channelname)
        module.exit_json(changed=True, msg="Channel %s removed" % channelname)

    client.auth.logout(session)


# include magic from lib/ansible/module_common.py
#<<INCLUDE_ANSIBLE_MODULE_COMMON>>
main()
