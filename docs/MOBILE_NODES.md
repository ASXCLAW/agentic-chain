# AGENTIC CHAIN - Mobile Node

This document describes how to run Agentic Chain nodes on mobile devices (iOS, Android) and integrate local AI models.

---

## Overview

| Platform | Node Type | AI Model | Earn Rate |
|----------|-----------|----------|-----------|
| Mac (Apple Silicon) | Full Node | Llama 3.2, Gemma 3 | 2x multiplier |
| iPhone/iPad | Mobile Node | Gemma 3n, SmolLM | 1.5x multiplier |
| Android | Mobile Node | Gemma 3, Qwen 2.5 | 1.5x multiplier |
| Linux Server | Full Node | DeepSeek R1 | 2x multiplier |
| Laptop/Desktop | Standard Node | Any | 1x |

---

## iOS Integration (Swift)

### Using MLX for Local Inference

```swift
import MLX
import MLXLLM

class AgenticNode: ObservableObject {
    @Published var walletAddress: String = ""
    @Published var balance: Double = 0.0
    @Published var isRunning: Bool = false
    @Published var modelLoaded: Bool = false
    
    private var modelContainer: ModelContainer?
    private var mlxStream: MLXLLMStream?
    
    // Load local AI model
    func loadModel(_ modelName: String) async throws {
        // Supported: llama-3.2-1b, gemma-3n-1b, smollm-135m
        modelContainer = try await ModelLoader.loadContainer(
            modelPath: "\(modelName).mlx",
            modelConfiguration: ModelConfiguration()
        )
        modelLoaded = true
    }
    
    // Process inference request
    func processInference(prompt: String) async -> String {
        guard let container = modelContainer else {
            return "No model loaded"
        }
        
        let parameters = GenerateParameters(
            temperature: 0.7,
            maxTokens: 256
        )
        
        var result = ""
        for try await token in container.generate(prompt: prompt, parameters: parameters) {
            result += token
        }
        
        // Record earnings
        await recordEarnings(source: "inference", amount: 0.01)
        
        return result
    }
    
    // Connect to Agentic Chain
    func connect(rpcURL: String = "https://mainnet.base.org") async throws {
        // Connect to Base
        // Create/load wallet
        // Start syncing blocks
        // Begin earning rewards
    }
}
```

---

## Android Integration (Kotlin)

### Using ML Kit + Local Models

```kotlin
class AgenticNode(private val context: Context) {
    
    private var wallet: Wallet? = null
    private var model: RemoteModel? = null
    private val baseRPC = "https://mainnet.base.org"
    
    // Load local model (Gemma 3)
    suspend fun loadModel() {
        val downloadConditions = DownloadConditions.Builder()
            .requireWifi()
            .build()
        
        // Download model for offline use
        RemoteModelManager.getInstance().download(
            CustomModel("gemma-3n-1b", "https://..."),
            downloadConditions
        )
    }
    
    // Process inference
    suspend fun processInference(prompt: String): String {
        // Use ML Kit or custom TensorFlow Lite
        val input = Tokenizer.encode(prompt)
        val output = model?.infer(input)
        
        // Record earnings to chain
        recordEarnings("inference", 0.01)
        
        return Tokenizer.decode(output)
    }
    
    // Start node
    suspend fun startNode() {
        // Connect to Base
        wallet = createOrLoadWallet()
        
        // Sync blocks
        startBlockSync()
        
        // Start earning
        startEarning()
    }
}
```

---

## Cross-Platform: React Native / Expo

```typescript
// Using expo-localai or custom native modules

import { LocalAI } from 'expo-localai';

interface AgenticNode {
  walletAddress: string;
  balance: number;
  isRunning: boolean;
  
  // Initialize
  initialize(): Promise<void>;
  
  // Load model
  loadModel(model: 'llama-3.2' | 'gemma-3n' | 'smollm'): Promise<void>;
  
  // Run inference
  infer(prompt: string): Promise<string>;
  
  // Chain operations
  getBalance(): Promise<number>;
  stake(amount: number): Promise<void>;
  claimRewards(): Promise<void>;
}

const node: AgenticNode = {
  async initialize() {
    // Connect to Base RPC
    await this.loadModel('gemma-3n');
  },
  
  async infer(prompt) {
    const startTime = Date.now();
    const response = await LocalAI.generate(prompt, {
      model: 'gemma-3n',
      temperature: 0.7,
      maxTokens: 256
    });
    
    // Calculate earnings based on compute time
    const computeTime = (Date.now() - startTime) / 1000;
    const earnings = calculateEarnings(computeTime);
    
    // Record on chain
    await this.recordEarnings('inference', earnings);
    
    return response;
  }
};
```

---

## Earning Mechanics

### Reward Calculation

```
Base Reward = 0.01 AGENTIC per inference
Platform Bonus:
  - Apple Silicon (Mac): 2.0x
  - iOS/Android (Mobile): 1.5x
  - Standard (PC/Server): 1.0x

Staking Bonus:
  - 100+ AGENTIC: 1.0x
  - 1000+ AGENTIC: 1.5x
  - 10000+ AGENTIC: 2.0x

Total = Base × Platform × Staking
```

### Example Earnings (Monthly)

| Device | Inferences/Day | Monthly Earn |
|--------|---------------|--------------|
| Mac M4 (2x) | 100 | ~120 AGENTIC |
| iPhone 16 (1.5x) | 50 | ~45 AGENTIC |
| Android Phone (1.5x) | 50 | ~45 AGENTIC |
| Laptop (1x) | 30 | ~18 AGENTIC |

---

## Node Architecture

```
┌─────────────────────────────────────────────────┐
│              Mobile / Edge Device                 │
├─────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌────────┐ │
│  │   Wallet    │  │   Local     │  │  Base  │ │
│  │  (Keys)     │  │  AI Model   │  │  RPC   │ │
│  └─────────────┘  └─────────────┘  └────────┘ │
├─────────────────────────────────────────────────┤
│              Agentic Node Engine                  │
│  • Block sync                                    │
│  • Inference processing                          │
│  • Reward calculation                           │
│  • Staking management                           │
└─────────────────────────────────────────────────┘
```

---

## Security

1. **Keys never leave device**
2. **Models run completely offline**
3. **No data sent to external servers**
4. **All transactions signed locally**

---

## Download

**iOS**: Coming soon to App Store
**Android**: Coming soon to Play Store
**Mac**: `brew install agentic-chain`

---

## API Reference

### `/node/status`
```json
{
  "wallet": "0x...",
  "balance": 100.5,
  "staked": 50,
  "model": "gemma-3n-1b",
  "inferences_today": 47,
  "earnings_today": 0.47
}
```

### `/node/infer`
```json
// POST
{
  "prompt": "Hello, how are you?",
  "max_tokens": 256
}

// Response
{
  "response": "I'm doing well...",
  "compute_time": 0.5,
  "earned": 0.01
}
```

---

## Roadmap

- [ ] iOS app with Gemma 3n
- [ ] Android app with Qwen 2.5
- [ ] Mac app with Llama 3.2
- [ ] Cross-device wallet sync
- [ ] Voice input support

---

*© 2026 Agentic Chain Foundation*
