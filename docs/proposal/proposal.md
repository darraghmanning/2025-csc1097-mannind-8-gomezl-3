# School of Computing &mdash; Year 4 Project Proposal

## SECTION A

|                     |                         |
|---------------------|-------------------------|
|Project Title:       | TimelineXtract          |
|Student 1 Name:      | Lorena Gomez            |
|Student 1 ID:        | 21734359                |
|Student 2 Name:      | Darragh Manning         |
|Student 2 ID:        | 21506373                |
|Project Supervisor:  | Tomas Ward              |


## SECTION B

### Introduction

This project is focused on developing a web-based application leveraging machine learning techniques to optimize the clinical trial process. Clinical trials are essential for validating the safety and efficacy of new treatments, but they can be complex, time-consuming, and costly. By streamlining key aspects of these trials, our platform aims to reduce trial time and improve patient compliance.

### Outline

The project aims to deliver a web-based application with two core features designed to assist both clinical trial vendors and patients:

1. Automated Timeline Extraction for Vendors: Utilizes Natural Language Processing (NLP) to extract Patient-Reported Outcomes (PROs) and Clinician-Reported Outcomes (ClinROs) timelines from clinical trial protocols, presented in a structured calendar format.
1. Generative AI for Patients: Generates instructional videos or images, using Generative AI, to guide patients in performing at-home clinical procedures described in trial documents.


The application will enhance efficiency for vendors and provide accessible, clear instructions for patients, thereby improving compliance and the overall success of clinical trials.

### Background

The idea for this project stems from challenges encountered in clinical trials, where managing trial protocols and ensuring patient adherence are major bottlenecks. Many trials are delayed due to the complexity of manual data extraction and patient miscompliance with home procedures. With advancements in machine learning, especially in NLP and generative AI, these challenges can be addressed by automating repetitive tasks and creating interactive tools for patients.

### Achievements

**The project will deliver:**

- **Automatic Timeline Extraction:** The web application will allow vendors to upload clinical trial protocols and receive structured timelines for PROs and ClinROs.

- **Generative AI Media for Patients:** The application will generate personalized step-by-step instructional videos or images based on textual descriptions, allowing patients to confidently follow trial procedures.

**Target Users:**

- **Vendors:** Companies managing clinical trials, who need efficient ways to handle protocol documents and schedules.
- **Patients:** Participants in clinical trials, especially those required to follow specific procedures at home.

### Justification

**The project is essential because:**

- **Speeding Up Trials:** Clinical trial protocols are lengthy and complex, and manually extracting schedules is inefficient. Automating this process saves time and resources.

- **Improving Patient Compliance:** Patients often struggle to follow complex clinical procedures at home. Clear, AI-generated visual instructions can help reduce errors and enhance adherence.

**Use Cases:**

- **Vendors**: Can use the platform to manage multiple clinical trials more efficiently.
- **Patients**: Will benefit from easy-to-follow instructional videos, improving the overall success of the trials.

### Programming language(s)

The project will primarily be developed using the following languages:

- **Python:** Backend processing, NLP, and AI model integration.
- **JavaScript (React JS):** Frontend development for the web interface.

### Programming tools / Tech stack

- **Backend:** Python (Django framework) for server-side logic, with most of the machine learning models and data processing being handled in Python.
- **Frontend:** React JS for building a responsive, user-friendly web interface.
- **Database:** MongoDB will be used for storing protocol documents, patient data, and generated timelines.
- **Machine Learning:** OpenAI models for generative AI and Adobe API for PDF extraction.
- **Other Tools:** Graphing tools for visualizing extracted timelines in an intuitive calendar format.

### Hardware

No non-standard hardware components are required. Users will interact with the application through standard web browsers.

### Learning Challenges

This project involves several technologies that require learning:

1. **Natural Language Processing (NLP):** Applying NLP for timeline extraction from clinical protocols.
2. **Generative AI Models:** Using text-to-image and text-to-video generation tools, which require understanding of generative AI and computer vision techniques.
3. **Adobe API Integration:** Understanding Adobe’s PDF extraction API to effectively parse clinical trial protocols.
4. **React JS:** While JavaScript is a common language, building a complex frontend application in React may present learning challenges.
5. **Clinical Trial Knowledge:** Gaining an understanding of how clinical trials are structured, including their phases, key outcomes (PROs, ClinROs), and the overall workflow involved in trial management.

### Breakdown of work

> Clearly identify who will undertake which parts of the project.
>
> It must be clear from the explanation of this breakdown of work both that each student is responsible for
> separate, clearly-defined tasks, and that those responsibilities substantially cover all of the work required
> for the project.

#### Lorena's Responsibilities

- Backend Development: Focus on the implementation of the machine learning models for the NLP timeline extraction.
- Integration of NLP Tools: Handle the integration of the NLP pipeline for extracting PRO and ClinRO timelines from protocols.
- Database Setup: Design and manage the MongoDB database for storing protocols and timelines.
- API Integration: Handle the integration with external services such as OpenAI’s generative models and Adobe’s PDF extraction service.

#### Student 2

> *Student 2 should complete this section.*

## System Architecture Diagram

<p align="center">
  <img src="./res/final_project_diagram-10.png" width="600px">
</p>

