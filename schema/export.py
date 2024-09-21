###############################################################
# by Crowfunder                                               #
# Copyright my ass but also the GPL-3.0 License               #
# Github: https://github.com/Crowfunder                       #
###############################################################

'''
Schema for Exportable post-processing in main.py

NOT REQUIRED FOR MODULES
'''

# External Imports
from dataclasses import dataclass

# Internal Imports
from schema.model import PrimitiveWrapper, Model


######################
# Model Export Types
######################

@dataclass(kw_only=True)
class StaticModel(Model):
    mode: str = 'Static'


@dataclass(kw_only=True)
class ArticulatedModel(Model):
    mode: str = 'Articulated'

    def _get_armature_str(self):
        if self.armature:
            return self.armature.tostring()
        return '<root><name>%ROOT%</name><transform> </transform><children> </children></root>'


def SetModelType(model: Model, mode: str):
    '''
    Sets the model type based on the given mode.

    Args:
        model (Model): The model object to set the type for.
        mode (str): The mode to set the model type to. Valid values are 'Articulated' or 'Static'.

    Returns:
        Model: The model object with the updated type.

    Raises:
        Exception: If an unknown model mode is provided.
    '''
    if mode.capitalize() == 'Articulated':
        return ArticulatedModel(primitives=PrimitiveWrapper(tag_name='skin', visible=model.primitives.visible),
                                materials=model.materials, armature=model.armature)
    elif mode.capitalize() == 'Static':
        return StaticModel(primitives=PrimitiveWrapper(tag_name='meshes', visible=model.primitives.visible),
                           materials=model.materials, armature=model.armature)
    else:
        raise Exception('Unknown model mode.')
