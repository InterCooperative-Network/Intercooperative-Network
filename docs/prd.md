# Intercooperative Network — Foundational PRD

**Project:** Intercooperative Network (ICN)

**Version:** 0.2 (Canonical Draft)

**Date:** September 2025

**Owner:** ICN Core Team

---

## 1. Purpose and Context

The Intercooperative Network provides simple, verifiable primitives that let cooperatives and communities coordinate without extractive platforms. ICN is a substrate, not a replacement ideology. It helps existing cooperation travel farther with less friction.

### Problem ICN solves

1. Co-ops coordinate locally using spreadsheets, email, and accounting tools that do not interoperate. 2) Cross-org trust is personal and fragile. 3) Platforms that promise “scale” introduce fees, lock-in, and governance capture. 4) Crisis coordination is ad hoc and loses institutional memory.

### What ICN delivers

* A minimal set of shared objects: identity, invoices, attestations, bulletins, disputes, and optional settlement suggestions.
* Sovereign-by-default deployment. Every org can run a node or use a trusted host.
* Boring integrity guarantees: signed writes, hash-chained audit, offline-verifiable checkpoints.
* Interop first: adapters for QuickBooks, Xero, Odoo, CSV, and email.

---

## 2. Goals and Non-Goals

### Primary goals

* **Immediate usefulness:** Replace email-and-spreadsheet reconciliation for cross-coop work.
* **Trust as memory:** Record who did what for whom, with evidence and resolutions, not gamified scores.
* **Sovereignty:** No token, no global ledger, no central authority required.
* **Progressive decentralization:** Start centralized where helpful, decentralize along the adoption curve.

### Non-goals for MVP

* Tokenized incentives or speculative currencies.
* Network-wide governance or voting protocols.
* High-speed consensus or smart contract VMs.
* Enforced labor-value schemes.

---

## 3. Design Principles

* **Weekend Project Rule:** Any component should be implementable by a competent dev in a weekend. If not, simplify.
* **Human-first workflows:** Follow existing accounting and logistics habits; do not force new rituals.
* **Visibility over prevention:** Make misbehavior obvious and accountable rather than expensive to make impossible.
* **Composable minimalism:** Add modules only when stable primitives prove insufficient.
* **Capture resistance:** No single choke point. Nodes remain sovereign. Relays are optional and replaceable.

---

## 4. Personas and Core User Stories

### Personas

* **Ops Coordinator** at a food co-op: posts surplus offers, receives needs, sends invoices, resolves occasional disputes.
* **Finance Lead** at a housing co-op: imports and exports invoices with QuickBooks. Wants clean month-end settlement.
* **Tech Worker Co-op Admin:** runs a node, manages keys, monitors health, integrates with Odoo, mentors new orgs.
* **Mutual Aid Organizer:** uses bulletin for crisis response, publishes attestations as public memory.

### Top user stories (MVP)

1. As an Ops Coordinator, I can post authenticated offers and needs to nearby orgs.
2. As a Finance Lead, I can issue, accept, dispute, and settle invoices that are signed and auditable.
3. As an Admin, I can attest to fulfillment, attach evidence, and query trust history across 0–3 network hops.
4. As any user, I can browse disputes and outcomes to decide who to work with.
5. As a cluster of co-ops, I can produce multilateral netting suggestions at month end and settle in fiat.

---

## 5. Domain Model and Core Objects

**Objects:** Org, Key, Policy, BulletinPost, Invoice, Attestation, Dispute, Checkpoint, SettlementSuggestion.

```text
[Org] 1—* [Key]
[Org] 1—* [Policy]
[Org] 1—* [BulletinPost]
[Org] 1—* [Invoice] *—1 [Org]
[Invoice] 1—* [Attestation]
[Invoice] 1—* [Dispute]
[Node] produces daily [Checkpoint]
[Org] —* [SettlementSuggestion] (computed view)
```

