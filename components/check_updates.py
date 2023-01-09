###############################################################
# by Crowfunder                                               #
# Copyright my ass but also the GPL-3.0 license License       #
# Github: https://github.com/Crowfunder                       #
###############################################################

import re
import os.path
from os import remove as DeleteFile
from wget import download as DownloadFile


# Constants
VERSION_CURRENT = 'v0.0.1dev'
VERSION_FILENAME = 'VERSION'
VERSION_URL = 'https://raw.githubusercontent.com/Crowfunder/Kozmadeus/main/VERSION'


# Function that checks github for updates
# Returns version fetched from github as string
# If the fetched version is not equal 
# to VERSION_CURRENT constant, assume updates are there
def CheckUpdates():
  
  if os.path.isfile(VERSION_FILENAME):
    DeleteFile(VERSION_FILENAME)
      
  try:
    DownloadFile(VERSION_URL)
  
    with open(VERSION_FILENAME, 'r') as version_file:
      version_github = version_file.read()
      
    # Strip string out of newlines etc
    version_github = re.sub(r"[\n\t\s]*", "", version_github)
        
    print('\n\nCurrent version: ', VERSION_CURRENT)
    print('Github version : ', version_github)
        
    if version_github != VERSION_CURRENT:
      print('Updates available! \nDownload at: '
            'https://github.com/Crowfunder/Kozmadeus/releases\n')
    
  except Exception as exception:
    print('Warning: Unable to fetch updates!\n'
          'Check your internet connection.')
    print(exception)