import json
import os
import logging
from srcExtractor.utils.data_processing import similar, extract_time_points, clean_string

logging.basicConfig(level=logging.INFO)


QUALITY_OF_LIFE_TERMS = [
    "quality of life", "qol", "qol assessment", "qol survey", "hrqol", "hrql", "hr-qol", "qol instruments"
    "health-related quality of life", "patient quality of life", "quality of life questionnaires", "patient questionnaire booklet"
    "quality of life measures", "health-related quality of life questionnaires", "patient-reported outcomes",
    "health-related quality of life assessments"
]


def is_quality_of_life_related(text):
    """
    Check if the study procedure is related to a quality of life term.
    The quality of life terms are different variations of
    the term "quality of life" and its abbreviations.
    This function uses a similarity threshold to determine if the text is related to any of the quality of life terms.
    Which are different names that could be used for the questionnaires.
    Args:
        text (str): The study procedure text to check.
    Returns:
        bool: True if the text is related to a quality of life term, otherwise False.
    """
    return any(similar(term, text) >= 0.8 for term in QUALITY_OF_LIFE_TERMS)


def find_matching_questionnaires(questionnaire_json_file, timeline_json_folder, similarity_threshold):
    """
    Finds matching questionnaires between a provided questionnaire JSON file and
    multiple timeline JSON files in a given folder based on a similarity threshold.

    Args:
        questionnaire_json_file (str): Path to the questionnaire JSON file.
        timeline_json_folder (str): Path to the folder containing timeline JSON files.
        output_directory (str): Directory where matching results should be saved.
        similarity_threshold (float): Minimum similarity score required for a match.

    Returns:
        dict: Success message or error message.
    """
    try:
        # Load the first JSON file
        with open(questionnaire_json_file, 'r', encoding='utf-8') as f:
            questionnaire_json_data = json.load(f)

        # Extract LongName and ShortName from the first JSON
        first_questionnaires = {}
        for q in questionnaire_json_data.get("questionnaires", []):
            long_name = q['longName'].strip().lower()
            short_name = q['shortName'].strip().lower()
            first_questionnaires[long_name] = q
            first_questionnaires[short_name] = q

        # Iterate through all JSON files in the second folder
        for file_name in os.listdir(timeline_json_folder):
            if file_name.endswith('.json'):
                timeline_json_path = os.path.join(timeline_json_folder, file_name)

                with open(timeline_json_path, "r", encoding="utf-8") as f:
                    timeline_json_data = json.load(f)

                # Collect all timepoints from QoL entries (if any)
                qol_timepoints = []
                for entry in timeline_json_data:
                    for key, value in entry.items():
                        if isinstance(value, str) and is_quality_of_life_related(value):
                            timepoints = extract_time_points(entry)
                            for tp in timepoints:
                                qol_timepoints.append(tp)

                # Check for matches in the second JSON
                for entry in timeline_json_data:
                    matching_questionnaires = []

                    # Create a copy of the values to iterate safely
                    entry_values = list(entry.values())

                    for value in entry_values:
                        if not isinstance(value, str):  # Ensure value is a string
                            continue

                        study_procedure = value.strip().lower()
                        for questionnaire_name, questionnaire_entry in first_questionnaires.items():
                            score = similar(questionnaire_name, study_procedure)
                            if score >= similarity_threshold:
                                matching_questionnaires.append(questionnaire_entry)

                    # Assign only the best match
                    if matching_questionnaires:
                        time_points = extract_time_points(entry)  # Extract relevant time points
                        if time_points:
                            for match in matching_questionnaires:
                                if "questionnaireTiming" not in match:
                                    match["questionnaireTiming"] = []

                                # Append time points while ensuring no duplicates
                                for time_point in time_points:
                                    if clean_string(time_point) not in [clean_string(item) for item in match["questionnaireTiming"]]:
                                        match["questionnaireTiming"].append(time_point)

                # Add QoL timepoints to all questionnaires that don't have any timepoints
                if qol_timepoints:
                    for q in questionnaire_json_data.get("questionnaires", []):
                        if "questionnaireTiming" not in q:
                            q["questionnaireTiming"] = []
                            for tp in qol_timepoints:
                                if clean_string(tp) not in [clean_string(x) for x in q["questionnaireTiming"]]:
                                    q["questionnaireTiming"].append(tp)

        # Save the modified questionnaire JSON back to file
        with open(questionnaire_json_file, "w", encoding="utf-8") as f:
            json.dump(questionnaire_json_data, f, indent=4)
        return {"success": questionnaire_json_data}
    except Exception as e:
        return {"error": f"Failed to find matching questionnaires in the JSON output from the questionnaire extraction process: {str(e)}"}


def match_questionnaires_with_timelines(pdf_file_name):
    """Match extracted questionnaires with timelines."""
    try:
        response = find_matching_questionnaires(
            f"output/{pdf_file_name}.json",
            f"table_extraction_output/json_{pdf_file_name}/",
            similarity_threshold=0.6,
        )
        if "error" in response:
            return response

        return {"extracted_data": response["success"]}

    except Exception as e:
        logging.error(f"Error matching questionnaires: {e}")
        return {"error": "Failed to match questionnaires"}