---

## 6. System Architecture

### Components

* **ICN Node:** API server + Postgres. Hosts an org’s data and signatures.
* **Relay (optional):** Directory, discovery, and search across consenting nodes. Mirrors public data. Not authoritative.
* **Adapters:** QuickBooks, Xero, Odoo, CSV, Email-to-Invoice. Webhooks to sync line items.

### Trust and integrity

* All write operations are signed by the org key. The database stores: row payload, `prev_hash`, `row_hash`, signer, and timestamp.
* A **Checkpoint** is a daily file containing rolling Merkle or linear hash of all writes. Any third party can mirror and verify offline.

### Diagram

```text
+------------+        HTTPS + Signed JSON        +------------+
|  Org A     | <--------------------------------> |   Org B    |
|  ICN Node  |                                     |  ICN Node  |
+------------+                                     +------------+
       ^                                                  ^
       |                                           optional|
       | mirroring                                       \/
   +---------+       public index + search         +-------------+
   |  Relay  | <---------------------------------> | Mirror/Index|
   +---------+                                     +-------------+
```

### Failure-first behaviors

* Nodes tolerate 30 percent offline partners. Writes queue and retry with idempotent request IDs.
* Conflicts are not blocked. They are recorded and surfaced with strong UI affordances.
* Back-pressure via rate limits per key and anomaly flags for duplicate serials and volume spikes.

---

## 7. Data Schemas (MVP JSON)

### Org

```json
{
  "org_id": "urn:coop:sunrise-bakery",
  "display_name": "Sunrise Bakery Cooperative",
  "contact": {"email": "ops@sunrise.coop", "phone": "+1-555-0101"},
  "pubkey": "base58...",
  "metadata": {"geo": "Rochester, NY", "tags": ["food", "bakery"]}
}
```

### Invoice

```json
{
  "invoice_id": "inv-2025-000123",
  "from_org": "urn:coop:sunrise-bakery",
  "to_org": "urn:coop:river-housing",
  "lines": [
    {"sku": "bread", "qty": 250, "unit": "loaf", "unit_price": 3.00, "currency": "USD"}
  ],
  "total": 750.00,
  "terms": {"due_net_days": 30, "can_net": "monthly"},
  "story": "Weekly food program fulfillment.",
  "status": "proposed",
  "signatures": [{"by": "urn:coop:sunrise-bakery", "alg": "ed25519", "sig": "..."}],
  "prev_hash": "...",
  "row_hash": "...",
  "created_at": "2025-09-10T14:00:00Z"
}
```

### Attestation

```json
{
  "attestation_id": "att-abc",
  "subject_type": "invoice",
  "subject_id": "inv-2025-000123",
  "by_org": "urn:coop:valley-food",
  "claim": "fulfilled_as_described",
  "evidence": ["ipfs://bafy...", "https://example.org/proof.jpg"],
  "sig": "...",
  "created_at": "2025-09-11T12:00:00Z"
}
```

### BulletinPost

```json
{
  "post_id": "offer-789",
  "org": "urn:coop:valley-food",
  "kind": "offer",
  "resource": {"type": "tomatoes", "qty": 300, "unit": "kg", "window": "2025-09-15..2025-09-22"},
  "terms": {"price": 1.10, "currency": "USD", "delivery": "pickup"},
  "visibility": "public",
  "sig": "...",
  "created_at": "2025-09-10T15:45:00Z"
}
```

### Dispute

```json
{
  "dispute_id": "disp-42",
  "invoice_id": "inv-2025-000123",
  "opened_by": "urn:coop:river-housing",
  "thread": [
    {"by": "urn:coop:river-housing", "msg": "Received 220 loaves, PO was 250.", "ts": "2025-09-12T09:10:00Z"},
    {"by": "urn:coop:sunrise-bakery", "msg": "Partial due to oven outage. Credit suggested.", "ts": "2025-09-12T10:20:00Z"}
  ],
  "resolution": {"outcome": "partial_credit", "notes": "30 loaves credited", "ts": "2025-09-13T18:00:00Z"},
  "sig": "...",
  "row_hash": "...",
  "prev_hash": "..."
}
```

