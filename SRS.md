# **Software Requirements Specification (SRS)**

**Project Title**: AI-Powered Career Roadmap Builder
**Document Version**: 1.0
**Date**: May 10, 2025

---

## **1. Introduction**

### **1.1 Purpose**

The purpose of this system is to help users achieve their desired job by analyzing job descriptions using LLM APIs to extract skill requirements (technical, soft, domain-specific, certifications, and experience), and then generating a personalized, structured learning roadmap based on their current skills and career aspirations.

### **1.2 Scope**

This application is built using a **microservices architecture** and leverages **LLMs (Large Language Models)** for skill extraction. The system will:

* Accept job descriptions as input.
* Call an AI model API to extract all relevant skills and experience.
* Categorize extracted skills into well-defined buckets.
* Assess user’s current skills via profile or quiz.
* Generate a detailed roadmap for skill acquisition and interview readiness.
* Track progress and provide curated learning resources.

### **1.3 Definitions, Acronyms, and Abbreviations**

| Term | Description                       |
| ---- | --------------------------------- |
| LLM  | Large Language Model              |
| API  | Application Programming Interface |
| NLP  | Natural Language Processing       |
| UI   | User Interface                    |
| REST | Representational State Transfer   |
| JWT  | JSON Web Token                    |

---

## **2. Overall Description**

### **2.1 Product Perspective**

This is a **modular web application** consisting of multiple services:

* **Job Analysis Service** (NLP-based skill extraction)
* **User Profile Service**
* **Roadmap Generator Service**
* **Resource Aggregation Service**
* **Progress Tracker Service**

Each service is independent and communicates over REST APIs. LLM integrations are stateless and triggered by job input.

### **2.2 Product Functions**

* Parse and analyze job descriptions.
* Extract and categorize skills.
* Compare extracted skills with user profile.
* Generate phase-wise learning roadmap.
* Offer curated learning resources and project ideas.
* Track learning progress.
* Provide roadmap updates as user improves.

### **2.3 User Classes and Characteristics**

| User Class   | Description                                                                                               |
| ------------ | --------------------------------------------------------------------------------------------------------- |
| General User | Individuals seeking career advancement. Can upload job descriptions, manage profile, and follow roadmaps. |
| Admin        | Manages LLM configurations, monitors service health, moderates content.                                   |

### **2.4 Operating Environment**

* **Frontend**: React (Vite) + Tailwind
* **Backend**: Node.js + Express
* **Database**: MongoDB (Mongoose)
* **LLM API**: OpenAI or similar
* **Deployment**: Cloud-based (Render / Heroku / AWS)

### **2.5 Design and Implementation Constraints**

* Must ensure API rate limits for LLMs are respected.
* Skill categorization logic must follow a consistent schema.
* Support modular roadmap updates as new roles emerge.

---

## **3. External Interface Requirements**

### **3.1 User Interfaces**

* Upload job description (textarea or PDF).
* Dashboard with skill comparison chart.
* Phase-wise roadmap view with resource links.
* Progress tracker and milestone editor.

### **3.2 Hardware Interfaces**

None – web application.

### **3.3 Software Interfaces**

| System                | Interface        | Purpose                                                     |
| --------------------- | ---------------- | ----------------------------------------------------------- |
| LLM API               | RESTful          | Send job description and receive skill set                  |
| GitHub API (optional) | OAuth, repo scan | Auto-fetch user skills via repositories                     |
| Learning Platforms    | Scraping/API     | Recommend resources (e.g., YouTube, Coursera, freeCodeCamp) |

### **3.4 Communications Interfaces**

HTTPS protocol for all service communications with secure tokens (JWT) and OAuth2 where needed.

---

## **4. System Features**

### **4.1 Job Description Analyzer**

**Description**: Accepts job input and invokes the LLM for detailed skill extraction.
**Inputs**: Freeform job description text
**Outputs**: Structured list of skills with categories and context
**Dependencies**: LLM API
**Errors**: Malformed input, API rate limit

### **4.2 Skill Categorizer**

**Description**: Categorizes extracted skills into defined buckets.
**Categories**:

* Technical
* Soft
* Domain-Specific
* Certifications
* Experience

### **4.3 User Profile Management**

**Description**: Stores and updates user's existing skills, qualifications, and experience.
**Data Fields**: Skills, certifications, education, uploaded resume, quiz scores

### **4.4 Roadmap Generator**

**Description**: Compares user profile with job skillset and generates a roadmap in phases.
**Phases**:

1. Foundations
2. Specialized Knowledge
3. Project Work
4. Interview Preparation
   **Output**: Interactive roadmap with links, project ideas, and deadlines

### **4.5 Resource Recommender**

**Description**: Maps each skill in the roadmap to curated learning resources.
**Sources**: YouTube, Medium, official docs, MOOCs, GitHub

### **4.6 Progress Tracker**

**Description**: Allows users to mark milestones, track learning, and auto-update roadmap based on achievements.

---

## **5. Non-Functional Requirements**

### **5.1 Performance Requirements**

* API response under 3 seconds for skill extraction
* Concurrent job analysis support for 100+ users

### **5.2 Security Requirements**

* JWT for user authentication
* Input sanitization for job descriptions
* Rate-limiting to prevent abuse of LLM API

### **5.3 Maintainability**

* Microservice architecture enables independent deployment and upgrades

### **5.4 Scalability**

* Horizontally scalable backend
* Stateless API communication

### **5.5 Usability**

* Mobile-responsive interface
* Accessibility-compliant (WCAG 2.1 AA)

---

## **6. Appendices**

### **6.1 Skill Schema Sample**

```json
{
  "skillName": "Distributed Systems",
  "category": "Technical",
  "context": "Mentioned as essential for designing scalable backend services"
}
```

