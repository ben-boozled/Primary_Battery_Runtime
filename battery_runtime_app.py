"""
Filename: battery_runtime_app.py
Author: Benjamin Goh
Date: 2 November 2025
Version: 1.0.0

Description: 
Calculates the theoretical runtime of a non-rechargeable primary battery.

Uses the following battery models as reference to calculate the temperature effects on battery capacity:
· Lithium metal batteries: AA Energiser L91 lithium battery (operating temperature: -40°C to 60°C).
· Alkaline batteries: AA Energiser LR6 alkaline battery (operating temperature: -18°C to 55°C).

To display on local Streamlit server, run "streamlit run battery_runtime_app.py" in terminal.
"""

import streamlit as st # documentation https://docs.streamlit.io/get-started/fundamentals/main-concepts
import pandas as pd

class Battery:
    """
    A class used to represent a primary battery.

    Attributes
    ----------
    battery_type: str
        battery type of either "Lithium Metal" (Default) or "Alkaline"
    
    battery_capacity : int
        capacity of battery in mAh

    operating_temp : float
        operating temperature of device in Celsius

    load_current : int
        maximum current draw when load is active in mA

    load_duration_per_day : int
        duration that load is run in seconds

    sleep_current : int
        current draw when device is in sleep mode in mA
    """

    # Attributes
    def __init__(self, battery_type, battery_capacity, operating_temp, load_current, load_duration_per_day=86400, 
                 sleep_current=0):
        self.battery_type = battery_type
        self.battery_capacity = battery_capacity # mAh
        self.operating_temp = operating_temp # Celsius
        self.load_current = load_current # mA
        self.load_duration_per_day = load_duration_per_day # seconds
        self.sleep_current = sleep_current # mA

        # do not directly modify properties below, use the update_battery_properties() function
        self._sleep_duration_per_day = None # seconds
        self._average_current_draw = 0 # mA
        self._self_discharge_rate = 0.01 # per year 
        self._max_shelf_life = 25 # years
        self._min_operating_temp = -40 # Celsius
        self._max_operating_temp = 60 # Celsius
        self._temperature_factor = None # no units
        self._effective_battery_capacity = None # mAh
        self._battery_runtime = None # days

        # current discharge limits to determine which battery curve to reference
        self._current_discharge_mode = None
        self._low_current_discharge = 25 # mA
        self._medium_current_discharge = 250 # mA
        self._high_current_discharge = 1000 # mA

    @property
    def battery_type(self):
        return self._battery_type
    
    @battery_type.setter
    def battery_type(self, value):
        if value in ["Lithium Metal", "Alkaline"]:
            self._battery_type = value

    @property
    def battery_capacity(self):
        return self._battery_capacity
    
    @battery_capacity.setter
    def battery_capacity(self, value):
        if isinstance(value, int) and value >= 0:
            self._battery_capacity = value

    @property
    def operating_temp(self):
        return self._operating_temp
    
    @operating_temp.setter
    def operating_temp(self, value):
        if isinstance(value, int) or isinstance(value, float):
            self._operating_temp = value

    @property
    def load_current(self):
        return self._load_current
    
    @load_current.setter
    def load_current(self, value):
        if (isinstance(value, int) or isinstance(value, float)) and value >= 0:
            self._load_current = value

    @property
    def load_duration_per_day(self):
        return self._load_duration_per_day
    
    @load_duration_per_day.setter
    def load_duration_per_day(self, value):
        if (isinstance(value, int) or isinstance(value, float)):
            if value >= 0 and value <= 86400:
                self._load_duration_per_day = value

    @property
    def sleep_current(self):
        return self._sleep_current
    
    @sleep_current.setter
    def sleep_current(self, value):
        if (isinstance(value, int) or isinstance(value, float)) and value >= 0:
            self._sleep_current = value

    @property
    def sleep_duration_per_day(self):
        return self._sleep_duration_per_day
    
    @property
    def average_current_draw(self):
        return self._average_current_draw
    
    @property
    def self_discharge_rate(self):
        return self._self_discharge_rate
    
    @property
    def max_shelf_life(self):
        return self._max_shelf_life
    
    @property
    def min_operating_temp(self):
        return self._min_operating_temp
    
    @property
    def max_operating_temp(self):
        return self._max_operating_temp
        
    @property
    def temperature_factor(self):
        return self._temperature_factor
    
    @property
    def effective_battery_capacity(self):
        return self._effective_battery_capacity
    
    @property
    def battery_runtime(self):
        return self._battery_runtime
    
    @property
    def current_discharge_mode(self):
        return self._current_discharge_mode
    
    @property
    def low_current_discharge(self):
        return self._low_current_discharge
    
    @property
    def medium_current_discharge(self):
        return self._medium_current_discharge
    
    @property
    def high_current_discharge(self):
        return self._high_current_discharge

    # Methods
    def battery_details(self):
        """
        Returns all the battery details in a dictionary format.

        Parameters
        ----------
            None

        Returns
        -------
            dict: all battery properties and their corresponding values 
        """
        return {
            "Battery Type": self.battery_type,
            "Battery Capacity (mAh)": self.battery_capacity,
            "Current Operating Temperature (°C)": self.operating_temp,
            "Load Current (mA)": self.load_current,
            "Load Duration Per Day (s)": self.load_duration_per_day,
            "Sleep Current (mA)": self.sleep_current,
            "Sleep Duration Per Day (s)": self.sleep_duration_per_day,
            "Average Current Draw (mA)": self.average_current_draw,
            "Annual Self-discharge Rate": self.self_discharge_rate,
            "Max Shelf Life (Years)": self.max_shelf_life,
            "Operating Temperature Range (°C)": {"Min": self.min_operating_temp,
                                                 "Max": self.max_operating_temp
                                                },
            "Temperature Factor": self.temperature_factor,
            "Effective Battery Capacity (mAh)": self.effective_battery_capacity,
            "Battery Runtime (Days)": self.battery_runtime,
            "Current Discharge Mode": self.current_discharge_mode,
            "Constant Current Discharge Limits (mA)": {"Low": self.low_current_discharge, 
                                                       "Medium": self.medium_current_discharge,
                                                       "High": self.high_current_discharge
                                                      }
        }

    def calculate_temperature_factor(self):
        """
        Calculates temperature factor to determine effective battery capacity.

        Parameters
        ----------
            None

        Returns
        ------
            float: temperature factor
        """
        if self.operating_temp < self.min_operating_temp or self.operating_temp > self.max_operating_temp:
            return float(0)
        
        else: 
            # extract dataframe from spreadsheet depending on battery type and average current draw
            sheet_name = "Li Temperature Factor"
            if self.battery_type == "Alkaline":
                sheet_name = "Alkaline Temperature Factor"

            columns = ["Constant Current Discharge / mA", "Operating Temperature / °C", "Temperature Factor"]
            df = pd.read_excel("Battery Parameters Data caa 20251104.xlsx", sheet_name = sheet_name, index_col=None, usecols=columns)
            df = df.loc[df["Constant Current Discharge / mA"] == self.battery_details()["Constant Current Discharge Limits (mA)"][self.current_discharge_mode]].reset_index(drop=True)

            if self.operating_temp == self.max_operating_temp: # edge case to extract temperature factor of max operating temp
                return df.loc[0, "Temperature Factor"]

            # linear interpolation of temperature factor from Excel data
            for row in range(df.shape[0]-1):
                if self.operating_temp < df.loc[row, "Operating Temperature / °C"] and self.operating_temp >= df.loc[row+1, "Operating Temperature / °C"]:
                    x1, y1 = df.loc[row+1, "Operating Temperature / °C"], df.loc[row+1,"Temperature Factor"]
                    x2, y2 = df.loc[row, "Operating Temperature / °C"], df.loc[row,"Temperature Factor"]
                    return y1 + ((y2-y1)/(x2-x1))*(self.operating_temp-x1) 
    
    def calculate_runtime(self):
        """
        Calculates the estimated runtime of the battery based on load, operating temperature, and self-discharge rates.

        Parameters
        ----------
            None

        Output
        ------
            float: estimated battery runtime
        """
        if self.effective_battery_capacity == 0:
            return 0
        
        daily_load_contribution = self.load_current * (self.load_duration_per_day/3600) # mAh
        daily_sleep_contribution = self.sleep_current * (self.sleep_duration_per_day/3600)
        
        total_daily_consumption = daily_load_contribution + daily_sleep_contribution + (self.self_discharge_rate*self.effective_battery_capacity/365)

        battery_runtime = self.effective_battery_capacity / total_daily_consumption # in days

        if battery_runtime/365 >= self.max_shelf_life:
            battery_runtime = self.max_shelf_life*365

        return round(battery_runtime,2)
    
    def update_current_discharge_mode(self):
        """
        Updates the battery's current discharge mode to determine effective battery capacity.

        Parameters
        ----------
        None

        Returns
        -------
            str: "Low", "Medium" or "High" 
        """
        if self.average_current_draw <= self.low_current_discharge:
            return "Low"
        elif self.average_current_draw <= self.medium_current_discharge:
            return "Medium"
        else:
            return "High"            

    def update_battery_properties(self):
        """
        Updates the battery's sleep duration per day, temperature factor, effective battery capacity, operating
        temperature limits, shelf life, and runtime properties.

        Parameters
        ----------
            None

        Returns
        -------
            int: returns 0 if the function executes successfully.
        """
        self._min_operating_temp = -40 # default to lithium metal battery properties
        self._max_operating_temp = 60
        self._max_shelf_life = 25

        if self.battery_type == "Alkaline":
            self._min_operating_temp = -18 # Celsius
            self._max_operating_temp = 55
            self._max_shelf_life = 10

        self._sleep_duration_per_day = 86400 - self.load_duration_per_day
        self._average_current_draw = round(self.load_current*self.load_duration_per_day/86400 + self.sleep_current*self.sleep_duration_per_day/86400,3)    
        self._current_discharge_mode = self.update_current_discharge_mode()
        self._temperature_factor = self.calculate_temperature_factor()
        self._effective_battery_capacity = self.temperature_factor * self.battery_capacity
        self._battery_runtime = self.calculate_runtime()
        return 0

