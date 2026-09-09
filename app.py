import streamlit as st
import pandas as pd
import plotly.graph_objects as go


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="GiatGuard",
    page_icon="👣",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

    /* Main background */
    .stApp {
        background-color: #f4f7fb;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0b1f3a;
    }

    section[data-testid="stSidebar"] * {
        color: white;
    }

    /* Main title */
    .main-title {
        font-size: 38px;
        font-weight: 700;
        color: #0b1f3a;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 17px;
        color: #667085;
        margin-top: 5px;
    }

    /* Metric cards */
    .metric-card {
        background: white;
        padding: 22px;
        border-radius: 15px;
        border: 1px solid #e6eaf0;
        box-shadow: 0px 3px 12px rgba(0,0,0,0.06);
        text-align: left;
    }

    .metric-title {
        font-size: 14px;
        color: #667085;
        margin-bottom: 8px;
    }

    .metric-value {
        font-size: 30px;
        font-weight: 700;
        color: #0b1f3a;
    }

    .metric-icon {
        font-size: 25px;
    }

    /* Status */
    .normal-status {
        color: green;
        font-weight: 700;
    }

    .warning-status {
        color: red;
        font-weight: 700;
    }

    /* Login box */
    .login-box {
        background: white;
        padding: 35px;
        border-radius: 18px;
        box-shadow: 0px 5px 20px rgba(0,0,0,0.08);
    }

    /* Patient table */
    .section-title {
        font-size: 24px;
        font-weight: 700;
        color: #0b1f3a;
        margin-top: 20px;
        margin-bottom: 15px;
    }

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

if "user_name" not in st.session_state:
    st.session_state.user_name = None


# =========================================================
# DEMO USERS
# =========================================================

DOCTOR_EMAIL = "doctor@giatguard.com"
DOCTOR_PASSWORD = "1234"

PATIENT_EMAIL = "patient@giatguard.com"
PATIENT_PASSWORD = "1234"


# =========================================================
# LOGIN PAGE
# =========================================================

