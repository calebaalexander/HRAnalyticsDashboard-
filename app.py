import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

def load_data():
    # Load your Excel file
    df = pd.read_excel('BusEmployeesInfo.xlsx')
    
    # Convert StartDate to datetime if not already
    df['StartDate'] = pd.to_datetime(df['StartDate'])
    
    # Calculate tenure
    df['Tenure'] = (datetime.now() - df['StartDate']).dt.days / 365
    
    return df

def format_large_number(num):
    if num >= 1000000:
        return f"${num/1000000:.1f}M"
    elif num >= 1000:
        return f"${num/1000:.1f}K"
    else:
        return f"${num:.0f}"

def main():
    st.markdown("# **HR Analytics Dashboard**")
    
    # Load data
    df = load_data()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Job Title filter
    job_titles = ["All"] + list(df["Job Title"].unique())
    selected_title = st.sidebar.selectbox("Select Job Title", job_titles)
    
    # Apply filters
    if selected_title != "All":
        df_filtered = df[df["Job Title"] == selected_title]
    else:
        df_filtered = df.copy()
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Employees", len(df_filtered))
    with col2:
        avg_salary = df_filtered["Salary"].mean()
        st.metric("Average Salary", format_large_number(avg_salary))
    with col3:
        avg_tenure = df_filtered["Tenure"].mean()
        st.metric("Avg Tenure (Years)", f"{avg_tenure:.1f}")
    with col4:
        total_salary = df_filtered["Salary"].sum()
        st.metric("Total Salary Cost", format_large_number(total_salary))

    # Create tabs for different analyses
    tab1, tab2, tab3 = st.tabs(["Salary Analysis", "Team Composition", "Tenure Insights"])
    
    with tab1:
        st.subheader("Salary Distribution")
        
        # Salary distribution plot
        fig_salary = px.histogram(
            df_filtered,
            x="Salary",
            nbins=20,
            title="Salary Distribution"
        )
        st.plotly_chart(fig_salary)
        
        # Salary by Job Title
        fig_salary_job = px.box(
            df_filtered,
            x="Job Title",
            y="Salary",
            title="Salary Range by Job Title"
        )
        fig_salary_job.update_xaxes(tickangle=45)
        st.plotly_chart(fig_salary_job)

    with tab2:
        st.subheader("Team Composition")
        
        # Job Title distribution
        job_dist = df_filtered["Job Title"].value_counts()
        fig_jobs = px.pie(
            values=job_dist.values,
            names=job_dist.index,
            title="Employee Distribution by Job Title"
        )
        st.plotly_chart(fig_jobs)
        
        # Geographic distribution
        zip_dist = df_filtered["Zip"].value_counts()
        fig_zip = px.bar(
            x=zip_dist.index,
            y=zip_dist.values,
            title="Employee Distribution by ZIP Code"
        )
        st.plotly_chart(fig_zip)

    with tab3:
        st.subheader("Tenure Analysis")
        
        # Tenure distribution
        fig_tenure = px.histogram(
            df_filtered,
            x="Tenure",
            nbins=20,
            title="Employee Tenure Distribution (Years)"
        )
        st.plotly_chart(fig_tenure)
        
        # Hiring timeline
        fig_timeline = px.scatter(
            df_filtered,
            x="StartDate",
            y="Job Title",
            title="Employee Start Dates by Job Title"
        )
        st.plotly_chart(fig_timeline)

    # Detailed employee table
    st.subheader("Employee Details")
    st.dataframe(
        df_filtered[["EMPID", "First Name", "Last Name", "Job Title", "Salary", "StartDate"]],
        hide_index=True
    )

if __name__ == "__main__":
    st.set_page_config(
        page_title="HR Analytics Dashboard",
        page_icon="👥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    main()
