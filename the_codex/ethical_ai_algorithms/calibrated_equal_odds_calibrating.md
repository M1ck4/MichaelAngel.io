# Calibrated Equalized Odds Postprocessing for AI Fairness

## Overview

**Calibrated Equalized Odds Postprocessing** is a bias-mitigation technique that modifies predictions after model training to ensure fairness across groups. It adjusts classifier score outputs by finding optimal probabilities to alter predictions, aiming to meet equalized odds objectives while maintaining calibration. Implemented in IBM’s **AI Fairness 360 (AIF360)** toolkit, this method is useful for cases where post-hoc adjustments to model outputs can promote fairer outcomes.

## License Information

This code is released under the Apache License, Version 2.0. You can view the full license [here](http://www.apache.org/licenses/LICENSE-2.0).

## Objective

The primary objectives of **Calibrated Equalized Odds Postprocessing** are:

- **Bias Mitigation in Predictions**: Adjusting predictions to be fairer across groups after model training.
- **Optimized Postprocessing**: Modifying classifier outputs to satisfy equalized odds without requiring retraining.
- **Calibrated Fairness**: Ensuring fair predictions while preserving the calibrated probability scores.

## How Calibrated Equalized Odds Works

**Calibrated Equalized Odds** operates on calibrated classifier outputs, modifying predictions probabilistically to achieve fairness objectives. It balances false positive and false negative rates across groups based on constraints (e.g., false positive rate, false negative rate, or weighted combination). By controlling these probabilities, the algorithm adjusts outcomes to meet equalized odds.

### Key Components and Classes

- **`CalibratedEqOddsPostprocessing` Class**: Implements the Calibrated Equalized Odds algorithm.
  - **Attributes**:
    - `unprivileged_groups` and `privileged_groups`: Specifies protected groups for fairness.
    - `cost_constraint`: Defines whether to balance false positive rates, false negative rates, or both.
    - `seed`: Controls randomness for reproducibility.
  - **Methods**:
    - `fit`: Calculates adjustment parameters based on the desired fairness constraints.
    - `predict`: Adjusts predicted scores to generate fairer outcomes.
    - `fit_predict`: Combines `fit` and `predict` to sequentially apply the adjustments.

---

## Code Example

The following code demonstrates how to apply **Calibrated Equalized Odds** using `CalibratedEqOddsPostprocessing` on a dataset.

### Requirements

Install the AI Fairness 360 package:

```
pip install aif360
```

### Implementation

```
# Import necessary libraries
import numpy as np
from aif360.algorithms.postprocessing import CalibratedEqOddsPostprocessing
from aif360.datasets import BinaryLabelDataset

# Define protected groups
privileged_groups = [{'race': 1}]
unprivileged_groups = [{'race': 0}]

# Load your dataset (example using BinaryLabelDataset)
dataset_true = BinaryLabelDataset(...)
dataset_pred = BinaryLabelDataset(...)

# Initialize CalibratedEqOddsPostprocessing
ceop = CalibratedEqOddsPostprocessing(unprivileged_groups=unprivileged_groups,
                                      privileged_groups=privileged_groups,
                                      cost_constraint='weighted',  # Balancing both FPR and FNR
                                      seed=42)

# Fit the model to calculate fair parameters
ceop.fit(dataset_true, dataset_pred)

# Adjust predictions for fairness
transformed_dataset = ceop.predict(dataset_pred)
```

### Explanation of Code Example

- **Protected Groups**: `unprivileged_groups` and `privileged_groups` specify sensitive attributes for fairness adjustments.
- **Cost Constraint**: Defines whether to optimize for false positive rate (`fpr`), false negative rate (`fnr`), or both (`weighted`).
- **Fit and Predict**: The `fit` method computes fair parameters, while `predict` applies them to generate adjusted predictions.

---

## Detailed Steps for Using Calibrated Equalized Odds

1. **Define Protected Groups and Constraints**:  
   Specify the protected attributes and set `cost_constraint` based on the fairness criteria (e.g., `fpr`, `fnr`, or `weighted`).

2. **Fit the Postprocessing Model**:  
   Use the `fit` method with true and predicted datasets to calculate fair probabilities for label adjustment.

3. **Adjust Predictions**:  
   Apply the `predict` method to alter predictions, creating fairer outcomes across sensitive groups.

4. **Evaluate Results**:  
   Measure fairness metrics (e.g., equalized odds) and accuracy to assess the impact of Calibrated Equalized Odds on prediction fairness.

---

## Important Considerations

### Balancing False Positive and Negative Rates

The `cost_constraint` parameter controls the trade-off between false positive and false negative rates. Use `fpr` to focus on false positives, `fnr` for false negatives, or `weighted` to balance both.

### Calibration and Fairness

Calibrated Equalized Odds optimizes fairness while preserving calibration, maintaining the probability distribution for fair outcomes across groups.

### Randomness Control

The `seed` parameter ensures consistent results by setting a random seed. This is beneficial for reproducibility, especially when tuning fairness adjustments.

---

## Example Application: UCI Adult Dataset

### Steps
1. **Load the Dataset**: Use the UCI Adult dataset, which includes sensitive attributes (e.g., race, gender).
2. **Apply Calibrated Equalized Odds**: Follow the code example to adjust predictions for fairness.
3. **Evaluate Bias Reduction**: Assess metrics to confirm the balance between groups and minimal bias in outcomes.

Calibrated Equalized Odds is particularly effective when post-hoc adjustments are needed to make fair predictions across groups.

---

## Further Reading and Resources

For more information on **Calibrated Equalized Odds** and its theoretical foundation, refer to:

- **Original Research Paper**: Pleiss, G., et al. "On Fairness and Calibration." Conference on Neural Information Processing Systems, 2017.
- **AIF360 Documentation**: [IBM AIF360 GitHub](https://github.com/Trusted-AI/AIF360)

This guide provides an overview of using **Calibrated Equalized Odds** to optimize predictions for fair outcomes across sensitive groups.

<div align="center">

---

[![View MichaelAngel.io on GitHub](https://img.shields.io/badge/GitHub-View%20MichaelAngel.io-blue?logo=github)](https://github.com/M1ck4/MichaelAngel.io)

[![Ethical AI](https://img.shields.io/badge/Ethical%20AI-Priority-orange.svg)](https://github.com/M1ck4/MichaelAngel.io/blob/main/docs/the_codex/AI_Artisians_FAQ.md) 

---

![Creative Commons License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey?style=for-the-badge&logo=creative-commons&logoColor=white)
</div>
