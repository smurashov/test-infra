import argparse
import yaml


parser = argparse.ArgumentParser(description="Yaml generator")

# Source parameters

parser.add_argument("-source_openstack_user", dest='source_openstack_user',
                    type=str, help="Source OpenStack username",
                    default='admin')

parser.add_argument("-source_openstack_password",
                    dest='source_openstack_password',
                    type=str, help="Source OpenStack password",
                    default='111')

parser.add_argument("-source_openstack_tenant",
                    dest='source_openstack_tenant',
                    type=str, help="Source OpenStack tenant",
                    default='admin')

parser.add_argument("-source_db_user", dest='source_db_user',
                    type=str, help="Source MySQL user",
                    default='root')

parser.add_argument("-source_db_password", dest='source_db_password',
                    type=str, help="Source MySQL password",
                    default='111')

parser.add_argument("-source_ip", dest='source_ip',
                    type=str, help="Source ip",
                    default='localhost')

# Destination parameters

parser.add_argument("-destination_openstack_user",
                    dest='destination_openstack_user',
                    type=str, help="Destination OpenStack username",
                    default='admin')

parser.add_argument("-destination_openstack_password",
                    dest='destination_openstack_password',
                    type=str, help="Destination OpenStack password",
                    default='111')

parser.add_argument("-destination_openstack_tenant",
                    dest='destination_openstack_tenant',
                    type=str, help="Destination OpenStack tenant",
                    default='admin')

parser.add_argument("-destination_db_user", dest='destination_db_user',
                    type=str, help="Destination MySQL user",
                    default='root')

parser.add_argument("-destination_db_password",
                    dest='destination_db_password',
                    type=str, help="Destination MySQL password",
                    default='111')

parser.add_argument("-destination_ip", dest='destination_ip',
                    type=str, help="Destination ip",
                    default='localhost')

args = parser.parse_args()

a = {
    "CLOUDS_RESET": True,
    "BIND_HOST": "0.0.0.0:5000",
    "PLUGINS": {
        "network": "nova"
    }
}

d = {
    #"CLOUDS_RESET": True,
    #"BIND_HOST": "0.0.0.0:5000",
    #"PLUGINS": {
    #    "network": "nova"
    #},
    "CLOUDS": {
        "source": {
            "endpoint": {
                "auth_url": "http://%s:5000/v2.0/" % args.source_ip,
                "username": args.source_openstack_user,
                "password": args.source_openstack_password,
                "tenant_name": args.source_openstack_tenant
            },
            "identity": {
                "connection":
                    "mysql+mysqlconnector://%s:%s@%s:3306/keystone" % (
                        args.source_db_user,
                        args.source_db_password,
                        args.source_ip)
            },
            "urls": {
                "horizon": "http://%s/" % args.source_ip
            },
            "populate": {
                "num_servers": 1,
                "num_tenants": 1
            },
            "workloads": {
                "flavors": {
                    "name": "pumphouse--flavor",
                    "ram": 64,
                    "vcpu": 1,
                    "disk": 0
                }
            },

        },
        "destination": {
            "endpoint": {
                "auth_url": "http://%s:5000/v2.0/" % args.destination_ip,
                "username": args.destination_openstack_user,
                "password": args.destination_openstack_password,
                "tenant_name": args.destination_openstack_tenant
            },
            "identity": {
                "connection":
                    "mysql+mysqlconnector://%s:%s@%s:3306/keystone" % (
                        args.destination_db_user,
                        args.destination_db_password,
                        args.destination_ip)
            },
            "urls": {
                "horizon": "http://%s/" % args.destination_ip,
                "mos": "http://127.0.0.1:40000/"
            },
        }
    }
}

with open('result.yaml', 'w') as yaml_file:
    yaml_file.write(yaml.dump(a, default_flow_style=False))

with open('result.yaml', 'a') as yaml_file:
    yaml_file.write(yaml.dump(d, default_flow_style=False))
