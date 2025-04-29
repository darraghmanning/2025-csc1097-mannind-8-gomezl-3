import os
import re
import ast
import pandas as pd
import json
import logging
from similarity_calculation import evaluate_dataframe_similarity, show_detailed_results

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- Configuration ---
GROUND_TRUTH_PATH = 'timelinextract/testing/GroundTruth.csv'
PREDICTIONS_FOLDER = 'timelinextract/testing/predictions/'
OUTPUT_PATH = 'timelinextract/testing/results/evaluation_results.csv'
SIMILARITY_THRESHOLD = 0.75

# --- Utility Functions ---


def string_to_list(text):
    if isinstance(text, str):
        return [item.strip() for item in text.split('\n') if item.strip()]
    return text


def extract_ground_truth_timepoints(val):
    print("Valor....")
    print(val)
    try:
        # Split the string into separate list chunks using regex
        list_strings = re.findall(r"\[.*?\]", val, re.DOTALL)

        all_items = []
        for list_str in list_strings:
            try:
                parsed = ast.literal_eval(list_str)
                if isinstance(parsed, list):
                    all_items.extend(parsed)
            except Exception:
                continue
        return string_to_list(all_items)
    except Exception:
        return []


def read_json_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            for encoding in ['utf-8-sig', 'latin-1', 'cp1252']:
                try:
                    decoded_content = content.decode(encoding)
                    return json.loads(decoded_content)
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
            return json.loads(content.decode('utf-8', errors='replace'))
    except Exception as e:
        logging.error(f"Failed to read JSON file {file_path}: {e}")
        return None


def extract_predictions(folder_path):
    file_names, questionnaires, timepoints = [], [], []
    for file in os.listdir(folder_path):
        if file.endswith('.json'):
            file_name = file.replace('.json', '')
            file_names.append(file_name)
            data = read_json_file(os.path.join(folder_path, file))
            if data and 'questionnaires' in data:
                tmp_questionnaires = []
                questionnaires_list = data['questionnaires']
                for questionnaire in questionnaires_list:
                    if isinstance(questionnaire, dict) and questionnaire.get("type") == "PRO":
                        short_name = questionnaire.get('shortName', '')
                        long_name = questionnaire.get('longName', '')
                        if short_name and long_name:
                            tmp_questionnaires.append(f"{long_name} ({short_name})")
                        elif short_name:
                            tmp_questionnaires.append(short_name)
                        elif long_name:
                            tmp_questionnaires.append(long_name)
                questionnaires.append(tmp_questionnaires)
                tmp_timepoints = []
                for questionnaire in questionnaires_list:
                    if questionnaire.get("type") == "PRO":
                        timepoint = questionnaire.get('questionnaireTiming')
                        if isinstance(timepoint, list):
                            tmp_timepoints.append(timepoint)
                flattened_timepoints = [tp for sublist in tmp_timepoints for tp in sublist]
                timepoints.append(flattened_timepoints)
            else:
                questionnaires.append(None)
                timepoints.append(None)
    return file_names, questionnaires, timepoints


def load_data(ground_truth_path, predictions_folder):
    ground_truth_df = pd.read_csv(ground_truth_path, encoding='unicode_escape')
    files, preds, times = extract_predictions(predictions_folder)
    preds_df = pd.DataFrame({'file_name': files, 'predicted_questionnaires': preds, 'predicted_timepoints': times})
    print(preds_df)

    gt_cols = ['ï»¿ProtocolName', 'Questionnaires', 'Timelines']
    if not all(col in ground_truth_df.columns for col in gt_cols):
        raise ValueError("Missing required columns in ground truth CSV.")

    ground_truth_df = ground_truth_df.rename(columns={
        'Questionnaires': 'ground_truth_questionnaires',
        'Timelines': 'ground_truth_timepoints'
    })
    merged = preds_df.merge(ground_truth_df, left_on='file_name', right_on='ï»¿ProtocolName', how='left').drop('ï»¿ProtocolName', axis=1)

    merged['ground_truth_questionnaires'] = merged['ground_truth_questionnaires'].apply(string_to_list)
    merged['predicted_questionnaires'] = merged['predicted_questionnaires']
    merged['ground_truth_timepoints'] = merged['ground_truth_timepoints'].apply(extract_ground_truth_timepoints)
    merged['predicted_timepoints'] = merged['predicted_timepoints']

    print("Predicted timepoint")
    print(merged['predicted_timepoints'])
    print("Ground truth timepoint")
    print(merged['ground_truth_timepoints'])
    return merged

# --- Main Execution ---


def main():
    logging.info("Loading and preparing data...")
    df = load_data(GROUND_TRUTH_PATH, PREDICTIONS_FOLDER)

    logging.info("Evaluating questionnaire similarity...")
    result_df, metrics = evaluate_dataframe_similarity(df, 'predicted_questionnaires', 'ground_truth_questionnaires', threshold=SIMILARITY_THRESHOLD)

    logging.info("Evaluating timepoints similarity...")
    timepoint_result_df, timepoint_metrics = evaluate_dataframe_similarity(
                                    df, 'predicted_timepoints', 'ground_truth_timepoints', threshold=SIMILARITY_THRESHOLD
                                )

    logging.info(f"Saving evaluation results to {OUTPUT_PATH}")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    result_df.to_csv(OUTPUT_PATH, index=False)

    # Print final metrics
    logging.info("Overall Questionnaire Evaluation Metrics:")
    for k, v in metrics.items():
        logging.info(f"{k}: {v:.4f}")

    logging.info("\nSchedule Timepoints Evaluation Metrics:")
    for k, v in timepoint_metrics.items():
        logging.info(f"{k}: {v:.4f}")

    # Show an example
    logging.info("\nDetailed results for first sample:")
    show_detailed_results(result_df, 0)

    logging.info("Analysis complete.")


if __name__ == "__main__":
    main()
