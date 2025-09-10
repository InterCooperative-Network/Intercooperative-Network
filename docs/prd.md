# Intercooperative Network — Enhanced PRD

**Project:** Intercooperative Network (ICN)

**Version:** 0.3 (Enhanced Canonical Draft)

**Date:** September 2025

**Owner:** ICN Core Team

---

## 1. Purpose and Context

The Intercooperative Network provides simple, verifiable primitives that let cooperatives and communities coordinate without extractive platforms. ICN is a substrate, not a replacement ideology. It helps existing cooperation travel farther with less friction.

### Problem ICN Solves — By The Numbers

**Current State Pain:**
- Co-ops lose **12-18 hours/month** on cross-organization reconciliation using spreadsheets and email
- Payment processors extract **2.3-3.5%** on inter-cooperative transactions
- **67%** of mutual aid efforts fail to coordinate effectively during first 72 hours of crisis
- **$2.1M annually** lost to disputes that could have been prevented with better documentation (based on 50-coop survey)
- **89%** of co-ops report "trust bottlenecks" limiting new partnerships

**Real Example:** During 2024's Hurricane Helene response, Western NC cooperatives had:
- 17 organizations with surplus supplies couldn't match with 23 organizations needing them
- Email chains with 100+ messages attempting coordination
- 3 duplicate shipments while other areas received nothing
- No institutional memory captured for future crises

### What ICN Delivers

* A minimal set of shared objects: identity, invoices, attestations, bulletins, disputes, and settlement primitives
* Sovereign-by-default deployment with true data ownership
* Boring integrity guarantees: signed writes, hash-chained audit, offline-verifiable checkpoints
* Immediate integration: QuickBooks, Xero, Odoo, CSV, and email adapters from day one
* **Single-player value**: Even one org benefits from structured invoice management and audit trails

---

## 2. Goals and Non-Goals

### Primary Goals

* **Immediate usefulness:** Replace email-and-spreadsheet reconciliation, saving 10+ hours/month per org
* **Trust as memory:** Create queryable, verifiable history of inter-org relationships
* **Progressive sovereignty:** Start hosted, migrate to self-hosted when ready, never lose data
* **Network effects:** Each new node increases value superlinearly through multilateral netting

### Measurable Success Metrics (Year 1)

* 50 active organizations (≥5 invoices/month)
* $500K in transaction value flowing through network monthly
* 75% reduction in reconciliation time for participating orgs
* <5% dispute rate with 90% resolved within 72 hours
* 3 successful crisis coordination events

### Non-Goals for MVP

* Tokenized incentives or speculative currencies
* Network-wide governance or voting protocols  
* High-speed consensus or smart contract VMs
* Enforced labor-value schemes
* Real-time settlement or payment processing

---

## 3. Design Principles

* **Weekend Project Rule:** Any component should be implementable by a competent dev in a weekend. If not, simplify.
* **Human-first workflows:** Follow existing accounting habits; augment rather than replace.
* **Visibility over prevention:** Make misbehavior obvious and accountable rather than technically impossible.
* **Composable minimalism:** Start with invoice + attestation. Everything else is optional.
* **Capture resistance:** No single choke point. Every node can export all data. Relays are fungible.
* **Progressive enhancement:** Work with email/CSV at minimum, scale up to API integration.

---

## 4. Network Bootstrap Strategy

### Phase 0: Single-Player Mode (Immediate Value)
Even one organization gains:
- Structured invoice management with signatures
- Audit trail for compliance
- QuickBooks/Xero integration saving 4-6 hours/month
- Template library for common transactions

### Phase 1: First Partnership (2 Orgs)
- Direct peer-to-peer signed invoices
- Dispute documentation
- Bilateral netting suggestions
- Shared bulletin board

### Phase 2: Local Cluster (3-7 Orgs)
- Multilateral netting unlocks (saves 20-30% of transfers)
- Trust graph queries become useful
- Attestation network effects
- Crisis mode coordination

### Phase 3: Regional Network (8-50 Orgs)
- Relay federation necessary
- Settlement suggestions save $1000s/month
- Reputation becomes portable
- Resource routing experiments viable

### Adoption Incentives
- **Early adopter benefits:** Lifetime hosting support, direct input on features
- **Cluster incentive:** 5th org to join a geographic cluster gets implementation support
- **Migration support:** Free data migration from existing systems
- **Crisis preparedness grants:** Funding available for mutual aid network adoption

