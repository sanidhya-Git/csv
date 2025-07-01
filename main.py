import streamlit as st
import plotly.express as px
from auth import signup_user, login_user, reset_password
from database import create_user_table
from analyze import analyze_csv
import pdf_report  

st.set_page_config(page_title="CSV Analyzer", page_icon="📊", layout="centered")

create_user_table()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.email = ""

def login_page():
    st.title("🔐 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login_user(email, password):
            st.session_state.logged_in = True
            st.session_state.email = email
            st.success("Logged in successfully!")
        else:
            st.error("Invalid credentials")
    st.info("Don't have an account? Go to Signup.")
    if st.button("Go to Signup"):
        st.session_state.page = "signup"
    st.info("Forgot your password?")
    if st.button("Reset Password"):
        st.session_state.page = "reset"

def signup_page():
    st.title("📝 Signup")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        if signup_user(email, password):
            st.success("Signup successful! Please login.")
            st.session_state.page = "login"
        else:
            st.error("User already exists.")
    if st.button("Go to Login"):
        st.session_state.page = "login"

def reset_page():
    st.title("🔁 Reset Password")
    email = st.text_input("Email")
    new_pass = st.text_input("New Password", type="password")
    if st.button("Update Password"):
        if reset_password(email, new_pass):
            st.success("Password updated. Please login.")
            st.session_state.page = "login"
        else:
            st.error("Email not found.")
    if st.button("Back to Login"):
        st.session_state.page = "login"

def dashboard():
    st.title("📊 CSV Analyzer Dashboard")
    st.success(f"Welcome, {st.session_state.email}!")

    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    if uploaded_file:
        st.write("✅ File uploaded!")
        report = analyze_csv(uploaded_file)
        df = report["df"]

        st.subheader("🔍 Shape of Data")
        st.write(report["Shape"])

        st.subheader("📉 Null Values")
        st.json(report["Null Values"])

        st.subheader("📋 Descriptive Statistics")
        st.markdown(report["Descriptive Stats"], unsafe_allow_html=True)

        st.subheader("📌 Correlation Matrix")
        st.markdown(report["Correlation"], unsafe_allow_html=True)

       
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

        if numeric_cols:
            st.subheader("📈 Visualize Data")

            chart_type = st.selectbox("Choose chart type", ["Scatter Plot", "Histogram", "Box Plot", "Correlation Heatmap"])

            if chart_type == "Scatter Plot":
                x_axis = st.selectbox("X-axis", numeric_cols)
                y_axis = st.selectbox("Y-axis", numeric_cols, index=1 if len(numeric_cols) > 1 else 0)
                fig = px.scatter(df, x=x_axis, y=y_axis, title=f"Scatter Plot of {x_axis} vs {y_axis}")
                st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "Histogram":
                col = st.selectbox("Select column for histogram", numeric_cols)
                fig = px.histogram(df, x=col, nbins=30, title=f"Histogram of {col}")
                st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "Box Plot":
                col = st.selectbox("Select column for box plot", numeric_cols)
                fig = px.box(df, y=col, title=f"Box Plot of {col}")
                st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "Correlation Heatmap":
                corr = df.corr(numeric_only=True)
                fig = px.imshow(corr, text_auto=True, aspect="auto", title="Correlation Heatmap")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No numeric columns available for plotting.")


        if st.button("📄 Export Insights as PDF"):
            pdf_bytes = pdf_report.generate_pdf(report, st.session_state.email)
            st.download_button(
                label="Download PDF Report",
                data=pdf_bytes,
                file_name="csv_analysis_report.pdf",
                mime="application/pdf"
            )

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "login"
        st.session_state.email = ""

if "page" not in st.session_state:
    st.session_state.page = "login"

if not st.session_state.logged_in:
    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "signup":
        signup_page()
    elif st.session_state.page == "reset":
        reset_page()
else:
    dashboard()

