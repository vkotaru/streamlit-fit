# pages/1_📊_Dashboard.py

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Dashboard & Stats")

# --- Load data from session state ---
if 'fitness_data' not in st.session_state or st.session_state[
        'fitness_data'].empty:
    st.warning(
        "No data found. Please go to the 'Data Entry' page to add or load data."
    )
    st.stop()

data = st.session_state['fitness_data']
today = pd.to_datetime(datetime.now().date())

# --- METRICS ---
st.header("Key Metrics")
col1, col2, col3 = st.columns(3)
with col1:
    latest_weight = data['Weight (kg)'].iloc[-1]
    previous_weight = data['Weight (kg)'].iloc[-2] if len(data) > 1 else 0
    delta = round(latest_weight -
                  previous_weight, 2) if previous_weight > 0 else 0
    st.metric("Latest Weight",
              f"{latest_weight} kg",
              delta=f"{delta} kg",
              delta_color="inverse")

with col2:
    start_of_week = today - pd.Timedelta(days=today.weekday())
    weekly_data = data[(data['Date'] >= start_of_week)
                       & (data['Date'] <= today)]
    avg_calories = pd.to_numeric(weekly_data['Daily Calories (kCal)'],
                                 errors='coerce').mean()
    if pd.notna(avg_calories):
        st.metric("Avg Calories (This Week)", f"{avg_calories:.0f} kCal")
    else:
        st.metric("Avg Calories (This Week)", "N/A")

with col3:
    total_cardio_time = pd.to_numeric(data['Cardio Duration (min)'],
                                      errors='coerce').sum()
    st.metric("Total Cardio Time", f"{total_cardio_time / 60:.1f} hours")

st.divider()

# --- WEIGHT TREND PLOT ---
st.header("📈 Weight Trend")
weight_chart = alt.Chart(data).mark_line(
    point=True, interpolate='basis').encode(
        alt.X("Date:T", axis=alt.Axis(title='Date', format='%b %d, %Y')),
        alt.Y("Weight (kg):Q",
              scale=alt.Scale(zero=False),
              title="Weight (kg)"),
        tooltip=['Date', 'Weight (kg)']).properties(height=400).interactive()

ma_line = weight_chart.transform_window(
    rolling_mean='mean(Weight (kg))',
    frame=[-7, 0]  # 7-day rolling average
).mark_line(color='red', strokeDash=[5, 5]).encode(y='rolling_mean:Q')
st.altair_chart(weight_chart + ma_line, use_container_width=True)

st.divider()

# --- NEW PLOTS: MACROS AND ACTIVITY ---
st.header("🥗 Macros & 🏃‍♀️ Activity Analysis")
plot_col1, plot_col2 = st.columns(2)

with plot_col1:
    st.subheader("Average Macronutrient Distribution")
    macro_data = data[['Carbs (g)', 'Protein (g)',
                       'Fat (g)']].mean().reset_index()
    macro_data.columns = ['Macro', 'Average Grams']

    macro_chart = alt.Chart(macro_data).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field="Average Grams", type="quantitative"),
        color=alt.Color(field="Macro", type="nominal", title="Macronutrient"),
        tooltip=['Macro', 'Average Grams']).properties(height=350)
    st.altair_chart(macro_chart, use_container_width=True)

with plot_col2:
    st.subheader("Cardio Activity Frequency")
    cardio_counts = data[data['Cardio Activity'] != 'None'][
        'Cardio Activity'].value_counts().reset_index()
    cardio_counts.columns = ['Activity', 'Count']

    activity_chart = alt.Chart(cardio_counts).mark_bar().encode(
        x=alt.X('Count:Q'),
        y=alt.Y('Activity:N', sort='-x', title=""),
        tooltip=['Activity', 'Count']).properties(height=350)
    st.altair_chart(activity_chart, use_container_width=True)
