"""
Filename: lithium_battery_runtime_app.py
Author: Benjamin Goh
Date: 1 November 2025
Version: 1.0.0

Description: 
Calculates the theoretical runtime of a non-rechargeable lithium metal battery.
Uses the Energiser L91 Ultimate Lithium AA Battery as a standard for the parameters.
"""

import streamlit as st # documentation https://docs.streamlit.io/get-started/fundamentals/main-concepts
import pandas as pd

class Battery:
    """
    A class used to represent a primary lithium metal battery.

    Attributes
    ----------
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
    def __init__(self, battery_capacity, operating_temp, load_current, load_duration_per_day=86400, sleep_current=0):
        self.battery_capacity = battery_capacity # mAh
        self.operating_temp = operating_temp # Celsius
        self.load_current = load_current # mA
        self.load_duration_per_day = load_duration_per_day # seconds
        self.sleep_current = sleep_current # mA

        # do not directly modify properties below, use the update_battery_properties() function
        self._sleep_duration_per_day = None # seconds
        self._self_discharge_rate = 0.01 # per year 
        self._max_shelf_life = 25 # years
        self._min_operating_temp = -40 # Celsius
        self._max_operating_temp = 60 # Celsius
        self._temperature_factor = None # no units
        self._effective_battery_capacity = None # mAh
        self._battery_runtime = None # days

    @property
    def battery_capacity(self):
        return self._battery_capacity
    
    @battery_capacity.setter
    def battery_capacity(self, value):
        if isinstance(value, int) and value > 0:
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
            "Battery Capacity (mAh)": self.battery_capacity,
            "Operating Temperature (°C)": self.operating_temp,
            "Load Current (mA)": self.load_current,
            "Load Duration Per Day (s)": self.load_duration_per_day,
            "Sleep Current (mA)": self.sleep_current,
            "Sleep Duration Per Day (s)": self.sleep_duration_per_day,
            "Annual Self-discharge Rate": self.self_discharge_rate,
            "Max Shelf Life (Years)": self.max_shelf_life,
            "Min Operating Temperature (°C)": self.min_operating_temp,
            "Max Operating Temperature (°C)": self.max_operating_temp,
            "Temperature Factor": self.temperature_factor,
            "Effective Battery Capacity (mAh)": self.effective_battery_capacity,
            "Battery Runtime (Days)": self.battery_runtime
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
        
        elif self.operating_temp >= -10:
            return float(1)
        
        else: # linear interpolation of temperature factor from Excel data
            columns = ["Operating Temperature", "Temperature Factor"]
            df = pd.read_excel("Battery Parameters Data caa 20251101.xlsx", sheet_name = "Temperature Factor", usecols=columns)
            for row in range(df.shape[0]-1):
                if self.operating_temp < df.loc[row, "Operating Temperature"] and self.operating_temp >= df.loc[row+1, "Operating Temperature"]:
                    x1, y1 = df.loc[row+1, "Operating Temperature"], df.loc[row+1,"Temperature Factor"]
                    x2, y2 = df.loc[row, "Operating Temperature"], df.loc[row,"Temperature Factor"]
                    return y1 + ((y2-y1)/(x2-x1))*(self.operating_temp-x1) 
    
    def calculate_runtime(self):
        """
        Calculates the estimated runtime of a lithium metal battery based on load, operating temperature, and 
        self-discharge rates.

        Parameters
        ----------
            None

        Output
        ------
            float: estimated battery runtime
        """

        daily_load_contribution = self.load_current * (self.load_duration_per_day/3600) # mAh
        daily_sleep_contribution = self.sleep_current * (self.sleep_duration_per_day/3600)
        
        total_daily_consumption = daily_load_contribution + daily_sleep_contribution + (self.self_discharge_rate*self.effective_battery_capacity/365)

        battery_runtime = self.effective_battery_capacity / total_daily_consumption # in days

        if battery_runtime/365 >= self.max_shelf_life:
            battery_runtime = self.max_shelf_life*365

        return battery_runtime
    
    def update_battery_properties(self):
        """
        Updates the battery's sleep duration per day, temperature factor, effective battery capacity, and runtime 
        properties.

        Parameters
        ----------
            None

        Returns
        -------
            int: returns 0 if the function executes successfully.
        """
        self._sleep_duration_per_day = 86400 - self.load_duration_per_day
        self._temperature_factor = self.calculate_temperature_factor()
        self._effective_battery_capacity = self.temperature_factor * self.battery_capacity
        self._battery_runtime = self.calculate_runtime()
        return 0

st.title("Lithium Battery Runtime Calculator")

# Collect parameters for calculation
battery_capacity = st.number_input("**Battery Capacity / mAh**", min_value=0, step=1, 
                                   help="For a bank of identical batteries, if batteries are in series, mAh capacity " \
                                   "remains the same as a single battery. If batteries are in parallel, mAh " \
                                   "capacities are added together.")
operating_temp = st.number_input("**Operating Temperature / °C**", step=0.1, format="%0.1f", help="Typical operating " \
                                "temperature range for high-quality lithium metal batteries is -40°C to 60°C.")
load_current = st.number_input("**Load Current / mA**", min_value = 0, step=1)
load_duration_per_day = st.number_input("**_Load Duration Per Day / s (Optional)_**", min_value=0, max_value=86400, 
                                        help="Defaults to 86400s.")
sleep_current = st.number_input("**_Sleep Current / mA (Optional)_**", step=1, help="Defaults to 0mA.")

# Button to initiate calculation of battery runtime
clicked = st.button("Calculate Runtime")

# Loading progress bar for calculation
# Display battery runtime results

# To display on local Streamlit server, run "streamlit run lithium_battery_runtime_app.py" in terminal

if __name__ == "__main__":
    TestBattery = Battery(16000, -35, 90, 5*48, 0.060167) 
    TestBattery.update_battery_properties()
    print(TestBattery.battery_details()) # expected battery runtime of 1260 days

    