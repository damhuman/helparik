import fetch from 'node-fetch';

async function login(key) {
  const res = await fetch('http://localhost:3000/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ eth_private_key: key }),
  });
  if (!res.ok) throw new Error(await res.text());
  const { sessionId, address } = await res.json();
  console.log('Session ID:', sessionId);
  console.log('Your address:', address);
  return sessionId;
}

// Виклик
login('0x78016a6f053d072107b6f1bb363f275a4fd4ad5934465dd5ef1be30fdd7be11f');
