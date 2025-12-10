import streamlit as st
import pandas as pd
from datetime import date, datetime

# ------------------------------------------------
# Initialize session state
# ------------------------------------------------
def init_state():
    if "projects" not in st.session_state:
        st.session_state.projects = []  # list of dicts: {id, name, color}
    if "tasks" not in st.session_state:
        st.session_state.tasks = []     # list of dicts
    if "next_id" not in st.session_state:
        st.session_state.next_id = 1


def get_new_id():
    nid = st.session_state.next_id
    st.session_state.next_id += 1
    return nid


def get_project_names():
    return [p["name"] for p in st.session_state.projects]


# ------------------------------------------------
# Sidebar
# ------------------------------------------------
def sidebar():
    st.sidebar.title("📝 Todo Manager")
    st.sidebar.caption("A simple Todoist-style task manager built with Streamlit.")

    username = st.sidebar.text_input("Your name", value="User")
    st.sidebar.markdown("---")

    view = st.sidebar.selectbox(
        "Quick View",
        ["Today", "Upcoming", "Overdue", "All Tasks", "Completed"]
    )

    st.sidebar.markdown("---")
    selected_project = st.sidebar.selectbox(
        "Filter by Project",
        ["All Projects"] + get_project_names()
    )

    st.sidebar.markdown("---")
    st.sidebar.write("Task status filter:")
    status_filter = st.sidebar.radio(
        "",
        ["All", "Pending", "Completed"],
        horizontal=True
    )

    return username, view, selected_project, status_filter


# ------------------------------------------------
# Dashboard / View Filter
# ------------------------------------------------
def filter_tasks(tasks, view, selected_project, status_filter):
    today = date.today()
    filtered = tasks

    # Filter by project
    if selected_project != "All Projects":
        filtered = [t for t in filtered if t["project"] == selected_project]

    # Filter by status
    if status_filter == "Pending":
        filtered = [t for t in filtered if t["status"] == "Pending"]
    elif status_filter == "Completed":
        filtered = [t for t in filtered if t["status"] == "Completed"]

    # Quick view logic
    if view == "Today":
        filtered = [
            t for t in filtered
            if t["due_date"] is not None and t["due_date"] == today
        ]
    elif view == "Upcoming":
        filtered = [
            t for t in filtered
            if t["due_date"] is not None and t["due_date"] > today
        ]
    elif view == "Overdue":
        filtered = [
            t for t in filtered
            if t["due_date"] is not None and t["due_date"] < today and t["status"] == "Pending"
        ]
    elif view == "Completed":
        filtered = [t for t in filtered if t["status"] == "Completed"]
    # "All Tasks" → no additional filter

    return filtered


# ------------------------------------------------
# Projects Page
# ------------------------------------------------
def projects_page():
    st.header("🗂 Projects")

    with st.form("add_project_form", clear_on_submit=True):
        name = st.text_input("Project name", placeholder="e.g. College", max_chars=50)
        color = st.color_picker("Color", value="#ff6b6b")
        add_btn = st.form_submit_button("Add Project")

        if add_btn:
            if not name.strip():
                st.error("Please enter a project name.")
            else:
                st.session_state.projects.append(
                    {
                        "id": get_new_id(),
                        "name": name.strip(),
                        "color": color
                    }
                )
                st.success(f"Project '{name}' added.")

    if st.session_state.projects:
        st.subheader("Your Projects")
        df = pd.DataFrame(st.session_state.projects)
        df_display = df[["name", "color"]]
        df_display.columns = ["Project", "Color"]
        st.table(df_display)
    else:
        st.info("No projects yet. Create one using the form above.")


# ------------------------------------------------
# Add Task Form
# ------------------------------------------------
def add_task_form():
    st.subheader("➕ Add New Task")

    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Task title", placeholder="e.g. Buy groceries")
        description = st.text_area("Description (optional)", height=80, key="desc")
    with col2:
        # Project
        projects = get_project_names()
        if not projects:
            project = st.text_input("Project", value="Inbox")
        else:
            project = st.selectbox("Project", ["Inbox"] + projects)

        # Priority
        priority = st.selectbox(
            "Priority",
            ["Low", "Medium", "High", "Urgent"],
            index=1
        )

        # Due date
        due_option = st.radio("Set due date?", ["No due date", "Pick a date"], index=0, horizontal=True)
        due_dt = None
        if due_option == "Pick a date":
            due_dt = st.date_input("Due date", value=date.today())

        # Labels
        labels_text = st.text_input(
            "Labels (comma separated)",
            placeholder="e.g. home, personal, quick"
        )

    add_button = st.button("Add Task")

    if add_button:
        if not title.strip():
            st.error("Please enter a task title.")
        else:
            labels = [l.strip() for l in labels_text.split(",") if l.strip()] if labels_text else []
            st.session_state.tasks.append(
                {
                    "id": get_new_id(),
                    "title": title.strip(),
                    "description": description.strip(),
                    "project": project,
                    "priority": priority,
                    "due_date": due_dt,
                    "labels": labels,
                    "status": "Pending",
                    "created_at": datetime.now()
                }
            )
            st.success(f"Task '{title}' added.")


