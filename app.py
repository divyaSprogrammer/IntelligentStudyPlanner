import streamlit as st
import pandas as pd
from datetime import datetime, date, time

# ---------------------------
# Helpers to init session state
# ---------------------------

def init_state():
    if "subjects" not in st.session_state:
        st.session_state.subjects = []  # list of dicts
    if "classes" not in st.session_state:
        st.session_state.classes = []   # list of dicts
    if "tasks" not in st.session_state:
        st.session_state.tasks = []     # list of dicts
    if "exams" not in st.session_state:
        st.session_state.exams = []     # list of dicts
    if "next_id" not in st.session_state:
        st.session_state.next_id = 1


def get_new_id():
    nid = st.session_state.next_id
    st.session_state.next_id += 1
    return nid


def find_subject_name(subj_id):
    for s in st.session_state.subjects:
        if s["id"] == subj_id:
            return s["name"]
    return "-"


# ---------------------------
# UI Components
# ---------------------------

def sidebar_info():
    st.sidebar.title("Student Life Planner")
    st.sidebar.caption("Inspired by 'My Study Life' – timetable + tasks + exams in one place.")
    st.sidebar.markdown("---")
    username = st.sidebar.text_input("Your name", value="Student")
    st.sidebar.markdown("Use the tabs at the top to manage your academic life.")
    return username


# ---------------------------
# Dashboard (Today Overview)
# ---------------------------

def dashboard(username):
    st.header(f"📊 Dashboard – Welcome, {username}!")

    today = date.today()
    today_str = today.strftime("%A, %d %B %Y")
    st.write(f"**Today:** {today_str}")

    # Today’s classes
    st.subheader("📚 Today’s Classes")
    TODAY_DAY_NAME = today.strftime("%A")  # Monday, Tuesday, ...
    classes_today = [c for c in st.session_state.classes if c["day"] == TODAY_DAY_NAME]

    if classes_today:
        df_classes = pd.DataFrame(classes_today)
        df_classes = df_classes[["subject_name", "start_time", "end_time", "room", "notes"]]
        df_classes.columns = ["Subject", "Start", "End", "Room", "Notes"]
        st.table(df_classes)
    else:
        st.info("No classes added for today.")

    # Tasks due today
    st.subheader("✅ Tasks Due Today")
    tasks_today = [
        t for t in st.session_state.tasks
        if t["due_date"] == today and t["status"] == "Pending"
    ]

    if tasks_today:
        df_tasks = pd.DataFrame(tasks_today)
        df_tasks = df_tasks[["title", "subject_name", "type", "priority"]]
        df_tasks.columns = ["Task", "Subject", "Type", "Priority"]
        st.table(df_tasks)
    else:
        st.info("No pending tasks due today. 🎉")

    # Next upcoming exam
    st.subheader("📝 Next Exam")
    future_exams = [e for e in st.session_state.exams if e["date"] >= today]
    future_exams.sort(key=lambda x: (x["date"], x["time"]))

    if future_exams:
        exam = future_exams[0]
        st.success(
            f"Next exam: **{exam['title']} ({exam['subject_name']})** "
            f"on **{exam['date'].strftime('%d %b %Y')} at {exam['time'].strftime('%H:%M')}**"
        )
        st.write(f"Type: {exam['type']}  |  Location: {exam['location'] or '—'}")
    else:
        st.info("No upcoming exams added yet.")


# ---------------------------
# Subjects Page
# ---------------------------

