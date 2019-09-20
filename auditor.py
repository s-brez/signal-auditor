from web3 import Web3
import requests
import json


class Auditor():
    """ Auditor provides functionality to scrape a given ETH address for
    transaction data matching Publisher signal formatting, as well as parsing
    and displaying the signals in a human-readable format."""

    def __init__(self, endpoint, data, etherscan_api_token, live: bool):
        self.endpoint = endpoint
        self.data = data
        self.token = etherscan_api_token
        self.live = live

        # Connect to ETH node.
        self.w3 = Web3(Web3.HTTPProvider(self.endpoint))

    def scrape_transactions(self, address):
        """ Return a list of Publisher-formattted signal strings scraped from
        the given Ethereum address. If the address's transactions contain no
        signal strings, return False.

        We use the etherscan API to grab all transactions for an address as the
        web3 python API lacks this capability - you'd have to manually parse
        all previous blocks data to do this with web3, very slow."""

        if self.live:
            baseurl = "api"
        else:
            baseurl = "api-ropsten"

        payload = (
            "http://" + baseurl + ".etherscan.io/api?module=account&action=" +
            "txlist&address=" + address + "&startblock=0&endblock=99999999&" +
            "sort=asc&apikey=" + self.token)

        # Get all transactions pertaining to the specified address
        response = requests.get(payload).json()

        # Strip transaction msg payloads, converting from hex string to bytes.
        result = [
            {i['timeStamp']: bytes.fromhex(
                i['input'][2:]).decode()} for i in response['result'] if self.verify(i, address)]  # noqa

        # Remove duplicates by converting list to set and back; return the list
        return [dict(t) for t in {tuple(d.items()) for d in result}]

    def verify(self, tx, address):
        """Return true if the given tx message begins with publisher header
        "SAE", originated from the specified address and is len(11)."""

        if(
            (bytes.fromhex(tx['input'][2:]).decode()[:3] == "SAE") and
                (tx['from'] == address.lower()) and (
                    len(bytes.fromhex(tx['input'][2:]).decode()) == 11)):
            return True

    def parse_signals(self, signals: list):
        """Retun a list of human-readable strings, given a list of Publisher
        -encoded signal strings."""
        pass
