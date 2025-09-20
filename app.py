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
    COLUMNS = [
        "Date", "Weight (kg)", "Waist (cm)", "Daily Calories (kCal)",
        "Carbs (g)", "Protein (g)", "Fat (g)", "Cardio Activity",
        "Cardio Duration (min)", "Cardio Calories (kCal)", "Strength Activity",
        "Strength Duration (min)"
    ]

    def __init__(self, csv_file_path: str):
        """
        Initializes the FitnessTrackerApp.
        Args:
            csv_file_path (str): The path to the CSV file for storing data.
        """
        self.csv_file_path = csv_file_path
        self.data = self._load_data()

    def _load_data(self) -> pd.DataFrame:
        """Loads data from the CSV file or creates a new DataFrame."""
        try:
            df = pd.read_csv(self.csv_file_path)
            # Ensure all defined columns are present, adding any that are missing
            for col in self.COLUMNS:
                if col not in df.columns:
                    df[col] = None  # Use None for object types or np.nan for numeric
            df = df[self.COLUMNS]  # Enforce column order
            df['Date'] = pd.to_datetime(df['Date'])
        except FileNotFoundError:
            print("CSV file not found. Creating a new DataFrame.")
            df = pd.DataFrame(columns=self.COLUMNS)
            df['Date'] = pd.to_datetime(
                df['Date'])  # Ensure Date column is datetime type

        return df.sort_values(by='Date').reset_index(drop=True)

    def _save_data(self):
        """Saves the current DataFrame to the CSV file."""
        # Ensure date format is consistent before saving
        save_df = self.data.copy()
        save_df['Date'] = pd.to_datetime(
            save_df['Date']).dt.strftime('%m/%d/%Y')
        save_df.to_csv(self.csv_file_path, index=False)
        st.success("Data saved successfully!")

    def _get_value(self,
                   entry_data: pd.DataFrame,
                   column: str,
                   default_value=None):
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

    def _display_input_form(self):
        """Renders the input form for adding or editing an entry."""
        st.subheader("Add/Edit Entry")
        date_to_edit_input = st.date_input("Date", datetime.now().date())
        # Convert date input to datetime for comparison with DataFrame
        date_to_edit = pd.to_datetime(date_to_edit_input)

        entry_data = self.data[self.data['Date'] == date_to_edit]

        with st.form(key='entry_form'):
            weight_tab, calorie_tab, cardio_tab, strength_tab = st.tabs(
                ["Weight", "Calories", "Cardio", "Strength"])
            with weight_tab:
                weight = st.number_input("Weight (kg)",
                                         value=self._get_value(
                                             entry_data, 'Weight (kg)', 0.0))
                waist = st.number_input("Waist (cm)",
                                        value=self._get_value(
                                            entry_data, 'Waist (cm)', 0.0))
            with calorie_tab:
                daily_calories = st.number_input(
                    "Daily Calories (kCal)",
                    value=self._get_value(entry_data, 'Daily Calories (kCal)',
                                          0))
                carbs = st.number_input("Carbs (g)",
                                        value=self._get_value(
                                            entry_data, 'Carbs (g)', 0))
                protein = st.number_input("Protein (g)",
                                          value=self._get_value(
                                              entry_data, 'Protein (g)', 0))
                fat = st.number_input("Fat (g)",
                                      value=self._get_value(
                                          entry_data, 'Fat (g)', 0))
            with cardio_tab:
                cardio_activity_val = self._get_value(entry_data,
                                                      'Cardio Activity', None)

                cardio_activity_index = None
                if cardio_activity_val in self.CARDIO_ACTIVITY_LIST:
                    cardio_activity_index = self.CARDIO_ACTIVITY_LIST.index(
                        cardio_activity_val)

                cardio_activity = st.selectbox(
                    "Cardio Activity",
                    self.CARDIO_ACTIVITY_LIST,
                    index=cardio_activity_index,
                    placeholder=
                    "Select cardio activity..."
                )

                cardio_duration = st.number_input(
                    "Cardio Duration (min)",
                    value=self._get_value(entry_data, 'Cardio Duration (min)',
                                          0))
                cardio_calories = st.number_input(
                    "Cardio Calories (kCal)",
                    value=self._get_value(entry_data, 'Cardio Calories (kCal)',
                                          0))
            with strength_tab:
                strength_activity_val = self._get_value(
                    entry_data, 'Strength Activity', None)

                strength_activity_index = None
                if strength_activity_val in self.STRENGTH_ACTIVITY_LIST:
                    strength_activity_index = self.STRENGTH_ACTIVITY_LIST.index(
                        cardio_activity_val)

                strength_activity = st.selectbox(
                    "Strength Activity",
                    self.STRENGTH_ACTIVITY_LIST,
                    index=strength_activity_index,
                    placeholder="Select strength activity...")

                strength_duration = st.number_input(
                    "Strength Duration (min)",
                    value=self._get_value(entry_data,
                                          'Strength Duration (min)', 0))

            submitted = st.form_submit_button("Save")
            if submitted:
                new_row_data = {
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
                    # Update existing row
                    self.data.loc[self.data['Date'] == date_to_edit,
                                  new_row_data.keys()] = new_row_data.values()
                else:
                    # Add new row
                    new_df = pd.DataFrame([new_row_data])
                    self.data = pd.concat([self.data, new_df],
                                          ignore_index=True)

                self._save_data()
                st.rerun()

    def _display_overview(self):
        """Renders the overview metrics and charts."""
        today = pd.to_datetime(datetime.now().date())

        if self.data.empty:
            st.info("No data available to display. Please add an entry.")
            return

        net_weight_cell, avg_cals_cell, col3, col4 = st.columns(4)
        with net_weight_cell:
            latest_weight = self.data['Weight (kg)'].iloc[-1]
            previous_weight = self.data['Weight (kg)'].iloc[-2] if len(
                self.data) > 1 else 0
            delta = round(latest_weight - previous_weight, 2)
            st.metric("Latest Weight",
                      f"{latest_weight} kg",
                      delta=f"{delta} kg",
                      delta_color="inverse")
        with avg_cals_cell:
            start_of_week = today - pd.Timedelta(days=6)
            weekly_data = self.data[(self.data['Date'] >= start_of_week)
                                    & (self.data['Date'] <= today)]
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

        # --- Charting Section ---
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
            horizon)) if horizon != "All Time" else self.data['Date'].min()

        filtered_data = self.data[(self.data['Date'] >= start_date)
                                  & (self.data['Date'] <= today)]

        if filtered_data.empty:
            st.warning("No data in the selected time horizon.")
            return

        weight_chart = alt.Chart(filtered_data).mark_line(
            interpolate='basis').encode(
                alt.X("Date:T", axis=alt.Axis(title='Date',
                                              format='%Y-%m-%d')),
                alt.Y("Weight (kg):Q").scale(zero=False),
            ).properties(height=300, title="Weight Trend")

        show_ma = st.toggle("Show Moving Average", value=True)
        if show_ma:
            ma_window = st.slider("Moving Average Window", 1, 30, 7)
            filtered_data['MA'] = filtered_data['Weight (kg)'].rolling(
                ma_window, min_periods=1).mean()
            ma_chart = alt.Chart(filtered_data).mark_line(
                color='red',
                interpolate='basis').encode(alt.X("Date:T"), alt.Y("MA:Q"))
            st.altair_chart(weight_chart + ma_chart, use_container_width=True)
        else:
            st.altair_chart(weight_chart, use_container_width=True)

    def _display_raw_data_table(self):
        """Renders the editable raw data table."""
        st.header("Raw Data")

        config = {
            'Date':
            st.column_config.DateColumn('Date', format="YYYY-MM-DD"),
            "Cardio Activity":
            st.column_config.SelectboxColumn(
                "Cardio Activity", options=self.CARDIO_ACTIVITY_LIST),
            "Strength Activity":
            st.column_config.SelectboxColumn(
                "Strength Activity", options=self.STRENGTH_ACTIVITY_LIST)
        }

        # Use a copy for display to avoid altering the main dataframe's date format
        display_data = self.data.sort_values(by='Date', ascending=False)

        if st.toggle("Enable editing"):
            edited_data = st.data_editor(display_data,
                                         column_config=config,
                                         use_container_width=True,
                                         hide_index=True)
            if st.button("Save Changes"):
                # Update self.data with the edited data
                edited_data['Date'] = pd.to_datetime(edited_data['Date'])
                self.data = edited_data.sort_values(by='Date').reset_index(
                    drop=True)
                self._save_data()
                st.rerun()
        else:
            st.dataframe(display_data,
                         column_config=config,
                         use_container_width=True,
                         hide_index=True)

    def run(self):
        """Main method to run the Streamlit application."""
        st.set_page_config(page_title="Fitness Dashboard",
                           page_icon="🏃",
                           layout="wide")
        st.title("💪 Fitness Tracker")
        st.markdown("Easily visualize your daily fitness stats.")

        top_row = st.columns([1, 3])  # Adjusted column ratio for better layout

        with top_row[0].container(border=True):
            self._display_input_form()

        with top_row[1].container(border=True):
            self._display_overview()

        st.divider()
        self._display_raw_data_table()


if __name__ == "__main__":
    # Define the path to your data file
    CSV_FILE_PATH = 'personal/fitness_data.csv'

    # Create an instance of the app and run it
    app = FitnessTrackerApp(csv_file_path=CSV_FILE_PATH)
    app.run()
