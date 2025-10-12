---
authors:
    - subhajit
title: "Outliers in Python: IQR and Z-Score"
description: This is an example blog description.
slug: detect-remove-outliers-python-iqr-zscore
date:
    created: 2025-09-30
categories:
    - Python
    - Data Science
meta:
    - name: keywords
      content: Outlier Detection, IQR Method, Z-Score
---

Outliers can significantly skew statistical analysis and machine learning model performance. This guide covers statistical and machine learning methods to detect and handle outliers effectively in Python.

<!-- more -->

## What Are Outliers

Outliers are data points that significantly differ from the majority of observations in a dataset. They can occur due to:

- Measurement errors
- Data entry mistakes
- Natural variation in the data
- Fraudulent activities
- Equipment malfunctions

## Types of Outliers

- **1. Univariate Outliers**
Extreme values in a single variable.
- **2. Multivariate Outliers**
Points that are outliers when considering multiple variables together.
- **3. Contextual Outliers**
Values that are outliers in a specific context but normal in others.

## Statistical Methods for Outlier Detection

### 1. Z-Score Method

The Z-Score measures how many standard deviations a data point is from the mean.

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Create sample dataset
np.random.seed(42)
data = np.random.normal(100, 15, 1000)
# Add some outliers
outliers = np.array([200, 250, -50, -20])
data = np.concatenate([data, outliers])

df = pd.DataFrame({'values': data})

# Calculate Z-scores
df['z_score'] = np.abs(stats.zscore(df['values']))

# Define threshold (typically 2 or 3)
threshold = 3
df['is_outlier_zscore'] = df['z_score'] > threshold

print(f"Number of outliers detected: {df['is_outlier_zscore'].sum()}")
print(f"Outlier values: {df[df['is_outlier_zscore']]['values'].values}")
```

### 2. Interquartile Range (IQR) Method

IQR method identifies outliers based on quartiles and is more robust to extreme values.

```python
def detect_outliers_iqr(data, column):
    """Detect outliers using IQR method"""
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    
    # Calculate bounds
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    # Identify outliers
    outliers = data[(data[column] < lower_bound) | (data[column] > upper_bound)]
    
    return outliers, lower_bound, upper_bound

# Apply IQR method
outliers_iqr, lower_bound, upper_bound = detect_outliers_iqr(df, 'values')
df['is_outlier_iqr'] = (df['values'] < lower_bound) | (df['values'] > upper_bound)

print(f"IQR bounds: ({lower_bound:.2f}, {upper_bound:.2f})")
print(f"Number of outliers detected by IQR: {df['is_outlier_iqr'].sum()}")
```

### 3. Modified Z-Score (MAD)

More robust than standard Z-Score as it uses median instead of mean.

```python
def modified_z_score(data):
    """Calculate modified Z-score using median absolute deviation"""
    median = np.median(data)
    mad = np.median(np.abs(data - median))
    modified_z_scores = 0.6745 * (data - median) / mad
    return np.abs(modified_z_scores)

# Apply modified Z-score
df['modified_z_score'] = modified_z_score(df['values'])
threshold_mad = 3.5
df['is_outlier_mad'] = df['modified_z_score'] > threshold_mad

print(f"Number of outliers detected by MAD: {df['is_outlier_mad'].sum()}")
```

## Machine Learning Methods for Outlier Detection

### 1. Isolation Forest

Isolation Forest isolates anomalies by randomly selecting features and split values.

```python
from sklearn.ensemble import IsolationForest

# Create multi-dimensional dataset for better demonstration
np.random.seed(42)
X = np.random.multivariate_normal([50, 50], [[100, 10], [10, 100]], 1000)
# Add outliers
X_outliers = np.array([[200, 200], [-50, -50], [300, 50], [50, 300]])
X = np.vstack([X, X_outliers])

df_multi = pd.DataFrame(X, columns=['feature1', 'feature2'])

# Apply Isolation Forest
iso_forest = IsolationForest(contamination=0.1, random_state=42)
df_multi['outlier_scores'] = iso_forest.fit_predict(df_multi[['feature1', 'feature2']])
df_multi['is_outlier_isolation'] = df_multi['outlier_scores'] == -1