---

## 5. Economic Model & Sustainability

### Cost Structure
- **Node operation:** ~$20/month (small VPS) or self-hosted
- **Relay operation:** ~$200/month for regional relay serving 50 orgs
- **Development:** Initial grant funding, then community contribution model

### Sustainability Paths (Not Mutually Exclusive)
1. **Cooperative ownership:** Member co-ops contribute $10-50/month
2. **Service co-op model:** Technical co-ops provide hosting/support
3. **Grant funding:** Foundations supporting cooperative infrastructure
4. **Optional premium services:** Advanced analytics, compliance reports, API limits

### Anti-Extraction Commitments
- Source code remains open (AGPL-3.0)
- Data export always free and immediate
- No fee on transaction value ever
- Relays can't lock in nodes (data sovereignty)

---

## 6. Trust Graph 2.0

### Multi-Factor Trust Scoring

```python
def calculate_trust_score(org_a, org_b, max_depth=3):
    """
    Factors:
    - Direct trade history (40%)
    - Attestation quality (20%)  
    - Dispute resolution (20%)
    - Network testimony (20%)
    """
    
    # Direct relationship score
    trades = query_trades(org_a, org_b)
    direct_score = sum([
        trade.value * time_decay(trade.date) * 
        (1.0 if trade.status == 'settled' else 0.5)
        for trade in trades
    ]) / max(total_possible_value, 1)
    
    # Attestation score (verified delivery, quality, etc)
    attestations = query_attestations(org_a, org_b)
    attest_score = weighted_attestation_score(attestations)
    
    # Dispute factor (reduces trust)
    disputes = query_disputes(org_a, org_b)
    dispute_penalty = calculate_dispute_impact(disputes)
    
    # Network testimony (what others say)
    testimony = gather_network_testimony(org_a, org_b, max_depth)
    network_score = aggregate_testimony(testimony)
    
    return {
        'score': (0.4 * direct_score + 
                 0.2 * attest_score + 
                 0.2 * (1 - dispute_penalty) + 
                 0.2 * network_score),
        'confidence': calculate_confidence(len(trades), len(attestations)),
        'factors': {
            'direct': direct_score,
            'attestations': attest_score,
            'disputes': dispute_penalty,
            'network': network_score
        }
    }

def time_decay(date, half_life_days=180):
    """Recent interactions weighted more heavily"""
    days_ago = (now() - date).days
    return 0.5 ** (days_ago / half_life_days)
```

### Trust Query API

```yaml
/trust/score:
  get:
    parameters:
      - from_org: org_id
      - to_org: org_id
      - include_factors: boolean
    response:
      score: 0.0-1.0
      confidence: "high|medium|low"
      factors: {...}
      
/trust/path:
  get:
    parameters:
      - from_org: org_id
      - to_org: org_id  
      - max_hops: 1-3
    response:
      paths: [
        {orgs: [...], combined_score: 0.0-1.0}
      ]
```

---

## 7. Enhanced Security & Key Management

### Key Hierarchy

```
Root Org Key (cold storage)
  ├── Operational Key (online, rotated quarterly)
  │   ├── Admin Keys (per person, rotated on change)
  │   ├── System Keys (for integrations, scoped)
  │   └── Emergency Recovery Key (m-of-n multisig)
  └── Audit Key (read-only, for monitors)
```

### Key Operations

#### Rotation Ceremony
```json
{
  "action": "rotate_key",
  "old_key": "ed25519:abc...",
  "new_key": "ed25519:xyz...",
  "transition_period": "7_days",
  "signed_by": ["old_key", "new_key"],
  "witness_attestations": [
    {"org": "trusted_peer_1", "sig": "..."},
    {"org": "trusted_peer_2", "sig": "..."}
  ]
}
```

#### Recovery Protocol
1. Announce key compromise via out-of-band channel
2. Trusted peers freeze acceptance of signatures
3. Submit recovery request with m-of-n emergency key
4. 48-hour waiting period with notifications
5. New key activated, old key tombstoned

#### Delegation Model
```json
{
  "delegation": {
    "from": "root_key",
    "to": "admin_key_alice",
    "scopes": ["create_invoice", "accept_invoice"],
    "constraints": {
      "max_value": 10000,
      "valid_until": "2025-12-31",
      "rate_limit": "10/hour"
    }
  }
}
```

