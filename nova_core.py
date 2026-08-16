from flask import Flask, render_template, request
from PyPDF2 import PdfReader
import os
import re
import json

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
EMPLOYEE_FILE = "employees.json"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ==============================
# EMPLOYEE DATA
# ==============================

def load_employees():

    if not os.path.exists(EMPLOYEE_FILE):

        return {}

    with open(EMPLOYEE_FILE, "r") as file:

        return json.load(file)


def save_employees(employees):

    with open(EMPLOYEE_FILE, "w") as file:

        json.dump(employees, file, indent=4)


# ==============================
# PDF READER
# ==============================

def extract_text(pdf_path):

    text = ""

    reader = PdfReader(pdf_path)

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:

            text += page_text.lower()

    return text


# ==============================
# MAIN PAGE
# ==============================

@app.route("/", methods=["GET", "POST"])
def home():

    result = ""
    leave_result = ""
    salary_result = ""
    chat_result = ""
    employee_result = ""

    employees = load_employees()

    if request.method == "POST":

        action = request.form.get("action")


        # ==============================
        # RESUME ANALYZER
        # ==============================

        if action == "resume":

            job = request.form["job"].lower()

            resume = request.files["resume"]

            filepath = os.path.join(
                UPLOAD_FOLDER,
                resume.filename
            )

            resume.save(filepath)

            resume_text = extract_text(filepath)

            skills = list(
                set(
                    re.findall(
                        r"[A-Za-z+#.]+",
                        job
                    )
                )
            )

            matched = []
            missing = []

            for skill in skills:

                if len(skill) < 3:

                    continue

                if skill.lower() in resume_text:

                    matched.append(skill)

                else:

                    missing.append(skill)


            total_skills = len(matched) + len(missing)


            if total_skills == 0:

                score = 0

            else:

                score = int(
                    len(matched)
                    / total_skills
                    * 100
                )


            if score >= 75:

                recommendation = "HIRE"

            elif score >= 50:

                recommendation = "CONSIDER"

            else:

                recommendation = "REJECT"


            result = f"""
========================================
          NOVA HR AI REPORT
========================================

MATCH SCORE:
{score}%

MATCHED SKILLS:
{chr(10).join("- " + x for x in matched)}

MISSING SKILLS:
{chr(10).join("- " + x for x in missing)}

RECOMMENDATION:
{recommendation}

========================================
"""


        # ==============================
        # LEAVE MANAGEMENT
        # ==============================

        elif action == "leave":

            emp_id = request.form["emp_id"]

            days = int(request.form["days"])


            if emp_id not in employees:

                leave_result = """
❌ EMPLOYEE NOT FOUND

Please enter a valid Employee ID.
"""

            else:

                employee = employees[emp_id]

                current_leave = employee.get(
                    "leave_taken",
                    0
                )

                remaining = 30 - current_leave


                if days <= 0:

                    leave_result = """
❌ INVALID NUMBER OF DAYS
"""


                elif days > remaining:

                    leave_result = f"""
❌ LEAVE REQUEST REJECTED

Employee:
{employee["name"]}

Requested:
{days} days

Leave Taken:
{current_leave} days

Remaining:
{remaining} days
"""


                else:

                    employee["leave_taken"] = (
                        current_leave + days
                    )

                    save_employees(employees)

                    new_remaining = (
                        30
                        - employee["leave_taken"]
                    )

                    leave_result = f"""
========================================

          🏖 LEAVE APPROVED

========================================

Employee:
{employee["name"]}

Department:
{employee["department"]}

Leave Requested:
{days} days

Total Leave Taken:
{employee["leave_taken"]} days

Remaining Leave:
{new_remaining} days

STATUS:
✅ APPROVED

========================================
"""


        # ==============================
        # PAYROLL
        # ==============================

        elif action == "salary":

            emp_id = request.form["salary_emp_id"]

            basic = float(
                request.form["basic_salary"]
            )

            hra_percent = float(
                request.form["hra"]
            )

            da_percent = float(
                request.form["da"]
            )

            deduction = float(
                request.form["deduction"]
            )


            if emp_id not in employees:

                salary_result = """
❌ EMPLOYEE NOT FOUND
"""

            else:

                employee = employees[emp_id]

                hra_amount = (
                    basic * hra_percent / 100
                )

                da_amount = (
                    basic * da_percent / 100
                )

                gross_salary = (
                    basic
                    + hra_amount
                    + da_amount
                )

                net_salary = (
                    gross_salary
                    - deduction
                )


                salary_result = f"""
========================================

             💰 PAYSLIP

========================================

Employee ID:
{emp_id}

Employee Name:
{employee["name"]}

Department:
{employee["department"]}

----------------------------------------

Basic Salary:
₹{basic:,.2f}

HRA:
₹{hra_amount:,.2f}

DA:
₹{da_amount:,.2f}

----------------------------------------

Gross Salary:
₹{gross_salary:,.2f}

Deduction:
₹{deduction:,.2f}

----------------------------------------

NET SALARY:
₹{net_salary:,.2f}

========================================
"""


       # ==============================
# HR SUPPORT BOT - GEMINI AI
# ==============================

elif action == "chat":

    message = request.form["message"]

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:

        chat_result = """
❌ GEMINI API KEY NOT FOUND

Please check the GEMINI_API_KEY
environment variable in Render.
"""

    else:

        try:

            from google import genai

            client = genai.Client(
                api_key=api_key
            )

            prompt = f"""
You are NOVA, an AI HR Assistant.

Help employees with:
- Salary and payroll
- Leave
- Attendance
- Holidays
- Login problems
- HR complaints
- General HR questions

Be professional, friendly and concise.

Employee message:
{message}

Give a helpful response.
"""

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            chat_result = f"""
🤖 NOVA AI

{response.text}
"""

        except Exception as e:

            chat_result = f"""
❌ NOVA AI ERROR

Unable to connect to Gemini.

Please try again later.
"""

        # ==============================
        # ADD EMPLOYEE
        # ==============================

        elif action == "add_employee":

            emp_id = request.form[
                "new_emp_id"
            ].strip()

            name = request.form[
                "new_name"
            ].strip()

            department = request.form[
                "new_department"
            ].strip()

            salary = float(
                request.form["new_salary"]
            )


            if emp_id in employees:

                employee_result = """
❌ EMPLOYEE ALREADY EXISTS
"""

            else:

                employees[emp_id] = {

                    "name": name,

                    "department": department,

                    "leave_taken": 0,

                    "salary": salary
                }

                save_employees(employees)

                employee_result = f"""
========================================

        ✅ EMPLOYEE ADDED

========================================

Employee ID:
{emp_id}

Name:
{name}

Department:
{department}

Basic Salary:
₹{salary:,.2f}

Leave Taken:
0 days

Status:
ACTIVE

========================================
"""


    # ==============================
    # DASHBOARD DATA
    # ==============================

    employee_list = list(
        employees.items()
    )


    total_employees = len(
        employees
    )


    total_leave = sum(
        emp.get("leave_taken", 0)
        for emp in employees.values()
    )


    total_salary = sum(
        emp.get("salary", 0)
        for emp in employees.values()
    )


    return render_template(
        "index.html",
        result=result,
        leave_result=leave_result,
        salary_result=salary_result,
        chat_result=chat_result,
        employee_result=employee_result,
        employee_list=employee_list,
        total_employees=total_employees,
        total_leave=total_leave,
        total_salary=total_salary
    )


# ==============================
# START APPLICATION
# ==============================

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)
