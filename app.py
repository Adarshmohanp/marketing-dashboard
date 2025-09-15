# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Marketing Intelligence Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load dataa
@st.cache_data
def load_data():
    # Load marketing data
    fb = pd.read_csv('Facebook.csv')
    google = pd.read_csv('Google.csv')
    tiktok = pd.read_csv('TikTok.csv')
    
    # Add a 'channel' column to each dataframee
    fb['channel'] = 'Facebook'
    google['channel'] = 'Google'
    tiktok['channel'] = 'TikTok'
    
    # Combine marketing data
    marketing_df = pd.concat([fb, google, tiktok], ignore_index=True)
    
    # Load business data
    business_df = pd.read_csv('Business.csv')
    
    # Convert date columns to datetime
    marketing_df['date'] = pd.to_datetime(marketing_df['date'])
    business_df['date'] = pd.to_datetime(business_df['date'])
    
    # Merge marketing and business data
    merged_df = pd.merge(marketing_df, business_df, on='date', how='left')
    
    # Calculate derived metrics
    merged_df['CTR'] = (merged_df['clicks'] / merged_df['impression'].replace(0, 1)) * 100
    merged_df['CPC'] = merged_df['spend'] / merged_df['clicks'].replace(0, 1)
    merged_df['CPA'] = merged_df['spend'] / merged_df['# of new orders'].replace(0, 1)
    merged_df['ROAS'] = merged_df['attributed revenue'] / merged_df['spend'].replace(0, 1)
    
    # Replace infinities and NaN with 0
    merged_df.replace([float('inf'), -float('inf')], 0, inplace=True)
    merged_df.fillna(0, inplace=True)
    
    return merged_df

# Load the data
df = load_data()

# Sidebar filters
st.sidebar.header('Filters')
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(df['date'].min(), df['date'].max()),
    min_value=df['date'].min(),
    max_value=df['date'].max()
)

channels = st.sidebar.multiselect(
    'Select Channels',
    options=df['channel'].unique(),
    default=df['channel'].unique()
)

tactics = st.sidebar.multiselect(
    'Select Tactics',
    options=df['tactic'].unique(),
    default=df['tactic'].unique()
)

states = st.sidebar.multiselect(
    'Select States',
    options=df['state'].unique(),
    default=df['state'].unique()
)

# Convert date_range to datetime
start_date = pd.to_datetime(date_range[0])
end_date = pd.to_datetime(date_range[1])

# Filter data based on selections
filtered_df = df[
    (df['date'] >= start_date) & 
    (df['date'] <= end_date) &
    (df['channel'].isin(channels)) &
    (df['tactic'].isin(tactics)) &
    (df['state'].isin(states))
]

# Dashboard title
st.title("📈 Marketing Intelligence Dashboard")
st.markdown("## Connecting Marketing Activity to Business Outcomes")

# KPI Metrics
st.header("Key Performance Indicators (KPIs)")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_revenue = filtered_df['attributed revenue'].sum()
    st.metric("Total Revenue", f"${total_revenue:,.0f}")

with col2:
    total_spend = filtered_df['spend'].sum()
    st.metric("Total Spend", f"${total_spend:,.0f}")

with col3:
    overall_roas = total_revenue / total_spend if total_spend > 0 else 0
    st.metric("Overall ROAS", f"{overall_roas:.2f}")

with col4:
    total_orders = filtered_df['# of new orders'].sum()
    st.metric("Total Orders", f"{total_orders:,.0f}")

# Time Series Charts
st.header("Performance Over Time")

tab1, tab2, tab3, tab4 = st.tabs(["Spend & Revenue", "Impressions & Clicks", "ROAS & CTR", "Orders & Customers"])

