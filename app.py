import streamlit as st
import pandas as pd
from datetime import date, datetime

# =========================================================
# Session State Initialization
# =========================================================

def init_state():
    """Initialize all session_state variables used by the app."""
    if "projects" not in st.session_state:
        st.session_state.projects = []  # list of dicts: {id, name, color}
    if "tasks" not in st.session_state:
        st.session_state.tasks = []     # list of dicts representing tasks
    if "next_id" not in st.session_state:
        st.session_state.next_id = 1


def get_new_id() -> int:
    """Generate a new unique ID for projects / tasks."""
    nid = st.session_state.next_id
    st.session_state.next_id += 1
    return nid


def get_project_names():
    """Return list of project names (for dropdowns)."""
    return [p["name"] for p in st.session_state.projects]


# =========================================================
# Sidebar Controls
# =========================================================

def sidebar():
    st.sidebar.title("📝 Todoist-style To-Do App")
    st.sidebar.caption("A clean, simple, project-based task manager built with Streamlit.")

    username = st.sidebar.text_input("Your name", value="User")

    st.sidebar.markdown("---")
    view = st.sidebar.selectbox(
        "Quick view",
        ["Today", "Upcoming", "Overdue", "All Tasks", "Completed"]
    )

    st.sidebar.markdown("---")
    project_filter = st.sidebar.selectbox(
        "Filter by project",
        ["All Projects"] + get_project_names()
    )

    st.sidebar.markdown("---")
    st.sidebar.write("Status filter:")
    status_filter = st.sidebar.radio(
        "",
        ["All", "Pending", "Completed"],
        horizontal=True
    )

    return username, view, project_filter, status_filter


# =========================================================
# Filtering Logic
# =========================================================

def filter_tasks(tasks, view, project_filter, status_filter):
    """Filter tasks based on sidebar selections."""
    today = date.today()
    filtered = list(tasks)  # make a copy

    # Filter by project
    if project_filter != "All Projects":
        filtered = [t for t in filtered if t["project"] == project_filter]

    # Filter by status
    if status_filter == "Pending":
        filtered = [t for t in filtered if t["status"] == "Pending"]
    elif status_filter == "Completed":
        filtered = [t for t in filtered if t["status"] == "Completed"]

    # Filter by quick view
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
    # "All Tasks" keeps whatever is there

    return filtered


# =========================================================
# Projects Tab
# =========================================================

def projects_tab():
    st.header("🗂 Projects")

    with st.form("add_project_form", clear_on_submit=True):
        name = st.text_input("Project name", placeholder="e.g. College", max_chars=50)
        color = st.color_picker("Project color", value="#ff6b6b")
        add_btn = st.form_submit_button("Add project")

        if add_btn:
            if not name.strip():
                st.error("Please enter a project name.")
            else:
                st.session_state.projects.append(
                    {
                        "id": get_new_id(),
                        "name": name.strip(),
                        "color": color,
                    }
                )
                st.success(f"Project '{name}' added successfully.")

    if st.session_state.projects:
        st.subheader("Your projects")
        df = pd.DataFrame(st.session_state.projects)
        df_display = df[["name", "color"]]
        df_display.columns = ["Project", "Color"]
        st.table(df_display)
    else:
        st.info("No projects yet. Add one using the form above.")


# =========================================================
# Add Task Form
# =========================================================

def add_task_form():
    st.subheader("➕ Add new task")

    col1, col2 = st.columns(2)

    with col1:
        title = st.text_input("Task title", placeholder="e.g. Complete math homework")
        description = st.text_area("Description (optional)", height=80, key="task_desc")

    with col2:
        projects = get_project_names()
        if projects:
            project = st.selectbox("Project", ["Inbox"] + projects)
        else:
            project = "Inbox"

        priority = st.selectbox(
            "Priority",
            ["Low", "Medium", "High", "Urgent"],
            index=1
        )

        due_choice = st.radio(
            "Due date",
            ["No due date", "Pick a date"],
            index=0,
            horizontal=True,
            key="due_choice"
        )
        due_dt = None
        if due_choice == "Pick a date":
            due_dt = st.date_input("Select due date", value=date.today())

        labels_text = st.text_input(
            "Labels (comma separated)",
            placeholder="e.g. home, quick, college"
        )

    add_btn = st.button("Add task")

    if add_btn:
        if not title.strip():
            st.error("Please enter a task title.")
        else:
            labels = [lbl.strip() for lbl in labels_text.split(",") if lbl.strip()] if labels_text else []
            st.session_state.tasks.append(
                {
                    "id": get_new_id(),
                    "title": title.strip(),
                    "description": description.strip(),
                    "project": project,
                    "priority": priority,
                    "due_date": due_dt,          # can be None or a date object
                    "labels": labels,            # list of strings
                    "status": "Pending",         # "Pending" or "Completed"
                    "created_at": datetime.now()
                }
            )
            st.success(f"Task '{title}' added successfully.")


# =========================================================
# Priority Helper
# =========================================================

def priority_order_value(priority: str) -> int:
    """Map priority string to numeric order for sorting (lower = more important)."""
    mapping = {
        "Urgent": 0,
        "High": 1,
        "Medium": 2,
        "Low": 3,
    }
    return mapping.get(priority, 4)