# ------------------------------------------------
# Tasks List / Main Page
# ------------------------------------------------
def tasks_page(view, selected_project, status_filter):
    st.header("✅ Tasks")

    # Add Task
    add_task_form()

    st.markdown("---")
    st.subheader("📋 Task List")

    tasks = st.session_state.tasks
    filtered = filter_tasks(tasks, view, selected_project, status_filter)

    if not filtered:
        st.info("No tasks matching this filter.")
        return

    # Sort filtered tasks by due date (None at end)
    def sort_key(t):
        return (t["due_date"] is None, t["due_date"] or date.max, t["priority"])

    filtered.sort(key=sort_key)

    # Display tasks in a nice table with actions
    for t in filtered:
        with st.container():
            cols = st.columns([0.06, 0.6, 0.14, 0.2])
            with cols[0]:
                done = st.checkbox("", value=(t["status"] == "Completed"), key=f"done_{t['id']}")
                if done:
                    t["status"] = "Completed"
                else:
                    t["status"] = "Pending"

            with cols[1]:
                title_disp = f"**{t['title']}**"
                if t["status"] == "Completed":
                    title_disp = f"~~{t['title']}~~ ✅"
                st.markdown(title_disp)

                meta = f"Project: `{t['project']}`"
                if t["labels"]:
                    meta += "  •  Labels: " + ", ".join([f"`{l}`" for l in t["labels"]])
                st.caption(meta)

                if t["description"]:
                    st.write(t["description"])

            with cols[2]:
                # Priority + Status
                prio_emoji = {
                    "Low": "🟢",
                    "Medium": "🟡",
                    "High": "🟠",
                    "Urgent": "🔴"
                }.get(t["priority"], "⚪")
                st.write(f"{prio_emoji} {t['priority']}")
                st.write("✔️" if t["status"] == "Completed" else "⏳ Pending")

            with cols[3]:
                if t["due_date"]:
                    today = date.today()
                    if t["due_date"] < today and t["status"] == "Pending":
                        st.error(f"Overdue: {t['due_date'].strftime('%d %b %Y')}")
                    elif t["due_date"] == today:
                        st.warning("Due today")
                    else:
                        st.info(f"Due: {t['due_date'].strftime('%d %b %Y')}")
                else:
                    st.caption("No due date")

            st.markdown("---")


# ------------------------------------------------
# Analytics Page
# ------------------------------------------------
def analytics_page():
    st.header("📊 Overview & Analytics")
    tasks = st.session_state.tasks

    if not tasks:
        st.info("No tasks yet to analyze.")
        return

    total = len(tasks)
    completed = len([t for t in tasks if t["status"] == "Completed"])
    pending = total - completed
    overdue = len([
        t for t in tasks
        if t["status"] == "Pending" and t["due_date"] is not None and t["due_date"] < date.today()
    ])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Tasks", total)
    col2.metric("Completed", completed)
    col3.metric("Pending", pending)
    col4.metric("Overdue", overdue)

    # Tasks per project
    st.subheader("Tasks by Project")
    proj_counts = {}
    for t in tasks:
        proj_counts[t["project"]] = proj_counts.get(t["project"], 0) + 1

    df_proj = pd.DataFrame(
        {"Project": list(proj_counts.keys()), "Tasks": list(proj_counts.values())}
    ).set_index("Project")
    st.bar_chart(df_proj)

    # Tasks by priority
    st.subheader("Tasks by Priority")
    prio_counts = {}
    for t in tasks:
        prio_counts[t["priority"]] = prio_counts.get(t["priority"], 0) + 1

    df_prio = pd.DataFrame(
        {"Priority": list(prio_counts.keys()), "Tasks": list(prio_counts.values())}
    ).set_index("Priority")
    st.bar_chart(df_prio)


# ------------------------------------------------
# About Page
# ------------------------------------------------
def about_page():
    st.header("ℹ️ About This App")
    st.markdown(
        """
        This app is a **Todoist-style task manager clone** built using **Python + Streamlit**.

        ### Core Features
        - Add tasks with title, description, project, priority, due date and labels  
        - Organize tasks into **projects**  
        - Mark tasks as **completed**  
        - Filter by **Today**, **Upcoming**, **Overdue**, **Completed** or **All**  
        - Filter by **Project** and **Status**  
        - Simple **analytics** (tasks per project, tasks per priority)  

        It uses **Streamlit session_state** to store data temporarily in memory, which is
        perfect for:

        - College mini-projects  
        - Demonstrations in viva  
        - Simple personal task management in browser  

        You can deploy it on **Streamlit Cloud** and access it from anywhere.
        """
    )


# ------------------------------------------------
# Main App
# ------------------------------------------------
def main():
    st.set_page_config(page_title="Todoist-style To-Do App", layout="wide")
    init_state()

    username, view, selected_project, status_filter = sidebar()

    tabs = st.tabs(["📋 Tasks", "🗂 Projects", "📊 Analytics", "ℹ️ About"])

    with tabs[0]:
        st.caption(f"Hello, {username}! Viewing: **{view}**")
        tasks_page(view, selected_project, status_filter)

    with tabs[1]:
        projects_page()

    with tabs[2]:
        analytics_page()

    with tabs[3]:
        about_page()


if __name__ == "__main__":
    main()
