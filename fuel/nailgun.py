import argparse
import re
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
        elif os.path.isfile("{}/cluster_networks.json".format(folder)):
            with open(
                    "{}/cluster_networks.json".format(folder)) as cluster_nets:
                cluster_nets_data = json.load(cluster_nets)
                if cluster_data["net_provider"] == "neutron":
                    new_cluster_data["net_segment_type"] = \
                        cluster_nets_data["networking_parameters"][
                            "segmentation_type"]
                else:
                    new_cluster_data["net_manager"] = \
                        cluster_nets_data["networking_parameters"][
                            "net_manager"]

        new_clust = client._create_cluster(new_cluster_data).json()
    else:
        raise NameError("Can not find cluster.json")

    if os.path.isfile("{}/cluster_attributes.json".format(folder)):
        with open(
                "{}/cluster_attributes.json".format(folder)) as cluster_attrs:
            cluster_attrs_data = json.load(cluster_attrs)

        new_cluster_attrs = client.update_cluster_attributes(
            new_clust["id"], cluster_attrs_data)

    if os.path.isfile("{}/cluster_networks.json".format(folder)):
        with open("{}/cluster_networks.json".format(folder)) as cluster_nets:
            cluster_nets_data = json.load(cluster_nets)

        restore_cluster_nets_data = client._get_list_networks(new_clust["id"])
        for key, value in cluster_nets_data["networking_parameters"].items():
            if key == "base_mac":
                continue
            restore_cluster_nets_data["networking_parameters"][key] = value

        for net in cluster_nets_data["networks"]:
            if net["name"] == "fuelweb_admin":
                continue
            for new_net in restore_cluster_nets_data["networks"]:
                if net["name"] == new_net["name"]:
                    for key, value in net.items():
                        if key in ["cluster_id", "id"]:
                            continue
                        new_net[key] = value

        client.update_cluster_networks(new_clust["id"],
                                       restore_cluster_nets_data)

    _nodes = re.compile('-(\d+)\.json$')
    nodes = [
        node.split('.')[0]
        for node in os.listdir(folder) if _nodes.search(node)]

    for node in nodes:
        with open("{}/{}.json".format(folder, node)) as node_base:
            node_base_cfg = json.load(node_base)

        available_nodes = [nod for nod in client._get_list_nodes()
                           if not nod["cluster"] and nod["online"]]
        for available_node in available_nodes:
            if (node_base_cfg["manufacturer"] !=
                    available_node["manufacturer"]):
                continue

            if os.path.isfile("{}/{}-networks.json".format(folder, node)):
                with open("{}/{}-networks.json".format(
                        folder, node)) as node_net:
                    node_net_cfg = json.load(node_net)

                new_interfaces = client.get_node_interfaces(
                    available_node["id"])

                if len(node_net_cfg) != len(new_interfaces):
                    continue

            if os.path.isfile("{}/{}-disks.json".format(folder, node)):
                with open("{}/{}-disks.json".format(
                        folder, node)) as node_disks:
                    node_disk_cfg = json.load(node_disks)

                new_disks = client.get_node_disks(available_node["id"])

                if len(node_disk_cfg) != len(new_disks):
                    continue
                good_disks = []
                for disk in sorted(node_disk_cfg,
                                   key=lambda k: k['size'], reverse=True):
                    needed_size = 0
                    for volume in disk["volumes"]:
                        needed_size += volume["size"]
                    for new_disk in new_disks:
                        if needed_size <= new_disk["size"]:
                            new_disk["volumes"] = disk["volumes"]
                            appr_disk = new_disk
                            break
                    else:
                        raise Exception("All disks are to small")
                    good_disks.append(new_disks.pop(
                        new_disks.index(appr_disk)))

            good_node = available_node
            break
        else:
            raise Exception("Can not find appropriate node")

        data = {
            "cluster_id": new_clust["id"],
            "pending_roles": node_base_cfg["pending_roles"],
            "pending_addition": True,
        }
        client.update_node(good_node["id"], data)

        if os.path.isfile("{}/{}-networks.json".format(folder, node)):
            all_nets = {}
            new_interfaces = client.get_node_interfaces(good_node["id"])
            for netw in new_interfaces:
                all_nets.update(
                    {net["name"]: net for net in netw["assigned_networks"]})
            for interface in node_net_cfg:
                for new_interface in new_interfaces:
                    if interface["name"] == new_interface["name"]:
                        ass_interfaces = [
                            all_nets[i["name"]] for i in interface[
                                "assigned_networks"]]
                        new_interface["assigned_networks"] = ass_interfaces

            resp = client.put_node_interfaces(
                [{"id": good_node["id"], "interfaces": new_interfaces}]
            )
            print resp
            print resp.content

        if os.path.isfile("{}/{}-disks.json".format(folder, node)):
            resp = client.put_node_disks(good_node["id"], good_disks)
