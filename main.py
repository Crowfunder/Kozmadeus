import re
import gc
import sys
import os
import os.path
import argparse
from zipfile import ZipFile
from os import remove as DeleteFile
from wget import download as DownloadFile

import modules

# Defining few necessary consts
version_current = 'v0.0.1dev'
restore_flair = ('Unable to run. Please restore the '
                'files from Options!')
separator = ('---------------------------------'
             '---------------------------------'
             '--------------')

# Retrieve a list of file types based on the modules.
# '__modules__' is a dict of all modules' names and objects
# Refer to 'modules/__init__.py' for relevant code. 
file_types_list = [] 
for extension in modules.__modules__.keys():
  extension = '*.' + extension
  file_type_part = ('Model', extension)
  file_types_list.append(file_type_part)

# Function that outputs module data
def ModuleData():
  
  print('List of installed modules:\n')
  print(separator[0:29])
  
  for module_name in modules.__modules__:
    
    module = modules.__modules__[module_name]
    data = module.module_data
    
    for key in data:
      print(f'{key} : {data[key]}')
      
    print(separator[0:29])
    
  print('Remember not to install any untrustworthy '
        'modules!\nThey pose real danger!')

# Function that checks github for updates
# Returns version fetched from github as string
def CheckUpdates():
  
  version_url = 'https://raw.githubusercontent.com/Crowfunder/Kozmadeus/main/VERSION'
  version_filename = 'VERSION'
  
  if os.path.isfile(version_filename):
    DeleteFile(version_filename)
      
  try:
    DownloadFile(version_url)
  
    with open(version_filename, 'r') as version_file:
      version_github = version_file.read()
      
    # Strip string out of newlines etc
    version_github = re.sub(r"[\n\t\s]*", "", version_github)
        
    print('\n\nCurrent version: ', version_current)
    print('Github version : ', version_github)
        
    if version_github != version_current:
      print('Updates available! \nDownload at: '
            'https://github.com/Crowfunder/Kozmadeus/releases\n')
    
  except Exception as exception:
    print('Warning: Unable to fetch updates!\n'
          'Check your internet connection.')
    print(exception)


# Function for files restoration
# Restores both modules and templates
# Download from github and unzip
def RestoreFiles():

  restore_url = 'https://github.com/Crowfunder/Kozmadeus/raw/main/assets/restore.zip'
  restore_filename = 'restore.zip'
    
  try:
    if not os.path.isfile(restore_filename):
      print('Downloading files...')
      DownloadFile(restore_url)
      
    print('Unpacking...')
    with ZipFile(restore_filename, 'r') as zip_file:
      zip_file.extractall()
      print('Success! Files restored.')

  except Exception as exception:
    print('Error: Unable to download!\n'
          'Check your internet connection.')
    print(exception)


# Export args data to the output file
# Based on the selected template
def ExportXML(file_name, template, args):

  try:

    # Trim out the extension and add an appropriate one
    export_file = file_name.rsplit('.', 1)[0] + '.xml'

    # In case a file with the same name exists
    # patch up a new file name.
    file_number = 1
    while os.path.isfile(export_file):
      export_file = file_name.rsplit('.', 1)[0] + f'({file_number})' + '.xml'
      file_number += 1

    # Assure the output dir exists
    with open(f'{export_file}', 'w+') as o, \
         open(f'templates/{template}', 'r') as i:

      # Write to output file using regex substitution
      print(f'Writing output with "{template}"...')    
      regex = re.compile(r'(?:{{ )([a-zA-Z_]*)(?: }})')

      for line in i:

        if any(f'{{ {arg} }}' in line for arg in args.keys()):
          line = regex.sub(args[regex.search(line).group(1)], line)

        o.write(line)
    print(f'Finished writing to "{o.name}"')

  except FileNotFoundError:
    print(f'Error: Template files not found!\n{restore_flair}')


