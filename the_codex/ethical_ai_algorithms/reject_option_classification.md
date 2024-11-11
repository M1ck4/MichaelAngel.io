# Reject Option Classification for AI Fairness

## Overview

**Reject Option Classification (ROC)** is a postprocessing technique that adjusts predictions from a classifier to mitigate bias, especially in cases where there is high uncertainty near the decision boundary. It works by giving favorable outcomes to unprivileged groups and unfavorable outcomes to privileged groups within a band of uncertainty around the classification threshold. This approach is beneficial for reducing disparate impacts in model predictions. Implemented in IBM's **AI Fairness 360 (AIF360)** toolkit, this technique allows practitioners to create fairer models by modifying prediction outcomes without retraining the classifier.

## License Information

This code is released under the Apache License, Version 2.0. You can view the full license [here](http://www.apache.org/licenses/LICENSE-2.0).

## Objective

The main objectives of **Reject Option Classification** are:

- **Reducing Bias in Predictions**: Adjusting model predictions to reduce unfair treatment of unprivileged groups.
- **Postprocessing Fairness**: Applying fairness techniques to model outputs rather than modifying training data or model parameters.
- **Balancing Decision Uncertainty**: Focusing adjustments on cases with high uncertainty near the decision boundary.

## How Reject Option Classification Works

The **Reject Option Classification** technique focuses on predictions close to the decision threshold, where uncertainty is highest. For predictions within this uncertain range, favorable outcomes are assigned to unprivileged groups and unfavorable outcomes to privileged groups, thereby reducing bias in the model's final predictions. This approach allows for fairness adjustments without needing to retrain the classifier.

### Key Components and Classes

- **`RejectOptionClassification` Class**: This class implements the Reject Option Classification algorithm, adjusting predictions based on a fairness metric.
  - **Attributes**:
    - `unprivileged_groups` and `privileged_groups`: Defines the protected groups.
    - `low_class_thresh` and `high_class_thresh`: Thresholds defining the range of classification probabilities for the optimization search.
    - `metric_name`: Fairness metric used for optimization, such as "Statistical parity difference" or "Average odds difference".
    - `metric_lb` and `metric_ub`: Lower and upper bounds for the fairness metric.
  - **Methods**:
    - `fit`: Estimates the optimal classification threshold and margin based on the provided metric.
    - `predict`: Adjusts predictions for fairer outcomes using the ROC method.

---

## Code Example

The following code demonstrates how to apply **Reject Option Classification** using `RejectOptionClassification` on a dataset.

### Requirements

Install the AI Fairness 360 package:

```
pip install aif360
```

### Implementation

```
# Import necessary libraries
import numpy as np
from aif360.algorithms.postprocessing import RejectOptionClassification
from aif360.datasets import BinaryLabelDataset

# Define privileged and unprivileged groups
privileged_groups = [{'race': 1}]  # Privileged group definition
unprivileged_groups = [{'race': 0}]  # Unprivileged group definition

# Load your true labels and predicted scores datasets (example using BinaryLabelDataset)
dataset_true = BinaryLabelDataset(...)  # True label dataset
dataset_pred = BinaryLabelDataset(...)  # Predicted scores dataset

# Initialize RejectOptionClassification with parameters
roc_classifier = RejectOptionClassification(unprivileged_groups=unprivileged_groups,
                                            privileged_groups=privileged_groups,
                                            low_class_thresh=0.01,
                                            high_class_thresh=0.99,
                                            num_class_thresh=100,
                                            num_ROC_margin=50,
                                            metric_name="Statistical parity difference",
                                            metric_ub=0.05,
                                            metric_lb=-0.05)

# Fit the model to identify optimal threshold and margin
roc_classifier.fit(dataset_true, dataset_pred)

# Obtain fair predictions using the adjusted classification
transformed_dataset = roc_classifier.predict(dataset_pred)
```

### Explanation of Code Example

- **Privileged and Unprivileged Groups**: Define the protected attribute (e.g., "race") and specify privileged (e.g., `{'race': 1}`) and unprivileged groups (e.g., `{'race': 0}`).
- **Thresholds and Margins**: Define classification thresholds and ROC margins to specify the uncertainty band around the decision boundary.
- **Metric Name and Bounds**: Define the fairness metric (e.g., "Statistical parity difference") and set acceptable bounds for optimization.
- **Fit**: The `fit` method searches for optimal threshold and margin values to minimize unfair outcomes.
- **Predict**: The `predict` method applies these settings to make fairer predictions on new data.

---

## Detailed Steps for Using Reject Option Classification

1. **Define Privileged and Unprivileged Groups**:  
   Specify the attribute that separates privileged and unprivileged groups (e.g., "race", "gender").

2. **Set Thresholds and Margins**:  
   Define the low and high classification thresholds as well as the ROC margins to target predictions near the decision boundary.

3. **Select Fairness Metric**:  
   Choose a fairness metric, such as "Statistical parity difference", and define acceptable lower and upper bounds.

4. **Fit the Model**:  
   Use the `fit` method to estimate optimal threshold and margin values based on the fairness metric.

5. **Make Predictions**:  
   Use the `predict` method to obtain adjusted predictions that promote fairer outcomes for unprivileged groups.

6. **Evaluate Results**:  
   Measure fairness and accuracy metrics to confirm the effect of Reject Option Classification on prediction outcomes.

---

## Important Considerations

### Choosing the Fairness Metric

Selecting the right fairness metric is essential to achieve desired outcomes. ROC supports metrics like "Statistical parity difference", "Average odds difference", and "Equal opportunity difference". Ensure that the selected metric aligns with the fairness goals of your application.

### Thresholds and Margins

The classification thresholds and ROC margins define the range in which Reject Option Classification operates. Careful tuning of these parameters can help optimize the balance between fairness and predictive accuracy.

### Postprocessing Approach

As a postprocessing method, Reject Option Classification does not alter the model or training data but focuses on modifying the output predictions. This makes it versatile, as it can be applied to any model’s predictions.

---

## Example Application: UCI Adult Dataset

### Steps
1. **Load the Dataset**: Use the UCI Adult dataset or a similar dataset with protected attributes like race and gender.
2. **Apply Reject Option Classification**: Follow the code example to adjust predictions for fairer outcomes.
3. **Evaluate Fairness**: Assess metrics across protected groups to verify the reduction in bias.

Reject Option Classification is particularly effective when a clear decision boundary exists, as it focuses on predictions near this boundary to improve fairness.

---

## Further Reading and Resources

For more information on **Reject Option Classification** and its theoretical foundation, refer to:

- **Original Research Paper**: Kamiran, F., Karim, A., & Zhang, X. "Decision Theory for Discrimination-Aware Classification." IEEE International Conference on Data Mining, 2012.
- **AIF360 Documentation**: [IBM AIF360 GitHub](https://github.com/Trusted-AI/AIF360)

This document provides an overview of using **Reject Option Classification** to enhance fairness in model predictions, ensuring that sensitive attributes do not unjustly influence outcomes.


<div align="center">

---

[![View MichaelAngel.io on GitHub](https://img.shields.io/badge/GitHub-View%20MichaelAngel.io-blue?logo=github)](https://github.com/M1ck4/MichaelAngel.io)

[![Ethical AI](https://img.shields.io/badge/Ethical%20AI-Priority-orange.svg)](https://github.com/M1ck4/MichaelAngel.io/blob/main/docs/the_codex/AI_Artisians_FAQ.md) 

---

![Creative Commons License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey?style=for-the-badge&logo=creative-commons&logoColor=white)
</div>