st.title("Battery Runtime Calculator")
st.markdown("**Created by: Benjamin Goh**")
st.write("Calculator to estimate the runtime of non-rechargeable batteries.")

# Collect parameters for calculation
battery_type = None
battery_capacity = None
operating_temp = None
load_current = None
load_duration_per_day = None
sleep_current = None

with st.container(border=True):
    battery_type = st.radio("**Battery Type**", ["Lithium Metal", "Alkaline"], index=0, horizontal=True)

with st.container(border=True):
    battery_capacity = st.number_input("**Battery Capacity / mAh**", min_value=0, step=1, 
                                    help="For a bank of identical batteries, if batteries are in series, mAh capacity " \
                                    "remains the same as a single battery. If batteries are in parallel, mAh " \
                                    "capacities are added together.")
    operating_temp = st.number_input("**Operating Temperature / °C**", step=0.1, format="%0.1f", help="Typical operating " \
                                    "temperature range for high-quality lithium metal batteries is -40°C to 60°C.")
    load_current = st.number_input("**Load Current / mA**", min_value=0.00)
    load_duration_per_day = st.number_input("**Load Duration Per Day / s**", min_value=0.0, max_value=86400.0, step=0.1, 
                                            format="%0.1f", help="0s to 86400s.")
    sleep_current = st.number_input("**_Sleep Current / mA (Optional)_**", min_value=0.00)

