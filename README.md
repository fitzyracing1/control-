# control- — Project Portfolio

A collection of software projects spanning web browsers, blockchain/DeFi, robotics control systems, and cryptographic security SDKs.

---

## Projects

### 🌐 browser-project — Open-Source Web Browser
A lightweight, extensible web browser built with **React** and **Framer Motion**.

**Features:**
- Multi-tab browsing support
- Navigation controls: back, forward, refresh, home, reset
- Browsing history tracking
- Bookmark bar
- Reset functionality to clear tabs and history

**Tech stack:** React 18, Framer Motion, Lucide React, JavaScript/JSX

📁 [`browser-project/`](./browser-project)

---

### 🔐 cp — Banking Encryption SDK
A production-grade **cryptographic SDK** for secure banking and financial operations.

**Features:**
- **AES-256-GCM** authenticated encryption and **AES-256-CBC** block cipher
- **PBKDF2-SHA256** password hashing with 100,000 iterations
- Enterprise **key lifecycle management**: generation, rotation (daily/weekly/monthly/yearly), tagging, deactivation
- **Password security**: policy validation, 5-level strength assessment, Shannon entropy, secure generation
- Secure key derivation from passwords
- Full type hints, comprehensive docstrings, zero external dependencies (beyond `cryptography`)
- 42 unit tests with 100% pass rate

**Tech stack:** Python 3.8+, `cryptography` library

📁 [`cp/`](./cp)

---

### 🪙 firecoin\_acela0.1..0 — FireCoin DeFi Token Platform
A decentralized finance (DeFi) token platform built on **Base Sepolia** (Ethereum L2), with a relayer and web interface.

**Features:**
- ERC-20 token smart contract (**FireCoin**) written in **Solidity** / **Hardhat**
- On-chain contract deployment to Base Sepolia testnet
- **Relayer** service for meta-transactions
- Web front-end (Vite/React) for interacting with the token
- Uniswap integration support
- Vercel deployment configuration

**Tech stack:** Solidity, Hardhat, TypeScript, Ethers.js, pnpm workspaces, Base/Sepolia, Vite, React

📁 [`firecoin_acela0.1..0/`](./firecoin_acela0.1..0)

---

### 🤖 meet — Autonomous Robot Protocol Standard Bot
An advanced **protocol-based autonomous robot control system** supporting ground navigation, vertical lift, and full autonomous flight.

**Features:**
- **Signal Processing**: links future signals to specific robot movement courses
- **Autonomous Ground Movement**: continuous forward navigation
- **Vertical Lift**: seamless transition from ground to air while maintaining autonomy
- **Flight Mode**: full 3D autonomous flight with continuous operation
- **Protocol Standard**: standardized command encoding/decoding for robot communication
- Thread-safe state machine with emergency stop
- Never interrupts autonomy during mode transitions (Ground → Lift → Flight)

**Tech stack:** Python 3.7+, threading, state machine architecture

📁 [`meet/`](./meet)

---

## Keywords

React · web browser · multi-tab · Framer Motion · AES-256 · encryption · cryptography · PBKDF2 · key management · password security · banking SDK · Python · DeFi · ERC-20 · Solidity · Hardhat · Base · Sepolia · FireCoin · blockchain · smart contracts · relayer · Vite · autonomous robot · robotics · flight control · signal processing · protocol standard · JavaScript · TypeScript