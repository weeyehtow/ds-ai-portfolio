import streamlit as st
import pandas as pd
from datetime import timedelta, datetime

# Set page config
st.set_page_config(page_title="IHL Student Numbers", layout="wide")

st.title("Intake, Enrollment and Graduation Figures for Institutes of Higher Learning in Singapore")
st.write("Source: data.gov.sg")

# Helper functions
@st.cache_data
def load_data():
    data = pd.read_csv("/media/user/TRANSCEND/2_Projects/sgIHLstats/data/combined.csv")
    # BUG FIX 1: Use format='%Y' so integers like 2020 are parsed as years,
    # not as nanoseconds since epoch (which produced dates near 1970-01-01).
    data['year'] = pd.to_datetime(data['year'], format='%Y')
    return data

def format_with_commas(number):
    return f"{number:,}"

def create_metric_chart(df, column, color, chart_type, height=150, time_frame='year'):
    chart_data = df.groupby([df.index.year, 'course'])[column].first().unstack('course').diff()
    chart_data.index.name = 'year'
    if chart_type == 'Bar':
        st.bar_chart(chart_data, height=height)
    if chart_type == 'Area':
        st.area_chart(chart_data, height=height)
    if chart_type == 'Line':
        st.line_chart(chart_data, height=height)

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
            create_metric_chart(df, column, color, time_frame=time_frame, chart_type=chart_selection)

# Load data
df = load_data()

# Set up input widgets
#st.logo(image="images/5-red-book-png-image-image-thumb.png",
#        icon_image="images/5-red-book-png-image-image-thumb.png")

with st.sidebar:
    st.title("Filters")
    st.header("⚙️ Settings")

    # BUG FIX 3: Added chart_selection widget — it was referenced in display_metric but never defined.
    chart_selection = st.selectbox("Chart Type", ["Line", "Bar", "Area"], index=0)

    max_year = df['year'].max()
    default_start_year = max_year - pd.DateOffset(years=1)
    default_end_date = max_year


    IHLType_filter = st.multiselect("IHL Type", options=sorted(df['IHL_type'].dropna().unique()), default=None)
    course_filter = st.multiselect("Course", options=sorted(df['course'].dropna().unique()), default=None)
    sex_filter = st.multiselect("Sex", options=sorted(df['sex'].dropna().unique()), default=None)
    

    start_date = st.date_input(
        "Start year",
        default_start_year.date(),
        min_value=df['year'].min().date(),
        max_value=max_year.date(),
    )
    end_date = st.date_input(
        "End year",
        default_end_date.date(),
        min_value=df['year'].min().date(),
        max_value=max_year.date(),
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
if sex_filter:
    df_filtered = df_filtered[df_filtered['sex'].isin(sex_filter)]

# BUG FIX 4: Changed st.columns(4) to st.columns(3) to match the 3 metrics.
cols = st.columns(3)
for col, (title, column, color) in zip(cols, metrics):
    total_value = df_filtered[column].sum()
    # BUG FIX 2 (call site): Pass df_filtered and time_frame correctly.
    display_metric(col, title, total_value, df_filtered, column, color, time_frame='year')

# DataFrame display
with st.expander('See DataFrame (IHL and Course type details)'):
    st.dataframe(df_filtered)