# Button to initiate calculation of battery runtime
clicked = st.button("Calculate Runtime", type="primary")

if clicked:
    # Compute results
    DeviceBattery = Battery(battery_type, battery_capacity, operating_temp, load_current, load_duration_per_day, sleep_current)
    DeviceBattery.update_battery_properties()
    battery_details = DeviceBattery.battery_details()

    # Display battery runtime results
    with st.container(border=True):

        result = f"""**Estimated Battery Runtime: {DeviceBattery.battery_runtime//365:.0f} year(s) {DeviceBattery.battery_runtime/365%1*365:.0f} day(s)**
        \n- Effective Battery Capacity: {DeviceBattery.effective_battery_capacity:.0f} mAh at {DeviceBattery.operating_temp:.1f}°C
        \n- Self-discharge Rate: {DeviceBattery.self_discharge_rate:.2%} per year
        \n- Load Consumption: {DeviceBattery.load_current*DeviceBattery.load_duration_per_day/3600:.2f} mAh per day
        \n- Sleep Consumption: {DeviceBattery.sleep_current*DeviceBattery.sleep_duration_per_day/3600:.2f} mAh per day
        """
        st.write(result)
        
        st.caption("_Note: These calculations are theoretical estimates. The actual battery runtime " \
                   "may vary depending on additional factors such as real-world conditions and system efficiency._")
    
if __name__ == "__main__":
    # Test Case
    # TestBattery = Battery("Lithium Metal", 16000, 50, 90, 240, 0.06) # expected battery runtime of 2031 days
    TestBattery = Battery("Lithium Metal", 16000, -35, 1500, 2000, 0.06) 
    TestBattery.update_battery_properties()
    print(TestBattery.battery_details()) 
