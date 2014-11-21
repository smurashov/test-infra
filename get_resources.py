import argparse
import requests
import json


parser = argparse.ArgumentParser(description="Get resources for test config")

parser.add_argument("-pumphouse_url", dest='pumphouse_url', type=str,
                    help="Pumphouse url",
                    default='http://localhost:5000')

args = parser.parse_args()

req = requests.get("%s/resources" % args.pumphouse_url).text
req = json.loads(req)
tenant = next(
    i for i in req['source']['resources']
    if i['type'] == 'tenant' and i['data']['name'] == 'admin')['id']

host = next(
    i for i in req['source']['resources'] if i['type'] == 'host')['id']

myconfig = {
    "endpoint": args.pumphouse_url,
    "timeout": 120,
    "cases": ["reset", "migrate", "evaculate"],
    "tenant": {
        "id": tenant,
        "type": "tenant",
        "cloud": "source"
    },
    "host": {
        "id": host,
        "type": "host",
        "cloud": "source"
    }
}
with open('config.js', 'w') as config:
    config.write(
        "module.exports = " + json.dumps(myconfig, config, indent=4) + ";")
