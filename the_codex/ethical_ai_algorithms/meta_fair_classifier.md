# Meta Fair Classifier for Fairness Optimization

## Overview

The **Meta Fair Classifier** is a meta-algorithm that optimizes for a chosen fairness metric as part of its objective. This approach integrates fairness constraints directly into the learning process, allowing the classifier to be trained with specific fairness goals in mind. The algorithm currently supports **False Discovery Rate** (FDR) and **Statistical Rate** (SR) as fairness metrics and can be extended to incorporate other fairness metrics if required.

## License Information

This code is based on the meta-algorithm presented in the paper "[Classification with Fairness Constraints: A Meta-Algorithm with Provable Guarantees](https://arxiv.org/abs/1806.06055)." You can view the code and details in the original repository [here](https://github.com/vijaykeswani/FairClassification).

## Objective

The primary objectives of the **Meta Fair Classifier** are:

- **Fairness-Constrained Learning**: Train a classifier that meets specified fairness constraints based on a defined metric.
- **Customizable Fairness Metric**: Enable flexibility by supporting different fairness metrics, allowing the algorithm to adapt to specific fairness requirements.
- **Guaranteed Fairness**: Provide a provable guarantee that the trained model meets the specified fairness criteria.

## How Meta Fair Classifier Works

The algorithm optimizes a classifier with respect to the selected fairness metric (e.g., FDR, SR). It uses the metric as an input constraint during training, which ensures that the resulting classifier satisfies fairness requirements defined by the metric.

### Key Components and Classes

- **`MetaFairClassifier` Class**: Implements the Meta Fair Classifier with built-in fairness constraints.
  - **Attributes**:
    - `tau`: Fairness penalty parameter.
    - `sensitive_attr`: Defines the protected attribute for fairness considerations.
    - `type`: Type of fairness metric (FDR or SR).
    - `seed`: Ensures reproducibility by setting a random seed.
  - **Methods**:
    - `fit`: Trains the classifier with fairness constraints.
    - `predict`: Generates predictions with fairness-optimized labels.

---

## Code Example

The following code demonstrates how to use **Meta Fair Classifier** with the `MetaFairClassifier` class to train and evaluate a fairness-constrained classifier.

### Requirements

Install the AI Fairness 360 package:

```
pip install aif360
```

### Implementation

```
# Import necessary libraries
import numpy as np
from aif360.algorithms.inprocessing import MetaFairClassifier
from aif360.datasets import BinaryLabelDataset

# Define protected groups and fairness metric
privileged_groups = [{'sex': 1}]
unprivileged_groups = [{'sex': 0}]
fairness_metric_type = "fdr"  # Can be "fdr" (False Discovery Rate) or "sr" (Statistical Rate)

# Load your dataset (example using BinaryLabelDataset)
dataset = BinaryLabelDataset(...)

# Initialize Meta Fair Classifier with fairness metric type
meta_clf = MetaFairClassifier(tau=0.8, sensitive_attr='sex', type=fairness_metric_type, seed=42)

# Fit the model with fairness constraints
meta_clf.fit(dataset)

# Predict labels with the fair classifier
transformed_dataset = meta_clf.predict(dataset)
```

### Explanation of Code Example

- **Protected Groups and Metric Type**: Defines `privileged_groups`, `unprivileged_groups`, and sets the fairness metric (`fdr` or `sr`).
- **Fit and Predict**: The `fit` method trains the classifier with fairness constraints, and `predict` applies the trained classifier to generate fair predictions.

---

## Detailed Steps for Using Meta Fair Classifier

1. **Define Protected Groups and Metric Type**:  
   Specify protected attributes and select the fairness metric (False Discovery Rate or Statistical Rate).

2. **Initialize the Classifier**:  
   Configure the `MetaFairClassifier` with the chosen fairness metric and penalty parameter (`tau`), which controls the trade-off between fairness and accuracy.

3. **Train the Fair Classifier**:  
   Use the `fit` method to train the classifier, incorporating fairness constraints based on the chosen metric.

4. **Generate Fair Predictions**:  
   Apply the `predict` method to create fair predictions that meet the specified fairness constraints.

---

## Important Considerations

### Choice of Fairness Metric

The choice of fairness metric (`fdr` or `sr`) determines the fairness constraint that the classifier will optimize for during training. This flexibility allows users to target specific fairness outcomes as per application needs.

### Fairness Penalty (Tau)

The `tau` parameter controls the strength of the fairness penalty. A higher `tau` enforces stricter adherence to fairness but may impact model accuracy. Adjust `tau` based on the fairness-accuracy trade-off desired.

### Reproducibility

The `seed` parameter ensures that the fairness adjustments are consistent across runs, aiding in reproducibility.

---

## Example Application: UCI Adult Dataset

### Steps
1. **Load the Dataset**: Use a dataset such as the UCI Adult dataset, which includes sensitive attributes like `sex` and `race`.
2. **Apply Meta Fair Classifier**: Train and predict using the Meta Fair Classifier, configured for a specific fairness metric.
3. **Evaluate Bias Reduction**: Assess model performance and fairness using metrics like Statistical Parity Difference or Equal Opportunity.

Meta Fair Classifier is useful when specific fairness constraints need to be integrated into the classifier’s objective during training.

---

## Further Reading and Resources

For more information on **Meta Fair Classifier** and its theoretical foundation, refer to:

- **Original Research Paper**: Celis, L. E., et al. "Classification with Fairness Constraints: A Meta-Algorithm with Provable Guarantees." 2018.
- **AIF360 Documentation**: [IBM AIF360 GitHub](https://github.com/Trusted-AI/AIF360)

This guide provides an overview of using **Meta Fair Classifier** to enhance model fairness by integrating fairness constraints directly into the learning process.


<div align="center">

---

[![View MichaelAngel.io on GitHub](https://img.shields.io/badge/GitHub-View%20MichaelAngel.io-blue?logo=github)](https://github.com/M1ck4/MichaelAngel.io)

[![Ethical AI](https://img.shields.io/badge/Ethical%20AI-Priority-orange.svg)](https://github.com/M1ck4/MichaelAngel.io/blob/main/docs/the_codex/AI_Artisians_FAQ.md) 

---

![Creative Commons License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey?style=for-the-badge&logo=creative-commons&logoColor=white)
</div>
