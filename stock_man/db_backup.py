import pyodbc
import schedule
import time
import os
import pandas as pd
from datetime import datetime
from imp_info import DATABASE_PWD,DB_NAME,DB_PATH,DB_SERVER,DATABASE_UID
import zipfile
from pathlib import Path



def take_backup():
    # Connection parameters
    server =DB_SERVER
    database = DB_NAME
    username = DATABASE_UID
    password = DATABASE_PWD

    # Backup directory
    backup_dir = DB_PATH

    # Create a connection object
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    conn.autocommit = True
    # Create a cursor object
    cursor = conn.cursor()

    # Backup file name
    backup_file = database+'_backup_' + str(datetime.now().strftime('%Y%m%d_%H%M%S')) + '.bak'

    # Backup command
    backup_command = 'BACKUP DATABASE '+ database +' TO DISK=\'' + os.path.join(backup_dir, backup_file) + '\''

    # Execute the backup command
    cursor.execute(backup_command)
    conn.autocommit = False
    # Backup details
    backup_details = {'database': [database], 'backup_file': [backup_file], 'backup_datetime': [datetime.now()]}

    # Create a DataFrame object from the backup details
    backup_df = pd.DataFrame(data=backup_details)

    # Backup details file
    backup_details_file = os.path.join(backup_dir, 'backup_details.csv')

    # Write backup details to a CSV file
    backup_df.to_csv(backup_details_file, index=False)
def take_photo_backup():
        # Specify the name of the zip file you want to create
    zip_filename = DB_PATH+'\\Photo_backup_' + str(datetime.now().strftime('%Y%m%d_%H%M%S')) + '.zip'
    BASE_DIR = Path(__file__).resolve().parent.parent
    # Specify the directory you want to zip
    directories_to_zip =[str(BASE_DIR)+"\\mysite\\static\\pdfs",str(BASE_DIR)+"\\mysite\\static\\img"]

    # Create a ZipFile object in write mode
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for directory_to_zip in directories_to_zip:
            # Add the entire directory and its contents to the zip file
            for foldername, subfolders, filenames in os.walk(directory_to_zip):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    zipf.write(file_path, os.path.relpath(file_path, directory_to_zip))

schedule.every().day.at("00:00").do(take_backup)
schedule.every().day.at("00:00").do(take_photo_backup)
while True:
    schedule.run_pending()
    time.sleep(1)
