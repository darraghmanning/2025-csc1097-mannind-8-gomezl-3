import logging
import numpy as np
from sentence_transformers import SentenceTransformer, util

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- Load Model Once Globally ---
model = SentenceTransformer('all-MiniLM-L6-v2')

# --- Core Functions ---


def compute_embeddings(items):
    """Compute embeddings for a list of questionnaire strings."""
    if not isinstance(items, list) or not items:
        return None
    valid_items = [item for item in items if isinstance(item, str)]
    if not valid_items:
        return None
    embeddings = model.encode(valid_items, convert_to_tensor=True)
    return embeddings, valid_items


def match_questionnaires(predicted, ground_truth, threshold: float = 0.75):
    """Match predicted questionnaires to ground truth using cosine similarity."""
    if not isinstance(predicted, list) or not isinstance(ground_truth, list):
        return {"matches": [], "unmatched_predictions": predicted, "unmatched_ground_truth": ground_truth}

    pred_embeds = compute_embeddings(predicted)
    truth_embeds = compute_embeddings(ground_truth)

    if pred_embeds is None or truth_embeds is None:
        return {"matches": [], "unmatched_predictions": predicted, "unmatched_ground_truth": ground_truth}

    pred_vecs, pred_valid = pred_embeds
    truth_vecs, truth_valid = truth_embeds

    cosine_scores = util.cos_sim(pred_vecs, truth_vecs).cpu().numpy()

    matches = []
    unmatched_pred = pred_valid.copy()
    unmatched_truth = truth_valid.copy()
    pred_matched = np.zeros(len(pred_valid), dtype=bool)
    truth_matched = np.zeros(len(truth_valid), dtype=bool)

    while True:
        max_sim = threshold
        max_i, max_j = -1, -1

        for i, pred_m in enumerate(pred_matched):
            if pred_m:
                continue
            for j, truth_m in enumerate(truth_matched):
                if truth_m:
                    continue
                if cosine_scores[i, j] > max_sim:
                    max_sim = cosine_scores[i, j]
                    max_i, max_j = i, j

        if max_i == -1:
            break

        matches.append((pred_valid[max_i], truth_valid[max_j], float(max_sim), "semantic"))
        pred_matched[max_i] = True
        truth_matched[max_j] = True
        unmatched_pred.remove(pred_valid[max_i])
        unmatched_truth.remove(truth_valid[max_j])

    return {"matches": matches, "unmatched_predictions": unmatched_pred, "unmatched_ground_truth": unmatched_truth}


def calculate_metrics(match_results, pred_list, truth_list):
    """Calculate evaluation metrics based on matching results."""
    matches = match_results["matches"]
    unmatched_pred = match_results["unmatched_predictions"]
    unmatched_truth = match_results["unmatched_ground_truth"]

    tp = len(matches)
    fp = len(unmatched_pred)
    fn = len(unmatched_truth)

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) else 0

    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "match_count": tp,
        "total_predicted": len(pred_list) if isinstance(pred_list, list) else 0,
        "total_ground_truth": len(truth_list) if isinstance(truth_list, list) else 0
    }


def evaluate_dataframe_similarity(df, pred_col, truth_col, threshold: float = 0.75):
    """Evaluate similarity between predicted and ground truth for each row in the dataframe."""
    result_df = df.copy()

    metric_columns = ['match_count', 'precision', 'recall', 'f1_score']
    for col in metric_columns:
        result_df[col] = 0.0
    for col in ['matched_items', 'unmatched_predictions', 'unmatched_ground_truth']:
        result_df[col] = [[] for _ in range(len(result_df))]

    for idx, row in result_df.iterrows():
        logging.info(f"Processing row {idx + 1}/{len(result_df)}...")
        pred_list = row[pred_col]
        truth_list = row[truth_col]

        if not isinstance(pred_list, list) or not isinstance(truth_list, list):
            continue

        match_results = match_questionnaires(pred_list, truth_list, threshold)
        metrics = calculate_metrics(match_results, pred_list, truth_list)

        for metric in metric_columns:
            result_df.at[idx, metric] = metrics[metric]
        result_df.at[idx, 'matched_items'] = [
            f"{pred} -> {truth} ({sim:.2f})" for pred, truth, sim, _ in match_results["matches"]
        ]
        result_df.at[idx, 'unmatched_predictions'] = match_results['unmatched_predictions']
        result_df.at[idx, 'unmatched_ground_truth'] = match_results['unmatched_ground_truth']

    overall_metrics = {f"avg_{m}": result_df[m].mean() for m in ['precision', 'recall', 'f1_score']}
    overall_metrics.update({
        'total_match_count': result_df['match_count'].sum(),
        'total_rows': len(result_df),
        'rows_with_matches': (result_df['match_count'] > 0).sum()
    })

    return result_df, overall_metrics


def show_detailed_results(df, row_idx):
    """Display detailed matching results for a specific row."""
    if row_idx < 0 or row_idx >= len(df):
        logging.error(f"Invalid row index: {row_idx}")
        return

    row = df.iloc[row_idx]
    logging.info(f"=== Results for row {row_idx} ===")
    print(f"File name: {row.get('file_name', 'N/A')}")
    print(f"Match count: {row['match_count']}")
    print(f"Precision: {row['precision']:.2f}")
    print(f"Recall: {row['recall']:.2f}")
    print(f"F1 score: {row['f1_score']:.2f}")

    print("\nMatched items:")
    for match in (row['matched_items'] or []):
        print(f"  {match}")

    print("\nUnmatched Predictions:")
    for item in (row['unmatched_predictions'] or []):
        print(f"  {item}")

    print("\nUnmatched Ground Truth:")
    for item in (row['unmatched_ground_truth'] or []):
        print(f"  {item}")
