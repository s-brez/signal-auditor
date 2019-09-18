from web3 import Web3


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
        a the given Ethereum public address. If the address's transactions
        contain no signal strings, return False."""
        pass

    def parse_signals(self, signals: list):
        """Retunr a list of human-readable strings, given a list of Publisher
        -encoded signals strings."""
        pass