print(f"Number of outliers detected by Isolation Forest: {df_multi['is_outlier_isolation'].sum()}")
```

### 2. Local Outlier Factor (LOF)

LOF measures local density deviation of a data point with respect to its neighbors.

```python
from sklearn.neighbors import LocalOutlierFactor

# Apply Local Outlier Factor
lof = LocalOutlierFactor(n_neighbors=20, contamination=0.1)
outlier_labels = lof.fit_predict(df_multi[['feature1', 'feature2']])
df_multi['is_outlier_lof'] = outlier_labels == -1

print(f"Number of outliers detected by LOF: {df_multi['is_outlier_lof'].sum()}")
```

### 3. One-Class SVM

One-Class SVM learns a decision function for novelty detection.

```python
from sklearn.svm import OneClassSVM

# Apply One-Class SVM
one_class_svm = OneClassSVM(nu=0.1, kernel="rbf", gamma=0.1)
outlier_labels = one_class_svm.fit_predict(df_multi[['feature1', 'feature2']])
df_multi['is_outlier_svm'] = outlier_labels == -1

print(f"Number of outliers detected by One-Class SVM: {df_multi['is_outlier_svm'].sum()}")
```

## Visualization of Outliers

### 1. Box Plot for Univariate Outliers

```python
plt.figure(figsize=(12, 4))

# Box plot
plt.subplot(1, 3, 1)
plt.boxplot(df['values'])
plt.title('Box Plot - Outlier Detection')
plt.ylabel('Values')

# Histogram with outliers highlighted
plt.subplot(1, 3, 2)
plt.hist(df[~df['is_outlier_iqr']]['values'], alpha=0.7, label='Normal', bins=30)
plt.hist(df[df['is_outlier_iqr']]['values'], alpha=0.7, label='Outliers', bins=30)
plt.title('Histogram with Outliers')
plt.xlabel('Values')
plt.ylabel('Frequency')
plt.legend()

# Z-score plot
plt.subplot(1, 3, 3)
plt.scatter(range(len(df)), df['z_score'], alpha=0.6)
plt.axhline(y=3, color='r', linestyle='--', label='Threshold (Z=3)')
plt.title('Z-Score Plot')
plt.xlabel('Data Point Index')
plt.ylabel('Z-Score')
plt.legend()

plt.tight_layout()
plt.show()
```

### 2. Scatter Plot for Multivariate Outliers

```python
plt.figure(figsize=(15, 5))

# Original data
plt.subplot(1, 3, 1)
plt.scatter(df_multi['feature1'], df_multi['feature2'], alpha=0.6)
plt.title('Original Data')
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')

# Isolation Forest results
plt.subplot(1, 3, 2)
normal = df_multi[~df_multi['is_outlier_isolation']]
outliers = df_multi[df_multi['is_outlier_isolation']]
plt.scatter(normal['feature1'], normal['feature2'], alpha=0.6, label='Normal')
plt.scatter(outliers['feature1'], outliers['feature2'], alpha=0.8, color='red', label='Outliers')
plt.title('Isolation Forest Detection')
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.legend()

# LOF results
plt.subplot(1, 3, 3)
normal_lof = df_multi[~df_multi['is_outlier_lof']]
outliers_lof = df_multi[df_multi['is_outlier_lof']]
plt.scatter(normal_lof['feature1'], normal_lof['feature2'], alpha=0.6, label='Normal')
plt.scatter(outliers_lof['feature1'], outliers_lof['feature2'], alpha=0.8, color='red', label='Outliers')
plt.title('LOF Detection')
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.legend()

