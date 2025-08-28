# College Student Management System (Tkinter + SQLite)

## 📌 Overview

This is a **Student Management System** built using **Python Tkinter** for the GUI and **SQLite** for the database. It provides two portals:

* **Teacher Portal**: Manage students, record grades, and track attendance.
* **Student Portal**: Students can log in to view their profile, grades, and attendance records.

The system is designed for college use but can be adapted for schools or training institutes.

---

## 🚀 Features

### Teacher Portal

* Secure login (default credentials: `admin / admin`)
* Add, update, delete, and search students
* Manage grades (add, view, delete)
* Manage attendance (mark, view, delete)

### Student Portal

* Login with **Roll Number + Date of Birth (YYYY-MM-DD)**
* View personal profile
* View grades by subject & term
* View attendance records

### General

* Built-in SQLite database (`college_sms.db`)
* Auto-initializes tables and default teacher account
* Simple and clean Tkinter GUI

---

## 📂 Project Structure

```
student_management.py   # Main application file
college_sms.db          # SQLite database (auto-created on first run)
README.md               # Project documentation
```

---

## ⚙️ Installation & Setup

1. Clone or download this repository.
2. Ensure you have Python 3 installed.
3. Install required libraries (Tkinter and SQLite come pre-installed with Python):

   ```bash
   pip install tk
   ```

   *(If you're on Linux, you may need to install Tkinter via your package manager.)*
4. Run the application:

   ```bash
   python student_management.py
   ```

---

## 🔑 Default Credentials

* **Teacher Login**:

  * Username: `admin`
  * Password: `admin`
* **Student Login**:

  * First, add a student via the Teacher Portal.
  * Use their Roll Number and Date of Birth (YYYY-MM-DD format) to log in.

---

## 🛠️ Future Improvements

* Password hashing for security
* Export data to CSV/PDF reports
* Multi-teacher accounts with role management
* Attendance percentage auto-calculation
* Improved UI with themes
