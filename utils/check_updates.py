###############################################################
# by Crowfunder                                               #
# Copyright my ass but also the GPL-3.0 License               #
# Github: https://github.com/Crowfunder                       #
###############################################################

import re
import os.path
from os import remove as DeleteFile
from wget import download as DownloadFile


# Constants
VERSION_CURRENT = 'v0.1.0beta'
VERSION_FILENAME = 'VERSION'
VERSION_URL = 'https://raw.githubusercontent.com/Crowfunder/Kozmadeus/main/VERSION'

# Function that checks github for updates
# Returns dict containing version fetched from github and current
# version as string, the rest of the logic is to be handled by UI
def CheckUpdates():

  # Special file handle for disabling update check
  if os.path.isfile('UPDATER_DISABLE'):
    output_version = dict()
    output_version['current'] = VERSION_CURRENT
    output_version['fetched'] = VERSION_CURRENT
    return output_version

  # Delete leftover VERSION file if there is any
  if os.path.isfile(VERSION_FILENAME):
    DeleteFile(VERSION_FILENAME)

  DownloadFile(VERSION_URL, bar=None, out=VERSION_FILENAME)
  with open(VERSION_FILENAME, 'r') as version_file:
    version_github = version_file.read()
    
  # Strip string out of newlines etc
  version_github = re.sub(r"[\n\t\s]*", "", version_github)
  
  # Form output dict
  output_version = dict()
  output_version['current'] = VERSION_CURRENT
  output_version['fetched'] = version_github

  return output_version
