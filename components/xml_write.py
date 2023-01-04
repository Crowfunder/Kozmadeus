###############################################################
# by Crowfunder                                               #
# Copyright my ass but also the License                       #
# Github: https://github.com/Crowfunder                       #
###############################################################
# Credits to Puzovoz, mostly based on Bootshuze               #
# https://github.com/Puzovoz/Bootshuze                        #
###############################################################
import re
import os

RESTORE_FLAIR = ('Unable to run. Please restore the '
                 'files from Options!')

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
      # Grabbed directly from Bootshuze
      print(f'[COMPONENT][INFO]: Writing output with "{template}"...')    
      regex = re.compile(r'(?:{{ )([a-zA-Z_]*)(?: }})')

      for line in i:

        if any(f'{{ {arg} }}' in line for arg in args.keys()):
          line = regex.sub(args[regex.search(line).group(1)], line)

        o.write(line)
    print(f'[COMPONENT][INFO]: Finished writing to "{o.name}"')

  except FileNotFoundError:
    print(f'[COMPONENT][ERROR]: Template files not found!\n{RESTORE_FLAIR}')