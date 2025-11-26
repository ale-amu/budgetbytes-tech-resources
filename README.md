# BudgetBytes — An Affordable Tech Resource Hub 
Composed of a Flask & Azure Storage app within Docker Container

## 1) Executive Summary
**The Problem:**  
In this day and age, the world heavily relies on technological advancement  hence students and early career technologists are required to come equipped with specific skills however they often struggle to find affordable yet credible technological resources, low-cost hardware, and a welcoming community of individuals like them within a single hub.

**The Solution:**  
BudgetBytes - A web application aimed at accumulating affordable yet credible tech resources in one central hub. This resource hub allows users to browse resources curated by other users while sharing some of their own. BudgetBytes is built with both a Flask backend and Azure Table Storage containerized using Docker, ensuring the system is portable and easy to reproduce.

## 2) System Overview

As we are no stranger to the fact that a variety of course content was touched on this year. It is necessary to highlight which of these primarily went into the construction of BudgetBytes.

### **Course Concept(s) Used**

Flask web API + Azure Table Storage + Azure Blob Storage (cloud data pipeline, persistent storage, REST API). 

***Architectural Diagram***

<img width="650" height="557" alt="Screenshot 2025-11-26 at 2 50 42 AM" src="https://github.com/user-attachments/assets/96664124-1665-4b7a-b554-b8f1f1064882" />

**Data/Models/Services:**

| Component              | Purpose                                            | Technology          |
| ---------------------- | -------------------------------------------------- | ------------------- |
| **Resource Metadata**  | name, category, tags, notes, created_at            | Azure Table Storage |
| **Logo/Image Uploads** | User-submitted images stored as blobs              | Azure Blob Storage  |
| **Frontend**           | Resource Hub UI, Submit Resource form              | Flask Templates     |
| **Backend API**        | Provides routes for uploads, list/create resources | Flask               |
| **Deployment**         | Reproducible environment                           | Docker              |


## 3) How to Run BudgetBytes
**Docker**
docker build -t budgetbytes:latest .
docker run --rm -p 8080:8080 --env-file .env budgetbytes:latest
Health Check:
curl http://localhost:8080/health

## 4) Design Decisions
**Why Flask + Azure?**
Flask and Azure Blob were utilized in the construction of this endeavor as Azure was the core web framework taught in class along with Azure Blob during Case 7; proving to be lightweight and ideal for building structured REST APIs. Moreover, Azure Blob NoSQL architecture removed the need for a traditional SQL database while providing a great binary pipeline. ***MongoDB and Firebase*** were a few alternatives considered  due to their schema flexibility and convenience however as these failed to be covered during the course, Azure remained the superior choice. 

**Tradeoffs:**
| Decision                | Tradeoff                                                  |
| ----------------------- | --------------------------------------------------------- |
| Azure Table Storage     | Harder querying vs SQL, but faster DevOps + simple schema |
| Blob Storage for images | Public access required to serve logos                     |
| Flask templates         | Simple but not dynamic (no React/Vue-style reactivity)    |

**Security & Privacy**
- No secrets committed—.env.example provided instead.
- Public container enables users easy viewing but requires sensitive data not be uploaded.

**Ops Considerations**
- Health endpoint included (/health).
- Smoke tests included.

## 5) Results & Evaluation
- Features Completed
- Resource Hub UI with categories + logos
- Submit a Resource page
- Flask backend with REST endpoints
- Azure Table Storage pipeline
- Azure Blob upload pipeline
- Docker container that runs the entire system
- Smoke test validation scripts

## 6) What’s Next
**Planned Improvements**
- Add live search + filtering
- Add optional dark mode toggle
- Add user accounts & authentication
- Add “favorites” or “save resources”

## 7) Links (Required)
GitHub Repo: <[REPO-URL](https://github.com/ale-amu/budgetbytes-tech-resources)>
Public Cloud App (optional): <[CLOUD-URL](https://budgetbytes-app.purplemeadow-43f006f4.canadacentral.azurecontainerapps.io/)>
