import streamlit as st
import pandas as pd
from datetime import date, timedelta

# =====================================================
# INITIALIZE SESSION STATE
# =====================================================

def init_state():
    if "subjects" not in st.session_state:
        st.session_state.subjects = []   # list of dicts
    if "tasks" not in st.session_state:
        st.session_state.tasks = []      # list of dicts
    if "exams" not in st.session_state:
        st.session_state.exams = []      # list of dicts
    if "next_id" not in st.session_state:
        st.session_state.next_id = 1
    if "schedule" not in st.session_state:
        st.session_state.schedule = []   # generated study plan (list of dicts)


def get_new_id():
    nid = st.session_state.next_id
    st.session_state.next_id += 1
    return nid


def get_subject_names():
    return [s["name"] for s in st.session_state.subjects]


# =====================================================
# SIDEBAR – GLOBAL SETTINGS
# =====================================================

def sidebar():
    st.sidebar.title("🎓 Study Planner")
    st.sidebar.caption("Student-friendly planner: subjects, tasks, exams, and smart schedule.")

    student_name = st.sidebar.text_input("Your name", value="Student")

    st.sidebar.markdown("### Plan Settings")
    daily_hours = st.sidebar.slider("Study hours per day for planning", 1, 16, 4)
    num_days = st.sidebar.slider("Number of days to plan", 1, 14, 5)

    st.sidebar.info(
        "These settings are used by the **Generate Study Plan** tab "
        "to create a day-wise schedule."
    )

    return student_name, daily_hours, num_days


# =====================================================
# DASHBOARD TAB
# =====================================================

def dashboard_tab(student_name):
    st.header(f"📊 Dashboard – Hello, {student_name}!")

    today = date.today()
    st.write(f"**Today:** {today.strftime('%A, %d %B %Y')}")

    # Today's schedule if generated
    st.subheader("🕒 Today's Study Plan")
    today_plan = [s for s in st.session_state.schedule if s["date"] == today]

    if today_plan:
        df_today = pd.DataFrame(today_plan)
        df_today_display = df_today[["time_block", "subject", "task_title", "planned_hours"]]
        df_today_display.columns = ["Time Block", "Subject", "Task", "Hours"]
        st.table(df_today_display)
    else:
        st.info("No generated study plan for today yet. Go to **Generate Study Plan** tab.")

    # Upcoming tasks
    st.subheader("📌 Upcoming Study Tasks (Next 7 Days)")
    upcoming_tasks = []
    for t in st.session_state.tasks:
        if t["status"] == "Pending" and t["due_date"] is not None:
            if today <= t["due_date"] <= today + timedelta(days=7):
                upcoming_tasks.append(t)

    if upcoming_tasks:
        df_up = pd.DataFrame(upcoming_tasks)
        df_up_display = df_up[["title", "subject", "due_date", "estimated_hours", "importance"]]
        df_up_display.columns = ["Task", "Subject", "Due Date", "Est. Hours", "Importance (1–5)"]
        st.table(df_up_display)
    else:
        st.info("No pending tasks due in the next 7 days.")

    # Upcoming exams
    st.subheader("📝 Upcoming Exams")
    upcoming_exams = [e for e in st.session_state.exams if e["date"] >= today]
    upcoming_exams.sort(key=lambda x: x["date"])

    if upcoming_exams:
        df_ex = pd.DataFrame(upcoming_exams)
        df_ex_display = df_ex[["subject", "title", "date", "syllabus"]]
        df_ex_display.columns = ["Subject", "Exam", "Date", "Syllabus / Chapters"]
        st.table(df_ex_display)
    else:
        st.info("No future exams added yet.")


# =====================================================
# SUBJECTS TAB
# =====================================================

def subjects_tab():
    st.header("📚 Subjects")

    with st.form("add_subject_form", clear_on_submit=True):
        name = st.text_input("Subject name", placeholder="e.g. Data Structures")
        teacher = st.text_input("Teacher name (optional)", placeholder="e.g. Dr. Sharma")
        code = st.text_input("Subject code (optional)", placeholder="e.g. CS301")
        submit = st.form_submit_button("Add Subject")

        if submit:
            if not name.strip():
                st.error("Subject name is required.")
            else:
                st.session_state.subjects.append(
                    {
                        "id": get_new_id(),
                        "name": name.strip(),
                        "teacher": teacher.strip(),
                        "code": code.strip(),
                    }
                )
                st.success(f"Added subject: {name.strip()}")

    if st.session_state.subjects:
        st.subheader("Your Subjects")
        df = pd.DataFrame(st.session_state.subjects)
        df_display = df[["name", "teacher", "code"]]
        df_display.columns = ["Subject", "Teacher", "Code"]
        st.table(df_display)
    else:
        st.info("No subjects added yet. Use the form above to add one.")


