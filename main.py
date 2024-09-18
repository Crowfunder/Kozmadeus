###############################################################
# by Crowfunder                                               #
# Copyright my ass but also the GPL-3.0 License               #
# Github: https://github.com/Crowfunder                       #
###############################################################

# External Imports
import gc

# Internal Imports
from utils.check_updates      import VERSION_CURRENT
from utils.check_updates      import CheckUpdates
from utils.restore_files      import RestoreFiles
from utils.logger             import GetLogger
from utils.logger             import InitRootLogger
from utils.logger             import SEPARATOR
from utils.logger             import LOGGING_FILE
from components.xml_write     import ExportXML
from components.module_import import ProcessModules
from components.module_import import ModuleData
from components.module_import import FILE_TYPES_LIST
from components.model         import SetModelType


def Main(file_names, mode, no_export_file, strip_armature_tree):

    # Initiate Logger
    InitRootLogger()
    logger = GetLogger()

    for file_name in file_names:

        try:
            logger.info('Processing: "%s"...', file_name)

            Extract, module_data = ProcessModules(file_name)
            logger.debug('Using "%s" module.', module_data["Name"])
            geometries = Extract(file_name)
            logger.info('Finished extracting the model data.')

            for model in geometries:

                logger.debug('Converting model to "%s" mode...', mode)
                model = SetModelType(model, mode)

                # Option necessary for importing armors.
                # Erases "bones" tag to fix armor armature
                # conflicting with pc model armature.
                if strip_armature_tree:
                    logger.debug('Stripped armature data.')
                    model.armature = None

                # Set template to model geometry template
                template = 'template_model'
                logger.info('Writing model data to xml...')

                if not no_export_file:
                    try:
                        ExportXML(file_name, template, model.toargs())

                    except FileNotFoundError:
                        logger.error('Template files not found! '
                                     'Attempting to restore the files from Options...')
                        RestoreFiles()
                        logger.info('Retrying to write to XML...')
                        ExportXML(file_name, template, model.toargs())

            if no_export_file:
                return geometries

            del geometries
            gc.collect()
            logger.info(SEPARATOR)

        except:
            logger.exception('Unhandled exception ocurred!')
            raise

        finally:
            logger.info('Finished logging to "%s"', LOGGING_FILE)
            logger.info(SEPARATOR)
