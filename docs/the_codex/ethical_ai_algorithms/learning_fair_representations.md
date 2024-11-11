# Learning Fair Representations for AI Fairness

## Overview

**Learning Fair Representations (LFR)** is a preprocessing technique that mitigates bias in training data by finding a latent representation of the data that obfuscates information about protected attributes while preserving predictive accuracy. This approach encodes data into a fairer format, allowing models to make predictions without reliance on sensitive attributes (e.g., race, gender). Implemented in IBM's **AI Fairness 360 (AIF360)** toolkit, LFR is beneficial for applications requiring bias mitigation before model training.

## License Information

This code is released under the Apache License, Version 2.0. You can view the full license [here](http://www.apache.org/licenses/LICENSE-2.0).

## Objective

The primary objectives of **Learning Fair Representations** are:

- **Removing Bias from Training Data**: Obfuscating sensitive attributes while maintaining data utility.
- **Latent Fair Representations**: Transforming data to represent sensitive and non-sensitive groups fairly.
- **Flexible Control over Fairness**: Providing weights to control the trade-off between fairness and predictive performance.

## How Learning Fair Representations Works

The **Learning Fair Representations** technique learns a latent representation of data that conceals protected attributes by utilizing prototypes and weights to encode group fairness. It applies fairness constraints and error minimization objectives, balancing the effects of fairness (removing protected attribute influence) and predictive accuracy. By obfuscating sensitive information, LFR allows models to learn unbiased patterns in the data.

### Key Components and Classes

- **`LFR` Class**: This class implements the Learning Fair Representations algorithm.
  - **Attributes**:
    - `unprivileged_groups` and `privileged_groups`: Specifies protected groups.
    - `k`: Number of prototypes representing the data.
    - `Ax`, `Ay`, and `Az`: Weights for input reconstruction quality, output prediction error, and fairness constraints.
    - `print_interval` and `verbose`: Controls output frequency for monitoring progress.
  - **Methods**:
    - `fit`: Learns the transformation parameters to create fair representations.
    - `transform`: Transforms the dataset using learned parameters.
    - `fit_transform`: Applies both `fit` and `transform` sequentially.

---

## Code Example

The following code demonstrates how to apply **Learning Fair Representations** using `LFR` on a dataset.

### Requirements

Install the AI Fairness 360 package:

```
pip install aif360
```

### Implementation

```
# Import necessary libraries
import numpy as np
from aif360.algorithms.preprocessing import LFR
from aif360.datasets import BinaryLabelDataset

# Define privileged and unprivileged groups
privileged_groups = [{'race': 1}]  # Privileged group definition
unprivileged_groups = [{'race': 0}]  # Unprivileged group definition

# Load your dataset (example using BinaryLabelDataset)
dataset = BinaryLabelDataset(...)

# Initialize LFR with parameters for bias mitigation
lfr = LFR(unprivileged_groups=unprivileged_groups,
          privileged_groups=privileged_groups,
          k=5,  # Number of prototypes
          Ax=0.01,  # Input reconstruction quality term
          Ay=1.0,  # Output prediction error weight
          Az=50.0,  # Fairness constraint term weight
          print_interval=250,  # Print frequency
          seed=42)

# Fit the model to learn fair representations
lfr.fit(dataset)

# Transform the dataset to fairer representations
transformed_dataset = lfr.transform(dataset)
```

### Explanation of Code Example

- **Privileged and Unprivileged Groups**: Define the protected attribute (e.g., "race") and specify privileged (e.g., `{'race': 1}`) and unprivileged groups (e.g., `{'race': 0}`).
- **Prototypes (k)**: Number of data points that serve as prototypes representing groups.
- **Fairness and Reconstruction Weights (Ax, Ay, Az)**: Control the trade-off between predictive accuracy and fairness constraints.
- **Fit and Transform**: `fit` learns fair representations, while `transform` applies these transformations to generate a fairer dataset.

---

## Detailed Steps for Using Learning Fair Representations

1. **Define Privileged and Unprivileged Groups**:  
   Specify the attribute that distinguishes privileged and unprivileged groups (e.g., "race", "gender").

2. **Set Fairness Weights and Prototypes**:  
   Define `Ax`, `Ay`, and `Az` weights to control the importance of accuracy vs. fairness. Set the number of prototypes `k` as needed.

3. **Fit and Transform Dataset**:  
   Use the `fit` and `transform` methods to learn and apply fair representations.

4. **Evaluate Results**:  
   Measure fairness and accuracy metrics to assess the effect of Learning Fair Representations on the transformed data.

---

## Important Considerations

### Balancing Fairness and Accuracy

Weights `Ax`, `Ay`, and `Az` allow control over the trade-off between predictive accuracy and fairness. Adjust these values based on the desired level of fairness without sacrificing too much predictive power.

### Number of Prototypes

The `k` parameter defines the number of prototypes used to represent data groups. Setting `k` too low may oversimplify group representation, while a high `k` could add unnecessary complexity.

### Seed for Consistency

Set the `seed` parameter to ensure reproducibility of results. This is particularly helpful for ensuring consistency across different training runs.

---

## Example Application: UCI Adult Dataset

### Steps
1. **Load the Dataset**: Use the UCI Adult dataset or a similar dataset with protected attributes like race and gender.
2. **Apply Learning Fair Representations**: Follow the code example to create fair representations.
3. **Evaluate Fairness**: Assess metrics across protected groups to verify the reduction in bias.

Learning Fair Representations is particularly effective for datasets with known biases, as it allows the model to learn representations without inheriting protected attribute influence.

---

## Further Reading and Resources

For more information on **Learning Fair Representations** and its theoretical foundation, refer to:

- **Original Research Paper**: Zemel, R., et al. "Learning Fair Representations." International Conference on Machine Learning, 2013.
- **AIF360 Documentation**: [IBM AIF360 GitHub](https://github.com/Trusted-AI/AIF360)

This guide provides an overview of using **Learning Fair Representations** to enhance fairness in training data, ensuring that models learn patterns without reliance on sensitive attributes.

<div align="center">

---

[![View MichaelAngel.io on GitHub](https://img.shields.io/badge/GitHub-View%20MichaelAngel.io-blue?logo=github)](https://github.com/M1ck4/MichaelAngel.io)

[![Ethical AI](https://img.shields.io/badge/Ethical%20AI-Priority-orange.svg)](https://github.com/M1ck4/MichaelAngel.io/blob/main/docs/the_codex/AI_Artisians_FAQ.md) 

---

![Creative Commons License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey?style=for-the-badge&logo=creative-commons&logoColor=white)
</div>
