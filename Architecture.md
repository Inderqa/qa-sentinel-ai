# QA Sentinel AI - Architecture Guide

> **Version:** 0.1.0
>
> This document describes the architectural vision, design principles, and engineering decisions behind QA Sentinel AI.
>
> It explains **why** the project is designed the way it is, rather than **how** individual modules are implemented.

---

# 1. Project Vision

QA Sentinel AI is an AI-powered QA Engineering Assistant designed to help software teams understand, debug, and improve automated test execution.

The long-term vision is to build an intelligent platform capable of:

- Analyzing failed automation tests
- Identifying probable root causes
- Detecting flaky tests
- Generating high-quality bug reports
- Reviewing test automation code
- Measuring test health
- Learning from previous failures
- Assisting QA Engineers throughout the software testing lifecycle

Rather than replacing QA Engineers, QA Sentinel AI aims to augment their productivity by reducing manual debugging effort and accelerating root cause analysis.

---

# 2. Problem Statement

Modern automation frameworks provide execution artifacts such as:

- Stack traces
- Screenshots
- Browser videos
- Trace files
- Network logs
- Console logs

While these artifacts contain valuable information, engineers still spend a significant amount of time manually analyzing failures.

Current automation tools generally answer:

> "The test failed."

QA Sentinel AI attempts to answer:

- Why did the test fail?
- What evidence supports this conclusion?
- Who should investigate?
- Has this happened before?
- Is this likely a flaky test?
- What should be done next?

---

# 3. Design Goals

The architecture is designed around the following engineering principles.

## Simplicity

Modules should have a single responsibility.

Each module should be easy to understand independently.

---

## Extensibility

The application should support additional automation frameworks without major architectural changes.

Future examples include:

- Selenium
- Cypress
- Appium
- Robot Framework

---

## Testability

Business logic should remain independent from infrastructure.

This allows every module to be unit tested without requiring external services.

---

## Maintainability

Large modules are difficult to understand.

The architecture encourages small, focused modules with well-defined responsibilities.

---

## Open Source Friendly

The project is intended to be community driven.

Every module should be:

- documented
- discoverable
- easy to contribute to

---

# 4. Architectural Principles

QA Sentinel AI follows several software engineering principles.

## Single Responsibility Principle (SRP)

Each module should have one responsibility.

Example:

Artifact Discovery

Responsible for locating files.

NOT responsible for parsing them.

---

Trace Parser

Responsible for reading trace.zip.

NOT responsible for AI reasoning.

---

Classifier

Responsible for determining failure categories.

NOT responsible for report generation.

---

## Separation of Concerns

Infrastructure code remains separated from business logic.

Examples:

Infrastructure

- Logging
- Configuration
- Storage

Business Logic

- Parsing
- Classification
- AI reasoning

---

## Dependency Direction

Higher-level modules should depend on abstractions rather than implementations whenever practical.

This improves flexibility and future extensibility.

---

# 5. High-Level Architecture

```
                    Playwright
                        │
                        ▼
              Artifact Discovery
                        │
                        ▼
                 Artifact Parser
                        │
                        ▼
                 Rule Engine
                        │
        ┌───────────────┴───────────────┐
        ▼                               ▼
  Rule-based Analysis             AI Analysis
        │                               │
        └───────────────┬───────────────┘
                        ▼
               Root Cause Engine
                        │
                        ▼
               Report Generator
                        │
                        ▼
             CLI / HTML / JSON / API
```

---

# 6. Data Flow

The application processes information in stages.

```
Automation Execution

↓

Artifacts Generated

↓

Artifact Discovery

↓

Artifact Parsing

↓

Feature Extraction

↓

Classification

↓

AI Reasoning

↓

Root Cause Report

↓

Output
```

Each stage performs a single responsibility.

---

# 7. Module Responsibilities

## CLI

Responsible for:

- accepting user commands
- validating arguments
- starting workflows

Should NOT contain business logic.

---

## Artifact Discovery

Responsible for:

- locating supported artifacts
- validating required files

Should NOT parse file contents.

---

## Parser

Responsible for extracting structured information from artifacts.

Examples:

- stack traces
- trace.zip
- screenshots
- network logs

Should NOT classify failures.

---

## Rule Engine

Responsible for deterministic failure analysis.

Example:

HTTP 500

↓

Backend Failure

---

## AI Engine

Responsible for:

- reasoning
- summarization
- confidence scoring
- recommendations

Should never read raw files directly.

---

## Report Generator

Responsible for producing output.

Supported formats may include:

- Markdown
- HTML
- JSON
- PDF

---

# 8. Technology Decisions

## Programming Language

Python

Reason:

- Excellent AI ecosystem
- Mature automation support
- Strong community
- Rapid development

---

## Automation Framework

Playwright (Phase 1)

Reason:

- Modern architecture
- Rich execution artifacts
- Cross-browser support
- Trace viewer

Future frameworks will be supported through plugins.

---

## Logging

Loguru

Reason:

- Simple API
- Structured logging
- File rotation
- Better developer experience

---

## AI

OpenAI API (initially)

Future support:

- Gemini
- Claude
- Ollama
- Azure OpenAI

---

## Storage

SQLite

Reason:

Simple local persistence.

Future:

PostgreSQL

---

# 9. Project Structure

```
src/

commands/

parser/

classifier/

reports/

storage/

models/

utils/
```

Each package owns a single domain.

---

# 10. Coding Standards

Every module should include:

- Module documentation
- Type hints
- Function docstrings
- Clear responsibilities
- Architecture notes
- Future enhancements

Business logic should never be placed inside:

- main.py
- configuration modules
- utility modules

---

# 11. Future Roadmap

Phase 1

- CLI
- Logging
- Artifact Discovery
- Parsing

Phase 2

- Rule Engine
- AI Analysis
- Root Cause Reports

Phase 3

- Dashboard
- Historical Analysis
- Similar Failure Detection

Phase 4

- Plugin System
- Multiple Automation Frameworks
- Cloud Deployment

---

# 12. Guiding Philosophy

QA Sentinel AI is designed as an engineering platform rather than a collection of scripts.

Every architectural decision should prioritize:

- readability
- simplicity
- extensibility
- maintainability
- testability

Features should be added only when they align with these principles.

The architecture should remain understandable by a new contributor within a short period of time.

```

---

# 📌 One suggestion

I'd like to introduce **Architecture Decision Records (ADRs)** from the very beginning.

Instead of putting every design decision into `ARCHITECTURE.md`, we'll keep that document stable and create a separate `docs/adr/` folder.

For example:

```text
docs/
├── architecture.md
├── developer-guide.md
├── contribution-guide.md
└── adr/
    ├── ADR-001-centralized-logging.md
    ├── ADR-002-plugin-architecture.md
    ├── ADR-003-artifact-discovery.md
    ├── ADR-004-rule-engine.md
    └── ADR-005-ai-engine.md
```

This is a common practice in mature engineering teams because it preserves the reasoning behind architectural choices. Months later, contributors can understand **why** a decision was made, not just **what** the code does. It also gives your repository a very professional structure that reviewers and contributors will appreciate.