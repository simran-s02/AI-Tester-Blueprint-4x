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