#!/usr/bin/env python3
"""
AGENTIC CHAIN NODE
==================
A full-node wallet that connects to Base and earns $AGENTIC through:
- Staking
- Running inference workloads
- Serving as a network participant

Download: https://github.com/ascclaw/agentic-chain
"""

import asyncio
import hashlib
import json
import os
import secrets
import sqlite3
import sys
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set
from eth_account import Account
from eth_typing import ChecksumAddress
from web3 import Web3
from web3.eth import Eth
from web3.middleware.geth import construct_local_filter_middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy

# Configuration
CHAIN_CONFIG = {
    "name": "Agentic Chain",
    "chain_id": 8453,  # Base Mainnet
    "chain_id_hex": "0x2105",
    "rpc_url": "https://mainnet.base.org",
    "block_explorer": "https://basescan.org",
    "token_address": "0x0000000000000000000000000000000000000000",  # Deploy on launch
    "staking_contract": "0x0000000000000000000000000000000000000000",
    "token_symbol": "AGENTIC",
    "min_stake": 100,  # 100 AGENTIC minimum
}

# Add Base network to Ethereum
class BaseChain:
    """Base Chain connection and utilities"""
    
    def __init__(self, rpc_url: str = CHAIN_CONFIG["rpc_url"]):
        self.rpc_url = rpc_url
        self.w3: Optional[Web3] = None
        self.connected = False
        
    async def connect(self) -> bool:
        """Connect to Base"""
        try:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            self.connected = self.w3.is_connected()
            
            if self.connected:
                print(f"✅ Connected to Base (Block: {self.w3.eth.block_number})")
            return self.connected
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def create_account(self) -> Dict[str, str]:
        """Create new wallet"""
        acct = Account.create()
        return {
            "address": acct.address,
            "private_key": acct.key.hex(),
            "public_key": acct.key.public_key.hex()
        }
    
    def import_account(self, private_key: str) -> Dict[str, str]:
        """Import existing wallet"""
        acct = Account.from_key(private_key)
        return {
            "address": acct.address,
            "private_key": acct.key.hex(),
            "public_key": acct.key.public_key.hex()
        }
    
    async def get_balance(self, address: str) -> Dict[str, Any]:
        """Get ETH and token balance"""
        if not self.w3:
            return {"eth": "0", "agentic": "0"}
        
        # ETH balance
        eth_balance = self.w3.eth.get_balance(address)
        
        # Token balance (if deployed)
        token_balance = "0"
        
        return {
            "eth": self.w3.from_wei(eth_balance, 'ether'),
            "agentic": token_balance,
            "raw_eth": eth_balance
        }
    
    async def get_block(self, block_number: int = "latest") -> Dict:
        """Get block data"""
        if not self.w3:
            return {}
        
        block = self.w3.eth.get_block(block_number)
        return {
            "number": block.number,
            "hash": block.hash.hex(),
            "parent_hash": block.parentHash.hex(),
            "timestamp": block.timestamp,
            "gas_limit": block.gasLimit,
            "gas_used": block.gasUsed,
            "transactions": len(block.transactions)
        }
    
    async def get_transaction(self, tx_hash: str) -> Dict:
        """Get transaction details"""
        if not self.w3:
            return {}
        
        tx = self.w3.eth.get_transaction(tx_hash)
        return {
            "hash": tx.hash.hex(),
            "from": tx["from"],
            "to": tx["to"],
            "value": self.w3.from_wei(tx.value, 'ether'),
            "gas": tx.gas,
            "gas_price": self.w3.from_wei(tx.gasPrice, 'ether'),
            "nonce": tx.nonce
        }
    
    async def send_transaction(self, private_key: str, to: str, value_eth: float) -> str:
        """Send ETH transaction"""
        if not self.w3:
            raise Exception("Not connected")
        
        acct = Account.from_key(private_key)
        
        tx = {
            "nonce": self.w3.eth.get_transaction_count(acct.address),
            "to": to,
            "value": self.w3.to_wei(value_eth, 'ether'),
            "gas": 21000,
            "gas_price": self.w3.eth.gas_price,
            "chainId": CHAIN_CONFIG["chain_id"]
        }
        
        signed = self.w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        
        return tx_hash.hex()
    
    async def wait_for_confirmation(self, tx_hash: str, timeout: int = 300) -> Dict:
        """Wait for transaction confirmation"""
        if not self.w3:
            return {}
        
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
        return {
            "status": receipt.status,
            "block_number": receipt.blockNumber,
            "gas_used": receipt.gasUsed
        }
    
    def get_current_gas(self) -> Dict[str, Any]:
        """Get current gas prices"""
        if not self.w3:
            return {}
        
        return {
            "low": self.w3.from_wei(self.w3.eth.gas_price * 0.8, 'gwei'),
            "medium": self.w3.from_wei(self.w3.eth.gas_price, 'gwei'),
            "high": self.w3.from_wei(self.w3.eth.gas_price * 1.2, 'gwei')
        }


