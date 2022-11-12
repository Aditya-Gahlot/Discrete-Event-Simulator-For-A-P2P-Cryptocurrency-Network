
class Block(object):
    """
           This class shall be used to implement the information related Block of blockchain
           written by : Vikas
    """

    def __init__(self, block_id, created_at, creator_id, prev_block_id, chain_len):

        super(Block, self).__init__()

        self.id = block_id
        self.created_at = created_at

        # Node that created this block
        self.creator_id = creator_id

        # This link helps create a chain of blocks
        self.prev_block_id = prev_block_id

        # Contains a dict of transactions keyed by the id
        self.transactions = {}

        # Length of the chain ending at this block
        self.chain_len = chain_len

    def __len__(self):
        """
            Method Name: __len__
            Description: Return the length of the blockchain ending at this block.
        """
        return self.chain_len

    def __repr__(self):
        """
            Method Name: __repr__
            Description: Return the information of block in blockchain
        """
        r = (self.id, self.prev_block_id, self.creator_id, self.chain_len, len(self.transactions))
        return "<Block id %d: prev_block id = %d, created by = %d, length = %d, transactions = %d>" % r


class Transaction(object):
    """
        This class shall be used to implement the information related Transaction of blocks in blockchain.
        written by : Vikas
    """

    def __init__(self, trans_id, from_id, to_id, coins):
        super(Transaction, self).__init__()

        self.id = trans_id
        self.from_id = from_id
        self.to_id = to_id
        self.coins = coins

    def __repr__(self):
        """
            Method Name: __repr__
            Description: Return the information about transaction in blocks
        """
        r = (self.id, self.from_id, self.to_id, self.coins)
        return "<Transaction id %d: from = %d, to = %d, amt = %d>" % r
