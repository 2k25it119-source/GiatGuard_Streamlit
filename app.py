import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="GiatGuard",
    page_icon="🦶",
    layout="wide"
)


# =========================================================
# DATABASE
# =========================================================

DATABASE = "giatguard.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def init_db():

    conn = get_db()
    cursor = conn.cursor()

    # USERS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # PATIENTS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            age INTEGER,
            gender TEXT,
            phone TEXT,
            medical_condition TEXT,
            injury_problem TEXT,
            address TEXT,
            emergency_contact TEXT,
            baseline_pressure REAL DEFAULT 0,
            baseline_angle REAL DEFAULT 0,
            target_steps INTEGER DEFAULT 5000,
            doctor_id INTEGER,
            user_id INTEGER,
            registration_date TEXT
        )
    """)

    # GAIT HISTORY
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gait_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            date TEXT,
            steps INTEGER,
            pressure REAL,
            gait_angle REAL,
            status TEXT
        )
    """)

    conn.commit()

    # -----------------------------------------------------
    # ADD NEW COLUMNS TO OLD DATABASE IF REQUIRED
    # -----------------------------------------------------

    cursor.execute("PRAGMA table_info(patients)")
    columns = [column["name"] for column in cursor.fetchall()]

    new_columns = {
        "gender": "TEXT",
        "phone": "TEXT",
        "medical_condition": "TEXT",
        "injury_problem": "TEXT",
        "address": "TEXT",
        "emergency_contact": "TEXT",
        "registration_date": "TEXT"
    }

    for column, datatype in new_columns.items():

        if column not in columns:

            cursor.execute(
                f"ALTER TABLE patients ADD COLUMN {column} {datatype}"
            )

    conn.commit()
    conn.close()


# =========================================================
# SESSION STATE
# =========================================================

def initialize_session():

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "user_id" not in st.session_state:
        st.session_state.user_id = None

    if "user_name" not in st.session_state:
        st.session_state.user_name = None

    if "user_role" not in st.session_state:
        st.session_state.user_role = None

    if "page" not in st.session_state:
        st.session_state.page = "Dashboard"

    if "selected_patient" not in st.session_state:
        st.session_state.selected_patient = None

    if "show_register" not in st.session_state:
        st.session_state.show_register = False


# =========================================================
# INITIALIZE
# =========================================================

init_db()
initialize_session()


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main-title {
    font-size: 38px;
    font-weight: 700;
}

.subtitle {
    color: #666;
    font-size: 17px;
}

.card {
    padding: 20px;
    border-radius: 15px;
    background-color: #f7f9fc;
    border: 1px solid #e5e7eb;
    margin-bottom: 15px;
}

.patient-card {
    padding: 18px;
    border-radius: 15px;
    background-color: #ffffff;
    border: 1px solid #dddddd;
    margin-bottom: 12px;
}

.success-box {
    padding: 15px;
    border-radius: 10px;
    background-color: #e8f5e9;
}

.warning-box {
    padding: 15px;
    border-radius: 10px;
    background-color: #fff8e1;
}

