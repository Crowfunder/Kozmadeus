###############################################################
# by Crowfunder                                               #
# Copyright my ass but also the GPL-3.0 License               #
# Github: https://github.com/Crowfunder                       #
###############################################################

# A workaround to get a dictionary of modules' names + objects. 
#
# Previous Source:  
# https://stackoverflow.com/questions/3365740/how-to-import-all-submodules
#
# Had to be rewritten since pkgutil.walk_packages() is broken with Nuitka
# New source: https://github.com/Nuitka/Nuitka/issues/1646

import pkgutil

__modules__ = {}
for module_class in pkgutil.iter_modules(__path__):
    
    module_name = module_class.name
    module_object = pkgutil.resolve_name('modules.' + module_name)
    __modules__[module_name] = module_object

