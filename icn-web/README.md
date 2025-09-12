# ICN Demo UI (icn-web)

A minimal React app to demo ICN flows for non-technical users.

## Quick start

```bash
cd icn-web
npm i
npm run dev
```

- Demo mode: works without a backend
- Live API mode: set API base (e.g., http://localhost:8000), Org ID, Key ID, and Base64 Ed25519 private key

## Notes
- Uses Vite + React
- Ed25519 signing via tweetnacl
- No Tailwind; simple CSS in `src/styles.css`