.danger-box {
    padding: 15px;
    border-radius: 10px;
    background-color: #ffebee;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# LOGIN
# =========================================================

def login_page():

    st.markdown(
        '<div class="main-title">🦶 GiatGuard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Smart Rehabilitation & Gait Monitoring System</div>',
        unsafe_allow_html=True
    )

    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        st.subheader("🔐 Login")

        email = st.text_input(
            "Email",
            placeholder="Enter your email"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        role = st.selectbox(
            "Login As",
            ["Doctor", "Patient"]
        )

        if st.button(
            "Login",
            use_container_width=True,
            type="primary"
        ):

            conn = get_db()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT *
                FROM users
                WHERE email = ?
                AND password = ?
                AND role = ?
            """, (email, password, role))

            user = cursor.fetchone()

            conn.close()

            if user:

                st.session_state.logged_in = True
                st.session_state.user_id = user["id"]
                st.session_state.user_name = user["name"]
                st.session_state.user_role = user["role"]

                if role == "Doctor":
                    st.session_state.page = "Dashboard"
                else:

                    conn = get_db()
                    cursor = conn.cursor()

                    cursor.execute("""
                        SELECT id
                        FROM patients
                        WHERE user_id = ?
                    """, (user["id"],))

                    patient = cursor.fetchone()

                    conn.close()

                    if patient:
                        st.session_state.selected_patient = patient["id"]
                        st.session_state.page = "Patient Dashboard"
                    else:
                        st.error("Patient profile not found.")
                        return

                st.rerun()

            else:

                st.error(
                    "Invalid Email, Password or Role."
                )


# =========================================================
# LOGOUT
# =========================================================

def logout():

    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.session_state.user_role = None
    st.session_state.page = "Dashboard"
    st.session_state.selected_patient = None

    st.rerun()


# =========================================================
# DOCTOR DASHBOARD
# =========================================================

def doctor_dashboard():

    doctor_id = st.session_state.user_id

    conn = get_db()
    cursor = conn.cursor()

    # Total patients
    cursor.execute("""
        SELECT COUNT(*)
        FROM patients
        WHERE doctor_id = ?
    """, (doctor_id,))

    total_patients = cursor.fetchone()[0]

    # Monitoring patients
    cursor.execute("""
        SELECT COUNT(*)
        FROM patients
        WHERE doctor_id = ?
        AND target_steps > 0
    """, (doctor_id,))

    monitoring_patients = cursor.fetchone()[0]

    # Abnormal alerts
    cursor.execute("""
        SELECT COUNT(*)
        FROM gait_history gh
        JOIN patients p
        ON gh.patient_id = p.id
        WHERE p.doctor_id = ?
        AND gh.status = 'Abnormal'
    """, (doctor_id,))

    abnormal_alerts = cursor.fetchone()[0]

    conn.close()

    st.title("👨‍⚕️ Doctor Dashboard")

    st.write(
        f"Welcome, **Dr. {st.session_state.user_name}**"
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Patients",
            total_patients
        )

    with col2:
        st.metric(
            "Monitoring Patients",
            monitoring_patients
        )

    with col3:
        st.metric(
            "Abnormal Alerts",
            abnormal_alerts
        )

    st.divider()

    st.subheader("Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button(
            "👤 Doctor Profile",
            use_container_width=True
        ):
            st.session_state.page = "Doctor Profile"
            st.rerun()

    with col2:

        if st.button(
            "🧑‍⚕️ My Patients",
            use_container_width=True
        ):
            st.session_state.page = "Patients"
            st.rerun()

    with col3:

        if st.button(
            "⚠️ Alerts",
            use_container_width=True
        ):
            st.session_state.page = "Alerts"
            st.rerun()


# =========================================================
# DOCTOR PROFILE
# =========================================================

def doctor_profile():

    doctor_id = st.session_state.user_id

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE id = ?
        AND role = 'Doctor'
    """, (doctor_id,))

    doctor = cursor.fetchone()

    cursor.execute("""
        SELECT *
        FROM patients
        WHERE doctor_id = ?
        ORDER BY id DESC
    """, (doctor_id,))

    patients = cursor.fetchall()

    conn.close()

    st.title("👨‍⚕️ Doctor Profile")

    # -----------------------------------------------------
    # DOCTOR INFORMATION
    # -----------------------------------------------------

    st.subheader("Doctor Information")

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            f"**Name:** {doctor['name']}"
        )

        st.write(
            "**Specialization:** Orthopedic / Rehabilitation"
        )

    with col2:

        st.write(
            "**Email:** " + doctor["email"]
        )

        st.write(
            "**Hospital:** GiatGuard Rehabilitation Center"
        )

    st.divider()

    # -----------------------------------------------------
    # MY PATIENTS
    # -----------------------------------------------------

    st.subheader("🧑‍⚕️ My Patients")

    if not patients:

        st.info(
            "No patients registered yet."
        )

    else:

        for patient in patients:

            col1, col2, col3 = st.columns(
                [4, 1, 1]
            )

            with col1:

                st.markdown(
                    f"### 🧑 {patient['name']}"
                )

                st.write(
                    f"Patient ID: **P{patient['id']:03d}**"
                )

                st.write(
                    f"Age: {patient['age']} | "
                    f"Email: {patient['email']}"
                )

            with col2:

                if st.button(
                    "View",
                    key=f"view_{patient['id']}"
                ):

                    st.session_state.selected_patient = patient["id"]
                    st.session_state.page = "Patient History"
                    st.rerun()

            with col3:

                if st.button(
                    "Dashboard",
                    key=f"dash_{patient['id']}"
                ):

                    st.session_state.selected_patient = patient["id"]
                    st.session_state.page = "Patient Dashboard"
                    st.rerun()

            st.divider()

    # -----------------------------------------------------
    # REGISTER PATIENT BUTTON
    # -----------------------------------------------------

    if not st.session_state.show_register:

        if st.button(
            "➕ Register New Patient",
            type="primary",
            use_container_width=True
        ):

            st.session_state.show_register = True
            st.rerun()

    else:

        st.subheader("➕ Register New Patient")

        with st.form("register_patient_form"):

            col1, col2 = st.columns(2)

            with col1:

                name = st.text_input(
                    "Patient Name *"
                )

                age = st.number_input(
                    "Age",
                    min_value=1,
                    max_value=120,
                    value=18
                )

                gender = st.selectbox(
                    "Gender",
                    [
                        "Male",
                        "Female",
                        "Other"
                    ]
                )

                phone = st.text_input(
                    "Phone Number"
                )

                email = st.text_input(
                    "Email *"
                )

            with col2:

                medical_condition = st.text_input(
                    "Medical Condition"
                )

                injury_problem = st.text_area(
                    "Injury / Rehabilitation Problem"
                )

                address = st.text_area(
                    "Address"
                )

                emergency_contact = st.text_input(
                    "Emergency Contact"
                )

            st.subheader(
                "Gait Baseline"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                baseline_pressure = st.number_input(
                    "Baseline Pressure",
                    min_value=0.0,
                    value=65.0
                )

            with col2:

                baseline_angle = st.number_input(
                    "Baseline Gait Angle",
                    min_value=0.0,
                    value=12.0
                )

            with col3:

                target_steps = st.number_input(
                    "Daily Target Steps",
                    min_value=1,
                    value=5000
                )

            submitted = st.form_submit_button(
                "Register Patient",
                use_container_width=True,
                type="primary"
            )

            if submitted:

                if not name or not email:

                    st.error(
                        "Patient Name and Email are required."
                    )

                else:

                    conn = get_db()
                    cursor = conn.cursor()

                    try:

                        # ---------------------------------
                        # CREATE PATIENT LOGIN
                        # ---------------------------------

                        patient_password = "1234"

                        cursor.execute("""
                            INSERT INTO users
                            (name, email, password, role)
                            VALUES (?, ?, ?, 'Patient')
                        """, (
                            name,
                            email,
                            patient_password
                        ))

                        user_id = cursor.lastrowid

                        # ---------------------------------
                        # CREATE PATIENT PROFILE
                        # ---------------------------------

                        cursor.execute("""
                            INSERT INTO patients
                            (
                                name,
                                email,
                                age,
                                gender,
                                phone,
                                medical_condition,
                                injury_problem,
                                address,
                                emergency_contact,
                                baseline_pressure,
                                baseline_angle,
                                target_steps,
                                doctor_id,
                                user_id,
                                registration_date
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            name,
                            email,
                            age,
                            gender,
                            phone,
                            medical_condition,
                            injury_problem,
                            address,
                            emergency_contact,
                            baseline_pressure,
                            baseline_angle,
                            target_steps,
                            doctor_id,
                            user_id,
                            str(date.today())
                        ))

                        conn.commit()

                        st.success(
                            f"✅ {name} registered successfully!"
                        )

                        st.info(
                            f"Patient Login → Email: {email} | Password: 1234"
                        )

                        st.session_state.show_register = False

                        conn.close()

                        st.rerun()

                    except sqlite3.IntegrityError:

                        conn.rollback()
                        conn.close()

                        st.error(
                            "This email is already registered."
                        )

    st.divider()

    if st.button("⬅ Back to Dashboard"):

        st.session_state.page = "Dashboard"
        st.rerun()


# =========================================================
# PATIENT LIST
# =========================================================

def patients_page():

    doctor_id = st.session_state.user_id

    conn = get_db()

    query = """
        SELECT *
        FROM patients
        WHERE doctor_id = ?
        ORDER BY id DESC
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=(doctor_id,)
    )

    conn.close()

    st.title("🧑‍⚕️ My Patients")

    if df.empty:

        st.info(
            "No patients registered."
        )

    else:

        for _, patient in df.iterrows():

            st.markdown(
                f"### 🧑 {patient['name']}"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.write(
                    f"Patient ID: P{int(patient['id']):03d}"
                )

                st.write(
                    f"Age: {patient['age']}"
                )

            with col2:

                st.write(
                    f"Email: {patient['email']}"
                )

                st.write(
                    f"Phone: {patient['phone']}"
                )

            with col3:

                if st.button(
                    "Open Patient",
                    key=f"open_patient_{int(patient['id'])}"
                ):

                    st.session_state.selected_patient = int(
                        patient["id"]
                    )

                    st.session_state.page = "Patient History"

                    st.rerun()

            st.divider()


# =========================================================
# PATIENT HISTORY
# =========================================================

def patient_history():

    patient_id = st.session_state.selected_patient

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM patients
        WHERE id = ?
    """, (patient_id,))

    patient = cursor.fetchone()

    cursor.execute("""
        SELECT *
        FROM gait_history
        WHERE patient_id = ?
        ORDER BY id ASC
    """, (patient_id,))

    history = cursor.fetchall()

    conn.close()

    if not patient:

        st.error(
            "Patient not found."
        )

        return

    st.title(
        f"🧑 Patient History — {patient['name']}"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Patient ID",
            f"P{patient['id']:03d}"
        )

    with col2:
        st.metric(
            "Age",
            patient["age"]
        )

    with col3:
        st.metric(
            "Baseline Pressure",
            patient["baseline_pressure"]
        )

    with col4:
        st.metric(
            "Baseline Angle",
            patient["baseline_angle"]
        )

    st.divider()

    st.subheader("Patient Information")

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            f"**Email:** {patient['email']}"
        )

        st.write(
            f"**Phone:** {patient['phone']}"
        )

        st.write(
            f"**Gender:** {patient['gender']}"
        )

    with col2:

        st.write(
            f"**Medical Condition:** {patient['medical_condition']}"
        )

        st.write(
            f"**Injury Problem:** {patient['injury_problem']}"
        )

        st.write(
            f"**Emergency Contact:** {patient['emergency_contact']}"
        )

    st.divider()

    st.subheader("📊 Gait History")

    if not history:

        st.info(
            "No gait data available yet."
        )

    else:

        data = []

        for row in history:

            data.append({
                "Date": row["date"],
                "Steps": row["steps"],
                "Pressure": row["pressure"],
                "Gait Angle": row["gait_angle"],
                "Status": row["status"]
            })

        df = pd.DataFrame(data)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button(
            "📈 Gait Analysis",
            use_container_width=True
        ):

            st.session_state.page = "Gait Analysis"
            st.rerun()

    with col2:

        if st.button(
            "🏃 Exercise Monitoring",
            use_container_width=True
        ):

            st.session_state.page = "Exercise Monitoring"
            st.rerun()

    with col3:

        if st.button(
            "🦶 Patient Dashboard",
            use_container_width=True
        ):

            st.session_state.page = "Patient Dashboard"
            st.rerun()


# =========================================================
# PATIENT DASHBOARD
# =========================================================

def patient_dashboard():

    patient_id = st.session_state.selected_patient

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM patients
        WHERE id = ?
    """, (patient_id,))

    patient = cursor.fetchone()

    cursor.execute("""
        SELECT *
        FROM gait_history
        WHERE patient_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (patient_id,))

    latest = cursor.fetchone()

    cursor.execute("""
        SELECT COALESCE(SUM(steps), 0)
        FROM gait_history
        WHERE patient_id = ?
    """, (patient_id,))

    total_steps = cursor.fetchone()[0]

    cursor.execute("""
        SELECT AVG(gait_angle)
        FROM gait_history
        WHERE patient_id = ?
    """, (patient_id,))

    avg_angle = cursor.fetchone()[0]

    cursor.execute("""
        SELECT AVG(pressure)
        FROM gait_history
        WHERE patient_id = ?
    """, (patient_id,))

    avg_pressure = cursor.fetchone()[0]

    conn.close()

    if not patient:

        st.error(
            "Patient not found."
        )

        return

    # Latest values

    if latest:

        today_steps = latest["steps"]
        gait_angle = latest["gait_angle"]
        pressure = latest["pressure"]
        status = latest["status"]

    else:

        today_steps = 0
        gait_angle = patient["baseline_angle"]
        pressure = patient["baseline_pressure"]
        status = "Waiting for Data"

    if avg_angle:

        avg_angle = round(avg_angle, 2)

    else:

        avg_angle = patient["baseline_angle"]

    if avg_pressure:

        avg_pressure = round(avg_pressure, 2)

    else:

        avg_pressure = patient["baseline_pressure"]

    target = patient["target_steps"] or 1

    progress = min(
        int((today_steps / target) * 100),
        100
    )

    st.title(
        f"🦶 Patient Dashboard"
    )

    st.write(
        f"Welcome, **{patient['name']}**"
    )

    st.divider()

    # -----------------------------------------------------
    # METRICS
    # -----------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Today's Steps",
            today_steps
        )

    with col2:

        st.metric(
            "Gait Angle",
            f"{gait_angle}°"
        )

    with col3:

        st.metric(
            "Pressure",
            f"{pressure}"
        )

    with col4:

        st.metric(
            "Gait Status",
            status
        )

    st.divider()

    # -----------------------------------------------------
    # WALKING PROGRESS
    # -----------------------------------------------------

    st.subheader("🚶 Daily Walking Progress")

    st.progress(
        progress / 100
    )

    st.write(
        f"{today_steps} / {target} steps ({progress}%)"
    )

    st.divider()

    # -----------------------------------------------------
    # STATUS
    # -----------------------------------------------------

    st.subheader("🤖 AI Gait Status")

    if status == "Normal":

        st.success(
            "✅ Normal gait pattern detected."
        )

    elif status == "Abnormal":

        st.error(
            "⚠️ Abnormal gait pattern detected."
        )

    else:

        st.warning(
            "⏳ Waiting for sensor data."
        )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button(
            "📊 Gait History",
            use_container_width=True
        ):

            st.session_state.page = "Patient History"
            st.rerun()

    with col2:

        if st.button(
            "📈 Gait Analysis",
            use_container_width=True
        ):

            st.session_state.page = "Gait Analysis"
            st.rerun()

    with col3:

        if st.button(
            "🏃 Exercise Monitoring",
            use_container_width=True
        ):

            st.session_state.page = "Exercise Monitoring"
            st.rerun()


# =========================================================
# PATIENT PROFILE
# =========================================================

def patient_profile():

    patient_id = st.session_state.selected_patient

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM patients
        WHERE id = ?
    """, (patient_id,))

    patient = cursor.fetchone()

    conn.close()

    if not patient:

        st.error(
            "Patient not found."
        )

        return

    st.title("👤 Patient Profile")

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            f"**Name:** {patient['name']}"
        )

        st.write(
            f"**Patient ID:** P{patient['id']:03d}"
        )

        st.write(
            f"**Age:** {patient['age']}"
        )

        st.write(
            f"**Gender:** {patient['gender']}"
        )

        st.write(
            f"**Phone:** {patient['phone']}"
        )

    with col2:

        st.write(
            f"**Email:** {patient['email']}"
        )

        st.write(
            f"**Medical Condition:** {patient['medical_condition']}"
        )

        st.write(
            f"**Injury Problem:** {patient['injury_problem']}"
        )

        st.write(
            f"**Emergency Contact:** {patient['emergency_contact']}"
        )

        st.write(
            f"**Registered:** {patient['registration_date']}"
        )


