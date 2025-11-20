# BudgetBytes — An Affordable Tech Resource Hub 
Composed of a Flask & Azure Storage app within Docker

## 1) Executive Summary
**The Problem:**  
In this day and age, the world heavily relies on technological advancement  hence students and early career technologists are required to come equipped with specific skills however they often struggle to find affordable yet credible technological resources, low-cost hardware, and a welcoming community of individuals like them within a single hub.

**The Solution:**  
BudgetBytes - A web application aimed at accumulating affordable yet credible tech resources in one central hub. This resource allows users to browse a curated resources while sharing some of their own uploaded to Azure Blob Storage. BudgetBytes is built with both a Flask backend and Azure Table Storage containerized using Docker, ensuring the system is portable and easy to reproduce.

## 2) System Overview

As we are no stranger to the fact that a variety of course content was touched on this year. It is necessary to highlight which of these primarily went into the construction of BudgetBytes.


### **Course Concept(s) Used**

Flask web API + Azure Table Storage + Azure Blob Storage (cloud data pipeline, persistent storage, REST API). 

### **Architecture Diagram**

---
## 2) How to Run BudgetBytes
Docker
docker build -t budgetbytes .
docker run --rm -p 8080:8080 --env-file .env budgetbytes
Health Check
curl http://localhost:8080/health