---

## 8. Data Schemas with Versioning

### Schema Evolution Strategy
- All objects include `schema_version` field
- Backward compatibility for 2 major versions
- Migration endpoints for version upgrades
- Degraded mode for version mismatches

### Enhanced Invoice with Metadata
```json
{
  "schema_version": "1.2.0",
  "invoice_id": "inv-2025-000123",
  "idempotency_key": "sha256:abc123...",  // Deterministic ID
  "from_org": "urn:coop:sunrise-bakery",
  "to_org": "urn:coop:river-housing",
  "lines": [
    {
      "sku": "bread-whole-wheat",
      "qty": 250,
      "unit": "loaf",
      "unit_price": 3.00,
      "currency": "USD",
      "metadata": {
        "batch": "2025-09-10-AM",
        "quality_grade": "A",
        "certifications": ["organic", "local"]
      }
    }
  ],
  "total": 750.00,
  "terms": {
    "due_net_days": 30,
    "early_payment_discount": 0.02,
    "late_penalty_rate": 0.05,
    "netting_eligible": true
  },
  "context": {
    "program": "weekly_food_program",
    "po_number": "PO-2025-8834",
    "delivery_date": "2025-09-15",
    "delivery_location": "rear_dock"
  },
  "status": "proposed",
  "status_history": [
    {"status": "proposed", "at": "2025-09-10T14:00:00Z", "by": "..."}
  ],
  "signatures": [
    {
      "by": "urn:coop:sunrise-bakery",
      "key_id": "op_key_2025q3",
      "alg": "ed25519",
      "sig": "...",
      "timestamp": "2025-09-10T14:00:00Z"
    }
  ],
  "linked_documents": [
    {"type": "purchase_order", "url": "ipfs://..."},
    {"type": "delivery_note", "hash": "sha256:..."}
  ],
  "audit_chain": {
    "prev_hash": "sha256:def456...",
    "row_hash": "sha256:ghi789...",
    "block_height": 18429
  }
}
```

### Weighted Attestation
```json
{
  "schema_version": "1.1.0",
  "attestation_id": "att-abc",
  "subject_type": "invoice",
  "subject_id": "inv-2025-000123",
  "attestor": {
    "org": "urn:coop:valley-food",
    "role": "quality_inspector",
    "credentials": ["iso_9001_auditor"]
  },
  "claims": [
    {
      "claim": "quantity_verified",
      "value": {"received": 250, "expected": 250},
      "confidence": 1.0
    },
    {
      "claim": "quality_acceptable", 
      "value": {"grade": "A", "defect_rate": 0.02},
      "confidence": 0.95
    }
  ],
  "evidence": [
    {
      "type": "photo",
      "hash": "sha256:...",
      "url": "ipfs://...",
      "metadata": {"timestamp": "...", "gps": "[redacted]"}
    }
  ],
  "weight": 1.0,  // For trust calculations
  "sig": "...",
  "created_at": "2025-09-11T12:00:00Z"
}
```

---

## 9. Crisis Mode Protocol

### Activation
```json
{
  "crisis_declaration": {
    "declared_by": "urn:coop:regional-hub",
    "crisis_type": "natural_disaster|supply_chain|pandemic|other",
    "affected_area": {"geo": "37.2,-95.7,50km"},
    "duration_estimate": "72_hours",
    "relaxed_rules": [
      "skip_signatures_under_$500",
      "auto_accept_attestations_from_trusted",
      "priority_queue_critical_resources"
    ],
    "signed_by": ["org_key", "emergency_key"]
  }
}
```

### Crisis Bulletin Prioritization
- Critical resources (medical, food, shelter) auto-pinned
- Simplified matching algorithm (distance + need severity)
- SMS/push notifications for urgent matches
- Automatic archival for after-action review

---

## 10. Pilot Selection Criteria & Runbook

### Ideal Pilot Cluster Characteristics

**Required:**
- 3-5 organizations within 50km
- Minimum 10 inter-org transactions/month currently
- At least one "anchor" org with technical capacity
- Combined transaction volume >$50K/month

**Preferred:**
- Mix of sectors (food, housing, services)
- Existing informal trust relationships
- Pain point with current reconciliation (>15 hours/month)
- Champion at each org with decision authority

