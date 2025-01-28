import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import os

# Configure the page
st.set_page_config(
    page_title="HR Analytics Dashboard",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cache the data loading function
@st.cache_data
def load_data():
    try:
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct path to data file
        data_path = os.path.join(script_dir, 'data', 'BusEmployeesInfo.xlsx')
        
        # Read the Excel file
        df = pd.read_excel(data_path)
        
        # Convert StartDate to datetime if not already
        df['StartDate'] = pd.to_datetime(df['StartDate'])
        
        # Calculate tenure
        df['Tenure'] = (datetime.now() - df['StartDate']).dt.days / 365
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def format_large_number(num):
    """Format large numbers with K/M suffix"""
    if num >= 1000000:
        return f"${num/1000000:.1f}M"
    elif num >= 1000:
        return f"${num/1000:.1f}K"
    else:
        return f"${num:.0f}"

def main():
    # Set up the dashboard header
    st.markdown("# **HR Analytics Dashboard**")
    
    # Load data
    df = load_data()
    
    if df is None:
        st.error("Unable to load data. Please check if the data file exists in the 'data' folder.")
        return
    
    # Sidebar filters
    with st.sidebar:
        st.header("Filters")
        
        # Job Title filter
        job_titles = ["All"] + sorted(df["Job Title"].unique().tolist())
        selected_title = st.selectbox("Select Job Title", job_titles)
        
        # ZIP Code filter
        zip_codes = ["All"] + sorted(df["Zip"].unique().astype(str).tolist())
        selected_zip = st.selectbox("Select ZIP Code", zip_codes)
        
        # Date range filter
        date_range = st.date_input(
            "Select Date Range",
            value=(df['StartDate'].min(), df['StartDate'].max()),
            min_value=df['StartDate'].min().date(),
            max_value=df['StartDate'].max().date()
        )
    
    # Apply filters
    mask = pd.Series(True, index=df.index)
    
    if selected_title != "All":
        mask &= df["Job Title"] == selected_title
    
    if selected_zip != "All":
        mask &= df["Zip"].astype(str) == selected_zip
    
    if len(date_range) == 2:
        mask &= (df['StartDate'].dt.date >= date_range[0]) & (df['StartDate'].dt.date <= date_range[1])
    
    df_filtered = df[mask]
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Employees", f"{len(df_filtered):,}")
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
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Salary distribution plot
            fig_salary = px.histogram(
                df_filtered,
                x="Salary",
                nbins=20,
                title="Salary Distribution"
            )
            fig_salary.update_layout(showlegend=False)
            st.plotly_chart(fig_salary, use_container_width=True)
        
        with col2:
            # Salary by Job Title
            fig_salary_job = px.box(
                df_filtered,
                x="Job Title",
                y="Salary",
                title="Salary Range by Job Title"
            )
            fig_salary_job.update_xaxes(tickangle=45)
            st.plotly_chart(fig_salary_job, use_container_width=True)

    with tab2:
        st.subheader("Team Composition")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Job Title distribution
            job_dist = df_filtered["Job Title"].value_counts()
            fig_jobs = px.pie(
                values=job_dist.values,
                names=job_dist.index,
                title="Employee Distribution by Job Title"
            )
            st.plotly_chart(fig_jobs, use_container_width=True)
        
        with col2:
            # Geographic distribution
            zip_dist = df_filtered["Zip"].value_counts()
            fig_zip = px.bar(
                x=zip_dist.index,
                y=zip_dist.values,
                title="Employee Distribution by ZIP Code",
                labels={'x': 'ZIP Code', 'y': 'Number of Employees'}
            )
            st.plotly_chart(fig_zip, use_container_width=True)

    with tab3:
        st.subheader("Tenure Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Tenure distribution
            fig_tenure = px.histogram(
                df_filtered,
                x="Tenure",
                nbins=20,
                title="Employee Tenure Distribution (Years)"
            )
            fig_tenure.update_layout(showlegend=False)
            st.plotly_chart(fig_tenure, use_container_width=True)
        
        with col2:
            # Hiring timeline
            fig_timeline = px.scatter(
                df_filtered,
                x="StartDate",
                y="Job Title",
                title="Employee Start Dates by Job Title"
            )
            st.plotly_chart(fig_timeline, use_container_width=True)

    # Detailed employee table
    st.subheader("Employee Details")
    
    # Format the table data
    display_df = df_filtered[["EMPID", "First Name", "Last Name", "Job Title", "Salary", "StartDate"]].copy()
    display_df["Salary"] = display_df["Salary"].apply(lambda x: f"${x:,.0f}")
    display_df["StartDate"] = display_df["StartDate"].dt.strftime('%Y-%m-%d')
    
    st.dataframe(
        display_df.sort_values("Last Name"),
        hide_index=True,
        use_container_width=True
    )

if __name__ == "__main__":
    main()
