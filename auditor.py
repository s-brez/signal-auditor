from web3 import Web3
from datetime import datetime
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

    def scrape(self, address):
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

        payload = str(
            "http://" + baseurl + ".etherscan.io/api?module=account&action=" +
            "txlist&address=" + address + "&startblock=0&endblock=99999999&" +
            "sort=asc&apikey=" + self.token)

        # Disguide our request as a browser, so etherscan doesnt block it.
        # Sometimes servers block non=browser traffic
        headers = {
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",  # noqa
            'Accept-Encoding': "gzip, deflate",
            'Accept-Language': "en-US,en;q=0.9",
            'Cache-Control': "max-age=0",
            'Connection': "keep=alive",
            'Host': 'api-ropsten.etherscan.io',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"}  # noqa

        # Get all transactions pertaining to the specified address
        response = requests.get(payload, headers=headers).json()

        # Strip transaction msg payloads, converting from hex string to bytes.
        result = [
            {i['timeStamp']: bytes.fromhex(
                i['input'][2:]).decode()} for i in response['result'] if self.verify(i, address)]  # noqa

        # Remove duplicates by converting list to set and back; return the list
        return [dict(t) for t in {tuple(d.items()) for d in result}]

    def verify(self, tx, address):
        """scrape() helper function. Return true if the given tx message begins
        with publisher header "SAE", is len(11), and originated from address
        parameter."""

        if(
            (bytes.fromhex(tx['input'][2:]).decode()[:3] == "SAE") and
                # lowercase address param as web3 returns lowercase addresses
                (tx['from'] == address.lower()) and (
                    len(bytes.fromhex(tx['input'][2:]).decode()) == 11)):
            return True

    def validate(self, param):
        """Return True if param is either an address or private key."""

        # check for address validity
        if len(param) == 42 and param[:2] == "0x":
            return "Valid"

        # check for private key validity
        if len(param) == 64 and type(int(param, 16)) == int:
            return "Valid"
        else:
            return "Invalid"

    def decode(self, signals: list):
        """Return a list of human-readable signal strings, given a list of
        Publisher-encoded signal dicts."""

        decoded = []
        if signals:
            for sig in signals:
                for key, val in sig.items():
                    time = datetime.utcfromtimestamp(int(key))
                    decoded.append([
                            time.strftime("%H:%M:%S%z %d-%m-%Y"),
                            self.data['data']['instrument'][val[3]],
                            self.data['data']['inst_type'][val[4]],
                            self.data['data']['exchange'][val[5]],
                            self.data['data']['strategy'][val[6]],
                            self.data['data']['direction'][val[7]],
                            self.data['data']['order_type'][val[8]],
                            self.data['data']['misc'][val[9]],
                            self.data['data']['trigger'][val[10]]])
            return decoded
        else:
            return None