### Checkpoint

```json
{
  "node": "urn:coop:sunrise-bakery",
  "date": "2025-09-10",
  "rows": 1842,
  "head_hash": "b8f2...",
  "prev_head_hash": "a77c...",
  "sig": "..."
}
```

---

## 8. API Surface (OpenAPI excerpt)

```yaml
openapi: 3.0.3
info:
  title: ICN Node API
  version: 0.1
paths:
  /orgs:
    post:
      summary: Register org
  /orgs/{id}:
    get:
      summary: Get org
  /invoices:
    post:
      summary: Create invoice
    get:
      summary: List invoices
  /invoices/{id}/accept:
    patch:
      summary: Accept invoice
  /invoices/{id}/dispute:
    patch:
      summary: Open dispute
  /attestations:
    post:
      summary: Create attestation
  /bulletin/offers:
    post:
      summary: Post offer
  /bulletin/needs:
    post:
      summary: Post need
  /trust/graph:
    get:
      summary: Query trust graph up to 3 hops
  /settlement/suggest:
    get:
      summary: Multilateral netting suggestions
```

**Auth:** HTTP Signatures of request body with Ed25519. Optional OAuth2 for human sessions. Every write persists the signature and derived `row_hash`.

**Idempotence:** All POST and PATCH calls accept `Idempotency-Key` header.

---

## 9. UX Flows

### 9.1 Onboarding

1. Admin creates org, generates keys, configures SSO. 2) Imports partner directory from CSV. 3) Sets policy: who can post, who can sign, visibility defaults.

### 9.2 Posting an Offer or Need

* Fill resource type, quantity, time window, terms. Choose visibility. Post. Relay indexes the post for discovery. Subscribers receive webhook or email.

### 9.3 Creating and Accepting an Invoice

* From an accepted offer or existing relationship: select counterparty, add lines, attach terms and story. Sign and send. Counterparty accepts or disputes. Status updates are signed and append-only.

### 9.4 Attestation

* A peer or third org vouches fulfillment. They attach evidence. Future queries show this attestation alongside invoice history.

### 9.5 Month-end Netting

* Finance runs `/settlement/suggest`. UI displays a netting plan. Orgs agree and settle in fiat. Export journal entries to QuickBooks.

### 9.6 Dispute Flow

* Open dispute with short note and attachments. Threaded responses. Suggested outcomes: partial credit, replacement, cancel. Final outcome signed by both parties or recorded as unresolved.

### 9.7 Crisis Response Mode

* Toggle cluster to “crisis.” Governance relaxes to predefined simple rules. Bulletin prioritizes critical resources. Audit chain continues normally.

---

## 10. Interoperability

* **CSV:** import and export invoices, orgs, and contacts.
* **Email-to-Invoice:** parse inbound emails into invoice drafts, human confirms, then signs.
* **Accounting adapters:** QuickBooks Online, Xero, Odoo. Map ICN invoices to journal entries. Round-trip settlement status.
* **Webhooks:** on invoice status change, dispute update, new attestations, and bulletin posts.

---

## 11. Security, Privacy, Compliance

* **Keys:** per-org primary key; optional per-admin subkeys. Rotation supported. Old signatures remain valid.
* **Scopes:** observer, trader, member, core. Mapped to API permissions.
* **PII minimization:** org-level by default. Redaction helpers in UI. Evidence can be hash-addressed without hosting private blobs.
* **Rate limiting and anomaly detection:** per-key budgets; flags on duplicate serials, sudden spikes, multi-assign attempts.
* **Legal alignment:** template library for trade credit, MOUs, dispute mediation. Attach signed PDFs to invoices.

