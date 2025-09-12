// Minimal Ed25519 signing for request bodies
import nacl from 'tweetnacl'

export async function signPayload(payloadString, privateKeyB64) {
  if (!privateKeyB64) throw new Error('Missing private key')
  const raw = Uint8Array.from(atob(privateKeyB64), c => c.charCodeAt(0))
  let secretKey = raw
  // Accept 32-byte seed or 64-byte secret key
  if (raw.length === 32) {
    const keyPair = nacl.sign.keyPair.fromSeed(raw)
    secretKey = keyPair.secretKey
  } else if (raw.length !== 64) {
    throw new Error('Expected 32-byte seed or 64-byte secret key (base64)')
  }
  const message = new TextEncoder().encode(payloadString)
  const signature = nacl.sign.detached(message, secretKey)
  const signatureB64 = btoa(String.fromCharCode(...signature))
  return { signatureB64 }
}
