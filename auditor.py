from web3 import Web3


# number  scalar value equal to the number of ancestor blocks (genesis block=0)
# size    size of the block in bytes
# timestamp   Unix's time() at this block's inception
# miner   160-bit address for fees collected from successful mining
# gasLimit    maximum gas expenditure allowed in this block
# gasUsed total gas used by all transactions in this block
# transactions    list of transaction hashes included in the block
# parentHash  Keccak256 hash of the parent block's header
# hash    current block's hash
# extraData   extra data in byte array

class Auditor():

    # node connection url
    ENDPOINT = "https://ropsten.infura.io/v3/c02db369ee524f88a410cbab6dc02dcf"

    def __init__(self):

        # create a connection to the endpoint
        self.w3 = Web3(Web3.HTTPProvider(self.ENDPOINT))

        block = self.w3.eth.getBlock('latest')
        print(block)


auditor = Auditor()