# =========================================================
# GAIT ANALYSIS
# =========================================================

def gait_analysis():

    patient_id = st.session_state.selected_patient

    conn = get_db()

    query = """
        SELECT *
        FROM gait_history
        WHERE patient_id = ?
        ORDER BY id ASC
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=(patient_id,)
    )

    conn.close()

    st.title("📈 Gait Analysis")

    if df.empty:

        st.info(
            "No gait data available."
        )

        return

    # -----------------------------------------------------
    # STEPS GRAPH
    # -----------------------------------------------------

    st.subheader("🚶 Steps")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["steps"],
            mode="lines+markers",
            name="Steps"
        )
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Steps"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # -----------------------------------------------------
    # PRESSURE
    # -----------------------------------------------------

    st.subheader("🦶 Pressure")

    fig2 = go.Figure()

    fig2.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["pressure"],
            mode="lines+markers",
            name="Pressure"
        )
    )

    fig2.update_layout(
        xaxis_title="Date",
        yaxis_title="Pressure"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # -----------------------------------------------------
    # GAIT ANGLE
    # -----------------------------------------------------

    st.subheader("📐 Gait Angle")

    fig3 = go.Figure()

    fig3.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["gait_angle"],
            mode="lines+markers",
            name="Gait Angle"
        )
    )

    fig3.update_layout(
        xaxis_title="Date",
        yaxis_title="Angle"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )


# =========================================================
# ALERTS
# =========================================================

def alerts_page():

    doctor_id = st.session_state.user_id

    conn = get_db()

    query = """
        SELECT
            p.name,
            gh.date,
            gh.pressure,
            gh.gait_angle,
            gh.status
        FROM gait_history gh
        JOIN patients p
        ON gh.patient_id = p.id
        WHERE p.doctor_id = ?
        AND gh.status = 'Abnormal'
        ORDER BY gh.id DESC
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=(doctor_id,)
    )

    conn.close()

    st.title("⚠️ Gait Alerts")

    if df.empty:

        st.success(
            "✅ No abnormal gait alerts."
        )

    else:

        st.error(
            f"⚠️ {len(df)} abnormal gait records detected."
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# EXERCISE MONITORING
# =========================================================

def exercise_monitoring():

    patient_id = st.session_state.selected_patient

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM patients
        WHERE id = ?
    """, (patient_id,))

    patient = cursor.fetchone()

    conn.close()

    if not patient:

        st.error(
            "Patient not found."
        )

        return

    st.title("🏃 Exercise Monitoring")

    st.write(
        f"Patient: **{patient['name']}**"
    )

    st.divider()

    exercises = [
        "Ankle Rotation",
        "Heel Raise",
        "Knee Extension",
        "Balance Exercise",
        "Walking Exercise"
    ]

    for exercise in exercises:

        col1, col2 = st.columns([4, 1])

        with col1:

            st.write(
                f"### 🏃 {exercise}"
            )

        with col2:

            st.checkbox(
                "Completed",
                key=exercise
            )


# =========================================================
# ADD DEMO GAIT DATA
# =========================================================

def add_demo_gait_data():

    patient_id = st.session_state.selected_patient

    conn = get_db()
    cursor = conn.cursor()

    demo_data = [

        ("Day 1", 3200, 68, 14, "Abnormal"),
        ("Day 2", 3800, 66, 13, "Abnormal"),
        ("Day 3", 4200, 65, 12, "Normal"),
        ("Day 4", 4700, 64, 11, "Normal"),
        ("Day 5", 5000, 63, 11, "Normal")

    ]

    for data in demo_data:

        cursor.execute("""
            INSERT INTO gait_history
            (
                patient_id,
                date,
                steps,
                pressure,
                gait_angle,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            patient_id,
            data[0],
            data[1],
            data[2],
            data[3],
            data[4]
        ))

    conn.commit()
    conn.close()

    st.success(
        "Demo gait data added successfully!"
    )

    st.rerun()


