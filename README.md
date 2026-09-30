# FT3: Fraud Tools, Tactics, and Techniques Framework

## Overview

Fraud Tools, Tactics, and Techniques (FT3) is Stripe's adaptation of ATT&CK-style security frameworks, specifically designed to enhance our understanding of the tactics, techniques, and procedures (TTPs) used by actors in fraudulent activities. Developed as a resource for combating financial crime and improving organizational fraud prevention, FT3 serves a variety of stakeholders across the Fraud ecosystem.

## Why FT3?

Fraud is an ever-evolving threat that necessitates a structured approach for organizations to adapt and respond effectively. By documenting the common tactics and techniques used by fraudsters, FT3 helps organizations to:

- **Understand the Fraud Landscape:** Gain insights into the tactics and techniques that fraudsters leverage.
- **Identify Security Gaps:** Discover shortcomings in current security measures to enhance defenses.
- **Develop Detection Mechanisms:** Establish precise detection capabilities tailored to counter current fraud tactics.
- **Improve Incident Response:** Enhance processes for responding to fraud incidents efficiently.
- **Foster Collaboration:** Share knowledge and insights within the fraud prevention community to strengthen collective defenses.

## Components of FT3

### 1. **Tactics**
High-level categories representing various phases or goals within the fraud lifecycle. Each tactic delineates specific objectives pursued by fraudsters.

**Example:** 
- **Initial Access:** Gaining unauthorized access to user accounts to execute fraudulent transactions.

### 2. **Techniques**
Methods or modes of operation fraudsters use to achieve their objectives under each tactic. Techniques can vary in complexity and sophistication.

**Example:** 
- **Account Takeover:** Using stolen credentials to gain control over a user's account for malicious purposes, such as transferring funds or making unauthorized purchases.

### 3. **Procedures**
Specific implementations of techniques that detail the exact methods actors use within the context of fraud, often involving unique tools and sequences of actions.

**Example:**
- **Phishing Scheme:** Crafting a fake email that appears legit to trick users into providing their login information.

### 4. **Indicators of Compromise (IOCs)**
Details that suggest fraudulent activity, such as unusual transaction patterns or changes in account behavior.

**Example:**
- **Unusual Purchase Locations:** Transactions occurring in locations that do not match the user's typical behavior, indicating potential fraud.

### 5. **Mitigations**
Proactive actions organizations can adopt to decrease the risk or impact of fraud.

**Example:**
- **Two-Factor Authentication (2FA):** Implementing extra security layers that require a second form of verification to access accounts.

### 6. **Detection**
Mechanisms for identifying potential fraud through analysis of transaction patterns and customer behaviors.

**Example:**
- **Anomaly Detection Algorithms:** Using machine learning models to identify deviations from normal purchasing behavior.

### 7. **Response**
Predefined procedures for organizational response to detected fraud events, aimed at minimizing impact and facilitating recovery.

**Example:**
- **Fraud Investigation Protocol:** Steps for initiating a fraud investigation when suspicious transactions are flagged.

This enhanced context focuses on the specific tactics, techniques, and procedures related to fraud, making it more applicable to your goals.

## Catalog date formats

The `created` and `last_modified` fields in the JSON catalogs use slash-separated calendar dates in month/day/year order. They are not ISO 8601 timestamps and contain no time or timezone. The corresponding CSV catalogs use the same date conventions as their JSON counterparts.

| Catalog | Format | Example |
| --- | --- | --- |
| [Techniques](FT3_Techniques.json) | `M/D/YY` (month and day without leading zeroes; two-digit year) | `1/30/24` = January 30, 2024 |
| [Tactics](FT3_Tactics.json) | `MM/DD/YYYY` (zero-padded month and day; four-digit year) | `01/30/2024` = January 30, 2024 |

For the currently published technique records, interpret the two-digit year in the 2000s: for example, `24` denotes 2024. This describes the current data, not a permanent century-pivot rule for future records.

## Contributing

We welcome contributions to the FT3 framework from the community! Here are some ways you can help:

Please see the [CONTRIBUTING](CONTRIBUTING.md) file for further details.

## Security
Please see the [SECURITY](SECURITY.md) file for further details.

## Code of Conduct
Please see the [CODE_OF_CONDUCT](CODE_OF_CONDUCT.md), file for further details.

## Contact Information

For further inquiries about the FT3 framework, please reach out to intel [at] stripe.com

## Notice
Please see the [LICENSE](LICENSE.md), [CODE_OF_CONDUCT](CODE_OF_CONDUCT.md), [CONTRIBUTING](CONTRIBUTING.md), and [SECURITY](SECURITY.md) files for further details.

Copyright © 2024-2025 Stripe Inc. All rights reserved.

## Persistent technique UUIDs

Each technique and sub-technique has a bare `uuid` identifying the continuing concept. JSON is authoritative for these assignments; the technique CSV copies the same values. The `id` field remains the human-readable FT code. `stix_id` remains reserved for a separate STIX object model and is not populated by this change.

Initial first-party assignments use UUIDv4, minted once and committed. Never regenerate UUIDs when titles, descriptions, tactic placement, codes, or row order change. Retain the UUID when the concept continues, and review any code correction explicitly. Do not merge concepts merely because their names match. New concepts receive new UUIDs; retired UUIDs must never be reused. Before a material replacement, merge, split, or deletion, record the predecessor UUIDs, dispositions, and any successors in a retained lifecycle record.

The immutable [initial assignments](docs/review/stripe-ft3/uuid-initial-assignments.json) record the reviewed input revision and record fingerprints. The historical FT053 collision is already corrected: FT053 is Card Holder Details Collection, while FT056 is 3DS Bypass; they receive different UUIDs.

A MISP converter can use the technique UUID as `values[].uuid`, retaining any independently established downstream mapping explicitly. No Stripe FT3 assignment mapping was found in the inspected official MISP Galaxy tree or public search; that does not establish absence of private or independent mappings. The included fixture demonstrates schema compatibility, not a production converter, rename-safe imports, or preservation of existing MISP attachments. No live MISP import was tested.
