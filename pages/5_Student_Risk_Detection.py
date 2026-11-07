
import html
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from data_utils import load_data, apply_styles, show_sidebar
from risk_engine import assess_student_risk

st.set_page_config(
    page_title="Student Risk Detection | EduAnalytics",
    page_icon="E",
    layout="wide",
)

apply_styles()
show_sidebar()

st.markdown("""
<style>
.stApp { background:#F4F6FC; color:#243451; }
h1,h2,h3 { color:#243451 !important; font-family:Manrope,sans-serif; }
.page-eyebrow {
    color:#5C7CFA; font-size:.68rem; font-weight:800;
    letter-spacing:1.5px; margin-bottom:7px;
}
.page-subtitle { color:#8792A5; font-size:.86rem; margin-bottom:18px; }
.panel-title { color:#243451; font-size:1rem; font-weight:750; }
[data-testid="stVerticalBlockBorderWrapper"] {
    background:#FFFFFF; border:1px solid #E3E8F2;
    border-radius:14px; box-shadow:0 3px 12px rgba(36,52,81,.035);
}
[data-testid="stMetric"] {
    background:#FFFFFF; border:1px solid #E3E8F2;
    border-radius:13px; padding:15px;
}
[data-testid="stMetricLabel"] { color:#73819A; }
[data-testid="stMetricValue"] { color:#243451; font-family:Manrope,sans-serif; }
.risk-label {
    display:inline-block; border-radius:20px;
    padding:5px 10px; font-size:.68rem; font-weight:750;
}
.risk-high { color:#C34E5B; background:#FCEBED; }
.risk-moderate { color:#A97822; background:#FFF4DD; }
.risk-low { color:#328B69; background:#E5F6EE; }
.detail-text { color:#73819A; font-size:.78rem; line-height:1.6; }
.stButton button,.stDownloadButton button {
    background:#5C7CFA; color:white; border:1px solid #5C7CFA;
    border-radius:9px; font-weight:650;
}
.stButton button:hover,.stDownloadButton button:hover {
    background:#4969E6; color:white; border-color:#4969E6;
}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

df = load_data()

if df is None or df.empty:
    st.warning("No student records are available.")
    st.stop()


# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------

st.markdown(
    '<div class="page-eyebrow">INTELLIGENCE / EARLY SUPPORT</div>',
    unsafe_allow_html=True,
)
st.title("Student Risk Detection")
st.markdown(
    '<div class="page-subtitle">Identify students who may benefit from '
    'additional academic support using current performance indicators.</div>',
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# ASSESS STUDENT RISK
# ------------------------------------------------------------

risk_results = []

for _, student in df.iterrows():
    result = assess_student_risk(student)

    risk_results.append({
        "student_id": student["student_id"],
        "name": student["name"],
        "class_name": student["class_name"],
        "average_marks": student["average_marks"],
        "attendance": student["attendance"],
        "study_hours": student["study_hours"],
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "risk_factors": result["risk_factors"],
        "weak_subjects": result["weak_subjects"],
    })

risk_df = pd.DataFrame(risk_results)


# ------------------------------------------------------------
# RISK SUMMARY
# ------------------------------------------------------------

st.markdown(
    '<div class="page-eyebrow">RISK OVERVIEW</div>',
    unsafe_allow_html=True,
)
st.subheader("Student Risk Summary")

high_count = int((risk_df["risk_level"] == "High").sum())
moderate_count = int((risk_df["risk_level"] == "Moderate").sum())
low_count = int((risk_df["risk_level"] == "Low").sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Students", len(risk_df))
c2.metric("High Risk", high_count)
c3.metric("Moderate Risk", moderate_count)
c4.metric("Low Risk", low_count)


# ------------------------------------------------------------
# RISK DISTRIBUTION
# ------------------------------------------------------------

st.markdown(
    '<div class="page-eyebrow">RISK DISTRIBUTION</div>',
    unsafe_allow_html=True,
)
st.subheader("Risk Classification")

distribution = (
    risk_df["risk_level"]
    .value_counts()
    .reindex(["High", "Moderate", "Low"], fill_value=0)
)

risk_colors = {
    "High": "#E68B96",
    "Moderate": "#E8C27C",
    "Low": "#8DD9B5",
}

chart_data = pd.DataFrame({
    "Risk Level": distribution.index,
    "Students": distribution.values,
})

left, right = st.columns([1.5, 1], gap="medium")

with left:
    with st.container(border=True):
        fig = go.Figure(
            go.Bar(
                x=chart_data["Risk Level"],
                y=chart_data["Students"],
                marker_color=[
                    risk_colors[level]
                    for level in chart_data["Risk Level"]
                ],
                text=chart_data["Students"],
                textposition="outside",
                cliponaxis=False,
            )
        )
        fig.update_layout(
            height=300,
            margin=dict(l=10, r=15, t=20, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans", color="#52617A"),
            xaxis=dict(title=None, showgrid=False),
            yaxis=dict(
                title="Number of Students",
                gridcolor="#E9EDF5",
                rangemode="tozero",
            ),
            showlegend=False,
        )
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False},
        )

with right:
    with st.container(border=True):
        st.markdown("**Risk category breakdown**")

        total = len(risk_df)

        for level in ["High", "Moderate", "Low"]:
            value = int(distribution[level])
            percentage = value / total * 100 if total else 0

            st.markdown(
                f"""
                <div style="margin:17px 0;">
                    <div style="display:flex;justify-content:space-between;
                    color:#52617A;font-size:.78rem;font-weight:650;">
                        <span>{level} Risk</span>
                        <span>{value} ({percentage:.1f}%)</span>
                    </div>
                    <div style="height:8px;background:#EDF0F6;
                    border-radius:20px;margin-top:7px;overflow:hidden;">
                        <div style="height:8px;width:{percentage:.1f}%;
                        background:{risk_colors[level]};
                        border-radius:20px;"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ------------------------------------------------------------
# FILTERS
# ------------------------------------------------------------

st.markdown(
    '<div class="page-eyebrow">STUDENT REGISTER</div>',
    unsafe_allow_html=True,
)
st.subheader("Find Students by Risk Level")

with st.container(border=True):
    f1, f2, f3 = st.columns(3)

    with f1:
        selected_risk = st.selectbox(
            "Risk level",
            ["All", "High", "Moderate", "Low"],
        )

    with f2:
        classes = sorted(
            risk_df["class_name"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
        selected_class = st.selectbox(
            "Class",
            ["All"] + classes,
        )

    with f3:
        search_query = st.text_input(
            "Search student",
            placeholder="Name or student ID",
        )

filtered_df = risk_df.copy()

if selected_risk != "All":
    filtered_df = filtered_df[
        filtered_df["risk_level"] == selected_risk
    ]

if selected_class != "All":
    filtered_df = filtered_df[
        filtered_df["class_name"].astype(str) == selected_class
    ]

if search_query.strip():
    query = search_query.strip()
    filtered_df = filtered_df[
        filtered_df["name"].astype(str).str.contains(
            query, case=False, na=False
        )
        | filtered_df["student_id"].astype(str).str.contains(
            query, case=False, na=False
        )
    ]

filtered_df = filtered_df.reset_index(drop=True)

st.caption(f"{len(filtered_df)} students match the selected filters.")


# ------------------------------------------------------------
# RISK REGISTER
# ------------------------------------------------------------

display_df = filtered_df[
    [
        "student_id",
        "name",
        "class_name",
        "average_marks",
        "attendance",
        "study_hours",
        "risk_score",
        "risk_level",
    ]
].copy()

display_df.columns = [
    "Student ID",
    "Student Name",
    "Class",
    "Average Marks",
    "Attendance (%)",
    "Study Hours",
    "Risk Score",
    "Risk Level",
]

for col in [
    "Average Marks",
    "Attendance (%)",
    "Study Hours",
]:
    display_df[col] = display_df[col].round(1)

with st.container(border=True):
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=350,
    )

if filtered_df.empty:
    st.info("No students match the selected filters.")


# ------------------------------------------------------------
# INDIVIDUAL RISK ASSESSMENT
# ------------------------------------------------------------

st.markdown(
    '<div class="page-eyebrow">INDIVIDUAL ASSESSMENT</div>',
    unsafe_allow_html=True,
)
st.subheader("Inspect Student Risk Factors")

if not filtered_df.empty:

    student_options = {
        f"{row['name']} ({row['student_id']})": row["student_id"]
        for _, row in filtered_df.iterrows()
    }

    selected_student = st.selectbox(
        "Select a student",
        list(student_options.keys()),
        key="risk_student",
    )

    selected_id = student_options[selected_student]

    selected_record = filtered_df[
        filtered_df["student_id"] == selected_id
    ].iloc[0]

    risk_level = selected_record["risk_level"]

    badge_class = {
        "High": "risk-high",
        "Moderate": "risk-moderate",
        "Low": "risk-low",
    }[risk_level]

    with st.container(border=True):
        top_left, top_right = st.columns([3, 1])

        with top_left:
            st.markdown(f"### {selected_record['name']}")
            st.caption(
                f"Student ID: {selected_record['student_id']}  |  "
                f"Class: {selected_record['class_name']}"
            )

        with top_right:
            st.markdown(
                f"""
                <div style="text-align:right;padding-top:12px;">
                    <span class="risk-label {badge_class}">
                        {risk_level} Risk
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.divider()

        a, b, c = st.columns(3)
        a.metric("Risk Score", selected_record["risk_score"])
        b.metric("Average Marks", f"{selected_record['average_marks']:.1f}%")
        c.metric("Attendance", f"{selected_record['attendance']:.1f}%")

        st.markdown("**Identified Risk Factors**")

        factors = selected_record["risk_factors"]

        if factors:
            for factor in factors:
                st.markdown(
                    f'<div class="detail-text">• '
                    f'{html.escape(str(factor))}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.success("No risk factors were identified.")

        st.markdown("")
        st.markdown("**Subjects Requiring Attention**")

        weak_subjects = selected_record["weak_subjects"]

        if weak_subjects:
            st.write(", ".join(weak_subjects))
        else:
            st.success("No subjects are currently below 40 marks.")

else:
    st.info("No student is available for individual assessment.")


# ------------------------------------------------------------
# DOWNLOAD RISK REPORT
# ------------------------------------------------------------

st.markdown(
    '<div class="page-eyebrow">EXPORT / RISK REGISTER</div>',
    unsafe_allow_html=True,
)
st.subheader("Download Risk Assessment Report")

report_df = risk_df[
    [
        "student_id",
        "name",
        "class_name",
        "average_marks",
        "attendance",
        "study_hours",
        "risk_score",
        "risk_level",
    ]
].copy()

report_df["risk_factors"] = risk_df["risk_factors"].apply(
    lambda factors: "; ".join(str(factor) for factor in factors)
)

report_df["weak_subjects"] = risk_df["weak_subjects"].apply(
    lambda subjects: "; ".join(str(subject) for subject in subjects)
)

with st.container(border=True):
    st.caption(
        "Export the risk classification and contributing indicators "
        "for all students."
    )

    st.download_button(
        label="Download Risk Assessment CSV",
        data=report_df.to_csv(index=False).encode("utf-8"),
        file_name="student_risk_assessment.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.caption(
    "Risk classifications use initial rule-based thresholds. "
    "They are indicators for teacher review, not definitive judgements "
    "or validated predictions of student outcomes."
)

st.markdown("""
<div style="text-align:center;color:#9AA4B6;font-size:.74rem;
padding:22px 0;border-top:1px solid #E3E8F2;margin-top:25px;">
EduAnalytics · Student Risk Intelligence
</div>
""", unsafe_allow_html=True)
