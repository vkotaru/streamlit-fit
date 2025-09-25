import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime


class FitnessTrackerApp:
    """
    A class-based Streamlit application for tracking fitness data.
    It encapsulates data loading, saving, and UI rendering logic.
    """

    # --- Configuration constants ---
    CARDIO_ACTIVITY_LIST = [
        "None", "🏃🏽‍♂️ Running", "🏃🏾 Trail Running", "🚵🏽‍♀️ Biking",
        "🏊🏽‍♂️ Swimming", "🥾 Hiking", "🚶🏽‍♂️ Walking", "🏕️ Backpacking"
    ]
    STRENGTH_ACTIVITY_LIST = [
        "None", 'Full Body', 'Arms', 'Legs', 'Core', 'Back'
    ]
    # NOTE: The duration columns will store total SECONDS.
    COLUMNS = [
        "Date", "Weight (kg)", "Waist (cm)", "Daily Calories (kCal)",
        "Carbs (g)", "Protein (g)", "Fat (g)", "Cardio Activity",
        "Cardio Duration (s)", "Cardio Calories (kCal)", "Strength Activity",
        "Strength Duration (s)"
    ]

    def __init__(self, csv_file_path: str):
        """
        Initializes the FitnessTrackerApp.
        Args:
            csv_file_path (str): The path to the CSV file for storing data.
        """
        self.csv_file_path = csv_file_path
        if 'fitness_data' not in st.session_state:
            st.session_state['fitness_data'] = self._load_data()

    def _load_data(self) -> pd.DataFrame:
        """Loads data from the CSV file or creates a new DataFrame."""
        try:
            df = pd.read_csv(self.csv_file_path)
            for col in self.COLUMNS:
                if col not in df.columns:
                    df[col] = None
            df = df[self.COLUMNS]
            df['Date'] = pd.to_datetime(df['Date'])
        except FileNotFoundError:
            print("CSV file not found. Creating a new DataFrame.")
            df = pd.DataFrame(columns=self.COLUMNS)
            df['Date'] = pd.to_datetime(df['Date'])

        return df.sort_values(by='Date').reset_index(drop=True)

    def _save_data(self):
        """Saves the current DataFrame to the CSV file."""
        save_df = st.session_state['fitness_data'].copy()
        save_df['Date'] = pd.to_datetime(
            save_df['Date']).dt.strftime('%m/%d/%Y')
        save_df.to_csv(self.csv_file_path, index=False)
        st.success("Data saved successfully!")

    def _get_value(self,
                   entry_data: pd.DataFrame,
                   column: str,
                   default_value=None) -> any:
        """Safely retrieves a value from the entry_data DataFrame."""
        if not entry_data.empty:
            val = entry_data[column].iloc[0]
            if pd.notna(val):
                if isinstance(default_value, int):
                    return int(val)
                if isinstance(default_value, float):
                    return float(val)
                return val
        return default_value

    def _seconds_to_hms(self, seconds_val) -> tuple[int, int, int]:
        """Converts seconds into a tuple of (hours, minutes, seconds)."""
        if not seconds_val or pd.isna(seconds_val):
            return 0, 0, 0
        seconds_val = int(seconds_val)
        hours = seconds_val // 3600
        minutes = (seconds_val % 3600) // 60
        secs = seconds_val % 60
        return hours, minutes, secs

    def _display_input_form(self):
        """Renders the input form for adding or editing an entry."""
        st.subheader("Add/Edit Entry")
        date_to_edit_input = st.date_input("Date", datetime.now().date())

        # --- STATE MANAGEMENT LOGIC ---
        # This block now only runs ONCE when the selected date changes.
        if 'form_date' not in st.session_state or st.session_state.form_date != date_to_edit_input:
            st.session_state.form_date = date_to_edit_input
            date_to_edit = pd.to_datetime(date_to_edit_input)
            data = st.session_state['fitness_data']
            entry_data = data[data['Date'] == date_to_edit]

            # Load ALL form values into session state from the DataFrame
            st.session_state.weight_kg = self._get_value(
                entry_data, 'Weight (kg)', None)
            st.session_state.waist_cm = self._get_value(
                entry_data, 'Waist (cm)', None)
            st.session_state.daily_calories = self._get_value(
                entry_data, 'Daily Calories (kCal)', None)
            st.session_state.carbs = self._get_value(entry_data, 'Carbs (g)',
                                                     None)
            st.session_state.protein = self._get_value(entry_data,
                                                       'Protein (g)', None)
            st.session_state.fat = self._get_value(entry_data, 'Fat (g)', None)
            st.session_state.cardio_activity = self._get_value(
                entry_data, 'Cardio Activity', None)
            st.session_state.cardio_calories = self._get_value(
                entry_data, 'Cardio Calories (kCal)', None)
            st.session_state.strength_activity = self._get_value(
                entry_data, 'Strength Activity', None)

            # Handle Cardio Duration
            cardio_s = self._get_value(entry_data, 'Cardio Duration (s)', None)
            ch, cm, cs = (None, None, None)
            if cardio_s is not None:
                ch, cm, cs = self._seconds_to_hms(int(cardio_s))
            st.session_state.ch, st.session_state.cm, st.session_state.cs = ch, cm, cs

            # Handle Strength Duration
            strength_s = self._get_value(entry_data, 'Strength Duration (s)',
                                         None)
            sh, sm, ss = (None, None, None)
            if strength_s is not None:
                sh, sm, ss = self._seconds_to_hms(int(strength_s))
            st.session_state.sh, st.session_state.sm, st.session_state.ss = sh, sm, ss

        # --- FORM RENDERING ---
        with st.form(key='entry_form'):
            weight_tab, calorie_tab, cardio_tab, strength_tab = st.tabs(
                ["Weight", "Calories", "Cardio", "Strength"])

            with weight_tab:
                st.number_input("Weight (kg)", key='weight_kg', format="%.2f")
                st.number_input("Waist (cm)", key='waist_cm', format="%.2f")

            with calorie_tab:
                st.number_input("Daily Calories (kCal)", key='daily_calories')
                st.number_input("Carbs (g)", key='carbs')
                st.number_input("Protein (g)", key='protein')
                st.number_input("Fat (g)", key='fat')

            with cardio_tab:
                st.selectbox("Cardio Activity",
                             self.CARDIO_ACTIVITY_LIST,
                             key='cardio_activity')

                st.write("Cardio Duration")
                c1, c2, c3 = st.columns(3)
                c1.number_input("Hours",
                                min_value=0,
                                max_value=23,
                                step=1,
                                key='ch')
                c2.number_input("Minutes",
                                min_value=0,
                                max_value=59,
                                step=1,
                                key='cm')
                c3.number_input("Seconds",
                                min_value=0,
                                max_value=59,
                                step=1,
                                key='cs')
                st.number_input("Cardio Calories (kCal)",
                                key='cardio_calories')

            with strength_tab:
                st.selectbox("Strength Activity",
                             self.STRENGTH_ACTIVITY_LIST,
                             key='strength_activity')
                st.write("Strength Duration")
                s1, s2, s3 = st.columns(3)
                s1.number_input("Hours",
                                min_value=0,
                                max_value=23,
                                step=1,
                                key='sh')
                s2.number_input("Minutes",
                                min_value=0,
                                max_value=59,
                                step=1,
                                key='sm')
                s3.number_input("Seconds",
                                min_value=0,
                                max_value=59,
                                step=1,
                                key='ss')

            # --- SAVE LOGIC ---
            submitted = st.form_submit_button("Save")
            if submitted:
                # On submission, read all values from session_state to save them
                date_to_edit = pd.to_datetime(st.session_state.form_date)
                entry_exists = not st.session_state['fitness_data'][
                    st.session_state['fitness_data']['Date'] ==
                    date_to_edit].empty

                # Calculate total seconds from state
                cardio_total_s = None
                if not all(v is None for v in [
                        st.session_state.ch, st.session_state.cm,
                        st.session_state.cs
                ]):
                    cardio_total_s = (st.session_state.ch or 0) * 3600 + (
                        st.session_state.cm or 0) * 60 + (st.session_state.cs
                                                          or 0)

                strength_total_s = None
                if not all(v is None for v in [
                        st.session_state.sh, st.session_state.sm,
                        st.session_state.ss
                ]):
                    strength_total_s = (st.session_state.sh or 0) * 3600 + (
                        st.session_state.sm or 0) * 60 + (st.session_state.ss
                                                          or 0)

                new_row_data = {
                    "Date": date_to_edit,
                    "Weight (kg)": st.session_state.weight_kg,
                    "Waist (cm)": st.session_state.waist_cm,
                    "Daily Calories (kCal)": st.session_state.daily_calories,
                    "Carbs (g)": st.session_state.carbs,
                    "Protein (g)": st.session_state.protein,
                    "Fat (g)": st.session_state.fat,
                    "Cardio Activity": st.session_state.cardio_activity,
                    "Cardio Duration (s)": cardio_total_s,
                    "Cardio Calories (kCal)": st.session_state.cardio_calories,
                    "Strength Activity": st.session_state.strength_activity,
                    "Strength Duration (s)": strength_total_s,
                }

                current_data = st.session_state['fitness_data']
                if entry_exists:
                    current_data.loc[
                        current_data['Date'] == date_to_edit,
                        new_row_data.keys()] = new_row_data.values()
                else:
                    new_df = pd.DataFrame([new_row_data])
                    current_data = pd.concat([current_data, new_df],
                                             ignore_index=True)

                st.session_state['fitness_data'] = current_data.sort_values(
                    by='Date').reset_index(drop=True)
                self._save_data()
                st.rerun()

    def _display_overview(self):
        """Renders the overview metrics and charts."""
        today = pd.to_datetime(datetime.now().date())
        data = st.session_state['fitness_data'].sort_values(by='Date',
                                                            ascending=False)
        data['Date'] = pd.to_datetime(data['Date'])
        if data.empty:
            st.info("No data available to display. Please add an entry.")
            return
        sorted_data = data.sort_values(by='Date', ascending=False)

        net_weight_cell, avg_cals_cell, col3, col4 = st.columns(4)

        with net_weight_cell:
            latest_weight = sorted_data['Weight (kg)'].iloc[0]
            previous_weight = sorted_data['Weight (kg)'].iloc[1] if len(
                data) > 1 else 0
            delta = round(latest_weight - previous_weight, 2)
            st.metric("Latest Weight",
                      f"{latest_weight} kg",
                      delta=f"{delta} kg",
                      delta_color="inverse")

        with avg_cals_cell:
            start_of_week = today - pd.Timedelta(days=6)
            weekly_data = sorted_data[(sorted_data['Date'] >= start_of_week)
                                      & (sorted_data['Date'] <= today)]
            weekly_data['Daily Calories (kCal)'] = pd.to_numeric(
                weekly_data['Daily Calories (kCal)'], errors='coerce')
            avg_calories = weekly_data['Daily Calories (kCal)'].mean()
            DAILY_NET_INTAKE = 2000
            if pd.notna(avg_calories):
                st.metric("Avg Weekly Calories",
                          f"{avg_calories:.0f} kCal",
                          delta=f"{avg_calories - DAILY_NET_INTAKE:.0f} kCal",
                          delta_color="inverse")
            else:
                st.metric("Avg Weekly Calories", "N/A")

        horizon_options = [
            "1 Week", "2 Weeks", "1 Month", "3 Months", "6 Months", "1 Year",
            "5 Years", "All Time"
        ]
        horizon = st.pills("Time horizon",
                           options=horizon_options,
                           default="3 Months")
        days_map = {
            "1 Week": 7,
            "2 Weeks": 14,
            "1 Month": 31,
            "3 Months": 90,
            "6 Months": 180,
            "1 Year": 365,
            "5 Years": 5 * 365
        }
        start_date = today - pd.Timedelta(days=days_map.get(
            horizon)) if horizon != "All Time" else data['Date'].min()
        filtered_data = data[(data['Date'] >= start_date)
                             & (data['Date'] <= today)]
        if filtered_data.empty:
            st.warning("No data in the selected time horizon.")
            return

        weight_chart_base = alt.Chart(
            filtered_data[filtered_data['Weight (kg)'].notna()]).encode(
                alt.X("Date:T", axis=alt.Axis(title='Date',
                                              format='%Y-%m-%d')),
                alt.Y("Weight (kg):Q").scale(domain=[89, 95]))

        area_chart = weight_chart_base.mark_area(interpolate='basis',
                                                 opacity=0.3)

        line_chart = weight_chart_base.mark_line(interpolate='basis')

        weight_chart = (area_chart + line_chart).properties(
            height=300, title="Weight Trend").interactive()
        show_ma = st.toggle("Show Moving Average", value=True)
        if show_ma:
            ma_window = st.slider("Moving Average Window", 1, 30, 7)
            filtered_data['MA'] = filtered_data['Weight (kg)'].rolling(
                ma_window, min_periods=1).mean()
            ma_chart = alt.Chart(
                filtered_data[filtered_data['MA'].notna()]).mark_line(
                    color='red',
                    interpolate='basis').encode(alt.X("Date:T"), alt.Y("MA:Q"))
            st.altair_chart(weight_chart + ma_chart, use_container_width=True)
        else:
            st.altair_chart(weight_chart, use_container_width=True)

    def _display_raw_data_table(self):
        """Renders the editable raw data table."""
        st.header("📜 Raw Data Log")

        config = {
            'Date':
            st.column_config.DateColumn('Date', format="YYYY-MM-DD"),
            "Cardio Activity":
            st.column_config.SelectboxColumn(
                "Cardio Activity", options=self.CARDIO_ACTIVITY_LIST),
            "Strength Activity":
            st.column_config.SelectboxColumn(
                "Strength Activity", options=self.STRENGTH_ACTIVITY_LIST),
            "Cardio Duration (s)":
            st.column_config.NumberColumn("Cardio Duration (s)",
                                          help="Duration in total seconds."),
            "Strength Duration (s)":
            st.column_config.NumberColumn("Strength Duration (s)",
                                          help="Duration in total seconds.")
        }

        display_df = st.session_state['fitness_data'].sort_values(
            by='Date', ascending=False)

        if st.toggle("Enable editing"):
            edited_df = st.data_editor(display_df,
                                       column_config=config,
                                       use_container_width=True,
                                       hide_index=True)
            if st.button("Save Changes"):
                edited_df['Date'] = pd.to_datetime(edited_df['Date'])
                st.session_state['fitness_data'] = edited_df.sort_values(
                    by='Date').reset_index(drop=True)
                self._save_data()
                st.rerun()
        else:
            st.dataframe(display_df,
                         column_config=config,
                         use_container_width=True,
                         hide_index=True)

    def run(self):
        """Main method to run the Streamlit application."""
        st.set_page_config(page_title="Fitness Dashboard",
                           page_icon="🏃",
                           layout="wide")
        st.markdown(
            """<style>[data-testid="stSidebar"] {width: 100px;}</style>""",
            unsafe_allow_html=True)
        st.title("💪 Fitness Tracker")
        st.markdown("Easily visualize your daily fitness stats.")

        top_row = st.columns([1, 3])
        with top_row[0].container(border=True):
            self._display_input_form()
        with top_row[1].container(border=True):
            self._display_overview()
        st.divider()
        self._display_raw_data_table()


if __name__ == "__main__":
    CSV_FILE_PATH = 'personal/fitness_data.csv'
    app = FitnessTrackerApp(csv_file_path=CSV_FILE_PATH)
    app.run()
