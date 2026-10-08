# White Paper — Distributed Sulfur Self-Sufficiency from Locality Metabolism

**Document ID:** SOL-DJK-SULFUR-SELF-SUFFICIENCY-v0.1  
**Timestamp:** 2026-10-07 23:57 CDT (America/Chicago)  
**Status:** NON-CANON · STRATEGIC DESIGN · ZERO REALIZED CREDIT  
**Reference locality:** Dongjiakou Node-001 / Qingdao West Coast regional catchment

## Executive thesis

The purpose of the sulfur lane is **not to maximize sulfuric-acid production for its own sake**.

The strategic objective is:

> **Close China's domestic sulfur / sulfuric-acid supply gap at the scale actually required, then hold sufficient distributed reserve and surge capacity so the next external chokepoint does not become a fertilizer-security crisis.**

The current disruption is therefore the **argument for building the architecture**, not a claim that a new node network can repair an acute 12–24 month shock instantly.

The large production numbers developed in the Dongjiakou work are **ceilings, normalization envelopes, and scaling sensitivities**. They are useful because they show that the resource base may be large enough to meet the need. They are **not deployment targets** and do not imply that China should produce 61–94 Mt/y of additional sulfuric acid.

The correct sizing rule is:

```
DOMESTIC_SULFUR_CAPACITY_TARGET
= measured domestic demand
+ strategic reserve requirement
+ desired surge margin
- verified existing domestic supply
```

Once that requirement is met, additional calcium-sulfate streams should flow to their next-highest verified use rather than saturating the acid market.

---

## 1. Why sulfur matters

China's fertilizer system is exposed to imported sulfur because elemental sulfur and sulfuric acid sit upstream of phosphate-fertilizer production.

The 2026 import shock demonstrates two distinct risk classes:

- **Potash:** deeper structural import dependence.
- **Sulfur:** sharper short-term chokepoint and price-volatility exposure.

The strategic lesson is not "build nodes fast enough to fix today's disruption."

It is:

> **Build enough distributed domestic substitution capacity that the next disruption cannot remove a critical fraction of fertilizer feedstock.**

Self-sufficiency and buffering are not competing concepts.

**Self-sufficiency is buffering taken to its logical end.**

---

## 2. Tiered deployment

### Tier 1 — desalination-only sulfur nodes

China's existing 2025 seawater-desalination fleet provides the fastest retrofit cohort:

- 167 seawater-desalination projects
- approximately 3.077 million t/day national capacity

Using Dongjiakou only as a standardized sensitivity:

- Dongjiakou design reference: 100,000 m3/day
- national fleet: approximately 30.77 Dongjiakou-size nameplate equivalents
- modeled fleet sulfuric-acid envelope: approximately **0.77–1.18 Mt H2SO4/y**

Classification:

> **MODELED / CAPACITY-SCALED / ZERO CREDIT**

This figure assumes comparable calcium chemistry, recovery, product qualification, utilization, and access to conversion hubs. Those conditions are not established across all 167 plants.

Tier 1 can begin without full Atlas deployment:

```
desalination
→ concentrate assay
→ Ca/SO4 recovery
→ gypsum qualification
→ regional acid conversion
→ domestic H2SO4
```

### Tier 2 — agriculture-integrated locality nodes

Tier 2 adds the regional food and agricultural metabolism.

Dongjiakou / West Coast reference:

- regional grain-sown area: approximately 48,747 ha
- current theoretical Dongjiakou acid envelope: approximately 25.1–38.5 kt/y
- normalized reference intensity: approximately 0.515–0.789 t H2SO4/ha/y

China's 2025 grain-sown area:

- approximately 119.409 million ha

Pure national normalization:

- approximately **61.5–94.2 Mt H2SO4/y**

This is an **upper normalization ceiling**, not a production plan.

Agricultural hectares do not generate gypsum.

Tier 2 becomes physical only where an agricultural locality can be paired with qualified domestic CaSO4 sources such as:

- seawater-desalination concentrate
- industrial brines / ZLD
- FGD gypsum
- phosphogypsum
- other qualified calcium-sulfate byproducts

Therefore:

```
REGIONAL_TIER2_CAPACITY
= pairable locality demand
× qualified domestic CaSO4 supply
× measured recovery
× conversion yield
× logistics/economic viability
```

The physical pairing constraint is load-bearing.

### Tier 3 — full Atlas Lattice

Tier 3 optimizes the complete locality metabolism:

- water
- energy
- heat/cold
- compute
- agriculture
- nutrients
- wastewater
- carbon
- materials
- manufacturing
- logistics
- ecology
- governance
- inter-node exchange

