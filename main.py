###############################################################
# by Crowfunder                                               #
# Copyright my ass but also the GPL-3.0 License               #
# Github: https://github.com/Crowfunder                       #
###############################################################

# External Imports
import gc
import os.path

# Internal Imports
import modules
from components.check_updates import CheckUpdates
from components.check_updates import VERSION_CURRENT
from components.restore_files import RestoreFiles
from components.logger        import LoggerInit
from components.logger        import SEPARATOR
from components.xml_write     import ExportXML


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