# Output the appropriate model data Extract function
def ProcessModules(file_name):

  file_extension = file_name.split('.')[-1]

  # "__modules__" is a dict of all modules' names and objects
  # Refer to "modules/__init__.py" for relevant code
  if file_extension in modules.__modules__.keys():

    extract_module = modules.__modules__[file_extension]
    return extract_module.Extract

  else:

    raise Exception('Unrecognized file type!')



def Main(file_names, template, no_export_file):

  if not modules.__modules__:
    raise Exception(f'No modules found!\n{restore_flair}')

  for file_name in file_names:
  
    print(fr'''Processing "{file_name}"...''')
    Extract = ProcessModules(file_name)
    geometries = Extract(file_name)

    for args in geometries:
      
      # If the model has bones, swap the template
      template_old = template
      if args['bones'] != '':
        template += '_bones'

      if not no_export_file:
        ExportXML(file_name, template, args)
        
      # Restore the old template
      template = template_old
      
    if no_export_file:
      return geometries

    del geometries
    gc.collect()
    print(separator)




# Command Line Interface, invoked if main is invoked 
# instead of gui.
def CliMenu():

  # Class for disabling the output log
  # strictly for --silent option
  # Source: https://stackoverflow.com/questions/8391411/how-to-block-calls-to-print
  class HiddenPrints:
      def __init__(self, silent):
        self.silent = silent

      def __enter__(self):
          if self.silent:
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

      def __exit__(self, exc_type, exc_val, exc_tb):
          if self.silent:
            sys.stdout.close()
            sys.stdout = self._original_stdout

  # Custom action for listing modules
  # Source: https://stackoverflow.com/questions/34352405/python-argparse-help-like-option
  class modules_action(argparse.Action):
    def __init__(self,
                 option_strings,
                 dest=argparse.SUPPRESS,
                 default=argparse.SUPPRESS,
                 help=None):
        super(modules_action, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        ModuleData()
        parser.exit()

  # Defining argparse args
  # A similar mess to that of GUI defining
  # can't be helped I guess
  parser = argparse.ArgumentParser(description=('Converts models to '
                                                'Spiral Knights XML.'),
                                   formatter_class=argparse.RawTextHelpFormatter,
                                   epilog=('Script written with love by Crowfunder\n'
                                           f'Version: {version_current}\n'
                                           'Credits: Puzovoz, XanTheDragon, '
                                           'Kirbeh \nGithub: '
                                           'https://github.com/Crowfunder/Kozmadeus'))
  
  parser.add_argument('files_list', nargs='+',
                      help='<Required> Input the files to process')
  parser.add_argument('-t', '--type', choices=['articulated', 'static'],
                      default='articulated', help='Output model type choice')
  parser.add_argument('-s', '--silent', action='store_true',
                      help='Disable all command line messages\n'
                           'Note: Does not apply for unhandled exceptions')
  parser.add_argument('--no-file', action='store_true',
                      help='Output raw data, no write to xml files\n'
                            'This argument also implies --silent')
  parser.add_argument('--restore-files', action='store_true',
                      help='Restore templates on start')
  parser.add_argument('--skip-update', action='store_true', 
                      help='Skip update check on start')
  parser.add_argument('--modules-list', action=modules_action, 
                      help='List all installed modules')
  
  parser_args = parser.parse_args()
  
  # --no-file implies --silent by default
  if parser_args.no_file:
    parser_args.silent = True

  with HiddenPrints(parser_args.silent):

    # Make use of argparse args
    # Restore files
    if parser_args.restore_files:
      RestoreFiles()
      print(separator)
      
    # Check for updates
    if not parser_args.skip_update:
      CheckUpdates()
      print(separator)

    template = 'template_' + parser_args.type
    geometry = Main(parser_args.files_list, template, parser_args.no_file)

  if parser_args.no_file:
    print(geometry)
  

if __name__ == '__main__':

  CliMenu()
