import argparse
import time

import novaclient.v1_1.client as nvclient


parser = argparse.ArgumentParser(description="Script for vm create")

parser.add_argument("-openstack_user",  dest='openstack_user',  type=str,
                    help="Openstack username",  default='admin')

parser.add_argument("-openstack_password",  dest='openstack_password',
                    type=str, help="Openstack password",
                    default='111')

parser.add_argument("-openstack_tenant",  dest='openstack_tenant',  type=str,
                    help="Openstack tenant",  default='admin')

parser.add_argument("-keystone_url",  dest='keystone_url',  type=str,
                    help="Keystone url", default='http://localhost:5000/v2.0/')

parser.add_argument("-server_name",  dest='server_name',  type=str,
                    help="Server name",  default='cimachine')

parser.add_argument("-image_id",  dest='image_id',  type=str,
                    help="Image id",  default='id')

parser.add_argument("-flavor_id",  dest='flavor_id',  type=str,
                    help="Flavor id",  default='id')

parser.add_argument("-net_id",  dest='net_id',  type=str,
                    help="Network id",  default='id')

parser.add_argument("-keypair",  dest='keypair',  type=str,
                    help="Keypair name",  default='huj')

args = parser.parse_args()

user = args.openstack_user
password = args.openstack_password
tenant = args.openstack_tenant
keystone_url = args.keystone_url
server_name = args.server_name
image_id = args.image_id
flavor_id = args.flavor_id
net_id = args.net_id
keypair = args.keypair

nova = nvclient.Client(user, password, tenant, keystone_url,
                       service_type="compute")

server = nova.servers.create(server_name, image_id, flavor_id,
                             key_name=keypair, nics=[{'net-id': net_id}])

start_time = time.time()

while nova.servers.get(server.id).status != 'ACTIVE':
    if time.time() - start_time > 250:
        raise Exception
    time.sleep(1)
