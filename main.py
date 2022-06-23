import re
import gc
import zipfile
import modules
import os.path
from zipfile import ZipFile
from os import remove as delete_file
from wget import download as download_file


version_number = "v0.0.1dev"
separator = ('---------------------------------'
             '------------------------------')

def cli_menu():
  # to be added
  pass


def templates_download():

  # Let's make the filename dynamic in case the name ever gets changed
  dl_url = "https://github.com/Crowfunder/Kozmadeus/raw/main/assets/templates.zip"
  dl_filename = dl_url.split('/')[-1]
  download_file(url)

  with ZipFile("templates.zip", 'r') as zip_file:
    zip_file.extractall()

  delete_file(dl_filename)



def export_xml(file_name, template, args):

  with open(f"{file_name}.xml", 'w+') as o, \
       open(f"templates/{template}", 'r') as i:

    print(f'Writing output with {template}...')    
    regex = re.compile(r'(?:{{ )([a-zA-Z_]*)(?: }})')

    for line in i:

      if any(f'{{ {arg} }}' in line for arg in args.keys()):
        line = regex.sub(args[regex.search(line).group(1)], line)

      o.write(line)
    print(f'Finished writing to {o.name}.')


# Output the appropriate model data extract function
def process_modules(file_name):

  file_extension = file_name.split('.')[-1]

  # "__modules__" is a dict of all modules' names and objects
  # Refer to "modules/__init__.py" for relevant code. 
  if file_extension in modules.__modules__.keys():

    extract_module = modules.__modules__[file_extension]
    return extract_module.extract

  else:

    raise Exception("Error: Unrecognized file type!")



def main(file, file_name, template, export_to_file):

  extract = process_modules(file_name)
  args = extract(file_name)

  # If the model has bones, swap the template
  # Needs a handle for animations (?)
  if args["bones"] != "":
    template = template + "_bones"

  if export_to_file:
    export_xml(file_name, template, args)
  
  else:
    return args


if __name__ == '__main__':

  if not os.path.isfile('templates/template_articulated'):
    if not os.path.isfile('templates/template_static'):
      try:
        print('Downloading template files...')
        templates_download()
        cli_menu()

      except:
        print("Template files are missing, make " 
              "sure they are in the same directory "
              "as this script and start again.")  
        quit()