# =========================================================
# SIDEBAR
# =========================================================

def sidebar():

    with st.sidebar:

        st.title("🦶 GiatGuard")

        st.write(
            f"**{st.session_state.user_name}**"
        )

        st.write(
            f"Role: {st.session_state.user_role}"
        )

        st.divider()

        if st.session_state.user_role == "Doctor":

            if st.button(
                "🏠 Dashboard",
                use_container_width=True
            ):

                st.session_state.page = "Dashboard"
                st.rerun()

            if st.button(
                "👨‍⚕️ Doctor Profile",
                use_container_width=True
            ):

                st.session_state.page = "Doctor Profile"
                st.rerun()

            if st.button(
                "🧑‍⚕️ My Patients",
                use_container_width=True
            ):

                st.session_state.page = "Patients"
                st.rerun()

            if st.button(
                "📈 Gait Analysis",
                use_container_width=True
            ):

                st.session_state.page = "Gait Analysis"
                st.rerun()

            if st.button(
                "⚠️ Alerts",
                use_container_width=True
            ):

                st.session_state.page = "Alerts"
                st.rerun()

        else:

            if st.button(
                "🏠 Patient Dashboard",
                use_container_width=True
            ):

                st.session_state.page = "Patient Dashboard"
                st.rerun()

            if st.button(
                "👤 Patient Profile",
                use_container_width=True
            ):

                st.session_state.page = "Patient Profile"
                st.rerun()

            if st.button(
                "📊 Gait History",
                use_container_width=True
            ):

                st.session_state.page = "Patient History"
                st.rerun()

            if st.button(
                "📈 Gait Analysis",
                use_container_width=True
            ):

                st.session_state.page = "Gait Analysis"
                st.rerun()

            if st.button(
                "🏃 Exercise Monitoring",
                use_container_width=True
            ):

                st.session_state.page = "Exercise Monitoring"
                st.rerun()

        st.divider()

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):

            logout()


# =========================================================
# PAGE ROUTER
# =========================================================

def doctor_router():

    page = st.session_state.page

    if page == "Dashboard":

        doctor_dashboard()

    elif page == "Doctor Profile":

        doctor_profile()

    elif page == "Patients":

        patients_page()

    elif page == "Patient History":

        patient_history()

    elif page == "Patient Dashboard":

        patient_dashboard()

    elif page == "Patient Profile":

        patient_profile()

    elif page == "Gait Analysis":

        gait_analysis()

    elif page == "Alerts":

        alerts_page()

    elif page == "Exercise Monitoring":

        exercise_monitoring()


def patient_router():

    page = st.session_state.page

    if page == "Patient Dashboard":

        patient_dashboard()

    elif page == "Patient Profile":

        patient_profile()

    elif page == "Patient History":

        patient_history()

    elif page == "Gait Analysis":

        gait_analysis()

    elif page == "Exercise Monitoring":

        exercise_monitoring()

    else:

        patient_dashboard()


# =========================================================
# MAIN
# =========================================================

if not st.session_state.logged_in:

    login_page()

else:

    sidebar()

    if st.session_state.user_role == "Doctor":

        doctor_router()

    else:

        patient_router()