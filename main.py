import re
import gc
import modules
import os.path
import argparse
from zipfile import ZipFile
from os import remove as DeleteFile
from os import makedirs as MakeDirs
from wget import download as DownloadFile

# Defining few necessary consts
version_current = 'v0.0.1dev'
restore_flair = ('Unable to run. Please restore the '
                'files from Options!')
separator = ('---------------------------------'
             '------------------------------')

# Function that checks github for updates
# Returns version fetched from github as string
def CheckUpdates():
  
  version_url = 'https://raw.githubusercontent.com/Crowfunder/Kozmadeus/main/VERSION'
  version_filename = 'VERSION'
  
  if os.path.isfile(version_filename):
    DeleteFile(version_filename)
      
  DownloadFile(version_url)
  
  with open(version_filename, 'r') as version_file:
    return version_file.read()


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

  except:
    print('Error: Unable to download!\n'
          'Check your internet connection.')



def ExportXML(file_name, template, args):

  try:

    # Trim out the extension and add an appropriate one
    export_file = file_name.rsplit('.', 1)[0] + '.xml'

    # In case a file with the same name exists
    # patch up a new file name.
    file_number = 1
    old_name = export_file
    while os.path.isfile(export_file):
      export_file = f'({file_number})' + old_name
      file_number += 1

    # Assure the output dir exists
    MakeDirs('output', exist_ok=True)
    with open(f'output/{export_file}', 'w+') as o, \
         open(f'templates/{template}', 'r') as i:

      # Write to output file using regex substitution
      print(f'Writing output with {template}...')    
      regex = re.compile(r'(?:{{ )([a-zA-Z_]*)(?: }})')

      for line in i:

        if any(f'{{ {arg} }}' in line for arg in args.keys()):
          line = regex.sub(args[regex.search(line).group(1)], line)

        o.write(line)
    print(f'Finished writing to output/{o.name}.')

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

    raise Exception('Error: Unrecognized file type!')



def Main(file_names, template, no_export_file):

  if modules.__modules__ == {}:
    raise Exception(f'Error: No modules found!\n{restore_flair}')

  try:

    for file_name in file_names:
    
      print(fr'''Processing "{file_name}"...''')
      Extract = ProcessModules(file_name)
      args = Extract(file_name)

      # If the model has bones, swap the template
      # Needs a handle for animations (?)
      if args['bones'] != '':
        template += '_bones'

      else:
        del args['bones']

      if not no_export_file:
        ExportXML(file_name, template, args)
        
        del args
        gc.collect()
    
      else:

        return args

  except AttributeError:

    print(f'ERROR: Module not found or corrupted!\n{restore_flair}')

  print(separator)

# Command Line Interface, invoked if main is invoked 
# instead of gui.
def CliMenu():

  # Defining argparse args
  # A similar mess to that of GUI defining
  # can't be helped I guess
  parser = argparse.ArgumentParser(description=('Converts models to '
                                                'Spiral Knights XML.'),
                                   formatter_class=argparse.RawTextHelpFormatter,
                                   epilog=('Script written with love by Crowfunder\n'
                                           'Credits: Puzovoz, XanTheDragon, '
                                           'Kirbeh \nGithub: '
                                           'https://github.com/Crowfunder/Kozmadeus'))
  
  parser.add_argument('files_list', nargs='+',
                      help='<Required> Input the files to process')
  parser.add_argument('-t', '--type', choices=['articulated', 'static'],
                      default='articulated', help='Output model type choice')
  parser.add_argument('--no-file', action='store_true',
                      help='Output raw data, no write to xml files')
  parser.add_argument('--restore-files', action='store_true',
                      help='Restore modules and templates on start')
  parser.add_argument('--skip-update', action='store_true', 
                      help='Skips update check on start')
  
  parser_args = parser.parse_args()
  
  # Make use of argparse args
  if parser_args.restore_files:
    RestoreFiles()
    
  # Check for updates
  if not parser_args.skip_update:
    try:
      print(separator)
      version_github = CheckUpdates()
      
      print('Current version: ', version_current)
      print('Github version : ', version_github)
      
      if version_github != version_current:
        print('Updates available! \nDownload at: '
              'https://github.com/Crowfunder/Kozmadeus/releases\n')
        print(separator)
    
    except:
      print('Warning: Unable to fetch updates!\n'
            'Check your internet connection.')
    
  template = 'template_' + parser_args.type
  
  Main(parser_args.file_names, template, parser_args.no_file)
  

if __name__ == '__main__':

  CliMenu()
