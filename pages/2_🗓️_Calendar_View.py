# pages/2_🗓️_Calendar_View.py

import streamlit as st
import pandas as pd
from datetime import datetime
import calendar

# --- PAGE CONFIG ---
st.set_page_config(page_title="Calendar View", page_icon="🗓️", layout="wide")

# --- DATA LOADING ---
# Safely get the data from session state
if 'fitness_data' not in st.session_state or st.session_state[
        'fitness_data'].empty:
    st.warning("No data found. Please go to the main page to add an entry.",
               icon="✍️")
    st.stop()

data = st.session_state['fitness_data'].copy()

data['Date'] = pd.to_datetime(data['Date']).dt.date

# --- STATE MANAGEMENT FOR CALENDAR MONTH/YEAR ---
# Initialize session state for the current year and month if not already present
today = datetime.now()
if 'calendar_year' not in st.session_state:
    st.session_state.calendar_year = today.year
if 'calendar_month' not in st.session_state:
    st.session_state.calendar_month = today.month

# --- EMOJI MAPPING FOR ACTIVITIES ---
STRENGTH_EMOJI_MAP = {
    'Full Body': '💪',
    'Arms': '🦾',
    'Legs': '🦵',
    'Core': '🔥',
    'Back': '🏋️‍♂️'
}

# Pre-process data into a lookup dictionary for quick access
# Key: datetime.date, Value: HTML string of emojis
events = {}
for _, row in data.iterrows():
    emojis = ""
    # Get cardio emoji (first character of the string)
    if isinstance(row['Cardio Activity'], str) and row['Cardio Activity'] != "None":
        emojis += f"<span title='{row['Cardio Activity']}'>{row['Cardio Activity'][0]}</span> "
    # Get strength emoji from map
    if isinstance(row['Strength Activity'], str) and row['Strength Activity'] != "None":
        emoji = STRENGTH_EMOJI_MAP.get(row['Strength Activity'], '🏋️')
        emojis += f"<span title='{row['Strength Activity']}'>{emoji}</span>"

    if emojis:
        events[row['Date']] = emojis.strip()


# --- CUSTOM HTML CALENDAR CLASS ---
class ActivityCalendar(calendar.HTMLCalendar):

    def __init__(self, events):
        super().__init__()
        self.events = events

    def formatday(self, day, weekday):
        """
        Return a day as a table cell.
        """
        if day == 0:
            # day outside month
            return '<td class="noday">&nbsp;</td>'
        else:
            current_date = datetime(st.session_state.calendar_year,
                                    st.session_state.calendar_month,
                                    day).date()
            event_html = self.events.get(current_date, "")
            if event_html:
                return f'<td class="{self.cssclasses[weekday]}">{day}<br><div class="activity-emoji">{event_html}</div></td>'
            else:
                return f'<td class="{self.cssclasses[weekday]}">{day}</td>'


# --- RENDER THE PAGE ---
# Header with navigation
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("⬅️ Previous Month"):
        if st.session_state.calendar_month == 1:
            st.session_state.calendar_month = 12
            st.session_state.calendar_year -= 1
        else:
            st.session_state.calendar_month -= 1
        st.rerun()

with col3:
    if st.button("Next Month ➡️"):
        if st.session_state.calendar_month == 12:
            st.session_state.calendar_month = 1
            st.session_state.calendar_year += 1
        else:
            st.session_state.calendar_month += 1
        st.rerun()

with col2:
    month_name = calendar.month_name[st.session_state.calendar_month]
    st.header(f"{month_name} {st.session_state.calendar_year}",
              anchor=False,
              divider="gray")

# --- DISPLAY CALENDAR ---
# Custom CSS for the calendar
st.markdown("""
    <style>
    .calendar-container table {
        border-collapse: collapse;
        width: 100%;
        font-size: 1.1em;
    }
    .calendar-container th {
        text-align: center;
        padding: 15px;
        background-color: #262730; /* Dark mode background */
        color: #FAFAFA; /* Light text */
    }
    .calendar-container td {
        border: 1px solid #444;
        text-align: center;
        vertical-align: top;
        padding: 10px;
        height: 100px;
        width: 14%;
        color: #FAFAFA;
    }
    .activity-emoji {
        font-size: 1.5em;
        margin-top: 10px;
    }
    .noday {
        background-color: #1a1a2e; /* Darker for empty days */
    }
    </style>
""",
            unsafe_allow_html=True)

# Generate and display the calendar
custom_calendar = ActivityCalendar(events=events)
html_calendar = custom_calendar.formatmonth(st.session_state.calendar_year,
                                            st.session_state.calendar_month)

st.markdown(f"<div class='calendar-container'>{html_calendar}</div>",
            unsafe_allow_html=True)
