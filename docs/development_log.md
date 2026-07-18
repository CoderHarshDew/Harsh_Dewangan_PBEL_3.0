# Observion - Development Log

This document records the major milestones, research, challenges, and solutions encountered during the development of **Observion**, an AI-powered cyber threat detection framework built using the CICIDS2017 dataset.

The purpose of this log is to document the engineering process behind the project.

---

# 1. Dataset Selection and Verification

## Objective

Identify a reliable version of the CICIDS2017 dataset suitable for model training.

## Work Performed

Before any implementation began, multiple copies and mirrors of the CICIDS2017 dataset were researched and compared. The following aspects were verified:

- Dataset integrity
- File structure
- Attack labels
- Feature count
- Availability of original CSV files

This ensured that development started on a trustworthy dataset rather than a modified or incomplete version.

---

# 2. Incorrect Dataset Loading

## Problem

While loading the dataset, all files inside the dataset directory were listed. Non-CSV files were removed from the same list while iterating through it.

Because the list was being modified during iteration, several CSV files were skipped, resulting in incomplete dataset loading.

## Root Cause

Mutating a list while iterating over it.

## Solution

Instead of removing items from the original list, a new list containing only CSV files was created using list comprehension.

This completely resolved the loading issue.

---

# 3. PyCharm CSV Viewer Misleading Dataset Inspection

## Problem

While inspecting the dataset inside PyCharm, the built-in CSV viewer displayed only approximately 7,000 rows from each file.

Those visible rows happened to contain only **BENIGN** traffic.

This created the false impression that the dataset contained no attack records.

The dataset was downloaded again for verification, and changing to another dataset was seriously considered.

## Investigation

Printing the DataFrame shape revealed that every CSV still contained hundreds of thousands of rows.

The issue originated from the IDE's visualization limit rather than the dataset itself.

## Lesson Learned

IDE previews should never be treated as authoritative sources for dataset validation.

---

# 4. Initial Dataset Research

Before implementing preprocessing, extensive research was performed on every feature contained in the CICIDS2017 dataset.

The research included:

- Feature descriptions
- Data types
- Units of measurement
- Expected value ranges
- Network protocol semantics
- Relationships between features
- Attack labels
- Traffic statistics

Understanding the dataset beforehand significantly reduced mistakes during preprocessing and validation.

---

# 5. Research on Valid and Invalid Values

One of the earliest engineering tasks involved determining which values should be considered valid.

Research included:

- Negative values
- Infinite values
- Missing values
- NaN values
- Packet counters
- Timing features
- Header lengths
- Statistical features
- Flow-based measurements

This research formed the basis for all subsequent validation rules.

---

# 6. Designing a Configurable Validation Framework

Instead of embedding validation logic directly into Python code, preprocessing was designed around configuration files.

Three YAML files were introduced:

- **schema.yaml** – feature definitions and data types
- **rules.yaml** – validation rules
- **cleaning.yaml** – data cleaning configuration
- **pipeline.yaml** - preprocessing pipeline configuration

This made preprocessing modular, easier to maintain, and significantly easier to modify without changing application code.

---

# 7. Designing Practical Validation Rules

Determining realistic validation rules proved more difficult than expected.

Many online references contradicted each other regarding acceptable network statistics.

Several questions had to be answered during research:

- Which values are physically impossible?
- Which values are unusual but still legitimate?
- Which features should permit negative values?
- Which features must never contain negatives?

The resulting validation framework was based on practical network behavior rather than arbitrary thresholds.

---

# 8. Improving Flow Duration Validation

During development, inconsistencies were found in the original flow duration validation logic.

Further analysis showed that active flow time, idle flow time, and total flow duration must remain internally consistent.

The validation rules were revised accordingly to better reflect actual network flow behavior.

---

# 9. Investigating Packet Length Variance

Packet Length Variance initially appeared to contain impossible values.

Several records contained values reaching into the millions, greatly exceeding expected packet sizes.

After investigating the original CICIDS2017 dataset, it was confirmed that these large variance values genuinely exist within the dataset.

Rather than incorrectly rejecting valid samples, validation rules were updated to accommodate legitimate observations.

---

# 10. Identifying Low-Quality Features

Exploratory analysis revealed several columns that contained:

- Mostly missing values
- Little useful information
- Extremely sparse data

Each feature was evaluated individually before deciding whether it should remain part of preprocessing.

This prevented unnecessary removal of potentially useful information.

---

# 11. Handling Invalid Numerical Values

Several numerical anomalies were discovered during preprocessing.

These included:

- Infinite values
- Negative flow rates
- Negative durations
- Invalid header lengths
- Invalid timing statistics
- Impossible segment sizes

Each anomaly was investigated individually to determine whether it represented genuine network behavior, measurement artifacts, or corrupted records before defining the appropriate cleaning strategy.

---

# 12. Aggressive Data Cleaning

Early versions of the cleaning pipeline were intentionally strict.

Although this produced a very clean dataset, it also removed a significant amount of legitimate data.

Cleaning thresholds were gradually adjusted until an acceptable balance between data quality and dataset preservation was achieved.

---

# 13. Missing Attack Classes After Cleaning

Following aggressive preprocessing, several attack classes completely disappeared from the cleaned dataset.

Investigation revealed that the cleaning rules eliminated nearly every sample belonging to those rare attack categories.

This highlighted the importance of evaluating cleaning effects on every class individually rather than relying solely on overall dataset statistics.

---

# 14. Large Number of Validation Violations

One validation rule generated an unexpectedly large number of violations.

Rather than immediately assuming the dataset was corrupted, the following possibilities were investigated:

- Incorrect validation rule
- Unrealistic thresholds
- Legitimate characteristics of the dataset

This investigation helped refine the validation framework and avoid unnecessary data loss.

---

# 15. Visualizing Severe Class Imbalance

The CICIDS2017 dataset contains an extremely imbalanced class distribution.

Using a standard bar chart caused the **BENIGN** class to dominate the visualization, making minority attack classes nearly invisible.

## Solution

The visualization was redesigned using a logarithmic scale.

This allowed every attack class to be inspected while still preserving the true distribution of the dataset.

---

# 16. Correlation Analysis

Correlation analysis was performed to identify redundant features.

Several strongly correlated feature pairs were discovered, indicating that certain measurements conveyed nearly identical information.

This research provided valuable insight into the dataset structure and informed future feature engineering decisions.

---

# 17. Researching Feature Importance Techniques

Several feature importance methods were evaluated for future integration, including:

- Random Forest Feature Importance
- Permutation Importance
- SHAP

The initial implementation adopted Random Forest feature importance due to its simplicity, interpretability, and compatibility with the existing machine learning pipeline.

---

# 18. Evaluating Model Performance Beyond Accuracy

High accuracy alone was considered insufficient for evaluating an intrusion detection system.

Additional evaluation techniques were researched and incorporated into the development process, including:

- Confusion Matrix
- Precision
- Recall
- F1 Score

These metrics provided a more comprehensive understanding of model performance, particularly for minority attack classes where overall accuracy can be misleading.

---

# Summary

The first development phase of Observion focused primarily on understanding the CICIDS2017 dataset, designing a robust validation framework, implementing reliable preprocessing, and establishing a strong analytical foundation for subsequent machine learning and system development.

Many of the challenges encountered during this phase were not implementation bugs, but engineering decisions requiring careful investigation, experimentation, and validation before a reliable solution could be adopted.