with tab1:
    daily_spend_rev = filtered_df.groupby('date').agg({'spend': 'sum', 'attributed revenue': 'sum'}).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily_spend_rev['date'], y=daily_spend_rev['spend'], name="Spend", line=dict(color='red')))
    fig.add_trace(go.Scatter(x=daily_spend_rev['date'], y=daily_spend_rev['attributed revenue'], name="Revenue", line=dict(color='green')))
    fig.update_layout(title="Daily Spend vs Revenue", xaxis_title="Date", yaxis_title="Amount ($)")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    daily_imp_clicks = filtered_df.groupby('date').agg({'impression': 'sum', 'clicks': 'sum'}).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily_imp_clicks['date'], y=daily_imp_clicks['impression'], name="Impressions", line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=daily_imp_clicks['date'], y=daily_imp_clicks['clicks'], name="Clicks", line=dict(color='orange')))
    fig.update_layout(title="Daily Impressions vs Clicks", xaxis_title="Date", yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    daily_roas_ctr = filtered_df.groupby('date').agg({'ROAS': 'mean', 'CTR': 'mean'}).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily_roas_ctr['date'], y=daily_roas_ctr['ROAS'], name="ROAS", line=dict(color='purple')))
    fig.add_trace(go.Scatter(x=daily_roas_ctr['date'], y=daily_roas_ctr['CTR'], name="CTR (%)", line=dict(color='brown')))
    fig.update_layout(title="Daily ROAS & CTR", xaxis_title="Date", yaxis_title="Value")
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    daily_orders_customers = filtered_df.groupby('date').agg({'# of new orders': 'sum', 'new customers': 'sum'}).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily_orders_customers['date'], y=daily_orders_customers['# of new orders'], name="Orders", line=dict(color='teal')))
    fig.add_trace(go.Scatter(x=daily_orders_customers['date'], y=daily_orders_customers['new customers'], name="New Customers", line=dict(color='magenta')))
    fig.update_layout(title="Daily Orders & New Customers", xaxis_title="Date", yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)

# Channel Performance
st.header("Channel Performance")

col1, col2 = st.columns(2)

with col1:
    channel_spend = filtered_df.groupby('channel').agg({'spend': 'sum'}).reset_index()
    fig = px.pie(channel_spend, values='spend', names='channel', title='Spend Distribution by Channel')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    channel_roas = filtered_df.groupby('channel').agg({'ROAS': 'mean'}).reset_index()
    fig = px.bar(channel_roas, x='channel', y='ROAS', title='Average ROAS by Channel', color='channel')
    st.plotly_chart(fig, use_container_width=True)

# Geographic Performance
st.header("Geographic Performance")
state_revenue = filtered_df.groupby('state').agg({'attributed revenue': 'sum'}).reset_index()
fig = px.choropleth(
    state_revenue,
    locations='state',
    locationmode='USA-states',
    color='attributed revenue',
    scope="usa",
    title="Revenue by State",
    color_continuous_scale="blues"
)
st.plotly_chart(fig, use_container_width=True)

# Campaign Performance
st.header("Top Campaigns by ROAS")
campaign_performance = filtered_df.groupby(['channel', 'campaign']).agg({
    'spend': 'sum',
    'attributed revenue': 'sum',
    'ROAS': 'mean'
}).reset_index()
campaign_performance = campaign_performance[campaign_performance['spend'] > 0]  # Filter out campaigns with no spend
campaign_performance = campaign_performance.sort_values('ROAS', ascending=False).head(10)

fig = px.bar(
    campaign_performance,
    x='campaign',
    y='ROAS',
    color='channel',
    title="Top 10 Campaigns by ROAS",
    labels={'ROAS': 'Return on Ad Spend', 'campaign': 'Campaign'}
)
st.plotly_chart(fig, use_container_width=True)

# Tactic Performance
st.header("Performance by Tactic")
tactic_performance = filtered_df.groupby('tactic').agg({
    'spend': 'sum',
    'attributed revenue': 'sum',
    'ROAS': 'mean'
}).reset_index()

col1, col2 = st.columns(2)

with col1:
    fig = px.bar(tactic_performance, x='tactic', y='spend', title='Spend by Tactic', color='tactic')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(tactic_performance, x='tactic', y='ROAS', title='ROAS by Tactic', color='tactic')
    st.plotly_chart(fig, use_container_width=True)

# Data Table
st.header("Detailed Data View")
st.dataframe(filtered_df.sort_values('date', ascending=False), use_container_width=True)

# Footer
st.markdown("---")
st.markdown("### 📊 Marketing Intelligence Dashboard | Built with Streamlit")
