# PRD → Implementation Mapping

| PRD Section | Implementation |
|-------------|----------------|
| §6 System Architecture | Signed writes middleware; async FastAPI |
| §6 Data Schemas (Invoice) | app/routers/invoices.py; app/models.py |
| §6 Data Schemas (Attestation) | app/routers/attestations.py; app/models.py |
| §6/§16 Trust Graph | app/routers/trust.py (stub factors) |
| §11 Reliability (Checkpoints) | app/routers/checkpoints.py; utils.merkle_root |
| §5 Domain Model (Audit) | app/models.py AuditLog; invoices/attestations write audit rows |
| §8 API Surface | docs/api.md examples |

