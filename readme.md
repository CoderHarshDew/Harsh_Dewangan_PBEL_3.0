# Observion - Watching Continuously

This project was made in response to IBM PBEL 3.0's AI Batch 2's project topic: _AI-Based Cyber Threat Detection Framework_

---

## Table of contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Repository structure](#repository-structure)
- [Features](#features)
- [Current Limitations](#current-limitation)
- [Development Progress](#development-progress)
- [Planned](#planned)
- [Dataset](#dataset)
- [FAQs](#faqs)
- [Contribution Policy](#contribution-policy)

---

## Overview

Observion is an AI-powered cyber threat detection and network observability platform designed to identify malicious network activity through machine learning.

---

## Getting Started

### Clone this repository

```bash
git clone https://github.com/CoderHarshDew/Harsh_Dewangan_PBEL_3.0.git
```

### Download Dataset

1. Go to [dataset website.](https://www.kaggle.com/datasets/chethuhn/network-intrusion-dataset)
2. Download the dataset.
3. Place the dataset files in your desired directory.

### Download prerequisites

```bash
pip install -r requirements.txt
```

### Train model

From the root folder of the repository, run the following command:

```bash
python app.py train dataset_path
```

replace dataset_path with the path to the directory where you placed the dataset files.

### Make predictions

From the root folder of the repository, run the following command:

```bash
python app.py predict input_folder_path
```

replace input_folder_path with the path to the directory where your input files are located.

---

## Repository Structure

```text
Observion/
├── config/
│   ├── ml/
│   │   └── rf_hyperparameters.yaml
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

## Features

* Detailed Validation Reports.
* Detailed prediction summary.
* Almost perfect accuracy on 10 labels.
* CLI based interaction.
* YAML based configuration.
* Highly modular code that should support future development.
* Can process all acceptable files of a directory.
* Thorough preprocessing.

---

## Current limitation

Some of these are intentional (marked with *):

* No UI or Frontend. *
* Only supports CSV files.
* Random Forest is the only model right now.
* Prediction of 5 classes is relevantly weak.
  * Some of these are due to high class imbalance in the original dataset.
  * Some are due to high semantic similarity between classes.

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

4. Application Development:
   - [x] Complete pipeline creation.
   - [x] CLI implementation.

---

## Planned

ContainerLab integration is part of the long-term roadmap and is not yet implemented. Current model development, feature engineering, and evaluation are performed using the CICIDS2017 dataset. Future releases aim to introduce automated network simulation, telemetry collection, and synthetic dataset generation through ContainerLab.

---

## Dataset

This project uses the [CICIDS2017](https://www.kaggle.com/datasets/chethuhn/network-intrusion-dataset) dataset.

---

## FAQs

Que: Why is there no frontend?

Ans: A frontend is not included in the current version because the model requires a large set of flow features as input, making manual data entry impractical. At this stage, predictions are performed through the CLI using prepared datasets. A frontend will be introduced alongside the network simulation, where flow data can be ingested automatically and the interface can display real-time predictions, alerts, and analysis without requiring manual input.

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
