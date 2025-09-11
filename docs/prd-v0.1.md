Product Requirements Document (PRD)

Project: Intercooperative Network (ICN)
Version: 0.1 (Foundational Draft)
Date: September 2025
Owner: ICN Core Team

1. Purpose

The Intercooperative Network (ICN) exists to provide digital infrastructure for cooperatives, communities, and allied organizations to coordinate resources, share value, and govern collaboratively without reliance on extractive platforms.

The network is not a new economy imposed from above, but a substrate for cooperation: simple primitives (identity, exchange, trust, memory) that communities can build upon in ways appropriate to their context.

2. Vision & Goals

Democratize infrastructure: Treat digital coordination tools as commons, not commodities.

Empower cooperation at all scales: From two co-ops sharing an invoice, to federations coordinating across regions.

Stay boring and familiar: Build on proven practices (double-entry accounting, invoices, attestations) rather than exotic abstractions.

Resist capture: Architect for federation, transparency, and local sovereignty.

Bridge layers of reality: Interface smoothly with legal/fiat systems, social trust, and logistical/resource optimization.

3. Scope (MVP)
3.1 Core Primitives

Identity Attestation

Each cooperative or community has a cryptographic keypair.

Signed attestations verify existence, trust relationships, and capabilities.

Invoices

The foundational economic unit: “Co-op A provided X to Co-op B.”

States: proposed, accepted, disputed, settled.

Supports narrative field (“story”) for transparency.

Bulletin Board

Authenticated posting of offers and needs.

Searchable and filterable (by resource type, geography, time).

Attestations & Reputation

Fact-based records: “Org X fulfilled invoice Y as agreed.”

Builds a trust graph rather than a gamified score.

Dispute Log

Public, append-only thread for conflicts and resolutions.

Minimal structure; supports evidence references.

4. Out of Scope (for MVP)

Complex tokenomics or speculative currencies.

Global governance protocols.

High-speed consensus mechanisms.

Formal labor-hour valuation schemes.

5. Users & Stakeholders
Primary Users

Worker cooperatives: tech, construction, services.

Consumer co-ops: food, housing, utilities.

Community groups: mutual aid networks, associations.

Secondary Users

Allied organizations: credit unions, nonprofits, municipalities.

Guilds/service co-ops: hosting, mediation, legal, accounting.

6. Architecture Overview

Sovereign Nodes: Each cooperative runs a lightweight node (API + DB).

Audit Chain: All records hash-chained with daily checkpoints.

Relays: Optional directory/search hubs; not authoritative.

Federation: Inter-node communication via signed JSON over HTTPS.

Interoperability: CSV import/export; QuickBooks/Xero/Odoo adapters.

7. Feature Requirements (MVP)
7.1 Identity & Authentication

Register new org with keypair and metadata.

Rotate keys with historical continuity.

SSO for human admins.

7.2 Invoices

CRUD operations with cryptographic signatures.

Track status lifecycle.

Attach legal contract PDFs (optional).

Export to fiat systems.

7.3 Bulletin

Post authenticated offers/needs.

Browse/search posts.

Subscribe to updates by category/region.

7.4 Attestations

Link attestations to invoices or posts.

Attach evidence (hash references, external URLs).

Query trust graph (0–3 hops).

7.5 Dispute Log

Append-only discussion per invoice.

Supports evidence references.

Resolution state recorded and signed.

8. Non-Functional Requirements

Simplicity: Deployable via docker-compose in <30 minutes.

Resilience: Handles 30% offline nodes, 10% malicious actors.

Transparency: All logs exportable and verifiable offline.

Privacy: Minimal PII, org-level focus, optional redaction.

Interoperability: Compatible with existing accounting tools.

9. Implementation Roadmap

Phase 1 (3–6 months):

Identity, invoice, bulletin MVP.

CSV/QuickBooks import/export.

Dockerized node with web UI.

Phase 2 (6–12 months):

Attestations + trust graph.

Dispute log.

Settlement suggestion engine.

Relay service with mirroring.

Phase 3 (12–18 months):

Federation of relays.

Crisis-response mode.

Optional governance modules.

Integration with mutual aid + guild services.

10. Risks & Mitigations

Complexity creep: enforce weekend-project rule for components.

Speculative capture: no native token; fiat and mutual credit only.

Adoption gap: start with invoice workflows co-ops already use.

Governance paralysis: governance features deferred until real demand.

11. Success Metrics

Adoption: number of active co-ops using ICN nodes.

Engagement: frequency of invoices, attestations, bulletin posts.

Efficiency: average time saved in reconciliation/settlement.

Trust: dispute resolution rate and satisfaction.

Resilience: proportion of trades fulfilled during network disruptions.

12. Appendices

Glossary: Coop, community, guild, relay, invoice, attestation, etc.

Data Schemas: JSON examples for invoices, attestations, bulletins.

Legal Templates: Trade credit, mutual aid MOU, dispute mediation.