def subjects_page():
    st.header("📚 Subjects")

    with st.form("add_subject_form"):
        name = st.text_input("Subject name", placeholder="e.g. Data Structures")
        teacher = st.text_input("Teacher name", placeholder="e.g. Dr. Sharma")
        color = st.color_picker("Color tag", value="#4CAF50")
        submitted = st.form_submit_button("Add Subject")

        if submitted:
            if name.strip() == "":
                st.error("Please enter a subject name.")
            else:
                st.session_state.subjects.append(
                    {
                        "id": get_new_id(),
                        "name": name.strip(),
                        "teacher": teacher.strip(),
                        "color": color
                    }
                )
                st.success(f"Added subject: {name}")

    if st.session_state.subjects:
        st.subheader("Your Subjects")
        df = pd.DataFrame(st.session_state.subjects)
        df_display = df[["name", "teacher", "color"]]
        df_display.columns = ["Subject", "Teacher", "Color"]
        st.table(df_display)
    else:
        st.info("No subjects added yet. Use the form above to add one.")


# ---------------------------
# Classes / Timetable Page
# ---------------------------

def classes_page():
    st.header("🕒 Class Timetable")

    if not st.session_state.subjects:
        st.warning("You must add at least one subject before adding classes.")
        return

    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    with st.form("add_class_form"):
        subject_names = [s["name"] for s in st.session_state.subjects]
        sel_subj_name = st.selectbox("Subject", subject_names)
        day = st.selectbox("Day of week", days_of_week)
        start = st.time_input("Start time", value=time(9, 0))
        end = st.time_input("End time", value=time(10, 0))
        room = st.text_input("Room / Location", placeholder="e.g. Lab 203")
        notes = st.text_input("Notes (optional)", placeholder="e.g. Bring laptop")
        submitted = st.form_submit_button("Add Class")

        if submitted:
            subj = next(s for s in st.session_state.subjects if s["name"] == sel_subj_name)
            st.session_state.classes.append(
                {
                    "id": get_new_id(),
                    "subject_id": subj["id"],
                    "subject_name": subj["name"],
                    "day": day,
                    "start_time": start.strftime("%H:%M"),
                    "end_time": end.strftime("%H:%M"),
                    "room": room.strip(),
                    "notes": notes.strip()
                }
            )
            st.success(f"Added class for {sel_subj_name} on {day} at {start.strftime('%H:%M')}")

    if st.session_state.classes:
        st.subheader("Weekly Timetable")

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for d in days:
            day_classes = [c for c in st.session_state.classes if c["day"] == d]
            if not day_classes:
                continue
            st.markdown(f"**{d}**")
            df = pd.DataFrame(day_classes)
            df = df[["subject_name", "start_time", "end_time", "room", "notes"]]
            df.columns = ["Subject", "Start", "End", "Room", "Notes"]
            st.table(df)
    else:
        st.info("No classes added yet.")


# ---------------------------
# Tasks / Homework Page
# ---------------------------

def tasks_page():
    st.header("✅ Tasks / Homework")

    if not st.session_state.subjects:
        st.warning("You must add at least one subject before adding tasks.")
        return

    with st.form("add_task_form"):
        subject_names = [s["name"] for s in st.session_state.subjects]
        sel_subj_name = st.selectbox("Subject", subject_names)
        title = st.text_input("Task title", placeholder="e.g. DAA Assignment 1")
        task_type = st.selectbox("Type", ["Homework", "Assignment", "Project", "Reading", "Revision"])
        due = st.date_input("Due date", value=date.today())
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        submitted = st.form_submit_button("Add Task")

        if submitted:
            if title.strip() == "":
                st.error("Please enter a task title.")
            else:
                subj = next(s for s in st.session_state.subjects if s["name"] == sel_subj_name)
                st.session_state.tasks.append(
                    {
                        "id": get_new_id(),
                        "subject_id": subj["id"],
                        "subject_name": subj["name"],
                        "title": title.strip(),
                        "type": task_type,
                        "due_date": due,
                        "priority": priority,
                        "status": "Pending"
                    }
                )
                st.success(f"Added task: {title}")

    if st.session_state.tasks:
        st.subheader("Pending Tasks")

        pending = [t for t in st.session_state.tasks if t["status"] == "Pending"]
        if pending:
            # Show checkboxes to mark as done
            cols = st.columns([4, 1])
            with cols[0]:
                df = pd.DataFrame(pending)
                df_display = df[["title", "subject_name", "type", "due_date", "priority"]]
                df_display.columns = ["Task", "Subject", "Type", "Due Date", "Priority"]
                st.table(df_display)
            with cols[1]:
                st.write("Mark Done")
                for t in pending:
                    if st.checkbox(f"{t['title']}", key=f"task_done_{t['id']}"):
                        t["status"] = "Completed"
                        st.success(f"Marked '{t['title']}' as completed.")

        else:
            st.info("No pending tasks. Good job ✨")

        st.subheader("Completed Tasks")
        completed = [t for t in st.session_state.tasks if t["status"] == "Completed"]
        if completed:
            dfc = pd.DataFrame(completed)
            dfc_display = dfc[["title", "subject_name", "type", "due_date", "priority"]]
            dfc_display.columns = ["Task", "Subject", "Type", "Due Date", "Priority"]
            st.table(dfc_display)
        else:
            st.info("No completed tasks yet.")
    else:
        st.info("No tasks added yet.")