# =====================================================
# STUDY TASKS TAB
# =====================================================

def tasks_tab():
    st.header("📌 Study Tasks")

    if not st.session_state.subjects:
        st.warning("Add at least one subject first in the **Subjects** tab.")
        return

    subjects = get_subject_names()

    with st.form("add_task_form", clear_on_submit=True):
        title = st.text_input("Task title", placeholder="e.g. Revise Sorting Algorithms")
        subject = st.selectbox("Subject", subjects)
        estimated_hours = st.number_input("Estimated hours needed", min_value=0.5, max_value=50.0, value=2.0, step=0.5)
        due_date = st.date_input("Due date (optional)", value=date.today())
        has_due = st.checkbox("This task has a due date", value=True)
        if not has_due:
            due_date = None

        importance = st.slider("Importance (1 = low, 5 = very high)", 1, 5, 3)
        difficulty = st.slider("Difficulty (1 = easy, 5 = very hard)", 1, 5, 3)

        submit = st.form_submit_button("Add Task")

        if submit:
            if not title.strip():
                st.error("Task title is required.")
            else:
                st.session_state.tasks.append(
                    {
                        "id": get_new_id(),
                        "title": title.strip(),
                        "subject": subject,
                        "estimated_hours": float(estimated_hours),
                        "due_date": due_date,
                        "importance": int(importance),
                        "difficulty": int(difficulty),
                        "status": "Pending",  # or Completed
                    }
                )
                st.success(f"Added task: {title.strip()}")

    if st.session_state.tasks:
        st.subheader("Pending Tasks")
        pending = [t for t in st.session_state.tasks if t["status"] == "Pending"]

        if pending:
            df_p = pd.DataFrame(pending)
            df_p_display = df_p[["title", "subject", "estimated_hours", "due_date", "importance", "difficulty"]]
            df_p_display.columns = ["Task", "Subject", "Est. Hours", "Due Date", "Importance", "Difficulty"]
            st.table(df_p_display)

            st.subheader("Mark Tasks as Completed")
            for t in pending:
                if st.checkbox(f"Mark '{t['title']}' as completed", key=f"task_done_{t['id']}"):
                    t["status"] = "Completed"
                    st.success(f"Task marked as completed: {t['title']}")
        else:
            st.info("No pending tasks.")

        st.subheader("Completed Tasks")
        completed = [t for t in st.session_state.tasks if t["status"] == "Completed"]
        if completed:
            df_c = pd.DataFrame(completed)
            df_c_display = df_c[["title", "subject", "estimated_hours", "due_date", "importance", "difficulty"]]
            df_c_display.columns = ["Task", "Subject", "Est. Hours", "Due Date", "Importance", "Difficulty"]
            st.table(df_c_display)
        else:
            st.info("No completed tasks yet.")
    else:
        st.info("No study tasks added yet.")


# =====================================================
# EXAMS TAB
# =====================================================

def exams_tab():
    st.header("📝 Exams")

    if not st.session_state.subjects:
        st.warning("Add at least one subject first in the **Subjects** tab.")
        return

    subjects = get_subject_names()

    with st.form("add_exam_form", clear_on_submit=True):
        subject = st.selectbox("Subject", subjects)
        title = st.text_input("Exam title", placeholder="e.g. Mid Semester Exam")
        exam_date = st.date_input("Exam date", value=date.today())
        syllabus = st.text_area("Syllabus / Chapters to cover", height=80, placeholder="e.g. Units 1–3")

        submit = st.form_submit_button("Add Exam")

        if submit:
            if not title.strip():
                st.error("Exam title is required.")
            else:
                st.session_state.exams.append(
                    {
                        "id": get_new_id(),
                        "subject": subject,
                        "title": title.strip(),
                        "date": exam_date,
                        "syllabus": syllabus.strip(),
                    }
                )
                st.success(f"Added exam: {title.strip()}")

    if st.session_state.exams:
        st.subheader("All Exams")
        df = pd.DataFrame(st.session_state.exams)
        df_display = df[["subject", "title", "date", "syllabus"]]
        df_display.columns = ["Subject", "Exam", "Date", "Syllabus / Chapters"]
        st.table(df_display)
    else:
        st.info("No exams added yet.")


# =====================================================
# STUDY PLAN GENERATOR TAB
# =====================================================