# =========================================================
# Tasks Tab (main)
# =========================================================

def tasks_tab(view, project_filter, status_filter, username):
    st.header("✅ Tasks")
    st.caption(f"Hello, **{username}**! Viewing: **{view}**")

    # Add task form
    add_task_form()

    st.markdown("---")
    st.subheader("📋 Task list")

    tasks = st.session_state.tasks
    filtered = filter_tasks(tasks, view, project_filter, status_filter)

    if not filtered:
        st.info("No tasks match the current filters.")
        return

    # Sort tasks by: due date (None last), then priority, then creation time
    def sort_key(task):
        due = task["due_date"] or date.max
        return (due, priority_order_value(task["priority"]), task["created_at"])

    filtered.sort(key=sort_key)

    today = date.today()

    for task in filtered:
        with st.container():
            cols = st.columns([0.06, 0.6, 0.16, 0.18])

            # Checkbox (done / pending)
            with cols[0]:
                checked = st.checkbox(
                    "", value=(task["status"] == "Completed"), key=f"chk_{task['id']}"
                )
                task["status"] = "Completed" if checked else "Pending"

            # Title + description + meta
            with cols[1]:
                if task["status"] == "Completed":
                    title_display = f"~~{task['title']}~~ ✅"
                else:
                    title_display = f"**{task['title']}**"

                st.markdown(title_display)

                meta_parts = [f"Project: `{task['project']}`"]
                if task["labels"]:
                    meta_parts.append("Labels: " + ", ".join(f"`{lbl}`" for lbl in task["labels"]))
                st.caption("  •  ".join(meta_parts))

                if task["description"]:
                    st.write(task["description"])

            # Priority & Status
            with cols[2]:
                prio_emoji = {
                    "Low": "🟢",
                    "Medium": "🟡",
                    "High": "🟠",
                    "Urgent": "🔴"
                }.get(task["priority"], "⚪")

                st.write(f"{prio_emoji} {task['priority']}")
                st.write("✔️ Completed" if task["status"] == "Completed" else "⏳ Pending")

            # Due date
            with cols[3]:
                if task["due_date"]:
                    if task["status"] == "Pending" and task["due_date"] < today:
                        st.error(f"Overdue: {task['due_date'].strftime('%d %b %Y')}")
                    elif task["due_date"] == today and task["status"] == "Pending":
                        st.warning("Due today")
                    else:
                        st.info(f"Due: {task['due_date'].strftime('%d %b %Y')}")
                else:
                    st.caption("No due date")

            st.markdown("---")


# =========================================================
# Analytics Tab
# =========================================================

def analytics_tab():
    st.header("📊 Analytics & Overview")
    tasks = st.session_state.tasks

    if not tasks:
        st.info("No tasks yet. Add some tasks to see analytics.")
        return

    total = len(tasks)
    completed = len([t for t in tasks if t["status"] == "Completed"])
    pending = total - completed
    overdue = len([
        t for t in tasks
        if t["status"] == "Pending" and t["due_date"] is not None and t["due_date"] < date.today()
    ])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total tasks", total)
    c2.metric("Completed", completed)
    c3.metric("Pending", pending)
    c4.metric("Overdue", overdue)

    # Tasks per project
    st.subheader("Tasks per project")
    proj_counts = {}
    for t in tasks:
        proj_counts[t["project"]] = proj_counts.get(t["project"], 0) + 1

    df_proj = pd.DataFrame(
        {"Project": list(proj_counts.keys()), "Tasks": list(proj_counts.values())}
    ).set_index("Project")
    st.bar_chart(df_proj)

    # Tasks per priority
    st.subheader("Tasks per priority")
    prio_counts = {}
    for t in tasks:
        prio_counts[t["priority"]] = prio_counts.get(t["priority"], 0) + 1

    df_prio = pd.DataFrame(
        {"Priority": list(prio_counts.keys()), "Tasks": list(prio_counts.values())}
    ).set_index("Priority")
    st.bar_chart(df_prio)


# =========================================================
# About Tab
# =========================================================

def about_tab():
    st.header("ℹ️ About this app")
    st.markdown(
        """
        This app is a **Todoist-style To-Do List clone** built with **Python + Streamlit**.

        ### What you can do
        - Create **projects** with color tags  
        - Add **tasks** with title, description, project, priority, due date, labels  
        - Mark tasks as **pending / completed**  
        - Filter by **Today / Upcoming / Overdue / Completed / All**  
        - Filter further by **Project** and **Status**  
        - View simple **analytics**: tasks per project and priority  

        It stores data in **Streamlit `session_state`**, which is perfect for demos,
        assignments, and viva presentations on Streamlit Cloud.
        """
    )


# =========================================================
# Main
# =========================================================

def main():
    st.set_page_config(page_title="Todoist-style To-Do App", layout="wide")
    init_state()

    username, view, project_filter, status_filter = sidebar()

    tabs = st.tabs(["📋 Tasks", "🗂 Projects", "📊 Analytics", "ℹ️ About"])

    with tabs[0]:
        tasks_tab(view, project_filter, status_filter, username)

    with tabs[1]:
        projects_tab()

    with tabs[2]:
        analytics_tab()

    with tabs[3]:
        about_tab()


if __name__ == "__main__":
    main()
