import argparse


parser = argparse.ArgumentParser(description="Get resources for test config")

parser.add_argument("-pumphouse_url", dest='pumphouse_url', type=str,
                    help="Pumphouse url",
                    default='http://localhost:5000')

args = parser.parse_args()

with open('config.js', 'w') as config:
    config.write("/*jslint node:true*/\n\n")
    config.write("'use strict';\n\n")

    config.write(
        "module.exports = {\n")
    config.write("    endpoint: '%s',\n" % args.pumphouse_url)
    config.write("    timeout: 2500,\n")
    config.write("    cases: [\n")
    config.write("        'reset',\n        'migrate'\n    ],\n")
    config.write("    tenant_name_mask: 'pumphouse-'\n};")