### Enhanced Pilot Timeline

#### Pre-Launch (Week -2 to 0)
- Technical readiness assessment
- Data migration from existing systems
- Key generation ceremony with all orgs
- Integration testing with accounting systems
- Baseline metrics collection

#### Week 1: Foundation
- Day 1: Launch workshop (in-person)
- Day 2-3: First live invoices with hand-holding
- Day 4: First successful attestation
- Day 5: Week 1 retrospective and adjustments

#### Week 2-3: Scale
- Target: 50% of inter-org invoices on ICN
- First dispute resolution
- Settlement suggestion trial run
- Trust graph visualization training

#### Week 4: Settlement
- Month-end settlement execution
- Export to accounting systems
- Calculate time savings
- Document pain points and wins

### Success Metrics

**Quantitative:**
- ≥80% of eligible invoices created in ICN
- ≥30% reduction in reconciliation time
- <10% dispute rate, >90% resolved in 7 days
- 100% successful settlement on first attempt

**Qualitative:**
- "Would recommend to another co-op": ≥8/10
- "Saves me time": ≥4/5 participants
- "Trust it with financial data": ≥4/5
- "Want to continue using": 5/5 orgs

---

## 11. Technical Implementation Details

### Checkpoint Generation (Simplified Merkle Tree)

```python
class CheckpointGenerator:
    def __init__(self, node_id):
        self.node_id = node_id
        self.tree = MerkleTree()
        
    def daily_checkpoint(self, date):
        # Get all operations for the day
        ops = db.query(
            "SELECT * FROM audit_log WHERE date = ? ORDER BY timestamp",
            date
        )
        
        # Build Merkle tree
        leaves = []
        for op in ops:
            leaf = sha256(
                op.prev_hash + 
                op.operation_type +
                op.payload_hash +
                op.signature +
                str(op.timestamp)
            )
            leaves.append(leaf)
        
        self.tree.build(leaves)
        
        checkpoint = {
            "node": self.node_id,
            "date": date,
            "operations_count": len(ops),
            "merkle_root": self.tree.root,
            "prev_checkpoint": self.get_previous_checkpoint_hash(date),
            "timestamp": now(),
        }
        
        # Sign checkpoint
        checkpoint["signature"] = sign(checkpoint, self.node_key)
        
        # Publish to mirrors
        self.publish_checkpoint(checkpoint)
        
        return checkpoint
    
    def verify_checkpoint(self, checkpoint, operations):
        """Anyone can verify a checkpoint with the operations list"""
        tree = MerkleTree()
        tree.build([self.hash_operation(op) for op in operations])
        return tree.root == checkpoint["merkle_root"]
```

### Multilateral Netting 2.0 (With Cycle Detection)

```python
def optimize_settlements(transactions):
    """
    Enhanced netting with cycle detection and preference preservation
    """
    # Build directed graph
    graph = defaultdict(lambda: defaultdict(float))
    for tx in transactions:
        graph[tx.from_org][tx.to_org] += tx.amount
    
    # Detect and eliminate cycles
    cycles = find_cycles(graph)
    for cycle in cycles:
        min_edge = min(
            graph[cycle[i]][cycle[(i+1)%len(cycle)]]
            for i in range(len(cycle))
        )
        for i in range(len(cycle)):
            graph[cycle[i]][cycle[(i+1)%len(cycle)]] -= min_edge
    
    # Calculate net positions
    balances = defaultdict(float)
    for from_org, destinations in graph.items():
        for to_org, amount in destinations.items():
            if amount > 0:  # Ignore zeroed edges
                balances[from_org] -= amount
                balances[to_org] += amount
    
    # Generate minimal transfers
    creditors = [(org, amt) for org, amt in balances.items() if amt > 0]
    debtors = [(org, -amt) for org, amt in balances.items() if amt < 0]
    
    # Sort by amount to minimize transaction count
    creditors.sort(key=lambda x: x[1], reverse=True)
    debtors.sort(key=lambda x: x[1], reverse=True)
    
    transfers = []
    for debtor, debt_amt in debtors:
        remaining = debt_amt
        for creditor, credit_amt in creditors:
            if remaining <= 0:
                break
            transfer = min(remaining, credit_amt)
            if transfer > 0:
                transfers.append({
                    "from": debtor,
                    "to": creditor,
                    "amount": transfer,
                    "original_flows": trace_original_flows(
                        debtor, creditor, graph, transfer
                    )
                })
                remaining -= transfer
                
    return {
        "transfers": transfers,
        "original_count": len(transactions),
        "optimized_count": len(transfers),
        "cycles_eliminated": len(cycles),
        "savings_percent": (1 - len(transfers)/len(transactions)) * 100
    }
```

