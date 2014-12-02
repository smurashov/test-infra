import requests
import urlparse
import json

from keystoneclient.v2_0 import Client as keystoneclient


class NailgunClient(object):

    def __init__(self, admin_node_ip, **kwargs):
        self.url = "http://{0}:8000".format(admin_node_ip)
        keystone_url = "http://{0}:5000/v2.0".format(admin_node_ip)
        ksclient = keystoneclient(auth_url=keystone_url, **kwargs)
        self.headers = {"X-Auth-Token": ksclient.auth_token}

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
        return requests.post(endpoint, headers=self.headers, data=data)

    def list_cluster_nodes(self, cluster_id):
        endpoint = urlparse.urljoin(
            self.url, "api/nodes/?cluster_id={}".format(cluster_id))
        return requests.get(endpoint, headers=self.headers).json()

    def update_cluster_attributes(self, cluster_id, attrs):
        endpoint = urlparse.urljoin(
            self.url, "api/clusters/{}/attributes".format(cluster_id))
        return requests.put(endpoint, headers=self.headers, data=attrs)

    def update_node(self, node_id, data):
        endpoint = urlparse.urljoin(self.url, "api/nodes/{}".format(node_id))
        return requests.put(endpoint, headers=self.headers, data=data)

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
        return requests.put(endpoint, headers=self.headers, data=data)

    def update_cluster_networks(self, cluster_id, data):
        net_provider = self._get_cluster(cluster_id)["net_provider"]
        endpoint = urlparse.urljoin(
            self.url,
            "api/clusters/{}/network_configuration/{}".format(cluster_id,
                                                              net_provider))
        return requests.put(endpoint, headers=self.headers, data=data)

    def get_node_disks(self, node_id):
        endpoint = urlparse.urljoin(self.url,
                                    "api/nodes/{}/disks".format(node_id))
        return requests.get(endpoint, headers=self.headers).json()

    def put_node_disks(self, node_id, data):
        endpoint = urlparse.urljoin(self.url,
                                    "api/nodes/{}/disks".format(node_id))
        return requests.put(endpoint, headers=self.headers, data=data)
