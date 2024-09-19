###############################################################
# by Crowfunder                                               #
# Copyright my ass but also the GPL-3.0 License               #
# Github: https://github.com/Crowfunder                       #
###############################################################

# External Imports
import gc
from dataclasses import dataclass

# Internal Imports
from components.check_updates      import VERSION_CURRENT
from components.check_updates      import CheckUpdates
from components.restore_files      import RestoreFiles
from components.logger             import GetLogger
from components.logger             import EndLogging
from components.logger             import InitRootLogger
from components.logger             import SEPARATOR
from components.logger             import LOGGING_FILE
from components.xml_write          import ExportXML
from components.module_import      import ProcessModules
from components.module_import      import ModuleData
from components.module_import      import FILE_TYPES_LIST
from schema.model                  import SetModelType
from schema.model                  import Model


@dataclass
class Settings:
    file_names: list[str]
    model_mode: str = 'articulated'
    no_export_file: bool = False
    strip_armature_tree: bool = False


def Main(settings: Settings):

    InitRootLogger()
    logger = GetLogger()
    for file_name in settings.file_names:

        try:
            logger.info('Processing: "%s"...', file_name)

            Extract, module_data = ProcessModules(file_name)
            logger.debug('Using "%s" module.', module_data["Name"])
            exportables_list = Extract(file_name)
            logger.info('Finished extracting the model data.')

            for exportable in exportables_list:

                if isinstance(exportable, Model):
                    logger.debug('Converting model to "%s" mode...', settings.model_mode)
                    model = SetModelType(exportable, settings.model_mode)

                    # Option necessary for importing armors.
                    # Erases "bones" tag to fix armor armature
                    # conflicting with pc model armature.
                    if settings.strip_armature_tree:
                        logger.debug('Stripped armature data.')
                        model.armature = None

                    # Set template to model geometry template
                    template = 'template_model'

                else:
                    raise Exception(f'Unknown exportable type: {type(exportable)}')

                if not settings.no_export_file:
                    try:
                        logger.info('Writing model data to xml...')
                        ExportXML(file_name, template, exportable.toargs())

                    except FileNotFoundError:
                        logger.error('Template files not found! '
                                     'Attempting to restore the files from Options...')
                        RestoreFiles()
                        logger.info('Retrying to write to XML...')
                        ExportXML(file_name, template, exportable.toargs())

            if settings.no_export_file:
                return exportables_list

            del exportables_list
            gc.collect()
            logger.info(SEPARATOR)

        except:
            logger.exception('Unhandled exception ocurred!')
            raise

        finally:
            EndLogging()
