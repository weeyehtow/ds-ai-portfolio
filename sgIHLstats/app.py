import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta, datetime

# Set page config
st.set_page_config(page_title="IHL Student Numbers", layout="wide")

st.title("Intake, Enrollment and Graduation Figures for Institutes of Higher Learning in Singapore")
st.write("Source: data.gov.sg")

# Helper functions
@st.cache_data
def load_data():
    url= "https://raw.githubusercontent.com/weeyehtow/ds-ai-portfolio/refs/heads/main/sgIHLstats/data/combined.csv"
    data = pd.read_csv(url)

def format_with_commas(number):
    return f"{number:,}"

def calculate_delta(df, column):
    if len(df) < 2:
        return 0, 0
    current_value = df[column].iloc[-1]
    previous_value = df[column].iloc[-2]
    delta = current_value - previous_value
    delta_percent = (delta / previous_value) * 100 if previous_value != 0 else 0
    return delta, delta_percent

# BUG FIX 2: Added missing `df` and `time_frame` parameters to match the call signature.
def display_metric(col, title, value, df, column, color, time_frame):
    with col:
        with st.container(border=True):
            delta, delta_percent = calculate_delta(df, column)
            delta_str = f"{delta:+,.0f} ({delta_percent:+.2f}%)"
            st.metric(title, format_with_commas(value), delta=delta_str)

# Load data
df = load_data()

# Set up input widgets
#st.logo(image="images/5-red-book-png-image-image-thumb.png",
#        icon_image="images/5-red-book-png-image-image-thumb.png")

with st.sidebar:
    st.title("Filters")
    st.header("⚙️ Settings")

    max_year = df['year'].max()
    default_start_year = max_year - pd.DateOffset(years=5)
    default_end_year = max_year

    IHLType_filter = st.multiselect("IHL Type", options=sorted(df['IHL_type'].dropna().unique()), default=None)
    course_filter = st.multiselect("Course", options=sorted(df['course'].dropna().unique()), default=None)
    gender_filter = st.multiselect("gender", options=sorted(df['gender'].dropna().unique()), default=None)
    
    start_date = st.date_input(
        "Start year",
        default_start_year,
        min_value=df['year'].min(),
        max_value=max_year,
    )
    end_date = st.date_input(
        "End year",
        default_end_year,
        min_value=df['year'].min(),
        max_value=max_year,
    )

# Display Key Metrics
st.subheader("Statistics")

metrics = [
    ("Total Intake", "intake", '#29b5e8'),
    ("Total Enrolled", "enrolment", '#FF9F36'),
    ("Total Graduated", "graduates", '#D45B90'),
]

df_display = df.set_index('year')

mask = (df_display.index >= pd.Timestamp(start_date)) & (df_display.index <= pd.Timestamp(end_date))
df_filtered = df_display.loc[mask]
if course_filter:
    df_filtered = df_filtered[df_filtered['course'].isin(course_filter)]
if gender_filter:
    df_filtered = df_filtered[df_filtered['gender'].isin(gender_filter)]

st.subheader("Stats by year")
trend = (
    df_filtered.groupby("year", as_index=False)[["enrolment"]]
    .sum()
    .sort_values("year")
)
# Create a Plotly line chart with month on x-axis and intake, enrolment and graduates numbers on y-axis
fig_trend = px.line(df, x="year", y=["intake", "enrolment", "graduates"], markers=True)
# Display the Plotly chart in Streamlit
st.plotly_chart(fig_trend, width=False)

# DataFrame display
with st.expander('See DataFrame (IHL and Course type details)'):
    st.dataframe(df_filtered)