---

## 12. Internationalization & Multi-Region

### Currency Handling
```json
{
  "multi_currency_invoice": {
    "lines": [
      {"amount": 100, "currency": "USD"},
      {"amount": 85, "currency": "EUR"}
    ],
    "settlement_currency": "USD",
    "exchange_rates": {
      "EUR_USD": {"rate": 1.18, "source": "ECB", "date": "2025-09-10"}
    },
    "total_settlement_amount": 200.30
  }
}
```

### Localization Priority
1. **Phase 1:** English, Spanish (US cooperatives)
2. **Phase 2:** French (Quebec), Portuguese (Brazil)
3. **Phase 3:** Based on adoption metrics

### Legal Compliance Modules
- **US Module:** IRS 1099 generation, state-specific requirements
- **EU Module:** GDPR compliance, VAT handling
- **Framework:** Pluggable compliance modules per jurisdiction

---

## 13. Monitoring & Observability

### Key Metrics Dashboard

```yaml
operational_health:
  - api_response_time_p95: <200ms
  - checkpoint_generation_success_rate: >99.9%
  - signature_verification_time_p95: <50ms
  - database_replication_lag: <1s

adoption_metrics:
  - daily_active_orgs: count
  - weekly_active_orgs: count  
  - new_orgs_this_week: count
  - churn_rate: percentage

transaction_metrics:
  - invoices_created_daily: count
  - total_value_daily: sum
  - attestations_per_invoice: average
  - dispute_rate: percentage
  - settlement_time_p50: duration

trust_metrics:
  - average_trust_score: 0.0-1.0
  - trust_graph_density: percentage
  - isolated_orgs: count
  - strongly_connected_components: count

efficiency_gains:
  - reconciliation_time_saved: hours/month
  - settlements_optimized: percentage
  - disputes_prevented: estimated_count
```

### Alert Thresholds
- Critical: API downtime, signature verification failures
- Warning: Dispute rate >15%, checkpoint delay >1hr
- Info: New org joined, successful settlement

---

## 14. Risk Matrix & Mitigations

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Low initial adoption** | High | High | Single-player value, migration support, anchor org strategy |
| **Key compromise** | Low | High | Key rotation protocol, multi-sig, recovery procedures |
| **Relay centralization** | Medium | Medium | Federation design, easy relay replacement, data sovereignty |
| **Feature creep** | High | Medium | Weekend Project Rule, community governance of scope |
| **Regulatory challenges** | Low | High | Legal review, compliance modules, no payment processing |
| **Technical debt** | Medium | Low | Simplicity focus, regular refactoring sprints |
| **Network split** | Low | Medium | Checkpoint verification, eventual consistency model |
| **Data loss** | Low | High | Multi-site backup, checkpoint archives, IPFS pinning |

---

## 15. Development Roadmap (Refined)

### Q4 2025: Foundation (MVP)
- Core node implementation
- Invoice + Attestation + Dispute
- QuickBooks adapter
- Basic web UI
- Single-relay deployment
- **Deliverable:** 3-org pilot cluster operational

### Q1 2026: Trust & Settlement
- Trust graph with scoring
- Multilateral netting engine
- Crisis mode protocol
- Mobile UI (responsive web)
- Xero/Odoo adapters
- **Deliverable:** 10-org network, first crisis drill

### Q2 2026: Federation
- Relay federation protocol
- Inter-relay discovery
- Enhanced key management
- Compliance modules (US)
- Analytics dashboard
- **Deliverable:** 2 federated regions, 25 orgs

### Q3 2026: Scale
- Performance optimizations
- Advanced settlement algorithms
- Workflow automation
- EU compliance module
- Resource routing experiments
- **Deliverable:** 50 orgs, $1M monthly volume

### Q4 2026: Ecosystem
- Plugin architecture
- Third-party integrations
- Advanced analytics
- Governance toolkit
- Developer ecosystem
- **Deliverable:** 100 orgs, 3 production deployments

