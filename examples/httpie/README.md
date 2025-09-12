HTTPie collection

Usage:

```bash
export DEMO_BASE_URL=http://localhost:8000
bash examples/httpie/00_health.sh
bash examples/httpie/10_create_invoice_alpha_to_beta.sh
bash examples/httpie/20_accept_invoice_beta.sh 1
bash examples/httpie/30_post_attestation_gamma_on_invoice.sh
bash examples/httpie/40_get_trust_score.sh
bash examples/httpie/50_generate_and_verify_checkpoint.sh
```

Each script invokes `tools/sign.py` to generate the signature header.


