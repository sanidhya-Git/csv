import streamlit as st
import plotly.express as px

from auth import signup_user
from otp import generate_otp, send_otp
from database import (
    init_db,
    get_user,
    record_upload,
    monthly_upload_count
)
from analyze import analyze_csv
from ai import generate_ai_insights
from pdf_report import generate_pdf

FREE_LIMIT = 15
ADMIN_EMAIL = "admin@csv.com"

st.set_page_config(
    page_title="CSV Analyzer",
    page_icon="📊",
    layout="wide"
)


st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
    color: white;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
}

div[data-testid="stMetric"] {
    background: #1f2937;
    padding: 15px;
    border-radius: 12px;
}

.stButton > button {
    width: 100%;
    border-radius: 8px;
}

table {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)


init_db()

if "user" not in st.session_state:
    st.session_state.user = None

if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False

if "login_otp" not in st.session_state:
    st.session_state.login_otp = ""

if "login_email" not in st.session_state:
    st.session_state.login_email = ""

if not st.session_state.user:

    st.title("📊 CSV Analyzer V2")
    st.caption("Upload CSV • Analyze • Visualize • Export")

    tab1, tab2 = st.tabs(["OTP Login", "Signup"])


    with tab1:

        email = st.text_input("Email", key="login_email_input")

        if not st.session_state.otp_sent:

            if st.button("Send OTP"):

                if email.strip() == "":
                    st.error("Enter email first")

                else:
                    otp = generate_otp()

                    st.session_state.login_otp = otp
                    st.session_state.login_email = email.strip()
                    st.session_state.otp_sent = True

                    try:
                        send_otp(email.strip(), otp)
                        st.success("OTP sent successfully")
                    except Exception as e:
                        st.error(f"OTP failed: {e}")

        else:

            entered_otp = st.text_input("Enter OTP")

            if st.button("Verify OTP"):

                if entered_otp == st.session_state.login_otp:

                    st.session_state.user = st.session_state.login_email
                    st.session_state.otp_sent = False
                    st.rerun()

                else:
                    st.error("Invalid OTP")

            if st.button("Resend OTP"):

                otp = generate_otp()

                st.session_state.login_otp = otp

                try:
                    send_otp(
                        st.session_state.login_email,
                        otp
                    )
                    st.success("OTP resent")
                except Exception as e:
                    st.error(f"OTP failed: {e}")

    with tab2:

        new_email = st.text_input(
            "Signup Email",
            key="signup_email"
        )

        new_pass = st.text_input(
            "Signup Password",
            type="password",
            key="signup_password"
        )

        if st.button("Create Account"):

            ok, msg = signup_user(
                new_email.strip(),
                new_pass
            )

            if ok:
                st.success(msg)
            else:
                st.error(msg)

    st.stop()


user = get_user(st.session_state.user)

if not user:
    st.session_state.user = None
    st.rerun()

plan = user["plan"]
used = monthly_upload_count(user["email"])
limit = "Unlimited" if plan == "pro" else FREE_LIMIT


st.sidebar.success(user["email"])
st.sidebar.info(f"Plan: {plan.upper()}")
st.sidebar.info(f"Uploads Used: {used}/{limit}")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Profile", "Analytics"]
)

if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()

if user["email"] == ADMIN_EMAIL:
    st.sidebar.subheader("👑 Admin Panel")
    st.sidebar.write("Manage Users")
    st.sidebar.write("Upgrade Plans")
    st.sidebar.write("View Stats")


