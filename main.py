import re
import gc
import os.path
from os import mkdir as mkdir
from wget import download as download_file
from modules import *

separator = ('---------------------------------'
             '------------------------------')

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



if __name__ == '__main__':

  if not os.path.isfile('templates/template_articulated'):
    if not os.path.isfile('templates/template_static'):
      try:
        print('Downloading template files...')
        templates_download()

      except:
        print("Template files are missing, make " 
              "sure they are in the same directory "
              "as this script and start again.")  
        quit()