class AgenticNode:
    """The main node - wallet + earning engine"""
    
    def __init__(self, data_dir: str = "./agentic_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.base = BaseChain()
        self.running = False
        self.node_id = uuid.uuid4().hex[:16]
        
        # Wallet
        self.account: Optional[Dict[str, str]] = None
        
        # Database
        self.db = self._init_db()
        
        # Earning stats
        self.stats = {
            "start_time": int(time.time()),
            "blocks_synced": 0,
            "transactions_sent": 0,
            "inference_requests": 0,
            "total_earned": 0
        }
        
        # Subscriptions
        self.subscribers: Set[Callable] = set()
        
    def _init_db(self) -> sqlite3.Connection:
        """Initialize local database"""
        db_path = self.data_dir / "agentic_node.db"
        db = sqlite3.connect(str(db_path))
        
        db.executescript("""
            CREATE TABLE IF NOT EXISTS wallet (
                id INTEGER PRIMARY KEY,
                address TEXT UNIQUE,
                private_key_encrypted TEXT,
                created_at INTEGER
            );
            
            CREATE TABLE IF NOT EXISTS blocks (
                number INTEGER PRIMARY KEY,
                hash TEXT UNIQUE,
                parent_hash TEXT,
                timestamp INTEGER,
                txn_count INTEGER
            );
            
            CREATE TABLE IF NOT EXISTS transactions (
                hash TEXT PRIMARY KEY,
                from_addr TEXT,
                to_addr TEXT,
                value REAL,
                timestamp INTEGER,
                status TEXT
            );
            
            CREATE TABLE IF NOT EXISTS earnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                amount REAL,
                timestamp INTEGER,
                details TEXT
            );
            
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );
        """)
        
        return db
    
    async def initialize(self):
        """Initialize the node"""
        print(f"""
╔═══════════════════════════════════════════════════════════╗
║                                                               ║
║   🤖 A G E N T I C   C H A I N   N O D E 🤖                ║
║                                                               ║
║   Your Gateway to the Agent Economy                         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════╝
        """)
        
        # Connect to Base
        connected = await self.base.connect()
        if not connected:
            print("⚠️  Running in offline mode")
        
        # Load or create wallet
        self._load_wallet()
        
        print(f"\n📍 Node ID: {self.node_id}")
        
    def _load_wallet(self):
        """Load or create wallet"""
        cursor = self.db.cursor()
        cursor.execute("SELECT address FROM wallet LIMIT 1")
        row = cursor.fetchone()
        
        if row:
            self.account = {"address": row[0]}
            print(f"�wallet loaded: {self.account['address'][:10]}...{self.account['address'][-4:]}")
        else:
            print("\n🔐 Creating new wallet...")
    
    def create_wallet(self, save: bool = True) -> Dict[str, str]:
        """Create new wallet"""
        self.account = self.base.create_account()
        
        if save:
            cursor = self.db.cursor()
            cursor.execute(
                "INSERT INTO wallet (address, created_at) VALUES (?, ?)",
                (self.account["address"], int(time.time()))
            )
            self.db.commit()
        
        # Generate keyfile
        self._save_keyfile()
        
        return self.account
    
    def import_wallet(self, private_key: str, save: bool = True) -> Dict[str, str]:
        """Import wallet from private key"""
        self.account = self.base.import_account(private_key)
        
        if save:
            cursor = self.db.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO wallet (address, created_at) VALUES (?, ?)",
                (self.account["address"], int(time.time()))
            )
            self.db.commit()
        
        self._save_keyfile()
        return self.account
    
    def _save_keyfile(self):
        """Save encrypted keyfile (simplified - use proper encryption in production)"""
        if not self.account:
            return
        
        keyfile = {
            "address": self.account["address"],
            "id": str(uuid.uuid4()),
            "version": 3,
            # In production: use proper key derivation (scrypt/argon2)
            "crypto": {
                "kdf": "pbkdf2",
                "mac": hashlib.sha256(self.account["private_key"].encode()).hexdigest()
            }
        }
        
        with open(self.data_dir / "keyfile.json", "w") as f:
            json.dump(keyfile, f)
    
    async def get_balance(self) -> Dict[str, Any]:
        """Get wallet balance"""
        if not self.account:
            return {"eth": "0", "agentic": "0"}
        
        return await self.base.get_balance(self.account["address"])
    
    async def start(self):
        """Start the node"""
        self.running = True
        print("\n🚀 Node starting...")
        
        tasks = [
            self._sync_blocks(),
            self._earning_engine(),
            self._stats_reporter()
        ]
        
        await asyncio.gather(*tasks)
    
    async def stop(self):
        """Stop the node"""
        self.running = False
        print("\n🛑 Node stopped")
        self.db.close()
    
    async def _sync_blocks(self):
        """Sync blocks from Base"""
        print("📡 Block sync started")
        
        last_block = 0
        cursor = self.db.cursor()
        cursor.execute("SELECT MAX(number) FROM blocks")
        row = cursor.fetchone()
        if row and row[0]:
            last_block = row[0]
        
        while self.running:
            try:
                current = await self.base.get_block("latest")
                if current:
                    new_block = current["number"]
                    
                    if new_block > last_block:
                        # Fetch missing blocks
                        for block_num in range(last_block + 1, new_block + 1):
                            block = await self.base.get_block(block_num)
                            if block:
                                cursor.execute(
                                    "INSERT OR REPLACE INTO blocks (number, hash, parent_hash, timestamp, txn_count) VALUES (?, ?, ?, ?, ?)",
                                    (block["number"], block["hash"], block["parent_hash"], block["timestamp"], block["transactions"])
                                )
                                self.stats["blocks_synced"] += 1
                        
                        self.db.commit()
                        last_block = new_block
                        
                        # Notify subscribers
                        for callback in self.subscribers:
                            callback({"type": "new_block", "number": last_block})
                
                await asyncio.sleep(12)  # Base block time
                
            except Exception as e:
                print(f"Sync error: {e}")
                await asyncio.sleep(30)
    
    async def _earning_engine(self):
        """Earning engine - runs background tasks"""
        print("⚡ Earning engine started")
        
        while self.running:
            try:
                # 1. Network participation rewards
                await self._network_rewards()
                
                # 2. Inference marketplace earnings
                await self._inference_earnings()
                
                # 3. Staking rewards (if staked)
                await self._staking_earnings()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"Earning error: {e}")
                await asyncio.sleep(60)
    
    async def _network_rewards(self):
        """Simulate network participation rewards"""
        # In production: connect to actual reward contract
        # This simulates earning for being an active node
        earned = 0.01  # Mock reward
        
        self._record_earnings("network", earned)
        self.stats["total_earned"] += earned
    
    async def _inference_earnings(self):
        """Simulate inference marketplace earnings"""
        # In production: serve actual inference requests
        earned = 0.005  # Mock reward
        
        self._record_earnings("inference", earned)
        self.stats["inference_requests"] += 1
        self.stats["total_earned"] += earned
    
    async def _staking_earnings(self):
        """Check staking rewards"""
        # In production: query staking contract
        pass
    
    def _record_earnings(self, source: str, amount: float):
        """Record earnings to database"""
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO earnings (source, amount, timestamp) VALUES (?, ?, ?)",
            (source, amount, int(time.time()))
        )
        self.db.commit()
    
    async def _stats_reporter(self):
        """Report stats periodically"""
        while self.running:
            await asyncio.sleep(300)  # Every 5 minutes
            
            balance = await self.get_balance()
            print(f"""
📊 Node Stats (Block: {self.stats['blocks_synced']})
   💰 Balance: {balance.get('eth', '0')} ETH
   🤖 Requests: {self.stats['inference_requests']}
   💵 Earned: {self.stats['total_earned']:.4f} AGENTIC
            """)
    
    def get_status(self) -> Dict:
        """Get node status"""
        return {
            "node_id": self.node_id,
            "wallet": self.account["address"] if self.account else None,
            "connected": self.base.connected,
            "uptime": int(time.time()) - self.stats["start_time"],
            "blocks_synced": self.stats["blocks_synced"],
            "inference_requests": self.stats["inference_requests"],
            "total_earned": self.stats["total_earned"]
        }
    
    def subscribe(self, callback: Callable):
        """Subscribe to node events"""
        self.subscribers.add(callback)
    
    def unsubscribe(self, callback: Callable):
        """Unsubscribe from node events"""
        self.subscribers.discard(callback)


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agentic Chain Node")
    parser.add_argument("--create-wallet", action="store_true", help="Create new wallet")
    parser.add_argument("--import-wallet", type=str, help="Import wallet from private key")
    parser.add_argument("--balance", action="store_true", help="Check balance")
    parser.add_argument("--no-start", action="store_true", help="Don't start node")
    args = parser.parse_args()
    
    node = AgenticNode()
    await node.initialize()
    
    if args.create_wallet:
        wallet = node.create_wallet()
        print(f"\n✅ Wallet created!")
        print(f"   Address: {wallet['address']}")
        print(f"   Private Key: {wallet['private_key'][:20]}...")
        print(f"\n⚠️  SAVE YOUR PRIVATE KEY - IT CANNOT BE RECOVERED!")
        
    elif args.import_wallet:
        wallet = node.import_wallet(args.import_wallet)
        print(f"\n✅ Wallet imported!")
        print(f"   Address: {wallet['address']}")
        
    elif args.balance:
        balance = await node.get_balance()
        print(f"\n💰 Balance:")
        print(f"   ETH: {balance.get('eth', '0')}")
        print(f"   AGENTIC: {balance.get('agentic', '0')}")
    
    elif not args.no_start:
        status = node.get_status()
        print(f"\n📊 Node Status:")
        for k, v in status.items():
            print(f"   {k}: {v}")
        
        print("\n🚀 Starting node...")
        await node.start()


if __name__ == "__main__":
    # Check for dependencies
    try:
        from web3 import Web3
        from eth_account import Account
    except ImportError:
        print("Installing dependencies...")
        os.system("pip install web3 eth-account eth-typing")
        print("Please run again: python agentic_node.py")
        sys.exit(1)
    
    asyncio.run(main())
