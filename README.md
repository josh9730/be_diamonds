# Description
This program accepts a CSV input and uploads to the Diamond Smartsheet.

# How to Run the Program
1. Upload the latest CSV to the `INPUTS` folder
    - Simply drag and drop the CSV file to folder
1. Click `Run` at the top of the window
1. On the right side, a window labeled `Console` will open and display a user interface. This is where all inputs will be done.
   - You may need to click on the `Console` tab if it is not already selected
1. The first input is the Smartsheet name. This value is saved between sessions, verify that it is correct and edit if needed
   - **IMPORTANT**: If the script fails, the first thing to check is that the value here matches Smartsheet!
1. The second Input is to input the new CSV
   - Click the 'Recent' button to find the most recent CSV
   - You can also select 'Browse', which will open a file browser to select the CSV
   - Finally, you can simply edit the field with the CSV name
1. The final prompt will ask for the date. This is used for the 'child' rows under each vendor
   - Click 'Today' if you wish to use today's date
   - Otherwise, input your own date
1. Click 'Submit' once you're ready
   - A pop-up window will display a waiting status
   - Once complete, a final window will show any new vendors added along with confirmation that the data was uploaded

Lastly, note that the CSV files are renamed automatically to be in `YYYY-MM-DD.csv` format for future reference. 

# Troubleshooting
The most common issues will be due to changes in sheet or column names in the Smartsheet. These values are stored in `src/constants.py`. Edit these as needed (The **right-side values only**).

For any issues that are encountered, please contact Mickey Avila for help.

**DO NOT MAKE ANY CHANGES TO ANY OTHER FILES OR FOLDERS IN THIS PROGRAM**