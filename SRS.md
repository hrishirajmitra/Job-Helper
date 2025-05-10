# Software Requirements Specification (SRS) Document

## 1. Introduction

### 1.1 Purpose

The purpose of this document is to define the software requirements for a career planning application that utilizes multiple microservices and LLMs to help users develop personalized roadmaps to reach their target job roles. The application extracts skills from job descriptions, recommends learning paths, and provides continuous support through evaluations and a Q\&A system.

### 1.2 Scope

This application is designed to:

* Parse job descriptions and extract detailed skill requirements.
* Categorize skills into Technical, Soft, Domain-Specific, Certifications, and Experience.
* Generate a personalized roadmap for skill acquisition and interview readiness.
* Use microservices to handle different aspects: parsing, recommendation, evaluation, user management, Q\&A, and feedback.
* Implement an LLM-enhanced feedback loop to evaluate and refine roadmap and response quality.
* Offer a general Q\&A assistant for guidance and preparation help.

### 1.3 Definitions, Acronyms, and Abbreviations

* LLM: Large Language Model
* NLP: Natural Language Processing
* API: Application Programming Interface
* UI: User Interface

## 2. Overall Description

### 2.1 Product Perspective

The system consists of several microservices communicating via REST APIs and includes the following components:

* Job Description Parsing Service
* Skill Categorization and Extraction Service
* Roadmap Generation Service
* Evaluation and Improvement Service (LLM-based)
* Q\&A Guidance Service (LLM-based)
* User Management and Progress Tracking Service
* Frontend Client (Web-based)

### 2.2 Product Functions

* Upload or paste job description.
* Extract and classify skills from job description.
* Generate a phase-wise learning roadmap.
* Evaluate generated outputs using a secondary LLM.
* Allow user interaction with a Q\&A assistant.
* Store and track user progress and preferences.
* Provide feedback and continuous improvement options.

### 2.3 User Classes and Characteristics

* **End User**: Job seekers aiming to target specific roles.
* **Admin/Trainer**: (Optional) For managing templates, feedback models.

### 2.4 Operating Environment

* Web Browser (Chrome, Firefox, Safari)
* Backend on cloud platforms (AWS/GCP/Azure)
* Database: MongoDB/PostgreSQL

### 2.5 Design and Implementation Constraints

* Use of LLMs requires integration with APIs (e.g. Anthropic).
* GDPR compliance for storing user data.

### 2.6 User Documentation

* User Manual
* FAQ and Troubleshooting Guide

## 3. Specific Requirements

### 3.1 Functional Requirements

1. **Input Job Description**

   * Users can paste or upload job descriptions.

2. **Skill Extraction and Categorization**

   * The system extracts and categorizes skills (Technical, Soft, etc.)

3. **Roadmap Generation**

   * A multi-phase roadmap is generated for each job description.

4. **LLM Evaluation Loop**

   * A second LLM evaluates output quality (e.g., roadmap accuracy, skill mapping) and iteratively improves it.

5. **Q\&A Assistant**

   * An LLM-based conversational assistant helps users clarify doubts or request custom guidance.

6. **Progress Tracking**

   * Users can mark skills as learned or phases as complete.

7. **User Profile Management**

   * Users can log in, view history, update preferences.

### 3.2 Non-Functional Requirements

* **Performance**: Output within 2-5 seconds for most LLM queries.
* **Reliability**: 99.9% uptime for core services.
* **Usability**: Intuitive and beginner-friendly UI/UX.
* **Scalability**: Microservices can scale independently.
* **Security**: Role-based access, encrypted data storage.

### 3.3 Interface Requirements

* **Frontend**: Web interface built with React or similar.
* **Backend**: REST APIs for service communication.
* **LLM APIs**: Integration with LLM endpoints.
* **Database**: Store user data, skill maps, roadmaps, Q\&A logs.

## 4. Appendices

* A. Sample Job Descriptions
* B. Example Skill Extraction Output
* C. Mock UI Screens
* D. Entity Relationship Diagram (ERD) – optional

---