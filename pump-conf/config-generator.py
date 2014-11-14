import yaml

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
                "auth_url": "http://localhost:5000/v2.0/",
                "username": "admin",
                "password": "111",
                "tenant_name": "admin"
            },
            "identity": {
                "connection":
                    "mysql+mysqlconnector://user:pass@localhost:3306/keystone"
            },
            "urls": {
                "horizon": "http://localhost/"
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
                "auth_url": "http://localhost:5000/v2.0/",
                "username": "admin",
                "password": "111",
                "tenant_name": "admin"
            },
            "identity": {
                "connection":
                    "mysql+mysqlconnector://user:pass@localhost:3306/keystone"
            },
            "urls": {
                "horizon": "http://localhost/",
                "mos": "http://127.0.0.1:40000/"
            },
        }
    }
}

with open('result.yaml', 'w') as yaml_file:
    yaml_file.write(yaml.dump(a, default_flow_style=False))

with open('result.yaml', 'a') as yaml_file:
    yaml_file.write(yaml.dump(d, default_flow_style=False))