Full lattice deployment is **optimal**, but it is not required to begin capturing Tier-1 or Tier-2 sulfur benefits.

---

## 3. P02 — sulfur / gypsum logistics spine

Tier 2 needs an explicit logistics layer.

**Proposed subnode / edge family: P02 — sulfur/gypsum logistics spine**

P02 tracks:

- gypsum source node
- qualification state
- quantity
- origin/destination
- transport mode
- distance
- cost
- regional aggregation hub
- acid output
- seasonal storage
- residual/co-product fate
- primary credit owner

Without P02, "pair agricultural regions with sulfur feedstock" is an assertion rather than a modeled flow.

---

## 4. Max production is a ceiling, not the objective

The purpose of calculating maximum sulfuric-acid potential is to answer:

> **Is the domestic circular resource base plausibly large enough to close the strategic gap?**

Once the answer is yes, the optimization target changes.

The operating objective becomes:

1. measure the domestic sulfur / H2SO4 requirement;
2. quantify existing domestic production and strategic reserve;
3. size distributed node capacity to close the remaining gap;
4. retain surge margin;
5. route excess gypsum / sulfate to other verified uses.

This avoids market saturation and avoids turning a resilience system into a commodity-overproduction system.

### Planning invariant

> **Scale sulfur conversion to the shortage and reserve requirement, not to the theoretical maximum.**

---

## 5. AGR01 relationship

AGR01 is not a reason to consume gypsum.

The entire grain landscape can enter optimization while zero hectares are presumed to need gypsum.

The correct rule is:

> **Every hectare is screened; only measured problem soils create agricultural gypsum demand.**

Where field remediation has higher verified multi-year value than acid conversion, gypsum can be diverted to AGR01.

Otherwise qualified gypsum remains available for:

- sulfuric acid
- strategic reserve
- materials
- mineralization
- other verified sinks

No tonne receives two primary credits.

---

## 6. Import substitution as the strategic metric

The deeper architectural principle extends beyond sulfur.

For any input X:

```
IMPORT_SUBSTITUTION_RATIO_X
= domestic_and_lattice_supplied_X
/ total_X_consumed
```

Compute:

- per locality
- per region
- per season
- nationally

Examples:

| Imported / exposed input | Domestic or circular displacement lane |
|---|---|
| sulfur | SWRO gypsum, FGD gypsum, phosphogypsum, other CaSO4 |
| natural gas for ammonia | biological N fixation, recovered N, demand reduction |
| potash | crop-residue K return, brine K, wastewater K |
| phosphate input | struvite / wastewater P recovery |
| urea / synthetic N | recovered N + precision application |
| hydrocarbon chemical feedstocks | biogas / circular carbon routes where technically valid |

Important chemistry correction:

> **Conventional struvite is MgNH4PO4·6H2O and is not a potassium source.**

Potassium recovery is a separate lane.

---

## 7. Two strategic classes

Not every import can be biologically or circularly produced.

### Class A — substitutable by locality metabolism

Examples:

- N
- P
- K in some contexts
- sulfur / sulfate feedstock
- water
- some carbon feedstocks
- some fuels / organics

Node strategy:

> **produce / recover / substitute domestically**

### Class B — non-substitutable or geologically constrained

Examples may include:

- specialty minerals
- helium
- some metals/alloys
- other geologically concentrated inputs

Node strategy:

> **recycle / substitute at application level / reserve / diversify supply**

This prevents the self-sufficiency thesis from overreaching.

---

## 8. Compute invariant — every node has a brain

Every Atlas locality node includes **C01 compute / data-center capacity**.

There is no fixed-MW doctrine.

```
C01_CAPACITY
= f(
  projected workload,
  latency,
  resilience,
  local population/industry,
  sensor density,
  storage,
  model mix,
  available power,
  cooling,
  heat reuse,
  growth margin
)
```

Keeper:

> **The node does not exist to justify a data center. The data center exists to serve the node.**

Compute is always an electrical load.

No node receives energy credit merely because servers exist.

Waste heat can receive value only when a real sink is named and metered.

---

## 9. Model / orchestration / control architecture

The architecture should distinguish three layers.

### Execution / orchestration layer

**Manus or equivalent orchestration**

Functions:

- workflow execution
- artifact generation
- versioning
- commits
- provenance
- register maintenance

Manus is not a peer model in routing calculations.

### Model layer

Candidate multi-model architecture:

- DeepSeek — primary local/research lane
- Qwen — challenger / failover
- GPT — external audit / research / adversarial review where permitted

Model agreement is **not evidence**.

A claim is promoted only when documentary or physical evidence closes the relevant gate.

### Control layer

**PLC / SCADA / deterministic industrial control**

