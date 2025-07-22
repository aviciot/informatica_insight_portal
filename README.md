# Informatica Insights Portal

## 🧭 Overview


The **Informatica Insights Portal** is a web-based dashboard , designed to provide a clear and organized view of Informatica metadata.

It allows users to:
- Explore folders, workflows, sessions, command tasks, and database connections
- Navigate metadata with an intuitive and interactive interface
- Analyze relationships and dependencies across Informatica components

In addition to metadata exploration,
the portal provides advanced capabilities to **analyze and visualize Informatica performance statistics** at various levels — from full workflows to individual sessions.  
helping teams identify inefficiencies, performance bottlenecks, and execution anomalies (baed ML scikit)

To ensure optimal performance and responsiveness,
the application fetch once once the data from PROD DB and caches all relevant metadata and execution data in a local database .  
This reduces the load on production Informatica environments and allows the portal to run independently with fast access to large-scale datasets.


> This portal is useful for developers, analysts, and admins looking to trace process dependencies, identify issues, and gain operational insights into Informatica workflows.

📘 **Documentation** available at:  
👉 [https://aviciot.github.io/informatica_insight_portal/](https://aviciot.github.io/informatica_insight_portal/)

---

## 🔑 Key Features

### 🔐 1. Authentication & Role-Based Access  
- Admin and user roles with permission control  - allowing fine-grained restrictions to sections or operations based on user roles.

### ⚙️ 2. YAML-Based Configuration  
- Centralized settings via `config.yaml`  
- Environment and database configuration management  

### 🗃️ 3. Informatica Metadata Exploration  
- View folders, workflows, sessions, command tasks, and connections  
- Search and filter processes by keyword or metadata  

### 🌳 4. Workflow Hierarchy Visualization  
- Interactive tree view of:
  - Folders → Workflows → Sessions → Scripts  
  - Command Tasks  
  - Connections  
  - Table Dependencies  
- Trace all processes related to a specific database or connection 

### 🧩 5. Session & Command Task Insights  
- Display of session execution data  
- Insight into command task usage and linkages  
- Identify broken or missing connections  

### 📈 6. Performance Insights  
- Visualize workflow and session execution durations  
- Spot long-running or abnormal tasks  
- Filter by date range, workflow, or session type  
- Useful for performance tuning and troubleshooting  

## ⚡ High-Performance Architecture

The portal is designed for speed and low impact on production systems.

All relevant Informatica metadata and execution statistics is cached in an internal database , allowing the app to:

- Minimize direct queries to the Informatica repository  
- Operate independently from the production environment  
- Deliver fast performance even for large datasets 

This approach ensures a smooth, responsive user experience while preserving system stability.

Note ,This is the **very first release**  — focused on foundational features for metadata visibility, performance monitoring, and system understanding.
More to come....

---

## 💡 Example Use Case

> *“Find all workflows connected to Database X and detect any sessions that consistently run over 30 minutes.”*

---

## 🛠️ Additional Functionalities

- **Search by Connection or Table Name**  
- **Compare Workflow Definitions** *(Planned)*  
- **Admin Panel** for cache reset and config control  
- **Export to CSV** *(Planned)*

---

## 📦 Tech Stack

- Python  
- SQLAlchemy  
- SQLite / PostgreSQL /Oracle 
- YAML for configuration  


---
## 📷 Screenshots

Explore the key features of the **Informatica Insights Portal** through the following screenshots.

---

## 📊 Informatica Insights & Workflow Explorer

### Home Page
![alt text](image-1.png)

Full visibility into Informatica components: workflows, sessions, connections, and command tasks.

### 📋 Tabular View  
Flat table showing all components in a workflow — sessions, commands, dependencies, and more.  
<img width="1526" height="824" alt="Workflow Table View" src="https://github.com/user-attachments/assets/c209fef4-0248-4277-8aa7-641881efcdaf" />

### 🌲 JSON Tree View  
Visual representation of workflow structure:  
*Workflows → Sessions → Commands → Connections → Related Tables*  
<img width="747" height="459" alt="Workflow JSON View" src="https://github.com/user-attachments/assets/8b11b2e7-1ea9-4ee9-b57d-f681ad462e4a" />

*DB details and commands(if any)
<img width="703" height="655" alt="image" src="https://github.com/user-attachments/assets/4f9023eb-1c77-4770-bdab-5e60ef84f720" />

---

## 🗃️ Database & Tables usage insight

### 🔎 Find proccesses by Host / Connection  
Find all processes interacting with a specific database or connection.  
<img width="659" height="785" alt="DB Related Processes" src="https://github.com/user-attachments/assets/49fdbc54-8aa2-4eaf-be99-289cf5111711" />

### 📌 Find processess by Table Name  
Search workflows by referenced table name (source/target/attribute match).  
<img width="1441" height="641" alt="Table Related Processes" src="https://github.com/user-attachments/assets/7e5f2353-9f70-487c-98bc-24694816488a" />


---

## 📈 Performance Analytics

Visualize workflow and session execution trends over time. Useful for identifying long-running tasks and performance issues.

Compare Average Runtime of Multiple Workflows
<img width="1544" height="761" alt="image" src="https://github.com/user-attachments/assets/f7c79399-432b-490f-8a1b-e423b4db6574" />

Analyze workflow execution trends, overlaps, and anomalies.

<img width="1553" height="743" alt="image" src="https://github.com/user-attachments/assets/07c9e413-c0a1-44d8-84c1-35637b0c56fd" />

Longest & Shortest Workflow Runs 
<img width="1540" height="347" alt="image" src="https://github.com/user-attachments/assets/6063d96f-7747-42a6-9f67-7d6a21ae7afb" />

With the workflow in context - Session Stats  
<img width="518" height="338" alt="image" src="https://github.com/user-attachments/assets/baad7b70-4362-4968-b6c8-96647c988426" />

Zoom in on specific run date and see all sessions run information as date, duration error and erros message 
<img width="815" height="418" alt="image" src="https://github.com/user-attachments/assets/bbcae800-9601-4e21-b720-0bae2870b372" />

## 📈 ML based Analysis ...(wip)

Workflow trends 
<img width="1811" height="843" alt="image" src="https://github.com/user-attachments/assets/e251ce7e-468f-4458-954d-430c6e560f93" />

Daily & Hourly Trends
<img width="1824" height="879" alt="image" src="https://github.com/user-attachments/assets/1bc154a1-384f-490c-98d9-a64ac053233c" />

HeatMap
For the selected workflow, see how average runtime varies by day and hour 
<img width="1457" height="607" alt="image" src="https://github.com/user-attachments/assets/29ec4ffe-526f-4fe6-99c0-bb10d76f62a9" />

Anomalous Insights for Workflow in context 
<img width="884" height="302" alt="image" src="https://github.com/user-attachments/assets/c55de179-f197-4922-a03c-9b4203ee55c4" />

Sessions Runtime Anomalies  for the workflow in context - user allow to exclude specific session,worklet
<img width="756" height="418" alt="image" src="https://github.com/user-attachments/assets/14c523b5-5c53-4f82-a163-5e52016ea81d" />

Overlap impact - in many case , some workflow shows bad performance as they impacted while running in parallel to other workflow(WIP)

---

## ⚙️ Admin Panel

Manage users, roles, and track login activity from the built-in admin panel.

### 🔑 Manage Users  
![Admin Panel](screenshots/admin_panel.png)

### 👥 Manage Roles  
<img width="1194" height="801" alt="Manage Roles" src="https://github.com/user-attachments/assets/94ead11f-c9a1-4804-8bcf-885a76088146" />

### 📊 Login History  
Track when users accessed the portal.  
<img width="1226" height="382" alt="Login History" src="https://github.com/user-attachments/assets/9da695fc-b7fa-423a-96e3-e3a1641fe565" />

For development purpose , the app allows bypassing the logging screen and security .

---

## 🔧 Configuration Management

YAML-based config editor and internal database tools.

### 📝 Live Config Editor  
Edit `config.yaml` directly from the UI.  
<img width="407" height="628" alt="Live Config Editor" src="https://github.com/user-attachments/assets/4a36bef4-9dbd-4404-800d-d1f948e8767a" />

### 🗃️ Manage Insight Data Sources  
Connect to Informatica metadata via DB connection or `tnsnames.ora`/`odbc.ini`.  
<img width="885" height="850" alt="Insight DB Sources" src="https://github.com/user-attachments/assets/76ffbc2b-6308-41b9-add4-d6fd9bfeec5d" />

### 📂 View Insight Internal Tables  
Explore the structure of the internal SQLite/PostgreSQL Insight DB.  
<img width="1063" height="867" alt="Insight DB Tables" src="https://github.com/user-attachments/assets/ec17b193-2d2c-40ae-ba0d-be782a77290f" />

---



## 📬 Contact

For questions or contributions, please contact aviciot@gmail.com