# ---------------------------
# Exams Page
# ---------------------------

def exams_page():
    st.header("📝 Exams")

    if not st.session_state.subjects:
        st.warning("You must add at least one subject before adding exams.")
        return

    with st.form("add_exam_form"):
        subject_names = [s["name"] for s in st.session_state.subjects]
        sel_subj_name = st.selectbox("Subject", subject_names)
        title = st.text_input("Exam title", placeholder="e.g. Midterm Exam")
        exam_type = st.selectbox("Type", ["Midterm", "Final", "Quiz", "Viva", "Other"])
        exam_date = st.date_input("Exam date", value=date.today())
        exam_time = st.time_input("Exam time", value=time(9, 0))
        location = st.text_input("Location / Room", placeholder="e.g. Hall A")
        submitted = st.form_submit_button("Add Exam")

        if submitted:
            if title.strip() == "":
                st.error("Please enter an exam title.")
            else:
                subj = next(s for s in st.session_state.subjects if s["name"] == sel_subj_name)
                st.session_state.exams.append(
                    {
                        "id": get_new_id(),
                        "subject_id": subj["id"],
                        "subject_name": subj["name"],
                        "title": title.strip(),
                        "type": exam_type,
                        "date": exam_date,
                        "time": exam_time,
                        "location": location.strip()
                    }
                )
                st.success(f"Added exam: {title}")

    if st.session_state.exams:
        st.subheader("All Exams")
        df = pd.DataFrame(st.session_state.exams)
        df_display = df[["title", "subject_name", "type", "date", "time", "location"]]
        df_display.columns = ["Exam", "Subject", "Type", "Date", "Time", "Location"]
        st.table(df_display)
    else:
        st.info("No exams added yet.")


# ---------------------------
# Main App
# ---------------------------

def main():
    st.set_page_config(page_title="Student Life Planner", layout="wide")
    init_state()
    username = sidebar_info()

    tabs = st.tabs(["🏠 Dashboard", "📚 Subjects", "🕒 Classes", "✅ Tasks", "📝 Exams", "ℹ️ About App"])

    with tabs[0]:
        dashboard(username)

    with tabs[1]:
        subjects_page()

    with tabs[2]:
        classes_page()

    with tabs[3]:
        tasks_page()

    with tabs[4]:
        exams_page()

    with tabs[5]:
        st.header("ℹ️ About This App")
        st.markdown(
            """
            This is a **Student Life Planner** web app inspired by the features of
            **My Study Life**:

            - Manage **subjects** with teacher and color tags  
            - Maintain a **class timetable** for each day of the week  
            - Track **tasks / homework** with due dates & priorities  
            - Add **exams** with date, time, and location  
            - See a **dashboard** of today's classes, tasks, and upcoming exam  

            Built with **Python + Streamlit** so it runs on the web and works great
            as a mini project or academic assignment.
            """
        )


if __name__ == "__main__":
    main()