---

## 12. Reliability and Operations

* **Offline tolerance:** queued delivery with exponential backoff. Delivery receipts include signature and `row_hash`.
* **Backups:** nightly database dumps plus daily Checkpoint files. Mirrors can verify integrity without DB access.
* **Observability:** metrics on API latency, queue depth, dispute rates, accept-to-settle time.
* **Upgrades:** semantic versions. Backward-compatible schema migrations. Checkpoint format versioned.

---

## 13. Launch Strategy and Pilot Plan

* **Cohort:** 3–5 co-ops in one metro with weekly trade potential: food, housing, tech support.
* **Documents:** two templates: goods delivery and service hours.
* **Tasks:** week 1 setup and training; weeks 2–3 live invoicing with attestations; week 4 settlement and retrospective.
* **Training:** 90-minute session for Ops and Finance. Cheatsheets for status lifecycle and dispute etiquette.

**Pilot success criteria**

* 80 percent of cross-coop invoices created inside ICN.
* Average accept-to-settle time reduced by 30 percent.
* Dispute rate under 10 percent and 90 percent resolved within 7 days.
* Finance reports at least 2 hours saved per month per org on reconciliation.

---

## 14. Roadmap and Progressive Decentralization

* **Phase 1:** single relay, sovereign nodes, checkpoints, adapters, basic UI.
* **Phase 2:** attestations, dispute log, settlement suggestions, trust graph, mirrors.
* **Phase 3:** relay federation with peering, crisis mode, graduated autonomy “mentor co-sign,” contribution showcase (opt in).
* **Phase 4:** modular governance tools: deadline module, expertise weighting, stake to vote, veto triggers.
* **Phase 5:** resource-routing experiments: idle compute jobs, fleet time, kitchen time, warehouse slots.

---

## 15. Governance and Dispute Handling

* Human-first approach. ICN records facts, outcomes, and evidence.
* Optional guilds for mediation. Dispute outcomes can be attested by a guild and appear in history.
* No global court. Clusters choose their dispute providers.

---

## 16. Risks and Mitigations

* **Complexity creep:** enforce Weekend Project Rule. Ship smaller, sooner.
* **Central capture risk:** relays are optional and easily replaced. Encourage mirrors by default.
* **Low adoption:** target invoice and bulletin flows that already exist. Start with two-party utility.
* **Privacy missteps:** default to org-level data, provide redaction and visibility scopes.
* **Speculation pressure:** no token, no built-in price assets. Encourage time-delay posting where needed.

---

## 17. Metrics and Telemetry

* **Adoption:** active orgs with at least 1 invoice in last 30 days.
* **Engagement:** invoices per org, attestations per invoice, bulletin responsiveness time.
* **Trust quality:** resolved disputes ratio, average resolution time, repeat trade rates.
* **Efficiency:** accept-to-settle duration, reconciliation time reported by finance teams.
* **Resilience:** successful retries, mirror verification rates, checkpoint drift alerts.

---

## 18. Implementation Plan

### Team

* 1 lead engineer, 2 backend engineers, 1 frontend, 0.5 devops, 0.5 designer, 0.5 partnerships.

### Milestones

* **M1 — 6 weeks:** Node API with Org, Invoice, Bulletin. Basic web UI. CSV import. Checkpoint generation. Docker Compose.
* **M2 — 6 weeks:** Attestations, Dispute Log, Trust Graph queries, Email-to-Invoice, QuickBooks adapter.
* **M3 — 6 weeks:** Settlement suggestions, Relay v1 with mirror endpoints, anomaly flags, pilot instrumentation.

### Dependencies

* Ed25519 libs, Postgres, container runtime, email parsing lib, accounting APIs.

---

## 19. Pseudocode and Algorithms

### 19.1 Multilateral Netting Suggestion

