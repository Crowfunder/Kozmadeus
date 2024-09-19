###############################################################
# by Crowfunder                                               #
# Copyright my ass but also the GPL-3.0 License               #
# Github: https://github.com/Crowfunder                       #
###############################################################

import os.path
from zipfile import ZipFile
from wget import download as DownloadFile


# Constants
RESTORE_FILENAME = 'restore.zip'
RESTORE_URL = 'https://github.com/Crowfunder/Kozmadeus/raw/main/assets/' + RESTORE_FILENAME


# Function for files restoration
# Restores both modules and templates
# Download from github and unzip
def RestoreFiles():
    if not os.path.isfile(RESTORE_FILENAME):
        DownloadFile(RESTORE_URL, bar=None, out=RESTORE_FILENAME)

    with ZipFile(RESTORE_FILENAME, 'r') as zip_file:
        zip_file.extractall()
