# 🤖 OpenClaw Integration

Agentic Chain is designed to work seamlessly with OpenClaw agents.

## Overview

OpenClaw is a platform for running autonomous AI agents. Agentic Chain provides:
- **Agent Wallets**: Agents can hold and manage $AGENTIC
- **Agent Gateway**: Smart contract for agent interactions
- **Node Software**: Agents can run nodes and earn rewards
- **Skills**: Pre-built OpenClaw skills for chain interaction

## Quick Start for OpenClaw Agents

### 1. Install the Skill

Copy to your OpenClaw skills directory:
```bash
mkdir -p ~/.openclaw/skills/agentic
cp -r openclaw/agentic/* ~/.openclaw/skills/agentic/
```

### 2. Configure

Set environment variables:
```bash
export AGENTIC_RPC="http://localhost:8545"
export AGENTIC_CHAIN_ID="999999"
```

### 3. Use in Agent

```javascript
// Import the skill
const agentic = require('~/.openclaw/skills/agentic');

// Check balance
const bal = await agentic.balance("0x...");

// Transfer tokens
await agentic.transfer(to, amount, privateKey);

// Start earning
const node = await agentic.startNode();
```

## Available Actions

| Action | Description |
|--------|-------------|
| `balance` | Get AGENTIC balance |
| `transfer` | Transfer tokens |
| `stake` | Stake for 12% APY |
| `unstake` | Unstake tokens |
| `claimRewards` | Claim staking rewards |
| `bridge` | Cross-chain bridge |
| `startNode` | Start a node |
| `getNodeStatus` | Get node earnings |

## Agent Gateway Contract

The `AgentGateway` contract (`contracts/AgentGateway.sol`) provides:
- Agent registration
- Task execution
- Cross-chain bridge requests
- Event subscriptions for agents

## Wise Usage Guidelines

1. **Start small**: Test with small amounts first
2. **Monitor gas**: Set appropriate gas limits
3. **Simulate first**: Use `eth_call` to predict outcomes
4. **Stay online**: Keep node running for max rewards

## Example: Auto-Bridge Agent

```javascript
// Auto-bridge when balance is low
async function autoBridge(agent, threshold) {
    const balance = await agentic.balance(agent.address);
    
    if (balance < threshold) {
        // Bridge from Ethereum
        await agentic.bridge(
            agent.address,
            threshold,
            "ethereum"
        );
    }
}
```

## Community

- **OpenClaw**: https://github.com/openclaw/openclaw
- **Agentic Chain**: https://github.com/ASXCLAW/agentic-chain

---

*© 2026 Agentic Chain Foundation*
