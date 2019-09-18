from web3 import Web3


class Publisher():
    """ Provides functionality to format and publish trade signals
    (price predictions) to the Ethereum blockchain using a formatted string
    encoded in Ethereum transaction data. Single chars used are for encoding
    to save space on chain. The idea is to keep the signal string shorter than
    an IPFS hash, as that is the next step up in terms of on-chain storage."""

    def __init__(self, endpoint, pub_k, pvt_k, data):
        self.pub_k = pub_k
        self.pvt_k = pvt_k
        self.endpoint = endpoint
        self.data = data

        # Connect to ETH node.
        self.w3 = Web3(Web3.HTTPProvider(self.endpoint))

    def publish(self, signal_string):
        """ Send a transaction containing an encoded signal string in the
        transaction payload on the Ethereum blockchain, then print and return
        the transaction hash. Note that the recipient of the transaction is
        ourself, our own public Eth address. This is because we use the
        blockchain only to immutably store a signal string, it doesnt actually
        matter to whom we transact, only that the transaction originates from
        our address for the sake of proving the signals are ours."""

        signed_txn = self.w3.eth.account.signTransaction(dict(
            nonce=self.w3.eth.getTransactionCount(self.pub_k),
            gasPrice=self.w3.eth.gasPrice,
            gas=100000,
            to=self.pub_k,
            value=12345,
            data=signal_string),
            self.pvt_k)

        tx_hash = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(tx_hash)
