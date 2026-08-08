# Resume Analysis Skill

## Purpose

This custom skill enables NOVA to analyze resumes against job descriptions
and provide recruiters with a quick candidate-match assessment.

## Inputs

The skill accepts:

1. A PDF resume
2. A job description

## Processing Pipeline

```text
Resume PDF
    ↓
Text Extraction
    ↓
Resume Text
    ↓
Job Description
    ↓
Skill/Keyword Comparison
    ↓
Matched Skills
    ↓
Missing Skills
    ↓
Match Assessment
