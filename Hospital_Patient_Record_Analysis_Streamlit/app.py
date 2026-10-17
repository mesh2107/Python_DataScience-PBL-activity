
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import date

DATA_FILE = Path("patients.csv")

COLUMNS = [
    "Patient ID", "Name", "Age", "Gender", "Blood Group", "Phone",
    "Department", "Diagnosis", "Doctor", "Admission Date",
    "Discharge Date", "Status", "Treatment Cost"
]

def load_data():
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
        return df[COLUMNS]
    return pd.DataFrame(columns=COLUMNS)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

st.set_page_config(
    page_title="Hospital Patient Record Analysis",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Hospital Patient Record Analysis System")
st.caption("Streamlit-based college micro project for managing and analyzing hospital patient records.")

df = load_data()

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Select Module",
    ["Dashboard", "Add Patient", "Patient Records", "Search Patient", "Analysis", "About Project"]
)

# Dashboard
if page == "Dashboard":
    st.header("📊 Dashboard")

    total = len(df)
    admitted = int((df["Status"].astype(str).str.lower() == "admitted").sum())
    discharged = int((df["Status"].astype(str).str.lower() == "discharged").sum())
    total_cost = pd.to_numeric(df["Treatment Cost"], errors="coerce").fillna(0).sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Patients", total)
    c2.metric("Currently Admitted", admitted)
    c3.metric("Discharged", discharged)
    c4.metric("Treatment Revenue", f"₹{total_cost:,.0f}")

    if not df.empty:
        st.subheader("Recent Patient Records")
        st.dataframe(df.tail(10), use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)
        with col1:
            dept = df["Department"].value_counts().reset_index()
            dept.columns = ["Department", "Patients"]
            fig = px.bar(dept, x="Department", y="Patients",
                         title="Patients by Department", text_auto=True)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            gender = df["Gender"].value_counts().reset_index()
            gender.columns = ["Gender", "Patients"]
            fig = px.pie(gender, names="Gender", values="Patients",
                         title="Gender Distribution", hole=0.35)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No patient records found. Add patients from the Add Patient module.")

# Add patient
elif page == "Add Patient":
    st.header("➕ Add New Patient")

    with st.form("patient_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            patient_id = st.text_input("Patient ID", placeholder="P001")
            name = st.text_input("Patient Name")
            age = st.number_input("Age", min_value=0, max_value=120, value=25)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            blood = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
            phone = st.text_input("Phone Number")
        with c2:
            department = st.selectbox(
                "Department",
                ["General Medicine", "Cardiology", "Orthopedics",
                 "Neurology", "Pediatrics", "Gynecology", "Emergency", "Other"]
            )
            diagnosis = st.text_input("Diagnosis")
            doctor = st.text_input("Doctor Name")
            admission = st.date_input("Admission Date", value=date.today())
            discharge = st.date_input("Discharge Date", value=None)
            status = st.selectbox("Status", ["Admitted", "Discharged"])
            cost = st.number_input("Treatment Cost (₹)", min_value=0.0, value=0.0, step=500.0)

        submitted = st.form_submit_button("Save Patient", type="primary")

    if submitted:
        if not patient_id.strip() or not name.strip():
            st.error("Patient ID and Patient Name are required.")
        elif patient_id in df["Patient ID"].astype(str).values:
            st.error("Patient ID already exists.")
        else:
            new_row = {
                "Patient ID": patient_id.strip(),
                "Name": name.strip(),
                "Age": age,
                "Gender": gender,
                "Blood Group": blood,
                "Phone": phone.strip(),
                "Department": department,
                "Diagnosis": diagnosis.strip(),
                "Doctor": doctor.strip(),
                "Admission Date": admission,
                "Discharge Date": discharge if discharge else "",
                "Status": status,
                "Treatment Cost": cost
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success(f"Patient {name} added successfully.")

# Records
elif page == "Patient Records":
    st.header("📋 All Patient Records")

    if df.empty:
        st.info("No records available.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.download_button(
            "⬇️ Download Patient Records (CSV)",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="hospital_patient_records.csv",
            mime="text/csv"
        )

        st.divider()
        st.subheader("Delete Patient")
        patient_to_delete = st.selectbox(
            "Select Patient ID",
            [""] + df["Patient ID"].astype(str).tolist()
        )
        if st.button("Delete Selected Patient", type="secondary"):
            if patient_to_delete:
                df = df[df["Patient ID"].astype(str) != patient_to_delete]
                save_data(df)
                st.success("Patient record deleted.")
                st.rerun()

# Search
elif page == "Search Patient":
    st.header("🔎 Search Patient")

    query = st.text_input("Search by Patient ID, Name, Diagnosis, Department or Doctor")

    if query:
        mask = df.astype(str).apply(
            lambda col: col.str.contains(query, case=False, na=False)
        ).any(axis=1)
        result = df[mask]

        st.write(f"**{len(result)} record(s) found**")
        if result.empty:
            st.warning("No matching patient found.")
        else:
            st.dataframe(result, use_container_width=True, hide_index=True)

# Analysis
elif page == "Analysis":
    st.header("📈 Patient Record Analysis")

    if df.empty:
        st.info("Add patient records to see analysis.")
    else:
        work = df.copy()
        work["Age"] = pd.to_numeric(work["Age"], errors="coerce")
        work["Treatment Cost"] = pd.to_numeric(work["Treatment Cost"], errors="coerce").fillna(0)

        col1, col2 = st.columns(2)

        with col1:
            dept = work["Department"].value_counts().reset_index()
            dept.columns = ["Department", "Patients"]
            st.plotly_chart(
                px.bar(dept, x="Department", y="Patients",
                       title="Department-wise Patient Count", text_auto=True),
                use_container_width=True
            )

        with col2:
            blood = work["Blood Group"].value_counts().reset_index()
            blood.columns = ["Blood Group", "Patients"]
            st.plotly_chart(
                px.pie(blood, names="Blood Group", values="Patients",
                       title="Blood Group Distribution"),
                use_container_width=True
            )

        col3, col4 = st.columns(2)

        with col3:
            st.plotly_chart(
                px.histogram(work, x="Age", nbins=10,
                             title="Age Distribution of Patients"),
                use_container_width=True
            )

        with col4:
            st.plotly_chart(
                px.box(work, x="Gender", y="Treatment Cost",
                       title="Treatment Cost by Gender"),
                use_container_width=True
            )

        st.subheader("Key Statistics")
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Average Age", f"{work['Age'].mean():.1f}")
        s2.metric("Average Treatment Cost", f"₹{work['Treatment Cost'].mean():,.0f}")
        s3.metric("Maximum Treatment Cost", f"₹{work['Treatment Cost'].max():,.0f}")
        s4.metric("Most Common Department",
                  work["Department"].mode().iloc[0] if not work["Department"].mode().empty else "N/A")

# About
else:
    st.header("ℹ️ About the Project")
    st.markdown("""
### Hospital Patient Record Analysis System

**Technology Used**
- Python
- Streamlit
- Pandas
- Plotly
- CSV database

**Main Modules**
1. Dashboard
2. Add Patient
3. Patient Records
4. Search Patient
5. Data Analysis
6. CSV Export

**Objective**

The project provides a simple hospital record management system that can store
patient information, search records, display important statistics and generate
visual analysis of hospital data.

**College Project Type:** Micro Project / Mini Project  
**Application Area:** Hospital / Healthcare Record Management
""")
