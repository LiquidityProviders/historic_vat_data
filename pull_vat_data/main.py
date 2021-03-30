import os
import sys
import requests
import argparse
import json

from pprint import pprint

class VatBal:

    def __init__(self, args: list):
        parser = argparse.ArgumentParser(prog='auction-syncer')

        parser.add_argument('--num-entries', type=int, required=True,
                            help="Starting block from which to look at history (set to block where MCD was deployed)")

        parser.add_argument("--vulcanize-host", default="https://api.makerdao.com/graphql", type=str,
                            help="graphql interface for VulcanizeDB lite node")

        parser.add_argument("--vulcanize-api-key", required=True, type=str,
                            help="vulcanize API key needed to query vulcanize provider.")

        parser.add_argument('--auction-config', required=True, type=argparse.FileType('r'),
                            help="configuration file to identify auction keeper addresses.")

        parser.add_argument('--vulcanize-query-file', default="auction_vat_bal.graphql", type=argparse.FileType('r'),
                            help="configuration file to identify graphql query")

        parser.add_argument("--debug", dest='debug', action='store_true',
                            help="Enable debug output")

        self.arguments = parser.parse_args(args)
        self.endpoint = self.arguments.vulcanize_host
        self.api_key = self.arguments.vulcanize_api_key
        self.vulc_query = self.arguments.vulcanize_query_file.read()

    def main(self):
        auction_config = json.loads(self.arguments.auction_config.read())

        for keeper in auction_config['members']:
            vault_data = self.run_query(self.vulc_query, keeper['config']['address'], self.arguments.num_entries)
            pprint(vault_data)

    def run_query(self, vulc_query, address, num_entries: int):
        assert isinstance(num_entries, int)

        data_needed = True
        page_size = 1000
        headers = {'Authorization': 'Basic ' + self.api_key}
        variables = {
            "numEntries": num_entries,
            "address": address,
        }
        response = requests.post(self.endpoint, json={'query': vulc_query, 'variables': json.dumps(variables)}, timeout=10.0, headers=headers)

        if not response.ok:
            error_msg = f"{response.status_code} {response.reason} ({response.text})"
            raise RuntimeError(f"Query failed: {error_msg}")


        result = json.loads(response.text)
        if 'data' not in result:
            raise RuntimeError(f"Vulcanize reported error: {result}")

        return result['data']


if __name__ == '__main__':
    VatBal(sys.argv[1:]).main()

