import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import io

def compute_fairness_metrics(file_bytes: bytes, target_col: str, sensitive_col: str):
    df = pd.read_csv(io.BytesIO(file_bytes))
    
    # Preprocessing
    df = df.dropna()
    
    # Simple label encoding for MVP
    df = pd.get_dummies(df, drop_first=True)
    
    # Ensure columns exist after dummy encoding
    target = target_col if target_col in df.columns else [c for c in df.columns if target_col in c][0]
    sensitive = sensitive_col if sensitive_col in df.columns else [c for c in df.columns if sensitive_col in c][0]
    
    X = df.drop(columns=[target])
    y = df[target]
    
    # Train Model
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    # Attach predictions back to test set for evaluation
    results = X_test.copy()
    results['predicted'] = y_pred
    results['actual'] = y_test
    
    # Find groups (assuming binary sensitive attribute for MVP)
    groups = results[sensitive].unique()
    if len(groups) < 2:
        raise ValueError("Sensitive attribute must have at least two distinct values in the test set.")
    
    group_0, group_1 = groups[0], groups[1]
    
    # P(Y=1 | S=g)
    prob_g0 = results[results[sensitive] == group_0]['predicted'].mean()
    prob_g1 = results[results[sensitive] == group_1]['predicted'].mean()
    
    # Metrics
    demographic_parity_diff = abs(prob_g0 - prob_g1)
    disparate_impact = (prob_g1 / prob_g0) if prob_g0 > 0 else 0
    
    # Calculate True Positive Rates for Equal Opportunity
    tpr_g0 = _calculate_tpr(results[results[sensitive] == group_0])
    tpr_g1 = _calculate_tpr(results[results[sensitive] == group_1])
    equal_opportunity_diff = abs(tpr_g0 - tpr_g1)
    
    return {
        "Group A representation": float(prob_g0),
        "Group B representation": float(prob_g1),
        "Demographic Parity Difference": float(demographic_parity_diff),
        "Disparate Impact Ratio": float(disparate_impact),
        "Equal Opportunity Difference": float(equal_opportunity_diff)
    }

def _calculate_tpr(df_group):
    if len(df_group) == 0: return 0
    tn, fp, fn, tp = confusion_matrix(df_group['actual'], df_group['predicted'], labels=[0, 1]).ravel()
    return tp / (tp + fn) if (tp + fn) > 0 else 0