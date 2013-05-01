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
#def create_vm(conn, vmname, ):

# create an instance from a template
def create_vm_template(conn, vmname, image, zone):
    vmparams = params.VM(name=vmname, cluster=conn.clusters.get(name=zone), template=conn.templates.get(name=image))
    try:
        conn.vms.add(vmparams)
    except:
        print 'error adding template %s' % image
        sys.exit(1)


# start instance
def vm_start(conn, vmname):
    vm = conn.vms.get(name=vmname)
    vm.start()

# Stop instance
def vm_stop(conn, vmname):
    vm = conn.vms.get(name=vmname)
    vm.stop()

# remove an instance
def vm_remove(conn, vmname):
    vm = conn.vms.get(name=vmname)
    vm.delete()

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
# Hypervisor operations
#



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
            cpu = dict(),
            nic = dict(),
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
    disk_size     = module.params['disk_size']
    cpu           = module.params['cpu']
    nic           = module.params['nic']


    #initialize connection
    c = conn(url, user, password)

    if state == 'present':
        if get_vm(c, vmname) == "empty":
            if instance_type == 'template':
                create_vm_template(c, vmname, image, zone)
                module.exit_json(changed=True, msg="created VM %s from template %s"  % (vmname,image))
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

    if state == 'absent':
        if get_vm(c, vmname) == "empty":
            module.exit_json(changed=False, msg="VM %s does not exist" % vmname)
        else:
            vm_remove(c, vmname)
            module.exit_json(changed=True, msg="VM %s removed" % vmname)




# include magic from lib/ansible/module_common.py
#<<INCLUDE_ANSIBLE_MODULE_COMMON>>
main()
