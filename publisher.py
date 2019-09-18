from web3 import Web3


class Publisher():
    """ Provides functionality to format and publish trade signals
    (price predictions) to the Ethereum blockchain using a formatted string
    encoded in Ethereum transaction data. Note: single chars used for encoding
    to save space on chain. The idea is to keep the signal string shorter than
    an IPFS hash, as that is the next step up in terms of on-chain storage."""

    def __init__(self, endpoint, pub_k, pvt_k, data):
        self.pub_k = pub_k
        self.pvt_k = pvt_k
        self.endpoint = endpoint
        self.data = data

        # Connect to ETH node.
        self.w3 = Web3(Web3.HTTPProvider(self.endpoint))
