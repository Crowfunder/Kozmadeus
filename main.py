import re
import gc
import os.path
from os import mkdir as mkdir
from wget import download as download_file
import modules

version_number = "v0.0.1dev"
separator = ('---------------------------------'
             '------------------------------')

def cli_menu():
  # to be added
  pass

# There must be a better way to resolve this 
# than 3 separate download url's
def templates_download():

  dl_urls = [
    "https://raw.githubusercontent.com/Crowfunder/Kozmadeus/master/templates/template_articulated",
    "https://raw.githubusercontent.com/Crowfunder/Kozmadeus/master/templates/template_static",
    "https://raw.githubusercontent.com/Crowfunder/Kozmadeus/master/templates/template_animation"
  ]

  if not os.path.isdir("templates") == True:
    mkdir("templates")

  for url in dl_urls:
    download_file(url, out = "templates/") 



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

  file_extension = file_name.split(".")[-1]

  # "__modules__" is a dict of all modules' names and objects
  # Refer to "modules/__init__.py" for relevant code. 
  if file_extension in modules.__modules__.keys():

    extract_module = modules.__modules__[file_extension]
    return extract_module.extract

  else:

    raise Exception("Error: Unrecognized file type!")



def main(file, file_name, template):

  extract = process_modules(file_name)
  args = extract(file_name)

  # If the model has bones, swap the template
  # Needs a handle for animations (?)
  if args["bones"] != "":
    template = template + "_bones"


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

