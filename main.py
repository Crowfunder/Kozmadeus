import re
import gc
import zipfile
import modules
import os.path
from zipfile import ZipFile
from os import makedirs as MakeDirs
from wget import download as DownloadFile


version_number = 'v0.0.1dev'
restore_flair = ('Unable to run. Please restore the '
                'files from Options!')
separator = ('---------------------------------'
             '------------------------------')

def CliMenu():
  # to be added
  pass

def TemplatesDownload():

  # Let's make the filename dynamic in case the name ever gets changed
  dl_url = 'https://github.com/Crowfunder/Kozmadeus/raw/main/assets/templates.zip'
  dl_filename = dl_url.split('/')[-1]
  
  if not os.path.isfile(dl_filename)
    print('Downloading template files...')
    DownloadFile(dl_url)

  print('Unpacking...')
  with ZipFile('templates.zip', 'r') as zip_file:
    zip_file.extractall()



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
    print(f'ERROR: Template files not found!\n{restore_flair}')


# Output the appropriate model data Extract function
def ProcessModules(file_name):

  file_extension = file_name.split('.')[-1]

  # "__modules__" is a dict of all modules' names and objects
  # Refer to "modules/__init__.py" for relevant code. 
  if file_extension in modules.__modules__.keys():

    extract_module = modules.__modules__[file_extension]
    return extract_module.Extract

  else:

    raise Exception('Error: Unrecognized file type!')



def Main(file_names, template, export_to_files):

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

      if export_to_files:
        ExportXML(file_name, template, args)
        
        del args
        gc.collect()
    
      else:

        # Gotta add a gc.collect() handle when done
        return args

  except AttributeError:

    print(f'ERROR: Module not found or corrupted!\n{restore_flair}')

  print(separator)


if __name__ == '__main__':

  CliMenu()
