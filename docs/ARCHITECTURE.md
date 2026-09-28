# Architecture

## Purpose
Research toolkit for testing whether autonomous-agent actions are supported by fresh, independent, non-conflicting evidence.

## Data/control flow
Evidence objects → freshness filtering → provenance/independence grouping → conflict detection → support aggregation → ACT / VERIFY / ESCALATE.

## Design invariants
1. Duplicate/correlated sources must not masquerade as independent evidence.
1. Conflicting fresh evidence must never silently authorize an action.
1. Expired evidence must not count as current support.

## Interfaces
The current prototype intentionally keeps interfaces small and inspectable. Future adapters should preserve provenance, explicit failure states, and testability instead of hiding decisions behind opaque orchestration.

## Failure handling
Every consequential output should expose enough state to explain why the system acted, deferred, verified, substituted, or escalated.
