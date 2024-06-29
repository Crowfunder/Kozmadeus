###############################################################
# by Crowfunder                                               #
# Copyright my ass but also the GPL-3.0 License               #
# Github: https://github.com/Crowfunder                       #
###############################################################

# External Imports
import gc

# Internal Imports
from components.check_updates import CheckUpdates
from components.check_updates import VERSION_CURRENT
from components.restore_files import RestoreFiles
from components.logger        import LoggerInit
from components.logger        import SEPARATOR
from components.xml_write     import ExportXML
from components.module_import import ProcessModules
from components.module_import import ModuleData
from components.module_import import FILE_TYPES_LIST


def Main(file_names, template, no_export_file, strip_armature_tree):

  # Initiate Logger
  logger_filename = 'kozmadeus.log'
  logger = LoggerInit(logger_filename)
  print(f'''[MAIN][INFO]: Kozmadeus version: "{VERSION_CURRENT}"''')
  
  def LoggerCloser():
    nonlocal logger
    nonlocal logger_filename
    logger.close()
    print(f'Finished logging to "{logger_filename}"')
    print(SEPARATOR)
    

  for file_name in file_names:

    try:

      print(fr'''[MAIN][INFO]: Processing: "{file_name}"...''')
      
      Extract, module_data = ProcessModules(file_name)
      print(f'''[MAIN][INFO]: Using "{module_data['Name']}" module.''')
      geometries = Extract(file_name)
      print('[MAIN][INFO]: Finished extracting the model data.')

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
          try:
            ExportXML(file_name, template, args)

          except FileNotFoundError:
            print('[COMPONENT][ERROR]: Template files not found! '
                  'Attempting to restore the files from Options...')
            RestoreFiles()
            print('[MAIN][INFO]: Retrying to write to XML...')
            ExportXML(file_name, template, args)
          
        # Restore the old template
        template = template_old
        
      if no_export_file:
        # Close the logger so it doesn't log the file contents!
        LoggerCloser()
        return geometries

      del geometries
      gc.collect()
      print(SEPARATOR)

    except:
      logger.log_exception()
      LoggerCloser()
      raise
    
  # Putting it solely into "finally" won't work
  # Simply because it executes before except
  LoggerCloser()
