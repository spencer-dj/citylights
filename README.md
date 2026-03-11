# City-Lights Quote & Invoice Management System
A lightweight internal application was developed for **City-Lights**, a small electrical services startup, to streamline the creation of **client quotes and invoices**.

This system enables staff to quickly generate professional PDF documents, store them in a database, and retrieve past records through an easy-to-use web interface.
The system is currently under active development, with additional features planned.

---

## Overview

Small service businesses often rely on spreadsheets or manual paperwork to create quotes and invoices.
This system digitizes that workflow for **City-Lights**, improving efficiency, consistency, and record management.

The application is built with **FastAPI and PostgreSQL** and provides a simple web interface for generating and managing documents.

---

## Current Features

* Create **client quotes**
* Create **client invoices**
* Generate **PDF documents automatically**
* Store quote and invoice records in a **PostgreSQL database**
* Retrieve document history
* Search for previously generated documents
* Simple **web interface for staff use**

---

## Technology Stack

| Layer                  | Technology                 |
| ---------------------- | -------------------------- |
| Backend                | FastAPI                    |
| Database               | PostgreSQL                 |
| ORM                    | SQLAlchemy                 |
| Migrations             | Alembic                    |
| PDF Generation         | Python-based PDF utilities |
| Frontend               | HTML / CSS / JavaScript    |
| Environment Management | python-dotenv              |

---

## Project Structure

```text
citylights/
│
├── app/
│   ├── main.py              # FastAPI application entrypoint
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy database models
│   ├── schemas.py           # Pydantic request schemas
│
│   ├── routes/
│   │   └── routes.py        # API endpoints
│
│   ├── services/            # Business logic
│   │   ├── quote.py
│   │   ├── invoices.py
│   │   ├── pdf_conversion.py
│   │   └── search.py
│
├── frontend/
│   └── index.html
│
├── generated_quotes/        # Generated quote PDFs
├── generated_invoices/      # Generated invoice PDFs
│
├── migrations/
├── alembic/
│
├── run.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/spencer-dj/citylights.git
cd citylights
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment:

**Windows**

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root.

Example configuration:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/citylights
```

The `.env` file is excluded from version control to protect sensitive credentials.

---

## Running the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

Then open the application in your browser:

```
http://127.0.0.1:8000
```

---

## Database Migrations

Apply database migrations:

```bash
alembic upgrade head
```

Create a new migration:

```bash
alembic revision --autogenerate -m "migration description"
```

---

## Planned Improvements

The system is still under active development. Planned improvements include:

* Converting approved **quotes into invoices automatically**
* Cloud storage for generated documents (Google Drive or S3)
* User authentication and role management
* Improved dashboard interface
* Automatic document numbering and reporting

---

## Author

**Spencer Muzondi**

GitHub:
https://github.com/spencer-dj

