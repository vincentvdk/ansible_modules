#!/usr/bin/python

def main():

    module = AnsibleModule(
        argument_spec = dict(
            state = dict(default='present', choices=['present', 'absent']),
            name = dict(required=True),
            sysname = dict(required=True),
            url = dict(required=True),
            user = dict(required=True),
            pwd = dict(required=True),
        )

    )

    state = module.params['state']
    channelname = module.params['name']
    systname = module.params['sysname']
    saturl = module.params['url']
    user = module.params['user']
    pwd = module.params['pwd']

    #initialize connection
    client = xmlrpclib.Server(saturl, verbose=0)
    session = client.auth.login(user, pwd)
     ¬   
    # get systemid
    sys_id = get_systemid(client, session, systname)

    # get channels for system
    chans = base_channels(client, session, sys_id)

    if state == 'present':
        if channelname in chans:
            module.exit_json(changed=False, msg="Channel %s already exists" % channelname)

        else:
            subscribe_channels(channelname, client, session, systname, sys_id)
            module.exit_json(changed=True, msg="Channel %s added" % channelname)

