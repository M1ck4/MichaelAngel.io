# Equalized Odds Postprocessing for AI Fairness

## Overview

**Equalized Odds Postprocessing** is a technique that modifies predicted labels to promote fairness after a classifier has made predictions. By using an optimization scheme, it aims to meet equalized odds by adjusting labels to ensure that the false positive and false negative rates are balanced across groups. Implemented within IBM’s **AI Fairness 360 (AIF360)** toolkit, this postprocessing method is effective when adjustments to classifier outputs are required to meet fairness criteria.

## License Information

This code is released under the MIT and Apache License, Version 2.0. You can view the full license [here](http://www.apache.org/licenses/LICENSE-2.0).

## Objective

The primary objectives of **Equalized Odds Postprocessing** are:

- **Fair Label Adjustment**: Alter predictions to meet equalized odds across protected groups.
- **Optimization of Prediction Fairness**: Use a linear programming approach to adjust labels, optimizing for fair outcomes.
- **Post-hoc Fairness Enhancement**: Adjust outputs without requiring classifier retraining, making it useful in settings where post-processing is preferred.

## How Equalized Odds Postprocessing Works

Equalized Odds Postprocessing adjusts predicted labels by solving a linear program that optimizes for equalized odds. This approach modifies the output labels probabilistically to meet specified fairness metrics, balancing the false positive and false negative rates across protected groups.

### Key Components and Classes

- **`EqOddsPostprocessing` Class**: Implements the Equalized Odds Postprocessing algorithm.
  - **Attributes**:
    - `unprivileged_groups` and `privileged_groups`: Defines the protected groups for fairness adjustments.
    - `seed`: Ensures reproducibility by setting a random seed.
  - **Methods**:
    - `fit`: Computes the optimal probabilities to adjust labels based on true and predicted datasets.
    - `predict`: Modifies labels probabilistically to meet fairness criteria.
    - `fit_predict`: Combines `fit` and `predict` for convenience.

---

## Code Example

The following code demonstrates how to apply **Equalized Odds Postprocessing** using `EqOddsPostprocessing` on a dataset.

### Requirements

Install the AI Fairness 360 package:

```
pip install aif360
```

### Implementation

```
# Import necessary libraries
import numpy as np
from aif360.algorithms.postprocessing import EqOddsPostprocessing
from aif360.datasets import BinaryLabelDataset

# Define protected groups
privileged_groups = [{'sex': 1}]
unprivileged_groups = [{'sex': 0}]

# Load your dataset (example using BinaryLabelDataset)
dataset_true = BinaryLabelDataset(...)
dataset_pred = BinaryLabelDataset(...)

# Initialize Equalized Odds Postprocessing
eop = EqOddsPostprocessing(unprivileged_groups=unprivileged_groups,
                           privileged_groups=privileged_groups,
                           seed=42)

# Fit the model to compute fairness parameters
eop.fit(dataset_true, dataset_pred)

# Adjust predictions for fairness
transformed_dataset = eop.predict(dataset_pred)
```

### Explanation of Code Example

- **Protected Groups**: Defines `unprivileged_groups` and `privileged_groups` based on sensitive attributes.
- **Fit and Predict**: The `fit` method computes fairness parameters, while `predict` applies adjustments for fairer outcomes.

---

## Detailed Steps for Using Equalized Odds Postprocessing

1. **Define Protected Groups**:  
   Specify protected attributes such as `sex`, `race`, etc., to target fairness adjustments for these groups.

2. **Fit the Model for Fairness**:  
   Use `fit` with the true and predicted datasets to compute the probabilities required to adjust labels for fair outcomes.

3. **Modify Predictions**:  
   Apply the `predict` method, which uses the computed probabilities to probabilistically adjust labels, meeting equalized odds.

4. **Evaluate Results**:  
   Compare fairness metrics, such as false positive and false negative rates across groups, to assess bias reduction.

---

## Important Considerations

### Fairness Constraints

Equalized Odds Postprocessing enforces fairness by balancing the false positive and false negative rates across groups. This is achieved by solving an optimization problem that probabilistically alters predictions to meet these constraints.

### Calibration

This technique is compatible with calibrated classifiers, as it adjusts labels post-hoc without affecting the calibration of the classifier's probabilities.

### Random Seed

The `seed` parameter controls randomness for reproducibility, ensuring consistent results when applying the fairness transformation.

---

## Example Application: UCI Adult Dataset

### Steps
1. **Load the Dataset**: Use a dataset like the UCI Adult dataset, which includes sensitive attributes (e.g., race, gender).
2. **Apply Equalized Odds Postprocessing**: Follow the code example to adjust predictions for fairness.
3. **Evaluate Bias Reduction**: Confirm that the false positive and false negative rates are balanced across sensitive groups.

Equalized Odds Postprocessing is particularly beneficial when classifier retraining is not feasible and fairness must be introduced in a post-hoc manner.

---

## Further Reading and Resources

For more information on **Equalized Odds Postprocessing** and its theoretical foundation, refer to:

- **Original Research Papers**:
  - Hardt, M., Price, E., & Srebro, N. "Equality of Opportunity in Supervised Learning." Conference on Neural Information Processing Systems, 2016.
  - Pleiss, G., et al. "On Fairness and Calibration." Conference on Neural Information Processing Systems, 2017.
- **AIF360 Documentation**: [IBM AIF360 GitHub](https://github.com/Trusted-AI/AIF360)

This guide provides an overview of using **Equalized Odds Postprocessing** to enhance prediction fairness in machine learning applications.


<div align="center">

---

[![View MichaelAngel.io on GitHub](https://img.shields.io/badge/GitHub-View%20MichaelAngel.io-blue?logo=github)](https://github.com/M1ck4/MichaelAngel.io)

[![Ethical AI](https://img.shields.io/badge/Ethical%20AI-Priority-orange.svg)](https://github.com/M1ck4/MichaelAngel.io/blob/main/docs/the_codex/AI_Artisians_FAQ.md) 

---

![Creative Commons License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey?style=for-the-badge&logo=creative-commons&logoColor=white)
</div>
