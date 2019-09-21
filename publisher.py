from web3 import Web3
import json


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
        """ Create a transaction containing an encoded signal string in the
        transaction payload, write it to Eth blockchain, then print and return
        the transaction hash. signal_string must be byte string (b'')

        Note that the recipient of the transaction is ourself; our own public
        Eth address. Because we are only interested in the immutable signal
        string, it doesnt actually matter to whom, or what amount of Ether we
        transact, only that the transaction originates from our address for the
        sake of proving the signals are ours."""

        # Create transaction
        signed_txn = self.w3.eth.account.signTransaction(dict(
            nonce=self.w3.eth.getTransactionCount(self.pub_k),
            gasPrice=self.w3.eth.gasPrice,
            gas=100000,
            to=self.pub_k,
            value=5,  # tiny tx value
            data=signal_string),
            self.pvt_k)

        # Execute transaction
        return self.w3.eth.sendRawTransaction(signed_txn.rawTransaction).hex()

    def encode(self, params: list):
        """ Return an encoded byte string ready to publish, given a list of
        signal parameter strings. Parameters must match the data.json format,
        otherwise raise an exception.

        Prefix signal bytestring payloads with "SAE" (Signal Auditor Ethereum)
        as a header as to filter signals from regular transactions easily."""

        signal = "SAE"

        # Check that each signal string param matches an entry in json.data.
        count = 0
        for i in self.data['data']:
            # If theres a match, append the dicts key to the signal string.
            # The keys of each dict are what will form the encoded signal.
            if params[count] in self.data['data'][i][self.key_from_value(
                    self.data['data'][i], params[count])]:
                signal = signal + self.key_from_value(
                    self.data['data'][i],
                    params[count])
            else:
                raise Exception("Signal parameter mis-match. Ensure input" +
                                "strings match each field in data.json.")
            count += 1

        # convert to bytes
        signal = bytes(signal, 'utf-8')

        return(signal)

    def key_from_value(self, data_dict, val):
        """Return the key where val matches a value from the given dict."""

        key = None
        try:
            key = list(data_dict.keys())[list(data_dict.values()).index(val)]
        except ValueError as e:
            raise Exception("Signal parameter mis-match. Ensure input",
                            "strings match each field in data.json", e)
        return key
