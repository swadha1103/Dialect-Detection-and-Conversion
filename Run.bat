@echo off
REM Navigate to the directory containing app.py
cd C:\Users\HP\Desktop\Project

REM Set up the Python environment (if necessary, e.g., for virtual environments)
REM You can uncomment the following line if you are using a virtual environment
REM call C:\path\to\your\virtualenv\Scripts\activate

REM Install necessary Python packages (Uncomment if needed)
REM pip install -r requirements.txt

REM Run the Flask app
start python app.py

REM Wait for Flask to start up (optional, if necessary)
timeout /t 5

REM Open the Flask URL in a browser
start http://127.0.0.1:5000

REM Exit the script
exit