```python
# Given debts A->B:x, B->C:y, C->A:z, find net transfers that minimize hops
# Input: edges = [(from_org, to_org, amount)]
# Output: transfers[]

balance = defaultdict(float)
for f,t,a in edges:
    balance[f] -= a
    balance[t] += a

creditors = [(org, amt) for org,amt in balance.items() if amt > 0]
debtors   = [(org,-amt) for org,amt in balance.items() if amt < 0]

transfers = []
i=j=0
while i < len(debtors) and j < len(creditors):
    d_org, d_amt = debtors[i]
    c_org, c_amt = creditors[j]
    x = min(d_amt, c_amt)
    transfers.append((d_org, c_org, x))
    debtors[i]  = (d_org, d_amt - x)
    creditors[j]= (c_org, c_amt - x)
    if debtors[i][1] == 0: i+=1
    if creditors[j][1] == 0: j+=1
return transfers
```

### 19.2 Trust Graph Query up to 3 Hops

```sql
-- Simplified: count successful trades and disputes per hop distance
WITH start AS (
  SELECT 'urn:coop:me'::text AS me
), hops AS (
  SELECT i.to_org AS org, 1 AS hop FROM invoices i JOIN start s ON i.from_org = s.me AND i.status='settled'
  UNION
  SELECT i.to_org, 2 FROM invoices i WHERE i.from_org IN (
    SELECT i.to_org FROM invoices i JOIN start s ON i.from_org = s.me AND i.status='settled'
  ) AND i.status='settled'
  UNION
  SELECT i.to_org, 3 FROM invoices i WHERE i.from_org IN (
    SELECT i.to_org FROM invoices i WHERE i.from_org IN (
      SELECT i.to_org FROM invoices i JOIN start s ON i.from_org = s.me AND i.status='settled') AND i.status='settled'
  ) AND i.status='settled'
)
SELECT org, MIN(hop) AS hop, COUNT(*) AS trades
FROM hops GROUP BY org ORDER BY hop, trades DESC;
```

---

## 20. UX Artifacts

### 20.1 Status lifecycle

```text
proposed -> accepted -> settled
       \-> disputed -> resolved_unpaid | resolved_partial | cancelled
```

### 20.2 Dispute etiquette checklist

* Be concrete: quantity, date, expectation vs observed.
* Attach evidence. Prefer photos and signed delivery slips.
* Propose a remedy: partial credit, replacement, cancel.
* Close the loop with signatures.

---

## 21. Glossary

* **Attestation:** A signed statement by an org about a specific fact.
* **Bulletin:** Authenticated posting of needs or offers.
* **Checkpoint:** Daily signed digest of a node’s writes for offline verification.
* **Dispute:** Threaded record of conflict tied to an invoice.
* **Relay:** Optional directory and search index across consenting nodes.
* **Settlement Suggestion:** Computed plan to net multilateral debts.
* **Sovereign Node:** An instance that stores an org’s data and accepts signed writes.

---

## 22. Acceptance Criteria for MVP

* Two independent orgs can exchange signed invoices and settle them.
* A third org can attest to fulfillment and have that appear in trust queries.
* A relay can index and mirror public bulletins and invoices without holding private data.
* A finance lead can export journals to QuickBooks and reconcile month end.
* A mirror can verify a node’s daily checkpoint and detect tampering.

---

## 23. Appendix — Security Notes

* HTTP body signatures prevent man-in-the-middle write forgery.
* Key rotation via new-key co-sign message stored on the audit chain.
* Evidence hashing: store content hash in record; blob storage is pluggable.
* Per-key rate limits and per-org anomaly flags with operator alerts.

---

## 24. Appendix — Pilot Runbook

* Preflight: confirm keys, configure SSO, import contacts, dry-run invoice.
* Week 1: training and first live invoices.
* Week 2–3: attestations, first disputes, settlement suggestions.
* Week 4: settlement, export to accounting, retrospective with metrics.

---

**End of Document**
