# Lattice Runtime Validator Scaffold

**Status:** implementation scaffold / not canon / not deployed  
**Purpose:** Provide lightweight validators for Agent DNA profiles and UWS/alum operation envelopes.

This package is the executable bridge between:

- Agent DNA typed policy metadata
- UWS/alum operation envelopes
- Council Brain / GPTBrain evidence boundaries
- human-root approval requirements

## What This Is

A small, dependency-free Python scaffold for validating design-time records before they are used for routing, task management, or future command-surface integration.

## What This Is Not

This is not:

- a production runtime
- live UWS/alum integration
- provider access
- execution authority
- canon
- proof of deployment

## Files

```text
lattice_validators.py
tests/test_lattice_validators.py
```

## Core Rules Enforced

### Agent DNA

- identity metadata is not execution authority
- inherited permissions must default to empty
- archive memory requires provenance
- canon authority must default false
- execute/write capability requires explicit approval classes

### UWS/alum Operation Envelope

- write/send/delete/share/sync actions require confirmation
- human approval is required before execution for risky actions
- memory cannot authorize action
- private source material cannot be treated as public evidence
- dry run is not execution
- connector availability must be explicit

## Usage

```bash
python -m lattice_runtime.lattice_validators agent-dna path/to/dna.json
python -m lattice_runtime.lattice_validators operation path/to/operation.json
```

## Test

```bash
python -m pytest lattice_runtime/tests
```

## Evidence Boundary

```text
schema = implementation scaffold
validator = guardrail aid
passing validation = format/risk check only
runtime execution = requires connector, code path, tests, audit, and human-root approval
canon = only after Council workflow
```