def generate_study_plan(daily_hours, num_days):
    """Simple greedy scheduler:
    - Take all pending tasks
    - Compute priority score based on importance, difficulty, due date
    - Allocate hours across upcoming days until tasks are filled or hours end
    """
    today = date.today()
    pending_tasks = [t for t in st.session_state.tasks if t["status"] == "Pending"]

    if not pending_tasks:
        st.session_state.schedule = []
        return []

    # Compute priority score
    tasks_with_score = []
    for t in pending_tasks:
        days_left = 30  # default if no due date
        if t["due_date"] is not None:
            d = (t["due_date"] - today).days
            if d < 0:
                d = 0
            days_left = d if d > 0 else 1

        # higher importance & difficulty, closer due date => higher score
        urgency = 1.0 / days_left
        score = t["importance"] * 2 + t["difficulty"] + urgency * 5
        tasks_with_score.append((t, score))

    # Sort by score descending
    tasks_with_score.sort(key=lambda x: x[1], reverse=True)

    # Available hours per day
    plan = []
    current_date = today
    for day_index in range(num_days):
        day_hours_left = float(daily_hours)
        time_block_index = 1

        for i in range(len(tasks_with_score)):
            t, score = tasks_with_score[i]
            if t["estimated_hours"] <= 0:
                continue

            if day_hours_left <= 0:
                break

            # assign min(hours_left, estimated_hours_remaining)
            assigned = min(day_hours_left, t["estimated_hours"])
            if assigned <= 0:
                continue

            plan.append(
                {
                    "date": current_date,
                    "time_block": f"Session {time_block_index}",
                    "subject": t["subject"],
                    "task_title": t["title"],
                    "planned_hours": round(assigned, 2),
                }
            )

            t["estimated_hours"] -= assigned
            day_hours_left -= assigned
            time_block_index += 1

        current_date += timedelta(days=1)

    # save plan
    st.session_state.schedule = plan
    return plan


def plan_tab(daily_hours, num_days):
    st.header("📅 Generate Study Plan")

    st.write(
        "This will create a **day-wise study schedule** for the next selected days "
        "based on your pending tasks, importance, difficulty, and due dates."
    )

    if not st.session_state.tasks:
        st.warning("Add some study tasks first in the **Study Tasks** tab.")
        return

    if st.button("Generate Study Plan"):
        plan = generate_study_plan(daily_hours, num_days)
        if not plan:
            st.info("No plan generated (no pending tasks).")
        else:
            st.success("Study plan generated successfully!")

    if st.session_state.schedule:
        st.subheader("Generated Plan")

        df = pd.DataFrame(st.session_state.schedule)
        df_display = df.copy()
        df_display["date"] = df_display["date"].apply(lambda d: d.strftime("%d %b %Y"))
        df_display = df_display[["date", "time_block", "subject", "task_title", "planned_hours"]]
        df_display.columns = ["Date", "Session", "Subject", "Task", "Hours"]
        st.table(df_display)

        # Summary: total hours per day
        st.subheader("Daily Study Hours Summary")
        df_summary = df.groupby("date")["planned_hours"].sum().reset_index()
        df_summary["date_str"] = df_summary["date"].apply(lambda d: d.strftime("%d %b"))
        df_summary = df_summary.set_index("date_str")
        st.bar_chart(df_summary["planned_hours"])


# =====================================================
# ABOUT TAB
# =====================================================

def about_tab():
    st.header("ℹ️ About This Study Planner")
    st.markdown(
        """
        This web app is a **Student Study Planner** built with **Python and Streamlit**.

        ### Main Features
        - Manage **subjects** with optional teacher and code  
        - Add **study tasks** with estimated hours, due dates, importance and difficulty  
        - Add **exams** with subject, date and syllabus  
        - Generate a **day-wise study plan** for a chosen number of days,
          based on your pending tasks and daily available hours  
        - View a **dashboard** of today's schedule, upcoming tasks and exams  

        The data is stored in **Streamlit session_state** (in memory) which is perfect for:
        - College projects  
        - Demos and viva presentations  
        - Personal lightweight use in browser  

        You can deploy this app on **Streamlit Community Cloud** easily using this single `app.py` file.
        """
    )


# =====================================================
# MAIN
# =====================================================

def main():
    st.set_page_config(page_title="Student Study Planner", layout="wide")
    init_state()

    student_name, daily_hours, num_days = sidebar()

    tabs = st.tabs(["🏠 Dashboard", "📚 Subjects", "📌 Study Tasks", "📝 Exams", "📅 Generate Plan", "ℹ️ About"])

    with tabs[0]:
        dashboard_tab(student_name)

    with tabs[1]:
        subjects_tab()

    with tabs[2]:
        tasks_tab()

    with tabs[3]:
        exams_tab()

    with tabs[4]:
        plan_tab(daily_hours, num_days)

    with tabs[5]:
        about_tab()


if __name__ == "__main__":
    main()
