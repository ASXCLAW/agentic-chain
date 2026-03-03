# 🤖 Agentic Chain

The first blockchain built for autonomous AI agents. OP Stack Layer-2. Launching on bankr.bot.

[Website](https://ASXCLAW.github.io/agentic-chain/) | [Whitepaper](./whitepaper.md) | [Contracts](./contracts/)

---

## 🚀 Quick Start

### 1. Download Node

```bash
git clone https://github.com/ASXCLAW/agentic-chain.git
cd agentic-chain
```

### 2. Install Dependencies

```bash
pip install web3 eth-account eth-typing
```

### 3. Create Wallet & Start Earning

```bash
python3 node/agentic_node.py --create-wallet
```

Your wallet is created and you're ready to earn $AGENTIC!

---

## 📦 What's Included

| Component | Description |
|-----------|-------------|
| `contracts/AgenticToken.sol` | $AGENTIC token with staking |
| `contracts/AgentGateway.sol` | Agent contract interactions |
| `contracts/AgentExtensions.sol` | Batch executor, safety, identity |
| `contracts/AgentMarketplace.sol` | NFT marketplace for agents |
| `node/agentic_node.py` | Full node + wallet software |
| `substrate/agentic_runtime.py` | Full Python blockchain |
| `openclaw/agentic/` | OpenClaw skill |
| `whitepaper.md` | Full white paper |
| `index.html` | Landing page |

---

## 💰 Earning $AGENTIC

- **Network Participation**: 0.01 AGENTIC/hour
- **Block Sync**: 0.001 AGENTIC/block
- **Inference Requests**: Variable
- **Staking**: 12% APY
- **Node Bonus**: 2x multiplier

---

## 🏦 Bootstrapping with Bankr.bot

To fund development without venture capital:

### Step 1: Launch Token via Bankr.bot

**Via Twitter/X:**
```
@bankrbot deploy token with name Agentic Chain ticker $AGENTIC on base
```

**Via CLI:**
```bash
bankr launch --name "Agentic Chain" --symbol AGENTIC --chain base
```

### Step 2: Zero Cost

- No gas fees upfront
- Bankr.bot handles ERC-20 deployment
- Auto-creates Uniswap v3 liquidity pool

### Step 3: Fee Structure

| Phase | Fee |
|-------|-----|
| Pre-migration | 0.5% to creator |
| Post-migration | 50% creator, 40% Bankr, 10% burn |

### Step 4: Treasury Funds

Use fees to fund:
- Node hosting ($500/mo)
- Smart contract audits ($10k+)
- Marketing
- Agent API credits

### Step 5: Bridge to Chain

Bridge $AGENTIC/ETH/USDC to Agentic Chain via:
- Optimism Native Bridge
- CCTP (Circle)
- LayerZero

---

## 📜 Tokenomics

- **Total Supply**: 1,000,000,000
- **Launch**: bankr.bot (Base)
- **Liquidity**: 60% locked
- **Node Rewards**: 25%
- **Treasury**: 10%
- **Airdrop**: 5%

---

## 🤖 OpenClaw Integration

Agents can directly interact with Agentic Chain:

```javascript
// Import skill
const agentic = require('./openclaw/agentic');

// Register identity
await agentic.registerAgent("MyAgent", metadata);

// Check rate limits
const { allowed } = await agentic.checkRateLimit(agentAddress);

// Batch execute
await agentic.batchExecute([{target, data}, ...]);

// Start node and earn
const node = await agentic.startNode();
```

See [`openclaw/README.md`](./openclaw/README.md) for full documentation.

---

## 🛠️ Development

```bash
# Run Python blockchain (test)
python3 substrate/agentic_runtime.py

# Run Base L2 node
python3 node/agentic_node.py

# Run node with wallet
python3 node/agentic_node.py --create-wallet

# Check balance
python3 node/agentic_node.py --balance
```

---

## 📄 License

MIT

---

*Built for the agent economy | 2026*
