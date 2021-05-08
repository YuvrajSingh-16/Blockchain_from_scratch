## BlockChain
from flask import Flask, request
from hashlib import sha256
import requests
import time
import json

mine_count = 0

class Block:
    """
    Single Block of the Blockchain.
    ---
    previous_hash : to ensure the immutability of the entire blockchain + integrity of entire chain, storing hash of previous block
    nonce : nonce number                                         
    """
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        
    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()
        
    
class Blockchain:
    '''
    The main Blockchain class
    --
    create_genesis_blockmethod : to initialize the blockchain    
    '''
    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, [], time.time(), "0")   ## This creates an initial block with an index of 0 and a previous hash of 0. 
                                                         ## We then add this to the list chain that keeps track of each block.
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]
    
    difficulty = 6
    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)
        
    def add_block(self, block, proof):
        ## fetch previous hash 
        previous_hash = self.last_block.hash 
        ## if block.previous_hash == previous_hash
        if previous_hash != block.previous_hash:
            return False 
        if not self.is_valid_proof(block, proof):
            return False 
        ## add hash to the given block 
        block.hash = proof 
        ## append block to the chain 
        self.chain.append(block)
        return True 
        
    def is_valid_proof(self, block, block_hash):
        return ( block_hash.startswith('0'*Blockchain.difficulty) and block_hash == block.compute_hash() )

    def mine(self):
        ## check if there exists unconfirmed_transactions
        if not self.unconfirmed_transactions:
            return False 

        ## fetch last block 
        last_block = self.last_block
        
        ## create new block
        new_block = Block(last_block.index+1, self.unconfirmed_transactions, time.time(), last_block.hash)
        
        ## cal proof of work
        proof = self.proof_of_work(new_block)
        
        ## add new block 
        self.add_block(new_block, proof)
        
        ## set unconfirmed_transactions to []
        transaction_id = self.unconfirmed_transactions.pop(0)
        print("[+] Transaction ", transaction_id, " done!!!")
        
        ## return new block index
        return new_block.index
        
        
## Creating the blockchain 
blockchain = Blockchain()

app = Flask(__name__)

@app.route("/chain", methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data})
 

@app.route("/mine", methods=['GET'])
def mine():
    global mine_count
    
    mine_count+=1
    blockchain.add_new_transaction(mine_count)
    new_block_idx = blockchain.mine()
    
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
        
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data,
                       "newBlockchainIndex": new_block_idx})

app.run(debug=True, port=5000)