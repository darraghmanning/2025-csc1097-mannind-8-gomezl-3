PROMPTS = {
    "protocol_extraction": (
        """
            Please analyse the attached file. 
            Extract the following structured information from the provided clinical trial protocol. The output should be in JSON format, including the required fields as described below. Ensure the extraction is accurate and based on the described locations in the protocol.

            Required Fields:
            0. Project Title: The title of the protocol. Extract the protocol name, typically found on the first pages of the protocol.
            1. Sponsor: The organisation sponsoring the clinical trial. Extract the sponsor's name, usually found on the first page of the protocol.
            2. Study Number: The unique identifier for the protocol. Extract the protocol number, found on the first page beneath the protocol objective.
            3. Protocol Version and Date: Extract the version and date of the protocol, located on the first page beneath the protocol objective.
            4. Study Title: The title of the clinical trial study. Extract the full protocol name, typically found on the first page of the protocol.
            5. Phase: The phase of the clinical trial (e.g., Phase I, Phase II, Phase III).
            6. Therapeutic Area: The therapeutic area or medical condition being studied.
            7. Number of Patients: The anticipated number of patients to be enrolled in the study.
            8. Number of Sites: The number of clinical sites participating in the study.
            9. Indication: Extract the disease being treated, typically found in the aim of the study section.
            10. Duration of Treatment: Extract the duration of treatment (e.g., weeks, days, or years), found in the schema, schedule of activities, or study design sections.
            11. Schedule of Assessments: Extract the table number reference (and section number) for the schedule of assessments.

            Instructions for Response:
            1. Extract each piece of information accurately based on its location in the protocol.
            2. Format the output in JSON with field names matching the structure below.
            3. If a field is not mentioned or available in the protocol, state "Not Available."

            Example Output:
            {
                "Sponsor": "<<Sponsor Name>>",
                "Study Number": "<<Study Number>>",
                "Protocol Version and Date": "<<Version and Date>>",
                "Study Title": "<<Full Protocol Name>>",
                "Protocol Title":"<<Protocol Title>>",
                "Phase": "<<Phase>>",
                "Therapeutic Area": "<<Therapeutic Area>>",
                "Number of Patients (if known)": "<<Number of Patients>>",
                "Number of Sites (if known)": "<<Number of Sites>>",
                "Duration of Treatment": "<<Number of Weeks, Days, or Years>>",
                "Schedule of Assessments": "<<Table Number Reference and Section Number>>"
            }

            Final Note:
            Once the response is generated, double-check the extracted information for accuracy and completeness."
        """
    ),
    "questionnaire_extraction": (
        """
            Extract and list all the questionnaires and their details from the attached file. 
            Objective:
                As a specialised GPT model designed for analysing clinical trial protocols and articles, your primary goal is to meticulously extract and categorise essential data necessary for advancing research and development efforts. This involves carefully parsing uploaded documents to extract vital components crucial for understanding the trial's scope and methodology.
                Instructions to Assistant:
                Step 1: Compile a comprehensive list of all questionnaires, assessment tools, indexes and related measurement instruments. Ensure no item is missed by examining all relevant sections, including the study procedures, assessments, outcomes, objectives, and appendices where questionnaires or tools may be referenced.
                Step 2: From the initial list extracted from the document, specify which items are Patient-Reported Outcomes (PROs), which are Clinician-Reported Outcomes (ClinROs), which are Observer-Reported Outcomes (ObsROs), which are Patient-Reported Experience of Care (Patient-Reported Experience Measures or PREMs), which are Composite outcomes, and which are none of the above. Include tools that are typically clinician-reported, even if not explicitly labeled.
                Step 3: Extract the schedule of each questionnaires mentioned in the protocol. If no schedule is found, return an empty string. 
                Inclusivity: Ensure inclusivity by thoroughly examining all sections of the document where questionnaires and tools may be referenced. This includes scrutinizing study procedures, assessments, outcomes, and any appendices for mentions of relevant instruments. Cross-verify with a standard list of known clinical trial instruments.
                Accuracy Check: Conduct a thorough review of the compiled list to ensure the precise capture of all questionnaires and tools, including electronic ones. Accuracy is paramount to maintain the integrity of the analysis. Revisit the list iteratively to ensure completeness.
                Completion: After compiling and verifying all items, present a comprehensive final list for review. This list should include all items categorized as PROs, ClinROs, ObsROs, PREMs, and any others, ensuring thorough coverage of all relevant instruments for detailed analysis and subsequent actions.

            Instructions for Response:
                {"questionnaires":[{
                    "longName": "string,
                    "shortName": "string",
                    "type": "PRO",
                    "questionnaireSchedule": "string"
                },{
                    "longName": "string",
                    "shortName": "string",
                    "type": "ClinRO",
                    "questionnaireSchedule": "string"
                }]}
                Provide the extracted information all in one list in the specified JSON format.
        """
    ),
    "table_classifier": (
        """
            You are an **expert in clinical trial protocol analysis** with deep expertise in identifying tables 
            related to participant care schedules.

            ### Task
            Your job is to classify whether a given CSV table is a **Schedule of Events (SoE)** or 
            **Schedule of Activities (SoA)** table.

            ### Characteristics of SoE/SoA Tables
            - Header rows specifying visit names and timings (e.g., "Baseline", "Follow-Up").
            - Body rows listing specific activities (assessments, treatments, patient-reported outcomes).
            - Common terms: "Informed Consent", "Treatment", "Protocols", "Blood Pressure", "BMI".
            - Contextual phrases: "Schedule of Events", "Schedule of Assessment", "Study Calendar".

            ### Characteristics of Non-SoE Tables
            - Tables focused on timepoints (e.g., minute-by-minute breakdowns).
            - Administrative or protocol-related tables without visit schedules.
            - Tables listing research objectives, endpoints, or laboratory values.

            ### Decision Rule
            1. Identify if the header rows define **time-based participant visits**.
            2. Verify if the body rows list **activities linked to those visits**.
            3. Check for **key terms** or **contextual clues**.
            4. **Final Output**: Return **ONLY "YES" or "NO"**, without additional text.

            ### Expected Output
            Return either:
            - "YES" → If it's an SoE/SoA table.
            - "NO" → If it's NOT an SoE/SoA table.
        """
    )
}
