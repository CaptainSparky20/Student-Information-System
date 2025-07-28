# Student Information System

## About Us

We, the students of CS4D Group, created this Student Information System as our final year project.

## Overview

The **Student Information System (SIS)** is a web application designed to manage academic records and interactions for students, lecturers, and administrators. It simplifies data management, role-based access, and communication within an educational institution.

## Key Features

* **Authentication System:** Secure login for Students, Lecturers, and Admins
* **Role-Based Dashboards:**
  * **Student Dashboard:** View grades, course schedules, and profile info
  * **Lecturer Dashboard:** Manage student grades, attendance, and course materials
  * **Admin Dashboard:** Manage users, courses, and announcements
* **Profile Management:** Update personal details for all user types
* **Course Management:** Enroll in courses, assign lecturers, and view syllabi
* **Responsive Design:** Mobile-friendly UI using Tailwind CSS

## Tech Stack

* **Frontend:** HTML, Tailwind CSS, JavaScript
* **Backend:** Django (Python)
* **Database:** SQLite (default, can switch to MariaDB/PostgreSQL for production)
* **Admin Interface:** Django Admin, Django Templates

---

## 🚀 Quick Start

### 1. Clone the Repository

##### git clone https://github.com/your-repo/student-information-system.git
##### cd student-information-system

### 2. Setup and activate a virtual environemnt
##### Set-ExecutionPolicy Unrestricted -Scope Process
##### .\venv\Scripts\activate

### 3. Run the server
##### cd .\SIS\
##### python manage.py runserver
