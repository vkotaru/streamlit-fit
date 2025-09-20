import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# ------------------------------------------------
# Data
# ------------------------------------------------

CSV_FILE_PATH = 'personal/fitness_data.csv'
# CSV_FILE_PATH = 'fitness_example_data.csv'

CARDIO_ACTIVITY_LIST = [
    "None", "🏃🏽‍♂️ Running", "🏃🏾 Trail Running", "🚵🏽‍♀️ Biking",
    "🏊🏽‍♂️ Swimming", "🥾 Hiking", "🚶🏽‍♂️ Walking", "🏕️ Backpacking"
]

STRENGTH_ACTIVITY_LIST = ["None", 'Full Body', 'Arms', 'Legs', 'Core', 'Back']

# ------------------------------------------------
# Helper functions
# ------------------------------------------------


def load_data():
    """Loads data from a CSV file or creates a new DataFrame if the file doesn't exist."""
    columns = [
        "Date", "Weight (kg)", "Waist (cm)", "Daily Calories (kCal)",
        "Carbs (g)", "Protein (g)", "Fat (g)", "Cardio Activity",
        "Cardio Duration (min)", "Cardio Calories (kCal)", "Strength Activity",
        "Strength Duration (min)"
    ]
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        # Ensure all columns are present
        for col in columns:
            if col not in df.columns:
                df[col] = None
        df = df[columns]
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        df = df.sort_values(by='Date').reset_index(drop=True)
    except FileNotFoundError:
        print("CSV file not found. Creating a new DataFrame.")
        df = pd.DataFrame(columns=columns)
    return df


def save_data(df):
    """Saves the DataFrame to a CSV file."""
    df.to_csv(CSV_FILE_PATH, index=False)
    st.success("Data saved successfully!")


def get_value(entry_data, column, default_value=None):
    if not entry_data.empty:
        val = entry_data[column].iloc[0]
        if pd.notna(val):
            if isinstance(default_value, int):
                return int(val)
            if isinstance(default_value, float):
                return float(val)
            return val
    return default_value


# ------------------------------------------------
# Page starts here
# ------------------------------------------------

st.set_page_config(
    page_title="Fitness dashboard",
    page_icon=":running_man:",
    layout="wide",
)
"""
# :material/monitor_weight: Fitness Tracker

Easily visualize your daily fitness stats.
"""
""  # Add some space.

# ------------------------------------------------
# Load data at the start of the app
data = load_data()
# ------------------------------------------------

top_row = st.columns([1, 3])

input_form_cell = top_row[0].container(border=True, height='stretch')

overivew_container = top_row[1].container(border=True, height='stretch')

with input_form_cell:
    st.subheader("Add/Edit Entry")
    date_to_edit = st.date_input("Date", datetime.now().date())

    entry_data = data[data['Date'] == date_to_edit]

    with st.form(key='entry_form'):
        weight_tab, calorie_tab, cardio_tab, strength_tab = st.tabs(
            ["Weight", "Calories", "Cardio", "Strength"])
        with weight_tab:
            weight = st.number_input("Weight (kg)",
                                     value=get_value(entry_data, 'Weight (kg)',
                                                     0.0))
            waist = st.number_input("Waist (cm)",
                                    value=get_value(entry_data, 'Waist (cm)',
                                                    0.0))
        with calorie_tab:
            daily_calories = st.number_input("Daily Calories (kCal)",
                                             value=get_value(
                                                 entry_data,
                                                 'Daily Calories (kCal)', 0))
            carbs = st.number_input("Carbs (g)",
                                    value=get_value(entry_data, 'Carbs (g)',
                                                    0))
            protein = st.number_input("Protein (g)",
                                      value=get_value(entry_data,
                                                      'Protein (g)', 0))
            fat = st.number_input("Fat (g)",
                                  value=get_value(entry_data, 'Fat (g)', 0))

        with cardio_tab:
            cardio_activity_val = get_value(entry_data, 'Cardio Activity',
                                            None)
            cardio_activity_index = CARDIO_ACTIVITY_LIST.index(
                cardio_activity_val
            ) if cardio_activity_val in CARDIO_ACTIVITY_LIST else None
            cardio_activity = st.selectbox(
                "Cardio Activity",
                CARDIO_ACTIVITY_LIST,
                index=cardio_activity_index,
                placeholder="Select cardio activity...")

            cardio_duration = st.number_input("Cardio Duration (min)",
                                              value=get_value(
                                                  entry_data,
                                                  'Cardio Duration (min)', 0))
            cardio_calories = st.number_input("Cardio Calories (kCal)",
                                              value=get_value(
                                                  entry_data,
                                                  'Cardio Calories (kCal)', 0))
        with strength_tab:
            strength_activity_val = get_value(entry_data, 'Strength Activity',
                                              None)
            strength_activity_index = STRENGTH_ACTIVITY_LIST.index(
                strength_activity_val
            ) if strength_activity_val in STRENGTH_ACTIVITY_LIST else None
            strength_activity = st.selectbox(
                "Strength Activity",
                STRENGTH_ACTIVITY_LIST,
                index=strength_activity_index,
                placeholder="Select strength activity...")

            strength_duration = st.number_input(
                "Strength Duration (min)",
                value=get_value(entry_data, 'Strength Duration (min)', 0))

        submitted = st.form_submit_button("Save")
        if submitted:
            new_row = {
                "Date": date_to_edit,
                "Weight (kg)": weight,
                "Waist (cm)": waist,
                "Daily Calories (kCal)": daily_calories,
                "Carbs (g)": carbs,
                "Protein (g)": protein,
                "Fat (g)": fat,
                "Cardio Activity": cardio_activity,
                "Cardio Duration (min)": cardio_duration,
                "Cardio Calories (kCal)": cardio_calories,
                "Strength Activity": strength_activity,
                "Strength Duration (min)": strength_duration
            }
            if not entry_data.empty:
                data.loc[data['Date'] == date_to_edit] = list(new_row.values())
            else:
                new_df = pd.DataFrame([new_row])
                data = pd.concat([data, new_df], ignore_index=True)

            data['Date'] = pd.to_datetime(data['Date']).dt.strftime('%m/%d/%Y')
            save_data(data)
            st.rerun()

