import argparse
import requests
import urlparse
import os
import json


from keystoneclient.v2_0 import Client as keystoneclient


class NailgunClient(object):

    def __init__(self, admin_node_ip, **kwargs):
        self.url = "http://{0}:8000".format(admin_node_ip)
        keystone_url = "http://{0}:5000/v2.0".format(admin_node_ip)
        ksclient = keystoneclient(auth_url=keystone_url, **kwargs)
        self.headers = {"X-Auth-Token": ksclient.auth_token,
                        "Content-Type": "application/json"}

    def _get_cluster_list(self):
        endpoint = urlparse.urljoin(self.url, "api/clusters")
        return requests.get(endpoint, headers=self.headers).json()

    def _get_cluster(self, cluster_id):
        endpoint = urlparse.urljoin(self.url,
                                    "api/clusters/{0}".format(cluster_id))
        return requests.get(endpoint, headers=self.headers).json()

    def _get_cluster_attributes(self, cluster_id):
        endpoint = urlparse.urljoin(self.url,
                                    "api/clusters/{0}/attributes".format(
                                        cluster_id))
        return requests.get(endpoint, headers=self.headers).json()

    def _get_list_nodes(self):
        endpoint = urlparse.urljoin(self.url, "api/nodes")
        return requests.get(endpoint, headers=self.headers).json()

    def _get_list_networks(self, cluster_id):
        net_provider = self._get_cluster(cluster_id)["net_provider"]
        endpoint = urlparse.urljoin(self.url,
                                    "/api/clusters/{0}"
                                    "/network_configuration/{1}".format(
                                        cluster_id, net_provider))
        return requests.get(endpoint, headers=self.headers).json()

    def _create_cluster(self, data):
        endpoint = urlparse.urljoin(self.url, "api/clusters")
        return requests.post(endpoint, headers=self.headers,
                             data=json.dumps(data))

    def list_cluster_nodes(self, cluster_id):
        endpoint = urlparse.urljoin(
            self.url, "api/nodes/?cluster_id={}".format(cluster_id))
        return requests.get(endpoint, headers=self.headers).json()

    def update_cluster_attributes(self, cluster_id, attrs):
        endpoint = urlparse.urljoin(
            self.url, "api/clusters/{}/attributes".format(cluster_id))
        return requests.put(endpoint, headers=self.headers,
                            data=json.dumps(attrs))

    def update_node(self, node_id, data):
        endpoint = urlparse.urljoin(self.url, "api/nodes/{}".format(node_id))
        return requests.put(endpoint, headers=self.headers,
                            data=json.dumps(data))

    def get_node_interfaces(self, node_id):
        endpoint = urlparse.urljoin(self.url,
                                    "api/nodes/{}/interfaces".format(node_id))
        return requests.get(endpoint, headers=self.headers).json()

    def put_node_interfaces(self, data):
        """

        :param data: [{'id': node_id, 'interfaces': interfaces}]
        :return: response
        """
        endpoint = urlparse.urljoin(self.url, "api/nodes/interfaces")
        return requests.put(endpoint, headers=self.headers,
                            data=json.dumps(data))

    def update_cluster_networks(self, cluster_id, data):
        net_provider = self._get_cluster(cluster_id)["net_provider"]
        endpoint = urlparse.urljoin(
            self.url,
            "api/clusters/{}/network_configuration/{}".format(cluster_id,
                                                              net_provider))
        return requests.put(endpoint, headers=self.headers,
                            data=json.dumps(data))

    def get_node_disks(self, node_id):
        endpoint = urlparse.urljoin(self.url,
                                    "api/nodes/{}/disks".format(node_id))
        return requests.get(endpoint, headers=self.headers).json()

    def put_node_disks(self, node_id, data):
        endpoint = urlparse.urljoin(self.url,
                                    "api/nodes/{}/disks".format(node_id))
        return requests.put(endpoint, headers=self.headers,
                            data=json.dumps(data))


