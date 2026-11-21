# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Adults coordinating school-age family logistics across more than one caregiver. They arrive with scattered notices and need to establish a trustworthy shared plan without losing the original evidence.

## Product Purpose

Relay turns household messages into reviewable, source-backed commitments. It helps a caregiver see what changed, decide what becomes true, and keep the current plan understandable for the household.

## Positioning

Relay is not a generic chat assistant or calendar: every plan is backed by the original notice and a durable revision trail.

## Operating Context

The local V1 is used on a family computer or phone. Its flow is briefing, inbox review, source-backed approval, plan/history inspection, bounded lookup, export, and local deletion.

## Capabilities and Constraints

Relay currently runs locally on Python and SQLite, uses fictional sample data, and accepts pasted text only. It intentionally has no provider-backed AI, account system, shared login, email connection, upload, OCR, live calendar, or remote deployment. Suggestions require human review before entering the approved plan.

## Brand Commitments

The product is named Relay. Its voice is calm, specific, evidence-led, and direct. It must feel like serious family infrastructure—not a generic SaaS dashboard or an AI chat surface.

## Evidence on Hand

The repository contains a working local application, a synthetic household dataset, workflow documentation, and browser captures. There is no user research, customer proof, pricing evidence, or real household data.

## Product Principles

1. Preserve the source behind every decision.
2. Keep suggestions visibly distinct from approved plans.
3. Make the next human decision obvious without pretending to automate it.
4. Prefer a small trustworthy workflow to a broad, ungrounded assistant.
5. Build for a shared household future while remaining explicit about V1 limits.

## Accessibility & Inclusion

Support keyboard navigation, visible focus, reduced motion, mobile layouts, native form controls, and clear status language. Do not rely on color alone for plan state.