with overivew_container:
    today = pd.to_datetime(datetime.now().date())
    data['Date'] = pd.to_datetime(data['Date'])

    if not data.empty:
        net_weight_cell, avg_cals_cell, col3, col4 = st.columns(4)
        with net_weight_cell:
            # Get latest weight and previous weight
            latest_weight = data['Weight (kg)'].iloc[-1]
            previous_weight = data['Weight (kg)'].iloc[-2] if len(
                data) > 1 else 0
            delta = round(latest_weight - previous_weight, 2)
            st.metric("Latest Weight",
                      f"{latest_weight} kg",
                      delta=f"{delta} kg",
                      delta_color="inverse")
        with avg_cals_cell:
            # Calculate this week's average calorie intake
            start_of_week = today - pd.Timedelta(days=6)
            weekly_calories_data = data[(data['Date'] >= start_of_week)
                                        & (data['Date'] <= today)]

            # Ensure 'Daily Calories (kCal)' is numeric and handle potential non-numeric values
            weekly_calories_data['Daily Calories (kCal)'] = pd.to_numeric(
                weekly_calories_data['Daily Calories (kCal)'], errors='coerce')

            average_weekly_calories = weekly_calories_data[
                'Daily Calories (kCal)'].mean()
            DAILY_NET_INTAKE = 2000

            if pd.notna(average_weekly_calories):
                st.metric(
                    "Avg Weekly Calories",
                    f"{average_weekly_calories:.0f} kCal",
                    delta=
                    f"{average_weekly_calories - DAILY_NET_INTAKE:.0f} kCal",
                    delta_color="inverse")
            else:
                st.metric("Avg Weekly Calories", "N/A")

        # Time horizon selector
        horizon_options = [
            "1 Week", "2 Weeks", "1 Month", "3 Months", "6 Months", "1 Year",
            "5 Years", "All Time"
        ]
        horizon = st.pills("Time horizon",
                           options=horizon_options,
                           default="3 Months")

        if horizon == "1 Week":
            start_date = today - pd.Timedelta(days=7)
        elif horizon == "2 Weeks":
            start_date = today - pd.Timedelta(days=14)
        elif horizon == "1 Month":
            start_date = today - pd.Timedelta(days=31)
        elif horizon == "3 Months":
            start_date = today - pd.Timedelta(days=90)
        elif horizon == "6 Months":
            start_date = today - pd.Timedelta(days=180)
        elif horizon == "1 Year":
            start_date = today - pd.Timedelta(days=365)
        elif horizon == "5 Years":
            start_date = today - pd.Timedelta(days=5 * 365)
        else:  # All Time
            start_date = data['Date'].min()

        filtered_data = data[(data['Date'] >= start_date)
                             & (data['Date'] <= today)]

        weight_chart = alt.Chart(filtered_data).mark_line(
            interpolate='basis').encode(
                alt.X("Date:T", axis=alt.Axis(title='Date',
                                              format='%Y-%m-%d')),
                alt.Y("Weight (kg):Q").scale(zero=False),
            ).properties(height=300, title="Weight Trend")

        # Add moving average
        show_ma = st.toggle("Show Moving Average", value=True)
        if show_ma:
            ma_window = st.slider("Moving Average Window", 1, 30, 7)
            filtered_data['MA'] = filtered_data['Weight (kg)'].rolling(
                ma_window).mean()
            ma_chart = alt.Chart(filtered_data).mark_line(
                color='red',
                interpolate='basis').encode(alt.X("Date:T"), alt.Y("MA:Q"))
            st.altair_chart(weight_chart + ma_chart)
        else:
            st.altair_chart(weight_chart)

# ---------------------
# Display the raw table.
# ---------------------
"""
## Raw data
"""

config = {
    'Date':
    st.column_config.DateColumn('Date'),
    "Cardio Activity":
    st.column_config.SelectboxColumn("Cardio Activity",
                                     help="Cardio activity",
                                     options=CARDIO_ACTIVITY_LIST),
    "Strength Activity":
    st.column_config.SelectboxColumn("Strength Activity",
                                     help="Strength activity",
                                     options=STRENGTH_ACTIVITY_LIST)
}

if st.toggle("Enable editing"):
    edited_data = st.data_editor(data.sort_values(by='Date', ascending=False),
                                 column_config=config,
                                 use_container_width=True,
                                 hide_index=True)
    if st.button("Save"):
        save_data(edited_data)
        st.rerun()
else:
    st.dataframe(
        data.sort_values(by='Date', ascending=False),
        column_config=config,
        use_container_width=True,
        hide_index=True,
    )
