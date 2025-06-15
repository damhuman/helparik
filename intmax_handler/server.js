// server.js
require('dotenv').config();

// Polyfill Web Crypto API for dependencies using Node's built-in WebCrypto
const { webcrypto } = require('crypto');
globalThis.crypto = webcrypto;

const express = require('express');
const { v4: uuidv4 } = require('uuid');
const { IntMaxNodeClient } = require('intmax2-server-sdk');

const app = express();
app.use(express.json());

// Custom JSON serializer to handle BigInt
const serializeBigInt = (obj) => {
    if (obj === null || obj === undefined) {
        return obj;
    }
    if (typeof obj === 'bigint') {
        return obj.toString();
    }
    if (Array.isArray(obj)) {
        return obj.map(serializeBigInt);
    }
    if (typeof obj === 'object') {
        const result = {};
        for (const [key, value] of Object.entries(obj)) {
            result[key] = serializeBigInt(value);
        }
        return result;
    }
    return obj;
};

// In-memory store for multiple client sessions
const sessions = new Map();

// Middleware to authenticate session for protected routes
app.use((req, res, next) => {
  if (req.path === '/login') return next();

  const sessionId = req.headers['x-session-id'];
  if (!sessionId || !sessions.has(sessionId)) {
    return res.status(401).json({ error: 'Invalid or missing session ID' });
  }

  // Attach client instance to request
  req.client = sessions.get(sessionId);
  next();
});

// POST /login
// Body: { eth_private_key: string }
// Returns: { sessionId, address }
app.post('/login', async (req, res) => {
  const { eth_private_key } = req.body;
  if (!eth_private_key) {
    return res.status(400).json({ error: 'eth_private_key is required' });
  }

  try {
    const client = new IntMaxNodeClient({
      environment: 'testnet',
      eth_private_key,
      l1_rpc_url: process.env.L1_RPC_URL,
    });

    await client.login();
    const sessionId = uuidv4();
    sessions.set(sessionId, client);

    return res.json(serializeBigInt({ sessionId, address: client.address }));
  } catch (err) {
    console.error('Login error:', err);
    return res.status(500).json({ error: err.message });
  }
});

// POST /logout
// Header: x-session-id
// Returns: { status }
app.post('/logout', async (req, res) => {
  const sessionId = req.headers['x-session-id'];
  try {
    const client = sessions.get(sessionId);
    await client.logout();
    sessions.delete(sessionId);
    return res.json({ status: 'Logged out' });
  } catch (err) {
    console.error('Logout error:', err);
    return res.status(500).json({ error: err.message });
  }
});

// GET /balances
app.get('/balances', async (req, res) => {
  try {
    const { balances } = await req.client.fetchTokenBalances();
    return res.json(serializeBigInt({ balances }));
  } catch (err) {
    console.error('Balances error:', err);
    return res.status(500).json({ error: err.message });
  }
});

// POST /sign
// Body: { message: string }
app.post('/sign', async (req, res) => {
  const { message } = req.body;
  if (!message) return res.status(400).json({ error: 'message is required' });

  try {
    const signature = await req.client.signMessage(message);
    return res.json(serializeBigInt({ signature }));
  } catch (err) {
    console.error('Sign error:', err);
    return res.status(500).json({ error: err.message });
  }
});

// POST /verify
// Body: { signature: string, message: string }
app.post('/verify', async (req, res) => {
  const { signature, message } = req.body;
  if (!signature || !message) {
    return res.status(400).json({ error: 'signature and message are required' });
  }

  try {
    const valid = await req.client.verifySignature(signature, message);
    return res.json(serializeBigInt({ valid }));
  } catch (err) {
    console.error('Verify error:', err);
    return res.status(500).json({ error: err.message });
  }
});

// GET /tokens
app.get('/tokens', async (req, res) => {
  try {
    const tokens = await req.client.getTokensList();
    return res.json(serializeBigInt({ tokens }));
  } catch (err) {
    console.error('Tokens error:', err);
    return res.status(500).json({ error: err.message });
  }
});

// POST /deposit/estimate
// Body: { amount: number, token: object, address?: string }
app.post('/deposit/estimate', async (req, res) => {
  const { amount, token, address } = req.body;
  try {
    const gas = await req.client.estimateDepositGas({
      amount,
      token,
      address: address || req.client.address,
      isGasEstimation: true,
    });
    return res.json(serializeBigInt({ gas }));
  } catch (err) {
    console.error('Estimate deposit gas error:', err);
    return res.status(500).json({ error: err.message });
  }
});

// POST /deposit
// Body: { amount: number, token: object, address?: string }
app.post('/deposit', async (req, res) => {
  const { amount, token, address } = req.body;
  try {
    const result = await req.client.deposit({ amount, token, address: address || req.client.address });
    return res.json(serializeBigInt({ result }));
  } catch (err) {
    console.error('Deposit error:', err);
    return res.status(500).json({ error: err.message });
  }
});

// POST /withdraw
// Body: { amount: number, token: object, address: string }
app.post('/withdraw', async (req, res) => {
  const { amount, token, address } = req.body;
  try {
    const fee = await req.client.getWithdrawalFee(token);
    const tx = await req.client.withdraw({ amount, token, address });
    return res.json(serializeBigInt({ fee, tx }));
  } catch (err) {
    console.error('Withdraw error:', err);
    return res.status(500).json({ error: err.message });
  }
});

// GET /deposits
app.get('/deposits', async (req, res) => {
  try {
    const deposits = await req.client.fetchDeposits({});
    return res.json(serializeBigInt({ deposits }));
  } catch (err) {
    console.error('Fetch deposits error:', err);
    return res.status(500).json({ error: err.message });
  }
});

// GET /transfers
app.get('/transfers', async (req, res) => {
  try {
    const transfers = await req.client.fetchTransfers({});
    return res.json(serializeBigInt({ transfers }));
  } catch (err) {
    console.error('Fetch transfers error:', err);
    return res.status(500).json({ error: err.message });
  }
});

// GET /transactions
app.get('/transactions', async (req, res) => {
  try {
    const txs = await req.client.fetchTransactions({});
    return res.json(serializeBigInt({ txs }));
  } catch (err) {
    console.error('Fetch transactions error:', err);
    return res.status(500).json({ error: err.message });
  }
});

// GET /pending-withdrawals
app.get('/pending-withdrawals', async (req, res) => {
  try {
    const pending = await req.client.fetchPendingWithdrawals();
    return res.json(serializeBigInt({ pending }));
  } catch (err) {
    console.error('Fetch pending withdrawals error:', err);
    return res.status(500).json({ error: err.message });
  }
});

// POST /claim-withdrawals
// Body: { withdrawalIds: array }
app.post('/claim-withdrawals', async (req, res) => {
  const { withdrawalIds } = req.body;
  if (!Array.isArray(withdrawalIds)) {
    return res.status(400).json({ error: 'withdrawalIds must be an array' });
  }

  try {
    const result = await req.client.claimWithdrawal(withdrawalIds);
    return res.json(serializeBigInt({ result }));
  } catch (err) {
    console.error('Claim withdrawals error:', err);
    return res.status(500).json({ error: err.message });
  }
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server listening on port ${PORT}`));
