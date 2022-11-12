from block import Block, Transaction
import random


class Event(object):
    """
        This class is used to implements the four kinds of events that can happen in the simulation.
        That are TransactionGenerate, TransactionReceive, BlockGenerate, BlockReceive
        Written by : Vikas
    """

    def __init__(self, node_id, creator_id, created_at, run_at):
        super(Event, self).__init__()

        # Node this event will happen on
        self.node_id = node_id

        # Node that created this event
        self.creator_id = creator_id

        # Time this event was created
        self.created_at = created_at

        # Time this event will be run at
        self.run_at = run_at

    def __lt__(self, other):
        """
            Method Name: __lt__
            Description: Allow sorting of events by their scheduled time.
        """
        return self.run_at < other.run_at


class TransactionGenerate(Event):
    """
        This class is used to implements the functions used in events TransactionGenerate.
        Written by : Vikas
    """

    def __init__(self, node_id, creator_id, created_at, run_at):
        super(TransactionGenerate, self).__init__(
            node_id, creator_id, created_at, run_at
        )

    def __repr__(self):
        """
            Method Name: __repr__
            Description: Return the information of Generated Transaction
        """
        return "Transaction Generated : on node id = %d" % self.node_id

    def run(self, sim):
        """
            Method Name: run
            Description: Return the information of next block transaction in blockchain
        """
        # The node that this event is running on
        me = sim.nodes[self.node_id]

        # Generate a random amount not greater than current node's balance
        trans_amt = me.coins * random.uniform(0, 1)

        # Find a random receiver who will receive the coins in the transaction
        all_but_me = list(set(sim.nodes) - set([me]))
        receiver = random.choice(all_but_me)

        # Update the coins of both sender & receiver
        me.coins -= trans_amt
        receiver.coins += trans_amt

        # Add transaction to current node's transaction list
        new_trans = Transaction(
            sim.trans_id,
            me.id,
            receiver.id,
            trans_amt
        )

        sim.trans_id += 1
        me.transactions[new_trans.id] = new_trans

        # Create a next transaction event for this node
        sim.events.put(TransactionGenerate(
            me.id,
            me.id,
            self.run_at,
            self.run_at + sim.transaction_delay()
        ))

        # Create next transaction events for neighbours
        for peer in me.peers:
            t = sim.latency(me, peer, msg_type="transaction")

            sim.events.put(TransactionReceive(
                new_trans,
                peer.id,
                me.id,
                self.run_at,
                self.run_at + t
            ))


class TransactionReceive(Event):
    """
        This class is used to implements the functions used in events TransactionReceive.
        Written by : Vikas
    """

    def __init__(self, transaction, node_id, creator_id, created_at, run_at):
        super(TransactionReceive, self).__init__(
            node_id, creator_id, created_at, run_at
        )

        # The transaction that was received
        self.transaction = transaction

    def __repr__(self):
        """
            Method Name: __repr__
            Description: Return the information of Received Transaction
        """
        return "Transaction Received from : node id =%d | %s" % (self.node_id, repr(self.transaction))

    def run(self, sim):
        """
            Method Name: run
            Description: This function generate Transaction Received events for all its neighbours
        """
        # The node that this event is running on
        me = sim.nodes[self.node_id]
        tx = self.transaction

        # Check if this node has already seen this transaction before
        if tx.id in me.transactions:
            return

        # If not, then add it to it's list
        me.transactions[tx.id] = tx

        # And generate TransactionReceive events for all its neighbours
        for peer in me.peers:

            t = sim.latency(me, peer, msg_type="transaction")
            sim.events.put(TransactionReceive(
                tx,
                peer.id,
                me.id,
                self.run_at,
                self.run_at + t
            ))


class BlockGenerate(Event):
    """
        This class is used to implements the functions used in event BlockGenerate.
        Written by : Vikas
    """

    def __init__(self, node_id, creator_id, created_at, run_at):
        super(BlockGenerate, self).__init__(
            node_id, creator_id, created_at, run_at
        )

    def __repr__(self):
        """
            Method Name: __repr__
            Description: Return the information of Generated block
        """
        return "Block Generated on : node id =%d" % self.node_id

    def run(self, sim):
        """
            Method Name: run
            Description: This function help to add block to another block
        """
        me = sim.nodes[self.node_id]

        for x in me.receivedStamps:
            if x > self.run_at:
                return

        # Traverse the longest chain and find all transactions that have been spent
        longest_chain = me.longest_chain()
        longest_blk = longest_chain[0]

        spent = set()

        for bk in longest_chain:
            spent |= set(bk.transactions.values())

        # Unspent = Seen - Spent
        unspent_txns = set(me.transactions.values()) - spent
        unspent_txns = {t.id: t for t in unspent_txns}

        # Only create a block if I have transactions to send
        if not unspent_txns:
            return

        # Generate a new block
        new_blk = Block(sim.block_id, self.run_at,
                        me.id, longest_blk.id, len(longest_blk))
        new_blk.transactions.update(unspent_txns)

        sim.block_id += 1

        # Add the block to my chain
        me.blocks[new_blk.id] = new_blk

        # And give me that sweet sweet mining reward!
        me.coins += 50

        # Generate BlockReceive events for all my peers
        for peer in me.peers:

            # Except who created the thing!
            if peer.id != new_blk.creator_id:
                t = sim.latency(me, peer, msg_type="block")

                sim.events.put(BlockReceive(
                    new_blk,
                    peer.id,
                    me.id,
                    self.run_at,
                    self.run_at + t
                ))


class BlockReceive(Event):
    """
        This class is used to implements the functions used in event BlockReceive.
        Written by : Vikas
    """
    def __init__(self, block, node_id, creator_id, created_at, run_at):
        super(BlockReceive, self).__init__(
            node_id, creator_id, created_at, run_at
        )

        # The block we've received
        self.block = block

    def __repr__(self):
        """
            Method Name: __repr__
            Description: Return the information about received block
        """
        return "Block Received from : node id = %d | %s" % (self.node_id, repr(self.block))

    def run(self, sim):
        """
            Method Name: run
            Description: This function help to received the information of next block
        """
        # The node that this event is running on
        me = sim.nodes[self.node_id]

        # Check if this node has already seen this block before
        if self.block.id in me.blocks:
            return

        # Find previous block to the one that we've just received
        prev_blk = me.blocks.get(self.block.prev_block_id)
        if prev_blk is None:
            return

        # Add transactions in this block to my list of seen ones
        me.transactions.update(self.block.transactions)

        # Make a copy of the block to increase the length
        new_blk = Block(
            self.block.id,
            self.block.created_at,
            self.block.creator_id,
            prev_blk.id,
            len(self.block) + 1
        )

        # Add the block to my chain
        me.blocks[new_blk.id] = new_blk
        me.receivedStamps.append(new_blk.created_at)

        # Generate BlockReceive events for all my peers
        for peer in me.peers:

            # Except for who created it
            if peer.id != self.block.creator_id:

                t = sim.latency(me, peer, msg_type="block")

                sim.events.put(BlockReceive(
                    self.block,
                    peer.id,
                    me.id,
                    self.run_at,
                    self.run_at + t
                ))

        # Create a new block generation event for me
        sim.events.put(BlockGenerate(
            me.id,
            me.id,
            self.run_at,
            self.run_at + sim.block_delay()
        ))