plt.tight_layout()
plt.show()
```

## Comprehensive Outlier Detection Function

```python
def comprehensive_outlier_detection(df, columns, methods=['iqr', 'zscore', 'isolation']):
    """
    Comprehensive outlier detection using multiple methods
    
    Parameters:
    df: pandas DataFrame
    columns: list of column names to analyze
    methods: list of methods to use
    
    Returns:
    DataFrame with outlier flags for each method
    """
    result_df = df.copy()
    
    for col in columns:
        if 'iqr' in methods:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            result_df[f'{col}_outlier_iqr'] = (df[col] < lower_bound) | (df[col] > upper_bound)
        
        if 'zscore' in methods:
            z_scores = np.abs(stats.zscore(df[col]))
            result_df[f'{col}_outlier_zscore'] = z_scores > 3
        
        if 'mad' in methods:
            mad_scores = modified_z_score(df[col])
            result_df[f'{col}_outlier_mad'] = mad_scores > 3.5
    
    if 'isolation' in methods and len(columns) > 1:
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        outlier_pred = iso_forest.fit_predict(df[columns])
        result_df['outlier_isolation'] = outlier_pred == -1
    
    return result_df

# Apply comprehensive detection
columns_to_analyze = ['feature1', 'feature2']
df_comprehensive = comprehensive_outlier_detection(
    df_multi, 
    columns_to_analyze, 
    methods=['iqr', 'zscore', 'isolation']
)

# Summary of outliers detected by each method
outlier_summary = {}
for col in df_comprehensive.columns:
    if 'outlier' in col:
        outlier_summary[col] = df_comprehensive[col].sum()

print("Outlier Summary:")
for method, count in outlier_summary.items():
    print(f"{method}: {count} outliers")
```

## Outlier Treatment Strategies

### 1. Removal

```python
def remove_outliers(df, outlier_column):
    """Remove outliers from dataset"""
    return df[~df[outlier_column]].copy()

# Remove outliers detected by IQR
df_clean = remove_outliers(df, 'is_outlier_iqr')
print(f"Original size: {len(df)}, After removal: {len(df_clean)}")
```

### 2. Transformation

```python
def winsorize_outliers(data, limits=(0.05, 0.05)):
    """Cap outliers at specified percentiles"""
    from scipy.stats.mstats import winsorize
    return winsorize(data, limits=limits)

# Apply winsorization
df['values_winsorized'] = winsorize_outliers(df['values'])

# Log transformation for skewed data
df['values_log'] = np.log1p(np.abs(df['values']))
```

### 3. Imputation

```python
def impute_outliers(df, column, outlier_column, method='median'):
    """Replace outliers with imputed values"""
    df_imputed = df.copy()
    
    if method == 'median':
        fill_value = df[~df[outlier_column]][column].median()
    elif method == 'mean':
        fill_value = df[~df[outlier_column]][column].mean()
    elif method == 'mode':
        fill_value = df[~df[outlier_column]][column].mode()[0]
    
    df_imputed.loc[df_imputed[outlier_column], column] = fill_value
    return df_imputed

# Impute outliers with median
df_imputed = impute_outliers(df, 'values', 'is_outlier_iqr', method='median')
```

## Domain-Specific Considerations

### Time Series Outliers

```python
def detect_time_series_outliers(ts_data, window=30, threshold=3):
    """Detect outliers in time series using rolling statistics"""
    rolling_mean = ts_data.rolling(window=window).mean()
    rolling_std = ts_data.rolling(window=window).std()
    
    z_scores = np.abs((ts_data - rolling_mean) / rolling_std)
    return z_scores > threshold

# Example with time series
dates = pd.date_range('2024-01-01', periods=365, freq='D')
ts_values = np.random.normal(100, 10, 365)
# Add seasonal outliers
ts_values[100:110] += 50  # Anomalous period

ts_df = pd.DataFrame({'date': dates, 'value': ts_values})
ts_df['is_outlier'] = detect_time_series_outliers(ts_df['value'])
```

### Categorical Outliers

```python
def detect_categorical_outliers(df, column, threshold=0.01):
    """Detect rare categories as outliers"""
    value_counts = df[column].value_counts(normalize=True)
    rare_categories = value_counts[value_counts < threshold].index
    return df[column].isin(rare_categories)

# Example with categorical data
categories = np.random.choice(['A', 'B', 'C'], 1000, p=[0.5, 0.4, 0.1])
# Add rare categories
rare_cats = np.array(['X', 'Y', 'Z'])
categories = np.concatenate([categories, rare_cats])

