# Prejudice Remover for AI Fairness

## Overview

**Prejudice Remover** is an in-processing technique that adds a discrimination-aware regularization term to the learning objective of a classifier, aiming to reduce bias against protected groups during model training. By introducing a fairness penalty term, it minimizes the influence of sensitive attributes in the learning process, helping the model achieve fairer predictions. Implemented in IBM's **AI Fairness 360 (AIF360)** toolkit, Prejudice Remover is effective for scenarios requiring a fair classification model.

## License Information

This code is released under the Apache License, Version 2.0. You can view the full license [here](http://www.apache.org/licenses/LICENSE-2.0).

## Objective

The primary objectives of **Prejudice Remover** are:

- **Bias Mitigation During Training**: Reducing discrimination by incorporating fairness directly into the training process.
- **Regularization with Fairness Constraints**: Adjusting model predictions to be less reliant on sensitive attributes.
- **In-Processing Fairness Approach**: Applying fairness adjustments within the model itself rather than modifying the data or postprocessing predictions.

## How Prejudice Remover Works

The **Prejudice Remover** algorithm introduces a regularization term to the learning objective, penalizing the model when sensitive attributes influence predictions. By adjusting this fairness penalty term, users can control the trade-off between predictive accuracy and fairness, making it a flexible approach for mitigating bias directly within the model’s learning process.

### Key Components and Classes

- **`PrejudiceRemover` Class**: This class implements the Prejudice Remover algorithm.
  - **Attributes**:
    - `eta`: Controls the fairness penalty term. Higher values place more emphasis on fairness.
    - `sensitive_attr`: Specifies the protected attribute to consider during regularization.
    - `class_attr`: Defines the label attribute for the model.
  - **Methods**:
    - `fit`: Trains the model using regularized logistic regression to minimize prejudice.
    - `predict`: Makes predictions on new data using the prejudice-removal model.

---

## Code Example

The following code demonstrates how to apply **Prejudice Remover** using `PrejudiceRemover` on a dataset.

### Requirements

Install the AI Fairness 360 package:

```
pip install aif360
```

### Implementation

```
# Import necessary libraries
import numpy as np
from aif360.algorithms.inprocessing import PrejudiceRemover
from aif360.datasets import BinaryLabelDataset

# Define model parameters
eta = 0.5  # Fairness penalty parameter (0 for no fairness constraint)
sensitive_attr = 'race'  # Define the protected attribute
class_attr = 'income'  # Define the label attribute

# Load your dataset (example using BinaryLabelDataset)
dataset = BinaryLabelDataset(...)

# Initialize PrejudiceRemover with specified parameters
pr_model = PrejudiceRemover(eta=eta, sensitive_attr=sensitive_attr, class_attr=class_attr)

# Train the model to learn fair representations
pr_model.fit(dataset)

# Obtain predictions using the learned prejudice remover model
transformed_dataset = pr_model.predict(dataset)
```

### Explanation of Code Example

- **Fairness Penalty (eta)**: Controls the balance between fairness and accuracy. Higher values increase the influence of fairness constraints.
- **Protected and Label Attributes**: `sensitive_attr` and `class_attr` specify the features representing protected attributes and labels.
- **Fit and Predict**: `fit` trains the model with a fairness-aware objective, while `predict` applies the learned model to generate fairer predictions.

---

## Detailed Steps for Using Prejudice Remover

1. **Set Fairness Penalty and Attributes**:  
   Define the `eta` value to control the influence of fairness and specify the sensitive and label attributes.

2. **Train the Model**:  
   Use the `fit` method to train the model with a regularization term that penalizes discrimination.

3. **Make Predictions**:  
   Apply the `predict` method to generate bias-mitigated predictions on new data.

4. **Evaluate Results**:  
   Measure fairness and accuracy metrics to assess the impact of Prejudice Remover on prediction outcomes.

---

## Important Considerations

### Balancing Fairness and Accuracy

The `eta` parameter controls the fairness penalty. A higher value increases the emphasis on fairness, potentially reducing accuracy. Finding an optimal balance is crucial to avoid over-penalizing predictive performance.

### In-Processing Fairness

As an in-processing method, Prejudice Remover incorporates fairness adjustments directly into the model, making it effective when retraining is feasible and a model with built-in fairness is desired.

### Data Formatting Requirements

The Prejudice Remover algorithm uses a specialized data format. Users should ensure that the protected attribute appears before the target class in the dataset. Missing values should be handled before training.

---

## Example Application: UCI Adult Dataset

### Steps
1. **Load the Dataset**: Use the UCI Adult dataset or a similar dataset with protected attributes (e.g., race, gender).
2. **Apply Prejudice Remover**: Follow the code example to train the model with fairness constraints.
3. **Evaluate Fairness**: Assess fairness and accuracy metrics to confirm reduced bias.

Prejudice Remover is particularly effective for training classifiers where discrimination-aware regularization can directly influence model outcomes.

---

## Further Reading and Resources

For more information on **Prejudice Remover** and its theoretical foundation, refer to:

- **Original Research Paper**: Kamishima, T., et al. "Fairness-Aware Classifier with Prejudice Remover Regularizer." Joint European Conference on Machine Learning and Knowledge Discovery in Databases, 2012.
- **AIF360 Documentation**: [IBM AIF360 GitHub](https://github.com/Trusted-AI/AIF360)

This guide provides an overview of using **Prejudice Remover** to embed fairness into the learning process, ensuring sensitive attributes do not unduly influence model predictions.


<div align="center">

---

[![View MichaelAngel.io on GitHub](https://img.shields.io/badge/GitHub-View%20MichaelAngel.io-blue?logo=github)](https://github.com/M1ck4/MichaelAngel.io)

[![Ethical AI](https://img.shields.io/badge/Ethical%20AI-Priority-orange.svg)](https://github.com/M1ck4/MichaelAngel.io/blob/main/docs/the_codex/AI_Artisians_FAQ.md) 

---

![Creative Commons License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey?style=for-the-badge&logo=creative-commons&logoColor=white)
</div>
