import argparse
import time

import novaclient.v1_1.client as nvclient


parser = argparse.ArgumentParser(description="Script for clean vms")

parser.add_argument("-openstack_user",  dest='openstack_user',  type=str,
                    help="Openstack username",  default='admin')

parser.add_argument("-openstack_password",  dest='openstack_password',
                    type=str, help="Openstack password",
                    default='111')

parser.add_argument("-openstack_tenant",  dest='openstack_tenant',  type=str,
                    help="Openstack tenant",  default='admin')

parser.add_argument("-keystone_url",  dest='keystone_url',  type=str,
                    help="Keystone url", default='http://localhost:5000/v2.0/')

args = parser.parse_args()

user = args.openstack_user
password = args.openstack_password
tenant = args.openstack_tenant
keystone_url = args.keystone_url

nova = nvclient.Client(user, password, tenant, keystone_url,
                       service_type="compute")


for i in nova.servers.list():
    if ("cidevstack" in i.name or "cipumphouse" in i.name)\
            and user == i.user_id:
        i.delete()
        start_time = time.time()
        while time.time() - start_time < 250:
            try:
                nova.servers.get(i.id)
            except Exception:
                break
