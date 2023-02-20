###############################################################
# by Crowfunder                                               #
# Copyright my ass but also the GPL-3.0 License               #
# Github: https://github.com/Crowfunder                       #
###############################################################

import os.path
from zipfile import ZipFile
from wget import download as DownloadFile


# Constants
RESTORE_URL = 'https://github.com/Crowfunder/Kozmadeus/raw/main/assets/restore.zip'
RESTORE_FILENAME = 'restore.zip'


# Function for files restoration
# Restores both modules and templates
# Download from github and unzip
def RestoreFiles():
    
  try:
    if not os.path.isfile(RESTORE_FILENAME):
      print('Downloading files...')
      DownloadFile(RESTORE_URL)
      
    print('Unpacking...')
    with ZipFile(RESTORE_FILENAME, 'r') as zip_file:
      zip_file.extractall()
      print('Success! Files restored.')

  except:
    print('Error: Unable to download!\n'
          'Check your internet connection.')
    raise