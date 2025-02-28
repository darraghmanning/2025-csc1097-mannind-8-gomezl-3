import json
import os
from srcExtractor.utils.data_processing import similar, extract_time_points

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
                                    if time_point not in match["questionnaireTiming"]:
                                        match["questionnaireTiming"].append(time_point)

        # Save the modified questionnaire JSON back to file
        with open(questionnaire_json_file, "w", encoding="utf-8") as f:
            json.dump(questionnaire_json_data, f, indent=4)
        return {"success": questionnaire_json_data}
    except Exception as e:
        return {"error": f"Failed to find matching questionnaires in the JSON output from the questionnaire extraction process: {str(e)}"}