cat_df = pd.DataFrame({'category': categories})
cat_df['is_rare'] = detect_categorical_outliers(cat_df, 'category', threshold=0.05)
```

## Model Performance Impact

### Before and After Comparison

```python
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Create synthetic regression dataset with outliers
X = np.random.normal(0, 1, (1000, 2))
y = 3*X[:, 0] + 2*X[:, 1] + np.random.normal(0, 0.1, 1000)

# Add outliers to target
outlier_indices = np.random.choice(1000, 50, replace=False)
y[outlier_indices] += np.random.normal(0, 10, 50)

# Create DataFrame
model_df = pd.DataFrame(X, columns=['feature1', 'feature2'])
model_df['target'] = y

# Detect outliers
z_scores_target = np.abs(stats.zscore(model_df['target']))
model_df['is_outlier'] = z_scores_target > 3

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    model_df[['feature1', 'feature2']], 
    model_df['target'], 
    test_size=0.2, 
    random_state=42
)

# Model with outliers
model_with_outliers = LinearRegression()
model_with_outliers.fit(X_train, y_train)
y_pred_with = model_with_outliers.predict(X_test)

# Model without outliers
train_mask = ~model_df.loc[X_train.index, 'is_outlier']
X_train_clean = X_train[train_mask]
y_train_clean = y_train[train_mask]

model_without_outliers = LinearRegression()
model_without_outliers.fit(X_train_clean, y_train_clean)
y_pred_without = model_without_outliers.predict(X_test)

# Compare performance
print("Model Performance Comparison:")
print(f"With outliers - MSE: {mean_squared_error(y_test, y_pred_with):.4f}, R²: {r2_score(y_test, y_pred_with):.4f}")
print(f"Without outliers - MSE: {mean_squared_error(y_test, y_pred_without):.4f}, R²: {r2_score(y_test, y_pred_without):.4f}")
```

## Best Practices

### 1. Multiple Method Validation

```python
def validate_outlier_methods(df, column, true_outliers=None):
    """Compare different outlier detection methods"""
    methods_results = {}
    
    # IQR
    Q1, Q3 = df[column].quantile([0.25, 0.75])
    IQR = Q3 - Q1
    iqr_outliers = (df[column] < Q1 - 1.5*IQR) | (df[column] > Q3 + 1.5*IQR)
    methods_results['IQR'] = iqr_outliers
    
    # Z-Score
    z_scores = np.abs(stats.zscore(df[column]))
    zscore_outliers = z_scores > 3
    methods_results['Z-Score'] = zscore_outliers
    
    # Modified Z-Score
    mad_scores = modified_z_score(df[column])
    mad_outliers = mad_scores > 3.5
    methods_results['MAD'] = mad_outliers
    
    # Summary
    summary = pd.DataFrame({
        method: results.sum() for method, results in methods_results.items()
    }, index=['Outliers Detected']).T
    
    print("Method Comparison:")
    print(summary)
    
    return methods_results
```

### 2. Threshold Sensitivity Analysis

```python
def threshold_sensitivity_analysis(data, method='zscore', thresholds=None):
    """Analyze sensitivity to threshold values"""
    if thresholds is None:
        thresholds = np.arange(1.5, 4.5, 0.5)
    
    results = []
    
    for threshold in thresholds:
        if method == 'zscore':
            z_scores = np.abs(stats.zscore(data))
            outliers = (z_scores > threshold).sum()
        elif method == 'iqr':
            Q1, Q3 = np.percentile(data, [25, 75])
            IQR = Q3 - Q1
            outliers = ((data < Q1 - threshold*IQR) | (data > Q3 + threshold*IQR)).sum()
        
        results.append({'threshold': threshold, 'outliers': outliers})
    
    return pd.DataFrame(results)

# Analyze threshold sensitivity
sensitivity_results = threshold_sensitivity_analysis(df['values'], method='zscore')
print(sensitivity_results)
```

## Integration with Data Pipelines

For production environments, implement outlier detection as part of your data quality monitoring pipeline. Consider using automated alerting when outlier rates exceed expected thresholds.


## Conclusion

Effective outlier detection requires understanding your data domain, choosing appropriate methods, and validating results. Combine statistical methods with machine learning approaches for robust detection. Always consider the business context before removing or transforming outliers, as they might contain valuable information about rare but important events. 