def get_cluster_id(cluster_name):
    for cluster in client._get_cluster_list():
        if cluster["name"] == cluster_name:
            return cluster["id"]
    else:
        raise NameError("Can not find cluster with specified name")


parser = argparse.ArgumentParser(
    description="Script for dump/restore cluster config")
parser.add_argument('admin_node_ip', metavar='10.20.0.2', type=str,
                    help='IP of fuel master node')

parser.add_argument("-fuel_user",  dest='fuel_user',  type=str,
                    help="Fuel username",  default='admin')

parser.add_argument("-fuel_password",  dest='fuel_password',
                    type=str, help="Fuel password",
                    default='admin')

parser.add_argument("-fuel_tenant",  dest='fuel_tenant',  type=str,
                    help="Fuel tenant",  default='admin')

parser.add_argument('-dump_cluster', dest='dump_cluster', type=str,
                    default="",
                    help='Name of cluster which configuration need to dump')

parser.add_argument("-dump_folder", dest="dump_folder", type=str,
                    default="",
                    help="Folder where cluster config will store")

parser.add_argument("-restore_cluster", dest="restore_cluster", type=str,
                    default="",
                    help="Folder which contains cluster config")

args = parser.parse_args()

client = NailgunClient(args.admin_node_ip, username=args.fuel_user,
                       password=args.fuel_password,
                       tenant_name=args.fuel_tenant)

if args.dump_cluster:
    cluster_id = get_cluster_id(args.dump_cluster)

    if args.dump_folder:
        if not os.path.exists(args.dump_folder):
            os.makedirs(args.dump_folder)
            folder = args.dump_folder
    else:
        os.makedirs(args.dump_cluster)
        folder = args.dump_cluster

    with open("{}/cluster.json".format(folder), "w") as cluster:
        json.dump(client._get_cluster(cluster_id), cluster, sort_keys=False,
                  indent=4)

    with open("{}/cluster_attributes.json".format(folder),
              "w") as cluster_attrs:
        json.dump(client._get_cluster_attributes(cluster_id), cluster_attrs,
                  sort_keys=False, indent=4)

    with open("{}/cluster_networks.json".format(folder), "w") as cluster_net:
        json.dump(client._get_list_networks(cluster_id), cluster_net,
                  sort_keys=False, indent=4)

    for node in client.list_cluster_nodes(cluster_id):
        with open("{}/node-{}.json".format(folder, node["id"]),
                  "w") as node_cfg:
            json.dump(node, node_cfg, sort_keys=False, indent=4)

        with open(
                "{}/node-{}-networks.json".format(folder,
                                                  node["id"]),
                "w") as node_net:
            json.dump(client.get_node_interfaces(node["id"]), node_net,
                      sort_keys=False, indent=4)

        with open(
                "{}/node-{}-disks.json".format(folder,
                                               node["id"]),
                "w") as node_disks:
            json.dump(client.get_node_disks(node["id"]), node_disks,
                      sort_keys=False, indent=4)

if args.restore_cluster:
    if not os.path.exists(args.restore_cluster):
        raise NameError("This folder does not exist")

    folder = args.restore_cluster

    if os.path.isfile("{}/cluster.json".format(folder)):
        with open("{}/cluster.json".format(folder)) as cluster:
            cluster_data = json.load(cluster)

        new_cluster_data = {
            "name": cluster_data["name"],
            "release": cluster_data["release_id"],
            "mode": cluster_data["mode"],
            "net_provider": cluster_data["net_provider"]
        }
        if cluster_data.get("net_segment_type"):
            new_cluster_data["net_segment_type"] = cluster_data[
                "net_segment_data"]

        new_clust = client._create_cluster(new_cluster_data).json()
    else:
        raise NameError("Can not find cluster.json")

    if os.path.isfile("{}/cluster_attributes.json".format(folder)):
        with open(
                "{}/cluster_attributes.json".format(folder)) as cluster_attrs:
            cluster_attrs_data = json.load(cluster_attrs)

        new_cluster_attrs = client.update_cluster_attributes(
            new_clust["id"], cluster_attrs_data)
