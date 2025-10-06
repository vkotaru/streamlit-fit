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
        "None", '🏋🏽‍♂️ Full Body', '💪🏽 Arms', '🦵🏽 Legs', '🧎🏽‍♂️ Core',
        '🏌🏽‍♂️ Back'
    ]
    # NOTE: The duration columns will store total SECONDS.
    METRICS_COLUMNS = [
        "Date",
        "Weight (kg)",
        "Waist (cm)",
        "Daily Calories (kCal)",
        "Carbs (g)",
        "Protein (g)",
        "Fat (g)",
        "Active Calories (kCal)",
    ]
    ACTIVITIES_COLUMNS = [
        "Date", "Type", "Activity", "Duration (s)", "Distance (mi)",
        "Calories (kCal)"
    ]

    def __init__(self, metrics_path: str, activites_path: str):
        """
        Initializes the FitnessTrackerApp.
        Args:
            csv_file_path (str): The path to the CSV file for storing data.
        """
        self._metrics_file_path = metrics_path
        self._activites_file_path = activites_path
        if 'metrics' not in st.session_state:
            st.session_state['metrics'] = self._load_metrics_data()
        if 'activities' not in st.session_state:
            st.session_state['activities'] = self._load_activities_data()

    def _load_metrics_data(self) -> pd.DataFrame:
        """Loads data from the CSV file or creates a new DataFrame."""
        try:
            df = pd.read_csv(self._metrics_file_path)
            for col in self.METRICS_COLUMNS:
                if col not in df.columns:
                    df[col] = None
            df = df[self.METRICS_COLUMNS]
            df['Date'] = pd.to_datetime(df['Date'])
        except FileNotFoundError:
            print("CSV file not found. Creating a new DataFrame.")
            df = pd.DataFrame(columns=self.METRICS_COLUMNS)
            df['Date'] = pd.to_datetime(df['Date'])
        return df.sort_values(by='Date').reset_index(drop=True)

    def _load_activities_data(self) -> pd.DataFrame:
        """Loads activites from csv into a dataframe.

        Returns:
            pd.DataFrame: _description_
        """
        try:
            df = pd.read_csv(self._activites_file_path,
                           dtype={
                               "Type": "str",
                               "Activity": "str"
                           })
            for col in self.ACTIVITIES_COLUMNS:
                if col not in df.columns:
                    df[col] = None
            df = df[self.ACTIVITIES_COLUMNS]
            df['Date'] = pd.to_datetime(df['Date'])
        except FileNotFoundError:
            print("CSV file not found. Creating a new DataFrame.")
            df = pd.DataFrame(columns=self.ACTIVITIES_COLUMNS)
            df['Date'] = pd.to_datetime(df['Date'])
        return df.sort_values(by='Date').reset_index(drop=True)

    def _save_data(self):
        """Saves the current DataFrame to the CSV file."""
        print("Saving data... to ")
        save_metrics_df = st.session_state['metrics'].copy()
        save_metrics_df['Date'] = pd.to_datetime(
            save_metrics_df['Date']).dt.strftime('%m/%d/%Y')
        print(f"Saving measurements to {self._metrics_file_path}")
        save_metrics_df.to_csv(self._metrics_file_path, index=False)
        save_activities_df = st.session_state['activities'].copy()
        save_activities_df['Date'] = pd.to_datetime(
            save_activities_df['Date']).dt.strftime('%m/%d/%Y')
        print(f"Saving activities to {self._activites_file_path}")
        save_activities_df.to_csv(self._activites_file_path, index=False)
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
        date_to_edit_input = st.date_input("Date", datetime.now().date())

        # --- STATE MANAGEMENT LOGIC for Metrics ---
        if 'form_date' not in st.session_state or st.session_state.form_date != date_to_edit_input:
            st.session_state.form_date = date_to_edit_input
            date_to_edit = pd.to_datetime(date_to_edit_input)
            metrics_data = st.session_state['metrics']
            entry_data = metrics_data[metrics_data['Date'] == date_to_edit]

            # Load metrics form values into session state from the DataFrame
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

        # --- FORM RENDERING ---
        body_metrics_tab, nutrition_tab, activities_tab = st.tabs(
            ["Body Metrics", "Nutrition", "Activities"])

        with body_metrics_tab:
            with st.form(key='body_metrics_form', border=False):
                st.number_input("Weight (kg)", key='weight_kg', format="%.2f")
                st.number_input("Waist (cm)", key='waist_cm', format="%.2f")
                submitted = st.form_submit_button("Save Body Metrics")
                if submitted:
                    date_to_edit = pd.to_datetime(st.session_state.form_date)
                    metrics_df = st.session_state['metrics']
                    entry_exists = not metrics_df[metrics_df['Date'] ==
                                                  date_to_edit].empty

                    new_row_data = {
                        "Date": date_to_edit,
                        "Weight (kg)": st.session_state.weight_kg,
                        "Waist (cm)": st.session_state.waist_cm,
                    }

                    if entry_exists:
                        for key, value in new_row_data.items():
                            metrics_df.loc[metrics_df['Date'] == date_to_edit,
                                           key] = value
                    else:
                        full_new_row = {
                            col: None
                            for col in self.METRICS_COLUMNS
                        }
                        full_new_row.update(new_row_data)
                        new_df = pd.DataFrame([full_new_row])
                        metrics_df = pd.concat([metrics_df, new_df],
                                               ignore_index=True)

                    st.session_state['metrics'] = metrics_df.sort_values(
                        by='Date').reset_index(drop=True)
                    self._save_data()
                    st.rerun()

        with nutrition_tab:
            with st.form(key='nutrition_form', border=False):
                st.number_input("Daily Calories (kCal)",
                                key='daily_calories',
                                step=1)
                st.number_input("Carbs (g)", key='carbs', step=1)
                st.number_input("Protein (g)", key='protein', step=1)
                st.number_input("Fat (g)", key='fat', step=1)
                submitted = st.form_submit_button("Save Nutrition")
                if submitted:
                    date_to_edit = pd.to_datetime(st.session_state.form_date)
                    metrics_df = st.session_state['metrics']
                    entry_exists = not metrics_df[metrics_df['Date'] ==
                                                  date_to_edit].empty

                    new_row_data = {
                        "Date": date_to_edit,
                        "Daily Calories (kCal)":
                        st.session_state.daily_calories,
                        "Carbs (g)": st.session_state.carbs,
                        "Protein (g)": st.session_state.protein,
                        "Fat (g)": st.session_state.fat,
                    }

                    if entry_exists:
                        for key, value in new_row_data.items():
                            metrics_df.loc[metrics_df['Date'] == date_to_edit,
                                           key] = value
                    else:
                        full_new_row = {
                            col: None
                            for col in self.METRICS_COLUMNS
                        }
                        full_new_row.update(new_row_data)
                        new_df = pd.DataFrame([full_new_row])
                        metrics_df = pd.concat([metrics_df, new_df],
                                               ignore_index=True)

                    st.session_state['metrics'] = metrics_df.sort_values(
                        by='Date').reset_index(drop=True)
                    self._save_data()
                    st.rerun()

        with activities_tab:
            activity_type = st.selectbox("Activity Type",
                                         ["Cardio", "Strength"])
            with st.form(key='activity_form', border=False):
                if activity_type == "Cardio":
                    activity = st.selectbox("Activity",
                                            self.CARDIO_ACTIVITY_LIST)
                else:
                    activity = st.selectbox("Activity",
                                            self.STRENGTH_ACTIVITY_LIST)

                c1, c2, c3 = st.columns(3)
                hours = c1.number_input("hrs",
                                        min_value=0,
                                        max_value=23,
                                        step=1,
                                        key='act_h')
                minutes = c2.number_input("mins",
                                          min_value=0,
                                          max_value=59,
                                          step=1,
                                          key='act_m')
                seconds = c3.number_input("secs",
                                          min_value=0,
                                          max_value=59,
                                          step=1,
                                          key='act_s')

                distance = st.number_input("Distance (mi)",
                                           format="%.2f",
                                           key='act_dist')
                calories = st.number_input("Calories (kCal)",
                                           key='act_cals',
                                           step=1)

                submitted = st.form_submit_button("Add Activity")
                if submitted:
                    duration_s = (hours * 3600) + (minutes * 60) + seconds
                    date = pd.to_datetime(st.session_state.form_date)

                    new_activity_data = {
                        "Date": date,
                        "Type": activity_type,
                        "Activity": activity,
                        "Duration (s)": duration_s,
                        "Distance (mi)": distance,
                        "Calories (kCal)": calories,
                    }

                    activities_df = st.session_state['activities']
                    new_df = pd.DataFrame([new_activity_data])
                    activities_df = pd.concat([activities_df, new_df],
                                              ignore_index=True)

                    st.session_state['activities'] = activities_df.sort_values(
                        by='Date').reset_index(drop=True)

                    # --- Update Active Calories in metrics ---
                    if calories and calories > 0:
                        metrics_df = st.session_state['metrics']
                        entry_exists = not metrics_df[metrics_df['Date'] == date].empty

                        if entry_exists:
                            current_calories = metrics_df.loc[metrics_df['Date'] == date, 'Active Calories (kCal)'].iloc[0]
                            if pd.isna(current_calories):
                                current_calories = 0
                            new_calories = current_calories + calories
                            metrics_df.loc[metrics_df['Date'] == date, 'Active Calories (kCal)'] = new_calories
                        else:
                            new_row_data = {col: None for col in self.METRICS_COLUMNS}
                            new_row_data['Date'] = date
                            new_row_data['Active Calories (kCal)'] = calories
                            new_df = pd.DataFrame([new_row_data])
                            metrics_df = pd.concat([metrics_df, new_df], ignore_index=True)

                        st.session_state['metrics'] = metrics_df.sort_values(
                            by='Date').reset_index(drop=True)

                    self._save_data()
                    st.success("Activity added!")

    def _display_overview(self):
        """Renders the overview metrics and charts."""
        today = pd.to_datetime(datetime.now().date())
        data = st.session_state['metrics'].sort_values(by='Date',
                                                       ascending=False)
        data['Date'] = pd.to_datetime(data['Date'])
        if data.empty:
            st.info("No data available to display. Please add an entry.")
            return

        net_weight_cell, avg_cals_cell, col3, col4 = st.columns(4)

        with net_weight_cell:
            latest_weight = data['Weight (kg)'].iloc[0]
            previous_weight = data['Weight (kg)'].iloc[1] if len(
                data) > 1 else 0
            delta = round(latest_weight - previous_weight, 2)
            st.metric("Latest Weight",
                      f"{latest_weight} kg",
                      delta=f"{delta} kg",
                      delta_color="inverse")

        with avg_cals_cell:
            start_of_week = today - pd.Timedelta(days=6)
            weekly_data = data[(data['Date'] >= start_of_week)
                                      & (data['Date'] <= today)]
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
        days_map = {
            "1 Week": 7,
            "2 Weeks": 14,
            "1 Month": 31,
            "3 Months": 90,
            "6 Months": 180,
            "1 Year": 365,
            "5 Years": 5 * 365
        }

        interpolation_cell, mov_avg_togg_cell, mov_avg_num_cell, time_horizon_cell = st.columns(
            4)
        with interpolation_cell:
            interpolate_options = ["basis", "linear"]
            interpolate = st.pills("Interpolation",
                                   options=interpolate_options,
                                   default="linear")
        with mov_avg_togg_cell:
            show_ma = st.toggle("Show Moving Average", value=True)

        with mov_avg_num_cell:
            ma_window = st.number_input('Moving Avg Window (days)',
                                        value=7,
                                        min_value=1)

        with time_horizon_cell:
            horizon = st.selectbox("Time horizon",
                                   options=horizon_options,
                                   index=2)

            start_date = today - pd.Timedelta(days=days_map.get(
                horizon)) if horizon != "All Time" else data['Date'].min()
            filtered_data = data[(data['Date'] >= start_date)
                                 & (data['Date'] <= today)]
            if filtered_data.empty:
                st.warning("No data in the selected time horizon.")
                return

        chart_data = filtered_data.sort_values(by='Date', ascending=True)
        weight_chart_base = alt.Chart(
            chart_data[chart_data['Weight (kg)'].notna()]).encode(
                alt.X("Date:T", axis=alt.Axis(title='Date',
                                              format='%Y-%m-%d')),
                alt.Y("Weight (kg):Q").scale(domain=[89, 95]))

        area_chart = weight_chart_base.mark_area(interpolate=interpolate,
                                                 opacity=0.3)

        line_chart = weight_chart_base.mark_line(interpolate=interpolate)

        weight_chart = (area_chart + line_chart).properties(
            height=300, title="Weight Trend")
        if show_ma:
            chart_data['MA'] = chart_data['Weight (kg)'].rolling(
                ma_window, min_periods=1).mean()
            ma_chart = alt.Chart(
                chart_data[chart_data['MA'].notna()]).mark_line(
                    color='red',
                    interpolate=interpolate).encode(alt.X("Date:T"),
                                                    alt.Y("MA:Q"))
            st.altair_chart(weight_chart + ma_chart, use_container_width=True)
        else:
            st.altair_chart(weight_chart, use_container_width=True)

    def _display_raw_data_table(self):
        """Renders the editable raw data table."""
        st.header("📜 Raw Data Log")

        metrics_tab, activities_tab = st.tabs(
            ["Metrics & Measurements", "Activities"])
        with metrics_tab:
            metrics_df = st.session_state['metrics'].sort_values(
                by='Date', ascending=False)
            config = {
                'Date': st.column_config.DateColumn('Date',
                                                    format="YYYY-MM-DD"),
            }
            if st.toggle("Enable Measurements editing"):
                edited_metrics_df = st.data_editor(metrics_df,
                                                   column_config=config,
                                                   use_container_width=True,
                                                   hide_index=True,
                                                   key="metrics_editor")
                if st.button("Save Measurement Changes", key="save_metrics_button"):
                    edited_metrics_df.replace('', None, inplace=True)
                    edited_metrics_df['Date'] = pd.to_datetime(
                        edited_metrics_df['Date'])
                    st.session_state[
                        'metrics'] = edited_metrics_df.sort_values(
                            by='Date').reset_index(drop=True)
                    self._save_data()
                    st.rerun()
            else:
                st.dataframe(metrics_df,
                             column_config=config,
                             use_container_width=True,
                             hide_index=True)

        with activities_tab:
            activities_df = st.session_state['activities'].sort_values(
                by='Date', ascending=False)
            config = {
                "Date":
                st.column_config.DateColumn('Date', format="YYYY-MM-DD"),
                "Type":
                st.column_config.SelectboxColumn(
                    "Type", options=["Cardio", "Strength"]),
                "Activity":
                st.column_config.SelectboxColumn(
                    "Activity",
                    options=self.CARDIO_ACTIVITY_LIST +
                    self.STRENGTH_ACTIVITY_LIST),
            }
            if st.toggle("Enable Activities editing"):
                edited_activities_df = st.data_editor(activities_df,
                                                      column_config=config,
                                                      use_container_width=True,
                                                      hide_index=True,
                                                      key="activities_editor")
                if st.button("Save Activity Changes", key="save_activities_button"):
                    edited_activities_df.replace('', None, inplace=True)
                    edited_activities_df['Date'] = pd.to_datetime(
                        edited_activities_df['Date'])
                    st.session_state[
                        'activities'] = edited_activities_df.sort_values(
                            by='Date').reset_index(drop=True)
                    self._save_data()
                    st.rerun()
            else:
                st.dataframe(activities_df,
                             column_config=config,
                             use_container_width=True,
                             hide_index=True)
        return

    def run(self):
        """Main method to run the Streamlit application."""
        st.set_page_config(page_title="Fitness Dashboard",
                           page_icon="🏃",
                           layout="wide")
        st.markdown(
            """<style>[data-testid="stSidebar"] {width: 100px;}</style>""",
            unsafe_allow_html=True)
        st.title("💪 Fitness Tracker")
        top_row = st.columns([1, 3])
        with top_row[0].container(border=False):
            self._display_input_form()
        with top_row[1].container(border=False):
            self._display_overview()
            pass
        st.divider()
        self._display_raw_data_table()


if __name__ == "__main__":
    FITNESS_CSV_PATH = 'personal/metrics.csv'
    ACTIVIES_CSV_PATH = 'personal/activities.csv'
    app = FitnessTrackerApp(metrics_path=FITNESS_CSV_PATH,
                            activites_path=ACTIVIES_CSV_PATH)
    app.run()
