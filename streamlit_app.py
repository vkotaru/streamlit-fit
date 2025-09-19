import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# ------------------------------------------------
# Data
# ------------------------------------------------

CSV_FILE_PATH = 'fitness_data.csv'

CARDIO_ACTIVITY_LIST = [
    "🏃🏽‍♂️ Running", "🏃🏾 Trail Running", "🚵🏽‍♀️ Biking", "🏊🏽‍♂️ Swimming",
    "🥾 Hiking", "🚶🏽‍♂️ Walking", "🏕️ Backpacking"
]

STRENGTH_ACTIVITY_LIST = ['Full Body', 'Arms', 'Legs', 'Core', 'Back']

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
        df['Date'] = pd.to_datetime(df['Date']).dt.date
    except FileNotFoundError:
        print("CSV file not found. Creating a new DataFrame.")
        df = pd.DataFrame(columns=columns)
    return df


def save_data(df):
    """Saves the DataFrame to a CSV file."""
    df.to_csv(CSV_FILE_PATH, index=False)
    st.success("Data saved successfully!")


def get_value(entry_data, column, default_value):
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

top_left_cell = top_row[0].container(border=True, height='stretch')

top_right_cell = top_row[1].container(border=True, height=600)

with top_left_cell:
    st.subheader("Add/Edit Entry")
    date_to_edit = st.date_input("Date", datetime.now().date())

    entry_data = data[data['Date'] == date_to_edit]

    with st.form(key='entry_form'):
        weight = st.number_input("Weight (kg)",
                                 value=get_value(entry_data, 'Weight (kg)',
                                                 0.0))
        waist = st.number_input("Waist (cm)",
                                value=get_value(entry_data, 'Waist (cm)', 0.0))
        daily_calories = st.number_input("Daily Calories (kCal)",
                                         value=get_value(
                                             entry_data,
                                             'Daily Calories (kCal)', 0))
        carbs = st.number_input("Carbs (g)",
                                value=get_value(entry_data, 'Carbs (g)', 0))
        protein = st.number_input("Protein (g)",
                                  value=get_value(entry_data, 'Protein (g)',
                                                  0))
        fat = st.number_input("Fat (g)",
                              value=get_value(entry_data, 'Fat (g)', 0))

        cardio_activity_val = get_value(entry_data, 'Cardio Activity', None)
        cardio_activity_index = CARDIO_ACTIVITY_LIST.index(
            cardio_activity_val
        ) if cardio_activity_val in CARDIO_ACTIVITY_LIST else 0
        cardio_activity = st.selectbox("Cardio Activity",
                                       CARDIO_ACTIVITY_LIST,
                                       index=cardio_activity_index)

        cardio_duration = st.number_input("Cardio Duration (min)",
                                          value=get_value(
                                              entry_data,
                                              'Cardio Duration (min)', 0))
        cardio_calories = st.number_input("Cardio Calories (kCal)",
                                          value=get_value(
                                              entry_data,
                                              'Cardio Calories (kCal)', 0))

        strength_activity_val = get_value(entry_data, 'Strength Activity',
                                          None)
        strength_activity_index = STRENGTH_ACTIVITY_LIST.index(
            strength_activity_val
        ) if strength_activity_val in STRENGTH_ACTIVITY_LIST else 0
        strength_activity = st.selectbox("Strength Activity",
                                         STRENGTH_ACTIVITY_LIST,
                                         index=strength_activity_index)

        strength_duration = st.number_input("Strength Duration (min)",
                                            value=get_value(
                                                entry_data,
                                                'Strength Duration (min)', 0))

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

with top_right_cell:
    if not data.empty:
        # Get latest weight and previous weight
        latest_weight = data['Weight (kg)'].iloc[0]
        previous_weight = data['Weight (kg)'].iloc[1] if len(data) > 1 else 0
        delta = round(latest_weight - previous_weight, 2)
        st.metric("Latest Weight", f"{latest_weight} kg", delta=f"{delta} kg")

        data['Date'] = pd.to_datetime(data['Date'])

        # Add a slider to select the number of days to display
        days_to_show = st.slider('Select number of days to display', 1,
                                 len(data), len(data))

        # Filter the data based on the slider
        filtered_data = data.head(days_to_show)

        st.altair_chart(
            alt.Chart(filtered_data).mark_line().encode(
                alt.X("Date:T", axis=alt.Axis(title='Date',
                                              format='%Y-%m-%d')),
                alt.Y("Weight (kg):Q").scale(zero=False),
            ).properties(height=300, title="Weight Trend"))

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
    edited_data = st.data_editor(data,
                                 column_config=config,
                                 use_container_width=True)
    if st.button("Save"):
        save_data(edited_data)
        st.rerun()
else:
    st.dataframe(data, column_config=config, use_container_width=True)
