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

## Project Structure

- `src/resource_dashboard`: planner, alerting, POD, and integration modules
- `tests`: pytest public-interface tests
- `world-contracts`: vendored Frontier dependency with submission-specific
  localnet extensions used by the MVP demo path

## Environment

The repository currently assumes Python is available locally and that tests are
run with `pytest`.

The included `world-contracts/` directory is intentionally vendored into this
submission repo because the MVP depends on local additions for planner resource
seeding and the localnet snapshot helper. A fresh upstream clone of
`evefrontier/world-contracts` is not a drop-in replacement for this repo as
submitted.

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

## Localnet Bootstrap

If you are running the localnet demo from a fresh clone of this submission
repo, install the JavaScript dependencies in `world-contracts/` first:

```bash
cd world-contracts
pnpm install
cd ..
```

The localnet demo path uses the bundled `world-contracts` helper scripts via
`pnpm exec tsx`, so those dependencies must be present before running the
planner or marketplace demo commands.

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
