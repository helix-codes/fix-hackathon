# Eve Frontier Logistics Dashboard

This repository contains an external Eve Frontier logistics dashboard built for
the March 11-31, 2026 hackathon. The headline product is a planner workflow for
tribe logistics and industry decisions. The secondary workflow is a minimal POD
intelligence marketplace that packages and sells higher-fidelity scan intel
without taking over the main product story.

The core user question is:

What can we produce right now, with what we have nearby, and what will break
first?

## Current Demo Scope

The current MVP submission path is localnet-backed.

It demonstrates:

- planner-visible operational intel from localnet world state
- industry feasibility evaluation
- shortage projection and first bottleneck identification
- deterministic alert rendering
- POD listing previews tied to live seeded scan intel
- POD purchase and premium reveal behavior through the localnet marketplace demo
  using a simulated wallet purchase seam

The mocked path remains as an explicit fallback.

It does not require:

- live Eve Frontier production API auth
- live Discord delivery
- production wallet connectivity
- production chain settlement

## Project Structure

- `src/resource_dashboard`: planner, alerting, POD, and integration modules
- `tests`: pytest public-interface tests
- `PRD.md`: current product requirements
- `PRE_SUBMISSION_CHECKLIST.md`: pre-submission release checklist
- `DEMO_RUNBOOK.md`: operator guide for the trusted demo path and fallback handling
- `docs/submission/MVP_FREEZE.md`: scope guardrails for submission mode
- `docs/submission/SAMPLE_LOCALNET_DASHBOARD_OUTPUT.txt`: captured dashboard artifact
- `docs/submission/SAMPLE_LOCALNET_MARKETPLACE_OUTPUT.txt`: captured marketplace artifact
- `log.txt`: project notes and implementation history

## Environment

The repository currently assumes Python is available locally and that tests are
run with `pytest`.

The verified command is:

```bash
pytest -q
```

## Run Tests

Run the full test suite:

```bash
pytest -q
```

Run a specific file:

```bash
pytest -q tests/test_api_client.py
```

## Run the Demo

Run the localnet planner dashboard:

```bash
PYTHONPATH=src python -m resource_dashboard.localnet_demo
```

Run the localnet marketplace demo:

```bash
PYTHONPATH=src python -m resource_dashboard.localnet_marketplace_demo
```

Fallback to the trusted mocked planner demo if localnet is unavailable:

```bash
PYTHONPATH=src python -m resource_dashboard.localnet_demo --fallback-to-mocked
```

The planner dashboard prints one coherent view showing:

- the localnet or mocked data source indicator
- systems and resources in view
- the selected industry goal
- whether the goal is feasible
- matching POD listings by preview-safe metadata
- the first projected bottleneck
- the alert outcome

## Demo Narrative

The preferred demo sequence is:

1. load localnet operational intel
2. inspect feasibility for a selected industry goal
3. inspect matching POD preview listings for the same goal
4. inspect the first projected shortage
5. show the alert outcome
6. run one POD purchase and premium reveal flow

If localnet is unstable during judging, fall back to the mocked planner path
and describe the wallet and Discord seams as intentionally non-blocking
extensions.

For the operator-facing script and fallback wording, see `DEMO_RUNBOOK.md`.

## Integration Status

- Localnet world data: implemented and used in the MVP demo path
- Eve Frontier production live data: unresolved and not required for submission
- Discord delivery: not implemented as a live transport; alert rendering is deterministic
- Marketplace listings: sourced from localnet-seeded scan intel
- Marketplace purchase: simulated through the wallet adapter seam in localnet demo flow

## Product Boundaries

- The dashboard is the primary product.
- The planner is a feasibility checker, not a global optimizer.
- POD preview exposes only approximate planning intel.
- POD reveal exposes premium exact intel only after purchase.
- DAO, governance, auctions, and DeFi mechanics are out of scope.

## Why Mocked Data Is Intentional

Mocked data is a product capability, not a temporary hack. The hackathon
environment has unresolved auth, indexing, and settlement details, so the
fallback mode protects the main planner story and keeps the demo reliable.
