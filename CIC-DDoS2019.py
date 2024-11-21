import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score


df = pd.read_parquet('tccc\Syn-training.parquet')  

# Step 1: Data Overview
print("Dataset Info:")
print(df.info())
print("\nSample Data:")
print(df.head())

# Step 2: Data Preprocessing

# Check for missing values
missing_values = df.isnull().sum()
print("\nMissing Values:\n", missing_values[missing_values > 0])

# Drop columns with a high number of missing values or fill in missing values
df = df.dropna()  # Simplest approach; alternatively, use df.fillna()

# Check for categorical features
categorical_cols = df.select_dtypes(include=['object']).columns
print("\nCategorical Columns:", categorical_cols)

# Encode categorical columns if necessary
# Here, assume 'Label' is the target column indicating attack type
df['Label'] = df['Label'].astype('category').cat.codes

# Step 3: Exploratory Data Analysis (EDA)

# Plot class distribution
plt.figure(figsize=(8, 6))
sns.countplot(x='Label', data=df)
plt.title('Distribution of Classes')
plt.xlabel('Class')
plt.ylabel('Count')
plt.show()

# Check feature correlation
plt.figure(figsize=(10, 8))
sns.heatmap(df.corr(), cmap='coolwarm', annot=False, fmt=".2f")
plt.title('Feature Correlation Matrix')
plt.show()

# Step 4: Feature Selection

# Define features (X) and target (y)
X = df.drop(columns=['Label'])  # Drop target column from features
y = df['Label']  # Target column

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Step 5: Model Training

# Use a simple Random Forest Classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Step 6: Model Evaluation

# Predictions
y_pred = model.predict(X_test)

# Evaluation metrics
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("Accuracy Score:", accuracy_score(y_test, y_pred))

# Feature Importance
feature_importance = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
plt.figure(figsize=(10, 6))
feature_importance.plot(kind='bar')
plt.title("Feature Importances")
plt.show()
