# Observion - Watching Continuously

This project was made in response to IBM PBEL 3.0's AI Batch 2's project topic: _AI-Based Cyber Threat Detection Framework_

---

## Table of contents

- [Overview](#overview)
- [Repository structure](#repository-structure)
- [Development Progress](#development-progress)
- [Planned](#planned)
- [Dataset](#dataset)
- [Contribution Policy](#contribution-policy)

---

## Overview

Observion is an AI-powered cyber threat detection and network observability platform designed to identify malicious network activity through machine learning.

---

## Repository Structure

```text
Observion/
├── config/
│   └── validation/
│       ├── cleaning.yaml
│       ├── validation_rules.yaml
│       └── validation_schema.yaml
├── notebooks/
├── src/
│   ├── core/
│   ├── dataset/
│   ├── ml/
│   └── preprocessing/
├── .gitignore
├── app.py
├── LICENSE
├── readme.md
└── requirements.txt
```

---

## Development Progress

1. Exploratory Data Analysis:
   - [x] Dataset inspection.
   - [x] Dataset validation.
   - [x] Dataset cleaning.

2. Feature Engineering:
   - [x] Feature importance analysis.
   - [x] Creating new features.

3. Model Development:
   - [x] Model Selection.
   - [x] Model Training.
   - [x] Model Evaluation.

---

## Planned

ContainerLab integration is part of the long-term roadmap and is not yet implemented. Current model development, feature engineering, and evaluation are performed using the CICIDS2017 dataset. Future releases aim to introduce automated network simulation, telemetry collection, and synthetic dataset generation through ContainerLab.

---

## Dataset

This project uses the [CICIDS2017](https://www.kaggle.com/datasets/chethuhn/network-intrusion-dataset) dataset.

---

## Contribution Policy

Thank you for your interest in Observion.

This repository is intentionally maintained as a solo development project.
External code contributions and pull requests are not being accepted.

Feel free to:
- Explore the code
- Clone the repository
- Open issues for questions or discussion

Development decisions and implementation remain solely under the author's direction.
