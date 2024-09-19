###############################################################
# by Crowfunder                                               #
# Copyright my ass but also the GPL-3.0 License               #
# Github: https://github.com/Crowfunder                       #
###############################################################

import modules
from components.logger import SEPARATOR

# Retrieve a list of file types based on the modules.
# '__modules__' is a dict of all modules' names and objects
# Refer to 'modules/__init__.py' for relevant code. 
FILE_TYPES_LIST = [] 
for extension in modules.__modules__.keys():
    extension = '*.' + extension
    file_type_part = ('Model', extension)
    FILE_TYPES_LIST.append(file_type_part)

if not modules.__modules__:
    raise Exception(f'No modules found.')


# Function that outputs module data
def ModuleData():
    """
    Prints the list of installed modules and their module data.
    """
    print('List of installed modules:\n')
  
    for module_name in modules.__modules__:
        module = modules.__modules__[module_name]
        data = module.module_data
  
        print(SEPARATOR[0:29])
        for key in data:
            # Do something with the module data
            print(f'{key} : {data[key]}')


def ProcessModules(file_name):
    """
    Process the modules based on the file extension.

    Args:
        file_name (str): The name of the file.

    Returns:
        tuple: A tuple containing the extract function and module data.

    Raises:
        Exception: If the file type is unrecognized.

    """
    file_extension = file_name.split('.')[-1]

    # "__modules__" is a dict of all modules' names and objects
    # Refer to "modules/__init__.py" for relevant code
    if file_extension in modules.__modules__.keys():
        extract_module = modules.__modules__[file_extension]
        return extract_module.Extract, extract_module.module_data
    else:
        raise Exception('Unrecognized file type!')
