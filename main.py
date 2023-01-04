# External Imports
import re
import gc
import os
import os.path

# Internal Imports
import modules
from components.check_updates import CheckUpdates
from components.check_updates import VERSION_CURRENT
from components.restore_files import RestoreFiles
from components.logger        import LoggerInit


# Defining few necessary consts
RESTORE_FLAIR = ('Unable to run. Please restore the '
                 'files from Options!')
SEPARATOR = ('---------------------------------'
             '---------------------------------'
             '--------------')


# Retrieve a list of file types based on the modules.
# '__modules__' is a dict of all modules' names and objects
# Refer to 'modules/__init__.py' for relevant code. 
FILE_TYPES_LIST = [] 
for extension in modules.__modules__.keys():
  extension = '*.' + extension
  file_type_part = ('Model', extension)
  FILE_TYPES_LIST.append(file_type_part)


# Function that outputs module data
def ModuleData():
  
  print('List of installed modules:\n')
  print(SEPARATOR[0:29])
  
  for module_name in modules.__modules__:
    
    module = modules.__modules__[module_name]
    data = module.module_data
    
    for key in data:
      print(f'{key} : {data[key]}')
      
    print(SEPARATOR[0:29])
    
  print('Remember not to install any untrustworthy '
        'modules!\nThey pose real danger!')


# Output the appropriate model data Extract function
def ProcessModules(file_name):

  file_extension = file_name.split('.')[-1]

  # "__modules__" is a dict of all modules' names and objects
  # Refer to "modules/__init__.py" for relevant code
  if file_extension in modules.__modules__.keys():

    extract_module = modules.__modules__[file_extension]
    return extract_module.Extract, extract_module.module_data

  else:

    raise Exception('Unrecognized file type!')


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
      print(f'[MAIN][INFO]: Writing output with "{template}"...')    
      regex = re.compile(r'(?:{{ )([a-zA-Z_]*)(?: }})')

      for line in i:

        if any(f'{{ {arg} }}' in line for arg in args.keys()):
          line = regex.sub(args[regex.search(line).group(1)], line)

        o.write(line)
    print(f'[MAIN][INFO]: Finished writing to "{o.name}"')

  except FileNotFoundError:
    print(f'[MAIN][ERROR]: Template files not found!\n{RESTORE_FLAIR}')


def Main(file_names, template, no_export_file, strip_armature_tree):

  if not modules.__modules__:
    raise Exception(f'No modules found.')

  # Initiate Logger
  logger = LoggerInit()

  for file_name in file_names:

    try:

      print(fr'''[MAIN][INFO]: Processing: "{file_name}"...''')
      
      Extract, module_data = ProcessModules(file_name)
      print(f'''[MAIN][INFO]: Using "{module_data['Name']}" module.''')
      geometries = Extract(file_name)

      for args in geometries:
        
        # If the model has bones, swap the template
        template_old = template
        if args['bones'] != '':
          template += '_bones'

          # Option necessary for importing armors.
          # Erases "bones" tag to fix armor armature
          # conflicting with pc model armature.
          # Also, there needs to be just any value 
          # in the tag, or SK xml parser will commit die
          # instantly with little to no elaboration.
          if strip_armature_tree:
            print('[MAIN][INFO]: Stripped armature tree data.')
            args['bone_tree'] = ' '

        if not no_export_file:
          ExportXML(file_name, template, args)
          
        # Restore the old template
        template = template_old
        
      if no_export_file:
        return geometries

      del geometries
      gc.collect()
      print(SEPARATOR)

    except Exception as e:
      logger.log_exception()
      logger.close()
      raise
    
  # Putting it solely into "finally" won't work
  # Simply because it executes before except
  logger.close()