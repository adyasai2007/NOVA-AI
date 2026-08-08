# NOVA HR AI Agent – System Architecture

## 1. Project Overview

NOVA is an intelligent HR management web application designed to simplify
employee management and HR support.

The system combines employee management, leave management, salary/payroll
management, resume screening, and an HR support chatbot into a single
web-based platform.

---

## 2. Architecture Overview

NOVA follows a lightweight client-server architecture.

```text
                    ┌──────────────────────┐
                    │       User / HR      │
                    │     Web Browser      │
                    └──────────┬───────────┘
                               │
                               │ HTTP
                               ▼
                    ┌──────────────────────┐
                    │      Flask App       │
                    │    nova_core.py      │
                    └──────────┬───────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
      ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
      │   Employee  │   │    Leave    │   │   Payroll   │
      │ Management  │   │ Management  │   │ Management  │
      └─────────────┘   └─────────────┘   └─────────────┘
             │                 │                 │
             └─────────────────┼─────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Employee Data     │
                    │   JSON / Local Data  │
                    └──────────────────────┘

                               │
                               ▼
                    ┌──────────────────────┐
                    │   Resume Analyzer    │
                    │       PyPDF2          │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Job Description +    │
                    │ Resume Text Analysis │
                    └──────────────────────┘

                               │
                               ▼
                    ┌──────────────────────┐
                    │    HR Support Bot    │
                    │   Offline Rule-Based │
                    │      Responses       │
                    └──────────────────────┘
