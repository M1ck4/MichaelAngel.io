# Disparate Impact Remover for AI Fairness

## Overview

**Disparate Impact Remover** is a preprocessing technique designed to improve group fairness by editing feature values in the dataset. This approach adjusts the feature distributions to reduce disparate impact while preserving the rank-ordering within each group, making it particularly useful in scenarios where bias mitigation is required in training data. Implemented in IBM's **AI Fairness 360 (AIF360)** toolkit, Disparate Impact Remover provides a way to ensure that sensitive attributes do not unfairly influence model outcomes.

## License Information

This code is released under the Apache License, Version 2.0. You can view the full license [here](http://www.apache.org/licenses/LICENSE-2.0).

## Objective

The primary goals of the **Disparate Impact Remover** are:

- **Group Fairness**: Editing feature values to balance distributions across protected groups.
- **Maintaining Rank-Order**: Preserving the relative ranking within groups to maintain data integrity.
- **Bias Mitigation in Training Data**: Adjusting features before model training to reduce the impact of sensitive attributes.

## How Disparate Impact Remover Works

The **Disparate Impact Remover** modifies feature values for specific groups, making their distributions more similar across protected attributes. By adjusting the features based on a specified "repair level," it reduces group disparities while preserving rank order within each group. This technique is particularly beneficial when the goal is to ensure fair representation of all groups in model training without impacting model parameters directly.

### Key Components and Classes

- **`DisparateImpactRemover` Class**: This class implements the Disparate Impact Remover algorithm.
  - **Attributes**:
    - `repair_level`: Degree of repair applied to the dataset. A value of 0.0 indicates no repair, while 1.0 applies full repair.
    - `sensitive_attribute`: The protected attribute to be repaired in the dataset.
  - **Methods**:
    - `fit_transform`: Applies the repair transformation to the dataset and returns the edited dataset.

---

## Code Example

The following code demonstrates how to apply **Disparate Impact Remover** using `DisparateImpactRemover` on a dataset.

### Requirements

Install the AI Fairness 360 package:

```
pip install aif360
```

### Implementation

```
# Import necessary libraries
import numpy as np
from aif360.algorithms.preprocessing import DisparateImpactRemover
from aif360.datasets import BinaryLabelDataset

# Define repair level and sensitive attribute
repair_level = 0.8  # Degree of repair from 0 (none) to 1 (full)
sensitive_attribute = 'race'  # Define the protected attribute for repair

# Load your dataset (example using BinaryLabelDataset)
dataset = BinaryLabelDataset(...)

# Initialize DisparateImpactRemover with specified parameters
di_remover = DisparateImpactRemover(repair_level=repair_level, sensitive_attribute=sensitive_attribute)

# Apply the repair transformation to mitigate bias
transformed_dataset = di_remover.fit_transform(dataset)
```

### Explanation of Code Example

- **Repair Level**: Controls the intensity of feature adjustments, where 0.0 applies no change and 1.0 applies maximum repair to remove disparate impact.
- **Sensitive Attribute**: Defines the protected attribute (e.g., "race", "gender") for which feature values will be adjusted.
- **Fit Transform**: Combines the `fit` and `transform` steps to edit the dataset and mitigate bias in one call.

---

## Detailed Steps for Using Disparate Impact Remover

1. **Set Repair Level and Sensitive Attribute**:  
   Define the intensity of repair needed and specify the protected attribute for bias mitigation (e.g., "race").

2. **Fit and Transform Dataset**:  
   Use the `fit_transform` method to apply the feature adjustments and generate a fairer version of the dataset.

3. **Evaluate Results**:  
   Measure the fairness and accuracy metrics to confirm the effect of Disparate Impact Remover on the data.

---

## Important Considerations

### Repair Level

The `repair_level` parameter defines the degree of transformation applied to the data. A repair level of 0.0 leaves the dataset unchanged, while 1.0 maximally adjusts feature values to balance group distributions. Selecting an appropriate repair level is essential to maintain predictive utility while reducing bias.

### Sensitive Attribute

Choosing the correct sensitive attribute for repair is crucial to achieving fairness. Disparate Impact Remover is most effective when the chosen attribute has a clear association with disparate impact in the dataset.

### Data Consistency

Disparate Impact Remover preserves rank-ordering within groups, ensuring that the relative feature rankings remain consistent even after adjustments. This approach is helpful for maintaining data integrity and minimizing unintended impacts on model training.

---

## Example Application: UCI Adult Dataset

### Steps
1. **Load the Dataset**: Use the UCI Adult dataset or a similar dataset containing protected attributes (e.g., race, gender).
2. **Apply Disparate Impact Remover**: Follow the code example to edit feature values for fairer representation.
3. **Evaluate Fairness**: Assess metrics across protected groups to verify the reduction in disparate impact.

Disparate Impact Remover is particularly effective for datasets where feature adjustments can reduce bias without impacting the structure or predictive quality of the data.

---

## Further Reading and Resources

For more information on **Disparate Impact Remover** and its theoretical foundation, refer to:

- **Original Research Paper**: Feldman, M., et al. "Certifying and Removing Disparate Impact." ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 2015.
- **AIF360 Documentation**: [IBM AIF360 GitHub](https://github.com/Trusted-AI/AIF360)

This guide provides an overview of using **Disparate Impact Remover** to enhance fairness in training data, ensuring balanced representation and mitigating biases in model development.

<div align="center">

---

[![View MichaelAngel.io on GitHub](https://img.shields.io/badge/GitHub-View%20MichaelAngel.io-blue?logo=github)](https://github.com/M1ck4/MichaelAngel.io)

[![Ethical AI](https://img.shields.io/badge/Ethical%20AI-Priority-orange.svg)](https://github.com/M1ck4/MichaelAngel.io/blob/main/docs/the_codex/AI_Artisians_FAQ.md) 

---

![Creative Commons License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey?style=for-the-badge&logo=creative-commons&logoColor=white)
</div>
