# Optimized Preprocessing for AI Fairness (IBM's Algorithm)

## Overview

The **Optimized Preprocessing** algorithm by IBM is a fairness-enhancing preprocessing technique that modifies features and labels within a dataset to promote group fairness while controlling for individual distortion and data fidelity constraints. Developed based on the work by Calmon et al. (2017) and enhanced by IBM, this algorithm performs probabilistic transformations on data, ensuring that sensitive attributes do not contribute to biased predictions in machine learning models.

This document provides a comprehensive guide on how to use the `OptimPreproc` class from IBM’s AI Fairness 360 (AIF360) toolkit to reduce bias in datasets by implementing the Optimized Preprocessing algorithm.

## License Information

This code is released under the Apache License, Version 2.0. You can view the full license [here](http://www.apache.org/licenses/LICENSE-2.0).

## Objective

The primary objectives of the **Optimized Preprocessing** algorithm are:

- **Group Fairness**: Reducing bias related to protected attributes (e.g., race, gender) across groups.
- **Data Fidelity**: Minimizing the impact of transformations on data utility, ensuring predictive performance is preserved.
- **Controlled Distortion**: Managing the degree to which feature values are modified to achieve fairness.

## How the Optimized Preprocessing Algorithm Works

The algorithm applies probabilistic mappings to dataset features and labels, balancing fairness constraints with data fidelity. It automatically adjusts transformations across all possible group combinations in the dataset, even if privileged and unprivileged groups are specified.

### Key Components and Classes

- **`OptimPreproc` Class**: Inherits from the `Transformer` class and implements the preprocessing transformation.
  - **Attributes**:
    - `optimizer`: Optimizer class to perform the transformation.
    - `optim_options`: Options dictionary for controlling the transformation.
    - `unprivileged_groups` and `privileged_groups`: Representations of sensitive groups.
    - `verbose`: Toggles verbosity of output.
    - `seed`: Sets a random seed for reproducibility.

### Code Structure and Methods

- **`fit`**: Computes the transformation based on the dataset.  
  The `fit` method prepares the transformation by identifying protected attributes and setting optimization parameters.

- **`transform`**: Applies the computed transformation to a new dataset.  
  The `transform` method uses probabilistic mappings to transform sensitive attributes in a dataset, resulting in a dataset with reduced bias.

- **`_apply_randomized_mapping`**: Supporting Function  
  This helper function applies random sampling based on computed probabilities, which helps implement the probabilistic transformation across different groups in the dataset.

---

## Code Example

The following code demonstrates how to apply **Optimized Preprocessing** with `OptimPreproc` on a dataset.

### Requirements

Install the AI Fairness 360 package:

```
pip install aif360
```

### Implementation

```
# Import necessary libraries
from aif360.algorithms.preprocessing.optim_preproc import OptimPreproc
from aif360.datasets import load_adult_income
import numpy as np

# Define the optimizer class and options
optimizer = YourOptimizerClass  # Replace with the specific optimizer class
optim_options = {
    'distortion_fun': 'your_distortion_function',  # Define distortion function
    'clist': [0.01, 0.1, 1.0],  # Constraints on distortion
    'epsilon': 0.01,
    'dlist': [0.1, 0.5, 1.0]
}

# Load a sample dataset (UCI Adult dataset)
data = load_adult_income()

# Initialize the OptimPreproc transformer with optimizer options
optim_preproc = OptimPreproc(optimizer=optimizer, optim_options=optim_options, seed=42)

# Fit the transformer to learn the optimal transformation
optim_preproc.fit(data)

# Transform the dataset to reduce bias
transformed_data = optim_preproc.transform(data)
```

### Explanation of Code Example

- **Optimizer**: An optimizer class that performs the optimization.
- **Options**: Define `distortion_fun`, `clist`, and other parameters to control the extent of transformation.
- **Fit**: The `fit` function prepares the probabilistic transformation by learning how sensitive features impact outcomes.
- **Transform**: Applies the transformation to create a fairer version of the dataset.

---

## Detailed Steps for Using Optimized Preprocessing

1. **Initialize Optimizer and Set Constraints**:  
   Select the optimizer class and configure options, including distortion constraints and randomness controls.

2. **Fit the Dataset**:  
   The `fit` method takes in a dataset and calculates necessary transformations based on distortion, utility, and fairness constraints.

3. **Apply Transformation**:  
   Using the `transform` method, modify features and labels to ensure fair representation of protected groups.

4. **Evaluate Results**:  
   Use fairness and accuracy metrics to confirm the reduced bias and retained predictive utility in the transformed dataset.

---

## Important Considerations

### Group Adjustments

The algorithm automatically adjusts all possible group combinations in the dataset, aiming to reduce bias without depending on explicitly defined privileged and unprivileged groups. For applications focusing on specific sensitive attributes, customization of the optimizer function might be required.

### Instance Weights

Instance weights are not considered in the Optimized Preprocessing implementation. The algorithm operates purely on feature and label transformations, ensuring equal treatment across instances.

### Distortion Constraints

The distortion function (`distortion_fun`) and constraint list (`clist`) control how much feature values can change during the transformation. Balancing distortion constraints is essential to prevent loss of data fidelity.

---

## Supporting Function: `_apply_randomized_mapping`

This function enables probabilistic transformations by mapping feature values and labels to a fairer distribution based on learned probabilities.

```python
def _apply_randomized_mapping(df, dfMap, features=[], random_seed=None):
    """Apply randomized mapping to create a transformed dataframe.

    Args:
        df (DataFrame): Original dataframe.
        dfMap (DataFrame): Mapping parameters.
        features (list): Feature names for mapping.
        random_seed (int): Seed for reproducibility.

    Returns:
        DataFrame: Transformed dataframe.
    """
    if random_seed is not None:
        np.random.seed(seed=random_seed)

    df2 = df[features].copy()
    remaining_columns = [col for col in df.columns if col not in features]
    
    if remaining_columns:
        df3 = df[remaining_columns].copy()

    # Index list from feature combinations
    idx_list = [tuple(row) for row in df2.itertuples(index=False)]
    draw_probs = dfMap.loc[idx_list]
    draws_possible = draw_probs.columns.tolist()

    # Random draws based on mapping probabilities
    def draw_ind(x): 
        return np.random.choice(len(draws_possible), p=x)
    
    draw_inds = [draw_ind(row) for row in draw_probs.values]
    df2.loc[:, dfMap.columns.names] = [draws_possible[i] for i in draw_inds]

    return pd.concat([df2, df3], axis=1) if remaining_columns else df2
```

The `_apply_randomized_mapping` function creates a probabilistically transformed DataFrame, adjusting values across sensitive attributes according to fairness constraints.

---

## Example Application: UCI Adult Dataset

### Steps
1. **Load the Dataset**: Use the UCI Adult dataset, which contains sensitive attributes like race and gender.
2. **Apply Optimized Preprocessing**: Follow the code example to preprocess the dataset.
3. **Evaluate Bias Mitigation**: Assess predictions across sensitive groups to confirm reduced disparities.

This approach is especially useful for datasets that exhibit known biases, as Optimized Preprocessing can help ensure that sensitive attributes are treated fairly by the model.

---

## Further Reading and Resources

To learn more about the **Optimized Preprocessing** algorithm, consult the following resources:

- **Original Research Paper**: [Calmon, F., et al. "Optimized Preprocessing for Discrimination Prevention." Conference on Neural Information Processing Systems, 2017](https://arxiv.org/abs/1704.03354)
- **AIF360 Documentation**: [IBM AIF360 GitHub](https://github.com/Trusted-AI/AIF360)

This document provides an in-depth guide to applying IBM’s **Optimized Preprocessing** for bias mitigation in datasets, promoting ethical AI development and improved fairness across sensitive groups.

<div align="center">

---

[![View MichaelAngel.io on GitHub](https://img.shields.io/badge/GitHub-View%20MichaelAngel.io-blue?logo=github)](https://github.com/M1ck4/MichaelAngel.io)

[![Ethical AI](https://img.shields.io/badge/Ethical%20AI-Priority-orange.svg)](https://github.com/M1ck4/MichaelAngel.io/blob/main/docs/the_codex/AI_Artisians_FAQ.md) 

---

![Creative Commons License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey?style=for-the-badge&logo=creative-commons&logoColor=white)
</div>
