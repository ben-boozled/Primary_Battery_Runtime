# Description
This repository contains the code for a primary battery runtime calculator that estimates the runtime of lithium metal and alkaline batteries. Feel free to try out the calculator application [here](https://primary-battery-runtime.streamlit.app/). 

# Running Locally
If you are interested in running the application locally, I recommend first creating a Python virual environment. 

Open the command line and follow the steps below:
1. Change the working directory to the location where you want to clone the repository.
2. Clone the respository.
'''
git clone https://github.com/ben-boozled/Primary_Battery_Runtime.git
'''
3. Change the working directory to 'Primary_Battery_Runtime/'.
'''
cd Primary_Battery_Runtime
'''
4. Create a virtual environment.
'''
python -m venv <name of virtual environment>
'''
5. Activate the virtual environment. 
'''
<name of virtual environment>\Scripts\activate
'''
6. Install the necessary dependencies in the 'requirements.txt' file.
'''
pip install -r requirements.txt
'''
7. Run the app locally (a browser window will automatically open to host the application).
'''
streamlit run battery_runtime_app.py
'''

To deactivate virtual environment, Enter 'deactivate' into the command line.