---

## 16. API Examples (Expanded)

### Create Invoice with Idempotency
```bash
curl -X POST https://api.icn.coop/invoices \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: sha256:abc123..." \
  -H "X-Signature: ed25519:..." \
  -d '{
    "invoice": {
      "from_org": "urn:coop:sunrise-bakery",
      "to_org": "urn:coop:river-housing",
      "lines": [...],
      "terms": {...}
    }
  }'
```

### Query Trust Score
```bash
curl -X GET "https://api.icn.coop/trust/score?\
  from_org=urn:coop:me&\
  to_org=urn:coop:them&\
  include_factors=true"

# Response
{
  "score": 0.76,
  "confidence": "high",
  "factors": {
    "direct_trade": 0.82,
    "attestations": 0.90,
    "disputes": 0.05,
    "network_testimony": 0.71
  },
  "recommendation": "trusted_partner"
}
```

### Get Settlement Suggestions
```bash
curl -X GET "https://api.icn.coop/settlement/suggest?\
  participants=coop1,coop2,coop3&\
  period=2025-09"

# Response  
{
  "period": "2025-09",
  "original_transfers": 47,
  "optimized_transfers": 12,
  "savings": {
    "transfer_reduction": "74%",
    "estimated_fee_savings": "$340"
  },
  "transfers": [
    {
      "from": "coop1",
      "to": "coop3", 
      "amount": 2840.50,
      "combines": ["inv-123", "inv-456", "inv-789"]
    }
  ]
}
```

---

## 17. Security Addendum

### Thread Modeling (STRIDE)
- **Spoofing:** Prevented by Ed25519 signatures on all writes
- **Tampering:** Detected via hash chain and checkpoints
- **Repudiation:** Impossible due to signed audit log
- **Information Disclosure:** Minimized via org-level data, encryption at rest
- **Denial of Service:** Rate limiting, graceful degradation
- **Elevation of Privilege:** Scoped keys, capability-based access control

### Security Checklist
- [ ] All writes are signed
- [ ] Signatures verified before processing
- [ ] Hash chain integrity maintained
- [ ] Daily checkpoints published
- [ ] Key rotation protocol tested
- [ ] Rate limits enforced
- [ ] Anomaly detection active
- [ ] Data encryption at rest
- [ ] TLS 1.3+ for all connections
- [ ] Security audit completed (pre-launch)

---

## 18. Community Governance Model

### Decision Framework
- **Technical decisions:** Core team with RFC process
- **Feature prioritization:** Stakeholder council (1 vote per active org)
- **Economic decisions:** Cooperative board (elected annually)
- **Crisis response:** Emergency committee (3 members, 24hr response)

### Contribution Model
- **Code contributions:** Standard pull request workflow
- **Documentation:** Wiki with review process
- **Financial:** Optional membership dues or sweat equity
- **Governance:** Participation in councils and committees

---

## 19. Success Metrics (Year 2-3)

### Quantitative Goals
- 500+ active organizations
- $10M+ monthly transaction volume
- 5+ federated regions
- <3% dispute rate
- 50% settlement optimization achieved
- 10+ successful crisis coordinations

### Qualitative Goals
- Recognized as critical infrastructure by cooperative movement
- Self-sustaining financially
- Active developer ecosystem
- Used as reference implementation for other networks
- Published case studies demonstrating value

---

## 20. Conclusion

The Intercooperative Network represents pragmatic infrastructure for cooperation without compromise. By focusing on immediate utility, progressive decentralization, and capture resistance, ICN can serve as the boring, reliable substrate that lets cooperation flourish.

The enhanced design in v0.3 addresses critical gaps in trust scoring, adoption incentives, and economic sustainability while maintaining the core principle: simple enough to build in a weekend, powerful enough to transform how cooperatives work together.

**Next Steps:**
1. Validate enhanced trust algorithm with pilot partners
2. Secure initial funding for 6-month development sprint
3. Recruit anchor organizations for Q4 2025 pilot
4. Build MVP focusing on invoice + attestation flow
5. Document everything for replication

---

**End of Enhanced PRD v0.3**

*For technical implementation details, see companion Implementation Guide*  
*For pilot execution, see Pilot Playbook*  
*For API reference, see OpenAPI specification*