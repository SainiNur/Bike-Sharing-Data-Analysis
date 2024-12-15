import streamlit as st
import pandas as pd 
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="Rent Bikes Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load dataset
hour_df = pd.read_csv("C:\SANS\knowledge\DICODING\submission\dashboard\hour fixed.csv")
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

# Add sidebar
with st.sidebar:
    st.title("Rent Bikes Dashboard")
    
    # Year selection
    year_list = list(hour_df['dteday'].dt.year.unique())[::-1]
    selected_year = st.selectbox("Select a year", year_list, index=len(year_list)-1)
    
    # Filter DataFrame by selected year
    hour_df_selected_year = hour_df[hour_df['dteday'].dt.year == selected_year]
    
    # Month selection
    month_name = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }
    selected_months = st.multiselect("Select month", list(hour_df['mnth'].map(month_name).unique()))

    # Filter DataFrame based on selected month
    if selected_months:
        selected_month_numbers = [list(month_name.values()).index(month) + 1 for month in selected_months]
        hour_df_selected_year = hour_df_selected_year[hour_df_selected_year['mnth'].isin(selected_month_numbers)]

    day_cat= {1: 'Weekday', 0: 'Weekend'} #workingday category

# Create columns for charts
c1, c2, c3 = st.columns((3, 3, 4))
with c1:
    user_char = hour_df_selected_year.groupby('workingday', as_index=False).agg({
                'registered' : 'sum',
                'casual' : 'sum'
                })
    user_char['workingday'] = user_char['workingday'].map(day_cat)
    user_fig = make_subplots(rows=1, cols=2, shared_yaxes=True)
    user_fig.add_trace(
    go.Bar(x=user_char['workingday'], y=user_char['registered'], 
           name='Registered',
           marker_color='#f48c06'),1,1
    )
    user_fig.add_trace(
    go.Bar(x=user_char['workingday'], y=user_char['casual'], 
           name='Casual',
           marker_color='#9d0208'),1,2
    )
    user_fig.update_layout(title_text='User Counts by Working Day')
    st.plotly_chart(user_fig, use_container_width=True)

with c2:
    # Bar chart (sesaon)
    season_amount = hour_df_selected_year.groupby('season', as_index=False).agg({'cnt':'sum'})
    season_amount.columns = ['season','amount']

    season_fig = px.bar(season_amount, 
                 x="season", 
                 y="amount",
                 title="Number of rent by season")
    season_fig.update_traces(marker_color='#d00000')
    season_fig.update_layout(
    xaxis_title=None,
    yaxis_title=None,
    )
    st.plotly_chart(season_fig, use_container_width=True)

with c3:
    # Pie chart
    selected = hour_df_selected_year[['casual', 'registered']]
    df_melt = selected.melt(var_name='User  Type', value_name='Count')
    color_sequence = ['#ffba08', '#d00000']
    pie_fig = px.pie(df_melt, values='Count',
                     names='User  Type', 
                     color_discrete_sequence= color_sequence,
                     title='Distribution of Casual and Registered Users')
    st.plotly_chart(pie_fig, use_container_width=True)

# Bar chart
hourly_traffic = hour_df_selected_year[['hr','cnt','workingday']]
hourly_traffic.columns = ['hour','count','workingday']
hourly_traffic['workingday'] = hourly_traffic['workingday'].map(day_cat)

fig = px.histogram(hourly_traffic, 
            x='hour', 
            y='count', 
            color='workingday',
            color_discrete_sequence=['#faa307', '#9d0208'], 
            title='Hourly Traffic Count')
fig.update_xaxes(tickvals=list(range(0, 25, 2)))
fig.update_layout(
xaxis_title="Hour",
yaxis_title=None,
)
st.plotly_chart(fig, use_container_width=True)

# Line chart
monthly_counts = hour_df_selected_year.groupby(hour_df_selected_year['dteday'].dt.month)['cnt'].sum().reset_index()
monthly_counts.columns = ['month', 'total_count']
monthly_counts['month'] = monthly_counts['month'].astype(object)
line = px.line(data_frame=monthly_counts,
                  x='month', y='total_count',
                  title='Renter Trend Line')
line.update_traces(line_color='#f48c06')
line.update_layout(
  xaxis_title=None,
  yaxis_title=None,
)
st.plotly_chart(line, use_container_width=True)