if page == "Dashboard":

    st.title("📈 Dashboard")

    uploaded_file = st.file_uploader(
        "Upload CSV File",
        type=["csv"]
    )

    if uploaded_file:

        if plan == "free" and used >= FREE_LIMIT:
            st.error(
                "Free plan monthly limit reached."
            )
            st.stop()

        try:
            report = analyze_csv(uploaded_file)
            df = report["df"]

            record_upload(
                user["email"],
                uploaded_file.name
            )

            st.success("File uploaded successfully!")

            st.subheader("📄 Data Preview")
            st.dataframe(
                df.head(100),
                use_container_width=True
            )

            rows, cols = report["Shape"]

            c1, c2 = st.columns(2)
            c1.metric("Rows", rows)
            c2.metric("Columns", cols)

            st.subheader("📉 Null Values")
            st.json(report["Null Values"])

            st.subheader("📊 Descriptive Statistics")
            st.markdown(
                report["Descriptive Stats"],
                unsafe_allow_html=True
            )

            st.subheader("📌 Correlation Matrix")
            st.markdown(
                report["Correlation"],
                unsafe_allow_html=True
            )


            numeric_cols = df.select_dtypes(
                include=["int64", "float64"]
            ).columns.tolist()

            all_cols = df.columns.tolist()

            if numeric_cols:

                st.subheader("📈 Advanced Visualizations")

                chart_type = st.selectbox(
                    "Choose Chart Type",
                    [
                        "Scatter Plot",
                        "Line Chart",
                        "Bar Chart",
                        "Histogram",
                        "Box Plot",
                        "Area Chart",
                        "Pie Chart",
                        "Violin Plot",
                        "Density Heatmap",
                        "Correlation Heatmap"
                    ]
                )

                if chart_type == "Scatter Plot":
                    x = st.selectbox("X Axis", numeric_cols)
                    y = st.selectbox("Y Axis", numeric_cols)
                    fig = px.scatter(df, x=x, y=y)

                elif chart_type == "Line Chart":
                    x = st.selectbox("X Axis", all_cols)
                    y = st.selectbox("Y Axis", numeric_cols)
                    fig = px.line(df, x=x, y=y)

                elif chart_type == "Bar Chart":
                    x = st.selectbox("X Axis", all_cols)
                    y = st.selectbox("Y Axis", numeric_cols)
                    fig = px.bar(df, x=x, y=y)

                elif chart_type == "Histogram":
                    col = st.selectbox("Column", numeric_cols)
                    fig = px.histogram(df, x=col)

                elif chart_type == "Box Plot":
                    col = st.selectbox("Column", numeric_cols)
                    fig = px.box(df, y=col)

                elif chart_type == "Area Chart":
                    x = st.selectbox("X Axis", all_cols)
                    y = st.selectbox("Y Axis", numeric_cols)
                    fig = px.area(df, x=x, y=y)

                elif chart_type == "Pie Chart":
                    names = st.selectbox("Category", all_cols)
                    values = st.selectbox("Values", numeric_cols)
                    fig = px.pie(df, names=names, values=values)

                elif chart_type == "Violin Plot":
                    col = st.selectbox("Column", numeric_cols)
                    fig = px.violin(df, y=col, box=True)

                elif chart_type == "Density Heatmap":
                    x = st.selectbox("X Axis", numeric_cols)
                    y = st.selectbox("Y Axis", numeric_cols)
                    fig = px.density_heatmap(df, x=x, y=y)

                elif chart_type == "Correlation Heatmap":
                    corr = df.corr(numeric_only=True)
                    fig = px.imshow(corr, text_auto=True)

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            st.subheader("🤖 AI Insights")

            insights = generate_ai_insights(df)

            for item in insights:
                st.info(item)

   
            pdf = generate_pdf(
                report,
                user["email"]
            )

            st.download_button(
                "📄 Download PDF Report",
                data=pdf,
                file_name="csv_report.pdf",
                mime="application/pdf"
            )

        except Exception as e:
            st.error(f"Error: {e}")

elif page == "Profile":

    st.title("👤 User Profile")

    st.write("📧 Email:", user["email"])
    st.write("💎 Plan:", user["plan"].upper())
    st.write("📂 Monthly Uploads:", used)


elif page == "Analytics":

    st.title("📊 Analytics Dashboard")

    st.subheader("Uploads Trend")
    st.line_chart([2, 5, 4, 8, 6, 10])

    st.subheader("User Growth")
    st.bar_chart([10, 20, 15, 28])