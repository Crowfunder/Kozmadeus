# A workaround to get all modules recursively imported
# and a dictionary of modules' names + objects. 
#
# Source:  
# https://stackoverflow.com/questions/3365740/how-to-import-all-submodules

import pkgutil

__modules__ = {}
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    _module = loader.find_module(module_name).load_module(module_name)
    __modules__[module_name] = _module
    globals()[module_name] = _module

