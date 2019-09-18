from web3 import Web3
import requests
import json


class Auditor():
    """ Auditor provides functionality to scrape a given ETH address for
    transaction data matching Publisher signal formatting, as well as parsing
    and displaying the signals in a human-readable format."""

    def __init__(self, endpoint, data, etherscan_api_token):
        self.endpoint = endpoint
        self.data = data
        self.token = etherscan_api_token

        # Connect to ETH node.
        self.w3 = Web3(Web3.HTTPProvider(self.endpoint))

    def scrape_transactions(self, address):
        """ Return a list of Publisher-formattted signal strings scraped from
        the given Ethereum address. If the address's transactions contain no
        signal strings, return False.

        We use the etherscan API to grab all transactions for an address as the
        web3 python API lacks this capability - you'd have to manually iterate
        through all previous blocks data to do this with web3, very slow."""

        payload = (
            "http://api-ropsten.etherscan.io/api?module=account&action=" +
            "txlist&address=" + address + "&startblock=0&endblock=99999999&" +
            "sort=asc&apikey=" + self.token)

        # Poll Etherscan API
        response = requests.get(payload).json()

        # Strip only the transaction msg, convert it from hex string to bytes.
        result = [
            bytes.fromhex(i['input'][2:]) for i in response['result'] if self.check_hex(i['input'])]  # noqa

        # Remove duplicates
        result = list(dict.fromkeys(result))

        print(result)

    def check_hex(self, hex_data):
        """Return true if the given hex string has len() > 2 and contains the
        publisher header."""

        if len(hex_data) > 2:
            return True

    def parse_signals(self, signals: list):
        """Retunr a list of human-readable strings, given a list of Publisher
        -encoded signals strings."""
        pass
