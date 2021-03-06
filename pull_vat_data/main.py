import os
import sys
import requests
import argparse
import json

from time import sleep
from pymaker import Address
from pprint import pprint

class VatBal:

    def __init__(self, args: list):
        parser = argparse.ArgumentParser(prog='auction-syncer')

        parser.add_argument('--before-or-equal-block', type=int, required=True,
                            help="before or equal to block from which to pull at historical DAI balance (set to block where MCD was deployed)")

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
        self.page_size = 1500

        print(f"URL (Vulcanize) Endpoint - {self.endpoint}")
        print(f"Block number we are querying before or at - {self.arguments.before_or_equal_block}")

        print(f"Repository that was used to generate this output: https://github.com/LiquidityProviders/historic_vat_data.git")


    def main(self):
        auction_config = json.loads(self.arguments.auction_config.read())
        combined_results = {}
        total = 0

        for keeper in auction_config['members']:
            unordered_vat_data = self.run_query(self.vulc_query, Address(keeper['config']['address']))
            vat_data = self.sort_vat_data_by_block_number(unordered_vat_data['allVatDais']['nodes'])
            if vat_data:
                if len(vat_data) == self.page_size:
                    raise RuntimeError(f"Results returned exceed page_size. Please make page size larger than {self.page_size} ")

                dai_bal, block_number, transactions = self.get_data_closest_to_block(self.arguments.before_or_equal_block, vat_data)
                combined_results[keeper['id']] = {
                        'DAI balance': dai_bal,
                        'block number': block_number,
                        'address': keeper['config']['address'],
                        'transactions': transactions
                        }

                total += float(combined_results[keeper['id']]['DAI balance'])

            else:
                combined_results[keeper['id']] = {
                        'DAI balance': 0.0,
                        'address': keeper['config']['address'],
                        'block number': 'This address has no Vat Dai history',
                        'transactions': 'This address has no Vat Dai history'
                        }

        pprint(combined_results)
        print(f"Total DAI in Vat's: {total}")


    def get_data_closest_to_block(self, target_block, vat_data):
        return_vat_entry = None
        last_vat_entry = vat_data[0]
        for vat_entry in vat_data:
            return_vat_entry = vat_entry
            if int(vat_entry['headerByHeaderId']['blockNumber']) >= target_block:
                return_vat_entry = last_vat_entry
                break
    # "{int(return_vat_entry['dai']) / 10**45:,.2f}"
            last_vat_entry = vat_entry
        return (int(return_vat_entry['dai']) / 10**45, \
                return_vat_entry['headerByHeaderId']['blockNumber'], \
                return_vat_entry['headerByHeaderId']['transactionsByHeaderId']['nodes'])


    def sort_vat_data_by_block_number(self, unordered_vat_data):
        return sorted(unordered_vat_data, key=lambda i: int(i['headerByHeaderId']['blockNumber']))


    def run_query(self, vulc_query, address):
        assert isinstance(address, Address)

        data_needed = True
        headers = {'Authorization': 'Basic ' + self.api_key}
        variables = {
            "pageSize": self.page_size,
            "address": address.address,
            "numOfTx": 100
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