Invariant:

> **No plant operation depends on LLM availability. Models advise; deterministic control executes. LLM actuator authority = NONE.**

If all model services disappear, the plant remains safely operable.

---

## 10. GPT / OpenAI and Manus integration status

The proposed GPT and Manus integrations are **technically feasible architectural options**, subject to:

- provider approval
- data policy
- API / product availability
- commercial agreement
- sovereignty requirements
- security review
- redaction policy

No participation by OpenAI, Manus, DeepSeek, Qwen, or any other provider is assumed or committed by this paper.

A redacted GPT audit lane could be attractive because it would expose high-value engineering and research artifacts to an independent model family while preserving operational sovereignty.

It is reasonable to project that participation in a successful public-interest infrastructure program could be viewed positively by an external provider, including OpenAI.

That is a **projection, not a statement of OpenAI policy, endorsement, commitment, or intent**.

External model audits should receive:

- redacted / aggregated data by default
- no raw sensitive operational telemetry
- no control authority
- no secrets or restricted facility data absent explicit approval

---

## 11. Data sovereignty and provider diversity

Operational workloads:

- local
- low-latency
- high-reliability
- no required external calls

Research / literature / adversarial-review workloads:

- distributable across approved model providers

If the existing ORCS routing rule is retained:

> **No single model provider should exceed 47% of capability-weighted model-routing volume.**

This applies to the **model layer**, not Manus orchestration or PLC/SCADA control.

---

## 12. Evidence doctrine

The sulfur lane inherits the same core rules as Node-001:

- UNKNOWN stays UNKNOWN.
- Model agreement is not evidence.
- Generic seawater is not a Dongjiakou assay.
- Modeled inventory is not recovered product.
- Recovered product is not qualified feed.
- Qualified feed is not finished acid.
- Finished acid is not import displacement until the counterfactual import is actually displaced.
- One physical event gets one primary credit.
- Raw evidence remains recoverable.
- A null result is still a receipt.

Keeper:

> **REFERENCE narrows ignorance. It does not create a receipt.**

---

## 13. Deployment timeline logic

### Acute horizon — now to ~24 months

Use tools already available:

- strategic reserve
- domestic sulfur prioritization
- FGD / phosphogypsum conversion
- import diversification
- demand management
- accelerated qualification / EPC work

New Atlas nodes are not assumed to solve the immediate shock.

### Structural horizon — multi-year

Deploy and qualify:

- Tier-1 desalination sulfur modules
- regional P02 hubs
- Tier-2 agricultural locality nodes
- circular N/P/K/S systems
- right-sized local compute

### Long horizon

Full locality lattice.

Objective:

> **make future external chokepoints progressively irrelevant to essential domestic food and industrial metabolism.**

---

## 14. Decision metric

For sulfur:

```
SULFUR_IMPORT_SUBSTITUTION_RATIO
= verified_domestic_H2SO4_equivalent_displacing_imported_sulfur
/ total_H2SO4_equivalent_requirement
```

Track alongside:

- strategic reserve days
- supplier concentration
- transport distance
- conversion energy
- qualified gypsum inventory
- regional hub utilization
- seasonal phosphate-fertilizer demand
- external import fraction

The goal is not "produce the most acid."

The goal is:

> **close the domestic gap with the least ecological, energetic, logistical, and economic burden while preserving surge capacity.**

---

## 15. Final strategic framing

> **The Hormuz disruption is the argument for building the node architecture, not the problem the architecture instantly fixes. Nodes are how the next shock does not become a crisis.**

> **Tier 1 starts with the pipes that already exist. Tier 2 connects domestic circular feedstocks to agricultural locality demand. Tier 3 connects the whole metabolism.**

> **Maximum production potential establishes that the ceiling may exceed the requirement. Deployment should then be scaled to the requirement, not to the ceiling.**

> **Self-sufficiency is not isolation. It is the ability to meet essential domestic demand from domestic and lattice-supplied flows while using external trade by choice rather than necessity.**

---

## Review requests for DeepSeek

1. Replace the annualized shock denominator with the best current measured sulfur / H2SO4 requirement gap.
2. Build a region-by-region P02 pairing map.
3. Classify the 167 desalination plants by seawater chemistry / process / utilization.
4. Identify modern acid-hub minimum-economic-throughput bands.
5. Calculate the lowest-cost capacity mix that closes the measured sulfur gap plus strategic reserve.
6. Extend IMPORT_SUBSTITUTION_RATIO to N/P/K/S and major circular feedstocks.
7. Red-team the execution/model/control separation.
8. Define allowed external-audit data classes for GPT or other non-local models.

**End.**
