# Reweighing for AI Fairness

## Overview

**Reweighing** is a preprocessing technique aimed at promoting fairness by adjusting the instance weights in a dataset based on group and label combinations. This technique assigns different weights to each (group, label) combination to mitigate bias and ensure fairness before model training. Implemented as part of IBM's **AI Fairness 360 (AIF360)** toolkit, Reweighing provides a flexible approach to achieving balance in datasets where disparities exist between protected groups.

## License Information

This code is released under the Apache License, Version 2.0. You can view the full license [here](http://www.apache.org/licenses/LICENSE-2.0).

## Objective

The main objectives of the **Reweighing** technique are:

- **Group Fairness**: Adjusting weights to balance distributions across protected groups (e.g., race, gender).
- **Reduction of Bias**: Counteracting systemic imbalances in the data to promote fairness in machine learning outcomes.
- **Preprocessing Fairness**: Making modifications at the data level before training, ensuring that any classifier can benefit from reweighted data.

## How the Reweighing Algorithm Works

The **Reweighing** algorithm calculates weights for each (group, label) combination in the dataset to ensure that each group is represented fairly. By balancing these weights before training, Reweighing reduces the likelihood of biased predictions, regardless of the classifier used.

### Key Components and Classes

- **`Reweighing` Class**: Part of the AIF360 toolkit, this class provides methods to compute and apply instance-level weights to the dataset.
  - **Attributes**:
    - `unprivileged_groups`: List of dictionaries defining the unprivileged group(s) (e.g., a subset of groups receiving unfavorable treatment).
    - `privileged_groups`: List of dictionaries defining the privileged group(s) (e.g., a subset of groups that have historically received favorable treatment).
    - `w_p_fav`, `w_p_unfav`, `w_up_fav`, `w_up_unfav`: Computed weights for each (group, label) combination.

### Code Structure and Methods

- **`fit`**: Computes weights based on the original dataset.  
  The `fit` method calculates weights for each (group, label) combination, which will be applied to balance the dataset.

- **`transform`**: Applies the computed weights to the dataset.  
  The `transform` method adjusts the dataset’s `instance_weights` attribute based on the weights calculated in `fit`.

- **`_obtain_conditionings`**: Supporting Function  
  This helper function generates boolean arrays for each (group, label) combination, which are used to determine the conditions for weight application.

---

## Code Example

The following code demonstrates how to apply **Reweighing** with `Reweighing` on a dataset.

### Requirements

Install the AI Fairness 360 package:

```
pip install aif360
```

### Implementation

```
# Import necessary libraries
import numpy as np
from aif360.algorithms.preprocessing import Reweighing
from aif360.datasets import BinaryLabelDataset
from aif360.metrics import utils

# Define privileged and unprivileged groups
privileged_groups = [{'race': 1}]  # Define the privileged group
unprivileged_groups = [{'race': 0}]  # Define the unprivileged group

# Load your dataset (example using BinaryLabelDataset)
dataset = BinaryLabelDataset(...)

# Initialize Reweighing with specified privileged and unprivileged groups
reweighing = Reweighing(unprivileged_groups=unprivileged_groups, privileged_groups=privileged_groups)

# Fit the transformer to learn the necessary weights
reweighing.fit(dataset)

# Transform the dataset to apply the weights
transformed_dataset = reweighing.transform(dataset)

```

### Explanation of Code Example

- **Privileged and Unprivileged Groups**: Define the protected attribute (e.g., "race") and specify privileged (e.g., `{'race': 1}`) and unprivileged groups (e.g., `{'race': 0}`).
- **Fit**: The `fit` method computes weights for each (group, label) combination.
- **Transform**: The `transform` method applies the calculated weights to balance the dataset.

---

## Detailed Steps for Using Reweighing

1. **Define Privileged and Unprivileged Groups**:  
   Specify the attribute that separates the privileged and unprivileged groups (e.g., "race", "gender").

2. **Fit the Transformer**:  
   The `fit` method calculates weights for each (group, label) combination based on the provided groups and dataset conditions.

3. **Apply Weights with Transform**:  
   Use the `transform` method to update the `instance_weights` attribute of the dataset, making it fairer across groups.

4. **Evaluate Results**:  
   Measure the fairness and accuracy metrics to assess the effect of reweighting on the dataset.

---

## Important Considerations

### Privileged and Unprivileged Groups

Reweighing relies on the correct definition of privileged and unprivileged groups to calculate weights accurately. If the groups are misclassified, the algorithm may not achieve the desired fairness.

### Weights Adjustment

The calculated weights adjust the dataset based on the relative frequency of each group and label combination. These weights are crucial in ensuring that each subgroup is represented fairly in model training.

### Supporting Function: `_obtain_conditionings`

The `_obtain_conditionings` function is a helper method used to create boolean vectors for each (group, label) combination. These vectors are essential in calculating and applying the correct weights.

---

## Example Application: UCI Adult Dataset

### Steps
1. **Load the Dataset**: Use the UCI Adult dataset or a similar dataset that includes protected attributes (e.g., race, gender).
2. **Apply Reweighing**: Follow the code example to preprocess the dataset and assign weights based on (group, label) combinations.
3. **Evaluate Fairness**: Assess fairness and accuracy metrics across protected groups to verify the effect of reweighing.

Reweighing can help prevent models from inheriting biases present in the data, especially in cases where certain subgroups are underrepresented or unfairly treated.

---

## Further Reading and Resources

For more information on **Reweighing** and its theoretical foundation, refer to:

- **Original Research Paper**: Kamiran, F., & Calders, T. "Data Preprocessing Techniques for Classification without Discrimination." Knowledge and Information Systems, 2012.
- **AIF360 Documentation**: [IBM AIF360 GitHub](https://github.com/Trusted-AI/AIF360)

This overview of applying **Reweighing** as part of ethical AI development, ensuring balanced representation across groups in a dataset and reducing the likelihood of biased predictions.


<div align="center">

---

[![View MichaelAngel.io on GitHub](https://img.shields.io/badge/GitHub-View%20MichaelAngel.io-blue?logo=github)](https://github.com/M1ck4/MichaelAngel.io)

[![Ethical AI](https://img.shields.io/badge/Ethical%20AI-Priority-orange.svg)](https://github.com/M1ck4/MichaelAngel.io/blob/main/docs/the_codex/AI_Artisians_FAQ.md) 

---

![Creative Commons License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey?style=for-the-badge&logo=creative-commons&logoColor=white)
</div>
