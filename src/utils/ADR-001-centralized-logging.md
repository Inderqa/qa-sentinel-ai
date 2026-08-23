# ADR-001: Centralized Logging Framework

## Status

Accepted

## Date

2026-08-04

---

## Context

QA Sentinel AI consists of multiple modules that require logging,
including CLI, artifact discovery, parsers, AI engine, reporting,
and storage.

Allowing each module to configure logging independently would lead to:

- duplicated configuration
- inconsistent formatting
- maintenance challenges
- difficult debugging

A centralized logging framework provides a single source of truth
for logging configuration.

---

## Decision

The application will use a dedicated logging module located at:

src/utils/logger.py

This module is responsible for:

- configuring logging
- creating log files
- formatting log messages
- exposing reusable logger instances

Business modules must never configure logging directly.

---

## Consequences

### Positive

- Consistent logging
- Easier debugging
- Centralized configuration
- Supports future enhancements
- Better contributor experience

### Negative

- All modules depend on the logging utility.
- Changes to formatting affect the entire application.

---

## Future Enhancements

- JSON logging
- Correlation IDs
- Performance timing
- Cloud logging
- Configurable log levels