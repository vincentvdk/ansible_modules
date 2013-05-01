#!/usr/bin/python
from ovirtsdk.api import API
from ovirtsdk.xml import params

# ------------------------------------------------------------------- #
# create connection with API
#
def conn(url, user, password):
    api = API(url=url, username=user, password=password, insecure=True)
    try:
        value = api.test()
    except:
        print "error connecting to the oVirt API"
        sys.exit(1)
    return api

# ------------------------------------------------------------------- #
# VM operations
#
# def create_vm():
#def create_vm(conn, vmname, 

# start vm
def vm_start(conn, vmname):
    vm = conn.vms.get(name=vmname)
    vm.start()

# Stop vm
def vm_stop(conn, vmname):
    vm = conn.vms.get(name=vmname)
    vm.stop()

# ------------------------------------------------------------------- #
# VM statuses
#
# Get the VMs status
def vm_status(conn, vmname):
    status = conn.vms.get(name=vmname).status.state
    print "vm status is : %s" % status
    return status


# Get VM object and return it's name if object exists
def get_vm(conn, vmname):
    vm = conn.vms.get(name=vmname)
    if vm == None:
        name = "empty"
        print "vmname: %s" % name
    else:
        name = vm.get_name()
        print "vmname: %s" % name
    return name

# ------------------------------------------------------------------- #
# Main

def main():

    module = AnsibleModule(
        argument_spec = dict(
            state = dict(default='present', choices=['present', 'absent', 'shutdown', 'started']),
            #name      = dict(required=True),
            user = dict(required=True),
            url = dict(required=True),
            vmname = dict(required=True),
            pwd = dict(required=True),
            image = dict(required=False),
            instance_type = dict(choices=['new', 'template']),
            zone = dict(),
            disk_size = dict(),
            cpus = dict(),
        )
    )

    state    = module.params['state']
    user          = module.params['user']
    url           = module.params['url']
    vmname        = module.params['vmname']
    password      = module.params['pwd']
    image         = module.params['image']
    instance_type = module.params['instance_type']
    zone          = module.params['zone']   # cluster


    #initialize connection
    c = conn(url, user, password)

    if state == 'present':
        if get_vm(c, vmname) == "empty":
            module.exit_json(changed=True, msg="we need to create VM %s" % vmname)
        else:
            module.exit_json(changed=False, msg="VM %s already exists" % vmname)

    if state == 'started':
        if vm_status(c, vmname) == 'up':
            module.exit_json(changed=False, msg="VM %s is already running" % vmname)
        else:
            vm_start(c, vmname)
            module.exit_json(changed=True, msg="VM %s started" % vmname)
    
    if state == 'shutdown':
        if vm_status(c, vmname) == 'down':
            module.exit_json(changed=False, msg="VM %s is already shutdown" % vmname)
        else:
            vm_stop(c, vmname)
            module.exit_json(changed=True, msg="VM %s is shutting down" % vmname)




# include magic from lib/ansible/module_common.py
#<<INCLUDE_ANSIBLE_MODULE_COMMON>>
main()