def login_page():

    st.markdown("<br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        st.markdown(
            """
            <div class="login-box">

                <div style="text-align:center;">

                    <div style="font-size:55px;">
                        👣
                    </div>

                    <div class="main-title">
                        GiatGuard
                    </div>

                    <div class="subtitle">
                        Smart Rehabilitation Insole
                    </div>

                    <br>

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### 🔐 Login")

        role = st.selectbox(
            "Login as",
            ["Doctor", "Patient"]
        )

        email = st.text_input(
            "Email",
            placeholder="Enter your email"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

        login_button = st.button(
            "LOGIN",
            use_container_width=True
        )

        if login_button:

            if role == "Doctor":

                if (
                    email == DOCTOR_EMAIL
                    and password == DOCTOR_PASSWORD
                ):

                    st.session_state.logged_in = True
                    st.session_state.role = "Doctor"
                    st.session_state.user_name = "Dr. GiatGuard"

                    st.rerun()

                else:

                    st.error(
                        "Invalid Doctor email or password."
                    )

            else:

                if (
                    email == PATIENT_EMAIL
                    and password == PATIENT_PASSWORD
                ):

                    st.session_state.logged_in = True
                    st.session_state.role = "Patient"
                    st.session_state.user_name = "Arun"

                    st.rerun()

                else:

                    st.error(
                        "Invalid Patient email or password."
                    )

        st.info(
            "Demo Doctor: doctor@giatguard.com / 1234\n\n"
            "Demo Patient: patient@giatguard.com / 1234"
        )


# =========================================================
# DOCTOR DASHBOARD
# =========================================================

def doctor_dashboard():

    # Sidebar

    st.sidebar.markdown(
        """
        <div style="text-align:center;">
            <div style="font-size:45px;">👣</div>
            <h2>GIATGUARD</h2>
            <p>Doctor Portal</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    menu = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "Patients",
            "Gait Analysis",
            "Alerts",
            "Recommendations"
        ]
    )

    if st.sidebar.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.user_name = None

        st.rerun()


    # =====================================================
    # DASHBOARD
    # =====================================================

    if menu == "Dashboard":

        st.markdown(
            '<div class="main-title">Doctor Dashboard</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="subtitle">Welcome, {st.session_state.user_name} 👋</div>',
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)


        # Metrics

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.markdown(
                """
                <div class="metric-card">
                    <div class="metric-icon">👥</div>
                    <div class="metric-title">
                        Total Patients
                    </div>
                    <div class="metric-value">
                        12
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:

            st.markdown(
                """
                <div class="metric-card">
                    <div class="metric-icon">📡</div>
                    <div class="metric-title">
                        Active Monitoring
                    </div>
                    <div class="metric-value">
                        9
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:

            st.markdown(
                """
                <div class="metric-card">
                    <div class="metric-icon">✓</div>
                    <div class="metric-title">
                        Normal Gait
                    </div>
                    <div class="metric-value">
                        10
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col4:

            st.markdown(
                """
                <div class="metric-card">
                    <div class="metric-icon">⚠️</div>
                    <div class="metric-title">
                        Alerts
                    </div>
                    <div class="metric-value">
                        2
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


        st.markdown(
            '<div class="section-title">📊 Patient Monitoring</div>',
            unsafe_allow_html=True
        )


        # Patient data

        data = pd.DataFrame(
            {
                "Patient": [
                    "Arun",
                    "Kavin",
                    "Rahul",
                    "Sanjay",
                    "Vijay"
                ],

                "Age": [
                    21,
                    23,
                    20,
                    22,
                    24
                ],

                "Gait Angle": [
                    13,
                    19,
                    12,
                    14,
                    21
                ],

                "Pressure": [
                    63,
                    78,
                    61,
                    65,
                    82
                ],

                "Steps": [
                    4250,
                    3200,
                    5100,
                    4600,
                    2800
                ],

                "Status": [
                    "Normal",
                    "Abnormal",
                    "Normal",
                    "Normal",
                    "Abnormal"
                ]
            }
        )

        st.dataframe(
            data,
            use_container_width=True,
            hide_index=True
        )


        # Charts

        col1, col2 = st.columns(2)


        with col1:

            st.markdown(
                '<div class="section-title">📐 Gait Angle Trend</div>',
                unsafe_allow_html=True
            )

            days = [
                "Day 1",
                "Day 2",
                "Day 3",
                "Day 4",
                "Day 5"
            ]

            angles = [
                18,
                16,
                15,
                14,
                13
            ]

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=days,
                    y=angles,
                    mode="lines+markers",
                    name="Gait Angle"
                )
            )

            fig.update_layout(
                height=350,
                margin=dict(
                    l=20,
                    r=20,
                    t=20,
                    b=20
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


        with col2:

            st.markdown(
                '<div class="section-title">👣 Pressure Trend</div>',
                unsafe_allow_html=True
            )

            pressure = [
                72,
                69,
                67,
                65,
                63
            ]

            fig2 = go.Figure()

            fig2.add_trace(
                go.Scatter(
                    x=days,
                    y=pressure,
                    mode="lines+markers",
                    name="Pressure"
                )
            )

            fig2.update_layout(
                height=350,
                margin=dict(
                    l=20,
                    r=20,
                    t=20,
                    b=20
                )
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )


    # =====================================================
    # PATIENTS
    # =====================================================

    elif menu == "Patients":

        st.markdown(
            '<div class="main-title">Patient Management</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            "Manage registered rehabilitation patients."
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.button(
            "➕ Register New Patient",
            use_container_width=False
        )

        patient_data = pd.DataFrame(
            {
                "Patient ID": [
                    "GG001",
                    "GG002",
                    "GG003",
                    "GG004"
                ],

                "Name": [
                    "Arun",
                    "Kavin",
                    "Rahul",
                    "Sanjay"
                ],

                "Age": [
                    21,
                    23,
                    20,
                    22
                ],

                "Target Steps": [
                    5000,
                    4500,
                    6000,
                    5000
                ],

                "Status": [
                    "Normal",
                    "Abnormal",
                    "Normal",
                    "Normal"
                ]
            }
        )

        st.dataframe(
            patient_data,
            use_container_width=True,
            hide_index=True
        )


    # =====================================================
    # GAIT ANALYSIS
    # =====================================================

    elif menu == "Gait Analysis":

        st.markdown(
            '<div class="main-title">Gait Analysis</div>',
            unsafe_allow_html=True
        )

        patient = st.selectbox(
            "Select Patient",
            [
                "Arun",
                "Kavin",
                "Rahul",
                "Sanjay"
            ]
        )

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Current Gait Angle",
                "13°"
            )

        with col2:

            st.metric(
                "Average Pressure",
                "63"
            )

        with col3:

            st.metric(
                "Today's Steps",
                "4,250"
            )

        st.markdown(
            "### 📈 Recovery Progress"
        )

        recovery = pd.DataFrame(
            {
                "Day": [
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7
                ],

                "Gait Angle": [
                    19,
                    18,
                    17,
                    15,
                    14,
                    13,
                    13
                ]
            }
        )

        st.line_chart(
            recovery.set_index("Day")
        )


    # =====================================================
    # ALERTS
    # =====================================================

    elif menu == "Alerts":

        st.markdown(
            '<div class="main-title">⚠️ Gait Alerts</div>',
            unsafe_allow_html=True
        )

        st.error(
            "Kavin — Abnormal gait detected"
        )

        st.warning(
            "Vijay — High plantar pressure detected"
        )

        st.success(
            "Arun — Gait condition is normal"
        )


    # =====================================================
    # RECOMMENDATIONS
    # =====================================================

    elif menu == "Recommendations":

        st.markdown(
            '<div class="main-title">📝 Doctor Recommendations</div>',
            unsafe_allow_html=True
        )

        patient = st.selectbox(
            "Select Patient",
            [
                "Arun",
                "Kavin",
                "Rahul",
                "Sanjay"
            ]
        )

        recommendation = st.text_area(
            "Enter rehabilitation recommendation",
            placeholder="Example: Continue walking exercise for 20 minutes daily."
        )

        if st.button("Save Recommendation"):

            if recommendation:

                st.success(
                    f"Recommendation saved for {patient}."
                )

            else:

                st.warning(
                    "Please enter a recommendation."
                )


# =========================================================
# PATIENT DASHBOARD
# =========================================================

def patient_dashboard():

    st.sidebar.markdown(
        """
        <div style="text-align:center;">
            <div style="font-size:45px;">👣</div>
            <h2>GIATGUARD</h2>
            <p>Patient Portal</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    menu = st.sidebar.radio(
        "Navigation",
        [
            "My Dashboard",
            "Gait History",
            "Exercise Monitoring"
        ]
    )

    if st.sidebar.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.user_name = None

        st.rerun()


    # =====================================================
    # PATIENT DASHBOARD
    # =====================================================

    if menu == "My Dashboard":

        st.markdown(
            '<div class="main-title">Patient Dashboard</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="subtitle">Welcome, {st.session_state.user_name} 👋</div>',
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)


        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "🚶 Today's Steps",
                "4,250",
                "350"
            )

        with col2:

            st.metric(
                "📐 Gait Angle",
                "13°",
                "-1°"
            )

        with col3:

            st.metric(
                "👣 Pressure",
                "63",
                "-2"
            )

        with col4:

            st.metric(
                "🩺 Gait Status",
                "Normal"
            )


        st.markdown(
            "### 🎯 Daily Walking Target"
        )

        progress = 4250 / 5000

        st.progress(
            progress
        )

        st.write(
            "4,250 / 5,000 steps completed"
        )


        st.markdown(
            "### 📈 Recovery Progress"
        )

        recovery = pd.DataFrame(
            {
                "Day": [
                    "Day 1",
                    "Day 2",
                    "Day 3",
                    "Day 4",
                    "Day 5"
                ],

                "Gait Angle": [
                    18,
                    16,
                    15,
                    14,
                    13
                ],

                "Pressure": [
                    72,
                    69,
                    67,
                    65,
                    63
                ]
            }
        )

        st.line_chart(
            recovery.set_index("Day")
        )


        st.success(
            "✓ Your gait condition is currently Normal."
        )


    # =====================================================
    # GAIT HISTORY
    # =====================================================

    elif menu == "Gait History":

        st.markdown(
            '<div class="main-title">📋 My Gait History</div>',
            unsafe_allow_html=True
        )

        history = pd.DataFrame(
            {
                "Day": [
                    "Day 1",
                    "Day 2",
                    "Day 3",
                    "Day 4",
                    "Day 5"
                ],

                "Steps": [
                    3200,
                    3800,
                    4200,
                    4700,
                    4250
                ],

                "Pressure": [
                    72,
                    69,
                    67,
                    65,
                    63
                ],

                "Gait Angle": [
                    18,
                    16,
                    15,
                    14,
                    13
                ],

                "Status": [
                    "Abnormal",
                    "Abnormal",
                    "Normal",
                    "Normal",
                    "Normal"
                ]
            }
        )

        st.dataframe(
            history,
            use_container_width=True,
            hide_index=True
        )


    # =====================================================
    # EXERCISE MONITORING
    # =====================================================

    elif menu == "Exercise Monitoring":

        st.markdown(
            '<div class="main-title">🏃 Exercise Monitoring</div>',
            unsafe_allow_html=True
        )

        st.write(
            "Monitor rehabilitation exercise performance."
        )

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Current Exercise Angle",
                "42°"
            )

        with col2:

            st.metric(
                "Required Angle",
                "40° - 45°"
            )

        st.success(
            "✓ Exercise performed correctly"
        )

        st.info(
            "Keep your movement slow and controlled."
        )


# =========================================================
# APPLICATION CONTROL
# =========================================================

if not st.session_state.logged_in:

    login_page()

else:

    if st.session_state.role == "Doctor":

        doctor_dashboard()

    elif st.session_state.role == "Patient":

        patient_dashboard()