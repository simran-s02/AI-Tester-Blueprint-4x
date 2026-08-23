# Assignment 01 — Job Tracker AI

## 📌 Overview

Job Tracker AI is a React-based web application designed to help users organize and manage their job applications through an interactive dashboard.

The application uses a Kanban-style workflow to organize jobs according to their application status and provides features for managing, searching, filtering, and tracking job applications.

---

## 🎯 Objective

The objective of this assignment is to build a functional job application tracker that allows users to:

- Add job applications
- Edit existing job applications
- View job details
- Delete jobs with confirmation
- Search job applications
- Filter job applications
- Clear active filters
- Move jobs between application stages
- View dynamic dashboard statistics
- Switch between light and dark mode
- Persist job data locally

---

## ✨ Features

### 📊 Dashboard Statistics

The dashboard displays statistics based on the stored job applications.

The statistics update dynamically as job data changes.

### ➕ Add Job

Users can create a new job application with information such as:

- Company
- Job title
- Application status
- Date applied
- Salary
- Resume
- LinkedIn URL
- Notes

### ✏️ Edit Job

Existing job applications can be edited through the job action menu.

### 👁️ View Details

Users can access the **View Details** option from a job's action menu.

### 🗑️ Delete Job

Users can delete a job application from the action menu.

A confirmation dialog appears before deletion to prevent accidental removal.

Users can cancel the deletion or confirm the deletion.

### 🔎 Search

Users can search job applications by:

- Company name
- Job title

### 🎯 Filters

Job applications can be filtered by:

- Application status
- Application date

Available date filters include:

- Today
- Last 7 days
- Last 30 days

The **Clear Filters** option removes the active search and filters.

### 🖱️ Drag and Drop

The application uses a Kanban board where jobs can be moved between application stages using drag and drop.

The job status is updated when the job is moved to another column.

### 🌙 Dark Mode

The application supports both light and dark modes.

### 💾 Local Data Persistence

Job application data is stored locally using IndexedDB.

This allows job data to remain available after refreshing the application.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| React | Frontend application |
| Vite | Development server and build tool |
| JavaScript | Application logic |
| Tailwind CSS | Styling |
| IndexedDB | Local data persistence |
| `@dnd-kit/core` | Drag-and-drop functionality |
| `lucide-react` | Icons |
| ESLint | Code linting |

---

## 🏗️ Application Architecture

The application follows a component-based React architecture.

```text
User Interface
      │
      ▼
    App.jsx
      │
      ├── Header
      ├── DashboardStats
      ├── SearchBar
      ├── KanbanBoard
      │      │
      │      └── KanbanColumn
      │             │
      │             └── JobCard
      │
      └── JobModal
             │
             ▼
          useJobs Hook
             │
             ▼
        Database Layer
             │
             ▼
          IndexedDB
```

---

## 📁 Project Structure

```text
Assignment_01_Job_Tracker_AI/
│
├── job-tracker/
│   └── React application
│
├── node_modules/
│   └── Installed project dependencies
│
├── package.json
├── package-lock.json
└── README.md
```

> `node_modules/` is generated automatically by npm and should be excluded from version control using `.gitignore`.

---

## 🚀 Installation & Setup

### Prerequisites

Make sure the following are installed:

- Node.js
- npm
- Git

You can verify the installations using:

```bash
node --version
npm --version
git --version
```

---

## 📦 Install Dependencies

From the `Assignment_01_Job_Tracker_AI` directory, run:

```bash
npm install
```

This installs the dependencies required by the project.

---

## ▶️ Run the Application

Navigate into the React application:

```bash
cd job-tracker
```

Start the Vite development server:

```bash
npm run dev
```

After starting the development server, Vite will display the local URL.

Open the application at:

```text
http://localhost:5173/
```

---

## 🛑 Stop the Application

To stop the development server, press:

```text
Ctrl + C
```

in the terminal where Vite is running.

---

## 🧪 Functional Verification

### Job Management

- Add a job
- Edit a job
- View job details
- Open the job action menu
- Delete a job
- Cancel deletion
- Confirm deletion

### Search and Filters

- Search by company
- Search by job title
- Filter by status
- Filter by date
- Clear filters

### Kanban Board

- Drag a job between columns
- Verify that its status changes
- Refresh the application
- Verify that job data remains available

### Dashboard

- Verify that dashboard statistics reflect the stored jobs

### UI

- Toggle dark mode
- Open and close job action menus
- Use the Kanban board

---

## 💾 Data Persistence

The application uses IndexedDB for local storage of job application data.

This allows job data to remain available after refreshing the application.

No external backend service is required for the implemented job tracking functionality.

---

## 📚 Chapter Information

**Chapter:** 05 — Job Tracker AI

**Assignment:** 01 — Job Tracker AI

**Application:** Job Tracker AI

**Development Server:** Vite

**Local URL:** `http://localhost:5173/`

**Storage:** IndexedDB

---

## 👤 Author

**Simran Satpathy**

---

## 📄 License

This project was created for educational and learning purposes.