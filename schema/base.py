###############################################################
# by Crowfunder                                               #
# Copyright my ass but also the GPL-3.0 License               #
# Github: https://github.com/Crowfunder                       #
###############################################################

'''
Schema for constructing other schemas

NOT REQUIRED FOR MODULES
'''

# External Imports
from dataclasses import dataclass
import math

#########################
# Data arrays
#########################

@dataclass
class DataSimple:
    '''
    Contains a simple data array exportable to an xml tag.
    '''
    data: 		list
    tag_name: 	str

    def _tostring(self):
        if len(self.data) == 0:
            return ' '
        return str(self.data)[1:-1].replace("'", "").replace('"', '')

    def tostring(self):
        return f'<{self.tag_name}>{self._tostring()}</{self.tag_name}>'

    def __iter__(self):
        for item in self.data:
            yield item

    def __getitem__(self, i):
        return self.data[i]

    def __setitem__(self, i, new_value):
        self.data[i] = new_value

    def __len__(self):
        return len(self.data)
    

@dataclass
class DataGrouped(DataSimple):
    '''
    Contains a data array that groups its members into self.size length subarrays.
    Raw data length has to be divisible by self.size
    '''
    size: int
    def __post_init__(self):
        if len(self.data) % self.size:
            raise ValueError(f'length of data not divisible by {self.size}')

    def tostring(self):
        return f'<{self.tag_name}><size>{self.size}</size><type>FLOAT</type><stride>{self.size*4}</stride><floatArray>{self._tostring()}</floatArray></{self.tag_name}>'

    def __iter__(self):
        for index in range(len(self.data)//self.size):
            yield self.data[index*self.size : index*self.size + self.size]

    def __len__(self):
        return len(self.data)//self.size

    def __getitem__(self, index):
        if isinstance(index, int):
            slice_start = index*self.size
            slice_stop = index*self.size + self.size
        elif isinstance(index, slice):
            slice_start = index.start*self.size
            slice_stop = index.stop*self.size
        else:
            raise TypeError(f'vertex indices must be integers or slices, not {type(index)}')
        if slice_start > len(self.data) or slice_stop > len(self.data):
            raise IndexError('vertex index out of range')
        return self.data[slice_start : slice_stop]


@dataclass
class DataFixed(DataSimple):
    '''
    Contains a fixed-size data array. Allows setting custom attributes.
    Data length has to be equal to self.size
    '''
    size: int
    def _size_check(self):
        if len(self.data) != self.size:
            raise ValueError(f'incorrect data length: found {len(self.data)}, expected {self.size}')

    def _set_data(self):
        '''
        Sets i.e x,y,z attribs referencing to specific elements in data
        '''
        pass

    def _convert_data(self):
        '''
        Method allowing converting input data in different format to intended format
        to accept input in various formats.
        '''
        pass

    def __post_init__(self):
        self._convert_data()
        self._size_check()
        self._set_data()


#########################
# Data arrays containers
#########################

@dataclass
class EntryArray:
    '''
    Container for list of objects with tostring() method. 
    Cascade-tostrings itself and its members.
    '''
    entry_list: list
    tag_name:   str

    def _tostring(self):
        entry_list_str = ''
        for entry in self.entry_list:
            entry_list_str += entry.tostring()
        if not entry_list_str:
            return ' '
        return entry_list_str

    def tostring(self):
        return f'<{self.tag_name}>{self._tostring()}</{self.tag_name}>'

    def __iter__(self):
        for entry in self.entry_list:
            yield entry

    def __getitem__(self, i):
        return self.entry_list[i]

    def __setitem__(self, i, new_value):
        self.entry_list[i] = new_value

    def __len__(self):
        return len(self.entry_list)



######################
# Transforms
######################
def EulerToQuaternion(euler_rotations):
    """
    Function for converting Euler Angles to Quaternions
    TAKES DEGREES AS INPUT, NOT RADIANS
    Credit: https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles

    Args:
        euler_rotations (list): Dictionary containing Euler rotation angles in degrees.

    Returns:
        list: Dictionary containing quaternion values (x, y, z, w).
    """

    # Initalize output quaternion dict
    quaternion = [0.0]*4

    # Simplify input dict data
    x = euler_rotations[0]
    y = euler_rotations[1]
    z = euler_rotations[2]

    # Convert degrees to radians
    x = x*(math.pi/180)
    y = y*(math.pi/180)
    z = z*(math.pi/180)

    # Trig functs of all angles with abbreviations
    # i.e. "cx" for cos(x*0.5)
    cx = math.cos(x*0.5)
    cy = math.cos(y*0.5)
    cz = math.cos(z*0.5)
    sx = math.sin(x*0.5)
    sy = math.sin(y*0.5)
    sz = math.sin(z*0.5)

    # Calculate quaternion elements
    quaternion[0] = sx * cy * cz - cx * sy * sz
    quaternion[1] = cx * sy * cz + sx * cy * sz
    quaternion[2] = cx * cy * sz - sx * sy * cz
    quaternion[3] = cx * cy * cz + sx * sy * sz

    return quaternion


def ApproximateUniformScale(scale_matrix):
    '''
    Approximates uniform scale from scale matrix, 
    rewritten directly from the Clyde engine.
    "The cube root of the signed volume of the 
     parallelepiped spanned by the axis vectors"

    Args:
        scale_matrix (list): A 3x3 scale matrix.

    Returns:
        float: The approximate uniform scale factor.

    '''
    
    m = scale_matrix
    vol1 = m[0][0] * (m[1][1] * m[2][2] - m[2][1] * m[1][2])
    vol2 = m[1][0] * (m[2][1] * m[0][2] - m[0][1] * m[2][2])
    vol3 = m[2][0] * (m[0][1] * m[1][2] - m[1][1] * m[0][2])

    scale = float(vol1 + vol2 + vol3) ** float(1/3)
    return scale


@dataclass
class Translation(DataFixed):
    '''
    Accepts translation as a list of 3 floats (xyz respectively)
    '''
    tag_name: str = 'translation'
    size: int = 3

    def _set_data(self):
        self.x = self.data[0]
        self.y = self.data[1]
        self.z = self.data[2]


@dataclass
class Rotation(DataFixed):
    '''
    Accepts rotation quaternion as list of 4 floats (xyzw respectively) 
    or euler rotation as 3 floats (xyz respectively) that get converted 
    into quaternion rotation on-the-fly.
    '''
    tag_name: str = 'rotation'
    size: int = 4
    def _set_data(self):
        self.x = self.data[0]
        self.y = self.data[1]
        self.z = self.data[2]
        self.w = self.data[3]

    def _convert_data(self):
        if len(self.data) == 3:
            self.data = EulerToQuaternion(self.data)


@dataclass
class Scale(DataFixed):
    '''
    Accepts a list of a single float as uniform scale or 9 floats as Euler scale matrix
    that gets converted into uniform scale on-the-fly
    '''
    tag_name: str = 'scale'
    size: int = 1
    def _convert_data(self):
        if len(self.data) == 3:
            self.data = ApproximateUniformScale(self.data)

    def _set_data(self):
        self.scale = self.data[0]


@dataclass
class Matrix(DataFixed):
    '''
    Accepts a list of 16 floats that represent a transform matrix.
    '''
    tag_name: str = 'matrix'
    size: int = 16


@dataclass
class Transform(EntryArray):
    '''
    Container for various transforms.
    '''
    entry_list: list[Translation | Rotation | Scale | Matrix]
    tag_name: str = 'transform'


#########################
# Exportables
#########################

@dataclass(kw_only=True)
class Exportable:
    '''
    Base class for all objects exportable with ExportXML
    - self.template_file: Points to the template file that should be used by ExportXML
    - self.toargs(): Returns a dict compatible with self.template_file
    '''
    template_file: str

    def toargs(self) -> dict:
        raise NotImplementedError('Mandatory method not implemented')
