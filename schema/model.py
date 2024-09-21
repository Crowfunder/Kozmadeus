###############################################################
# by Crowfunder                                               #
# Copyright my ass but also the GPL-3.0 License               #
# Github: https://github.com/Crowfunder                       #
###############################################################

'''
Schema for constructing Models.
'''

# External Imports
from dataclasses import dataclass, field
import math

# Internal Imports
from schema.base import DataSimple, DataGrouped, EntryArray, Transform, Exportable, Translation, Rotation, Scale, Matrix

#######################
# Ungrouped model data
#######################


@dataclass
class Bones(DataSimple):
    '''
    Container for list of bone names used by SkinnedPrimitive.
    '''
    data: list[str]
    tag_name: str = 'bones'


@dataclass
class Indices(DataSimple):
    '''
    Container for face indices of primitive. 
    NOTE: Primitives use a single, shared set of indices for Vertices, Normals, Texcoords and VertexAttribs
    '''
    data: list[int]
    tag_name: str = 'indices'


#######################
# Grouped model data
#######################

@dataclass
class Vertices(DataGrouped):
    '''
    Container for primitive vertices. 
    Each vertex is xyz respectively.
    '''
    size: 	  int = 3
    tag_name: str = 'vertexArray'


@dataclass
class Normals(DataGrouped):
    '''
    Container for primitive normals.
    Each normal is xyz respectively.
    '''
    size: 	  int = 3
    tag_name: str = 'normalArray'


@dataclass
class Texcoords(DataGrouped):
    '''
    Container for single set of primitive texcoords.
    Has to be contained within TexcoordsArray as primitives
    can have more than one set of texcoords.
    '''
    size: 	  int = 2
    tag_name: str = 'entry'


@dataclass
class TexcoordsArray(EntryArray):
    '''
    Container for Texcoords.
    '''
    entry_list: list[Texcoords]
    tag_name: str = 'texCoordArrays'


@dataclass
class VertexAttribData(DataGrouped):
    '''
    Base class for special vertex bone data tags.
    '''
    name: str
    def tostring(self):
        return f'<{self.tag_name}><size>{self.size}</size><stride>{self.size*4}</stride><type>FLOAT</type><floatArray>{self._tostring()}</floatArray><name>{self.name}</name></{self.tag_name}>'


@dataclass
class BoneIndices(VertexAttribData):
    '''
    Container for indices pointing to bone names in Bones names array.
    Should be the same length as BoneWeights and Vertices.
    NOTE: Clyde limits number of vertex bone data slots to 4. Any extra ones have to be
    removed manually.
    '''
    size: int = 4
    tag_name: str = 'entry'
    name: str = 'boneIndices'


@dataclass
class BoneWeights(VertexAttribData):
    '''
    Container for weights affecting the vertex by bone selected by BoneIndices.
    Should be the same length as BoneIndices and Vertices.
    NOTE: Clyde limits number of vertex bone data slots to 4. Any extra ones have to be
    removed manually.
    '''
    size: int = 4
    tag_name: str = 'entry'
    name: str = 'boneWeights'


@dataclass
class VertexAttribArray(EntryArray):
    '''
    Special container for BoneWeights and BoneIndices.
    '''
    entry_list: list[BoneIndices | BoneWeights]
    tag_name: str = 'vertexAttribArrays'


######################
# Armature Tree
######################
@dataclass
class ArmatureNode:
    '''
    Singular node of armature. If parent is None, automatically sets _tag_name to "root".
    Automatically attaches itself to parent object.
    Calling self.tostring() cascade-tostrings current node and its children.
    '''
    transform: Transform
    name: str
    parent: 'ArmatureNode | None' = None
    children: 'list[ArmatureNode]' = field(default_factory=list)	 # Lazy evaluation of types needed if dataclass contains itself
    _tag_name: str = 'entry'

    def __post_init__(self):
        if not self.parent:
            self._tag_name = 'root'
        else:
            self._add_to_parent()
        self._children = EntryArray(self.children, tag_name='children')
        self.children = self._children.entry_list   # link by reference
        if self.children:
            self._add_to_children()

    def _add_to_parent(self):
        if self.parent:
            self.parent._children.entry_list.append(self)

    def _add_to_children(self):
        for child in self._children.entry_list:
            child.parent = self

    def tostring(self):
        return f'<{self._tag_name}><name>{self.name}</name>{self.transform.tostring()}{self._children.tostring()}</{self._tag_name}>'


######################
# Primitives
######################

@dataclass(kw_only=True)
class Primitive:
    '''
    Non-skinned geometry primitive. Features automatic min/max extent calculation.
    - self.tag and self.texture: Point to the material this primitive uses. (Both have to match)
    - self.mode: Selects geometry mode. Possible values are: LINES, TRIANGLES, QUADS, POLYGONS
    
    Other attribs are self-explanatory.

    Can be converted to SkinnedPrimitive with PrimitiveAddSkin method.
    NOTE: Primitives use a single, shared set of indices for Vertices, Normals, Texcoords and VertexAttribs
    '''
    vertices: 	 Vertices
    normals: 	 Normals
    texcoords: 	 TexcoordsArray
    indices: 	 Indices
    tag: 		 str
    texture: 	 str
    mode:		 str
    geom_class:  str = 'com.threerings.opengl.geometry.config.GeometryConfig$IndexedStored'

    def __post_init__(self):
        self._check_mode_value()
        self._calculate_indices_end()
        self._trim_unnecessary_data()
        self._calculate_extents()

    def _check_mode_value(self):
        self.mode = self.mode.upper()
        if self.mode not in ['LINES', 'TRIANGLES', 'POLYGONS', 'QUADS']:
            raise ValueError(f'incorrect mode value: {self.mode}')

    def _trim_unnecessary_data(self):
        self.vertices.data = self.vertices[0:self.indices_end+1]
        self.normals.data = self.vertices[0:self.indices_end+1]
        for i, texcoord in enumerate(self.texcoords):
            self.texcoords[i].data = texcoord[0:self.indices_end+1]

    def _calculate_indices_end(self):
        self.indices_end = max(self.indices)

    def _calculate_extents(self):
        vertex_size=3
        min_extent = [math.inf]*vertex_size
        max_extent = [-math.inf]*vertex_size

        # Iterate through vertices to find min/max
        for vertex in self.vertices:
            for index, point in enumerate(vertex):
                min_extent[index] = min(min_extent[index], point)
                max_extent[index] = max(max_extent[index], point)

        self.min_extent = DataSimple(min_extent, 'minExtent')
        self.max_extent = DataSimple(max_extent, 'maxExtent')

    def tostring(self):
        return f'''<entry><texture>{self.texture}</texture><tag>{self.tag}</tag><geometry class="{self.geom_class}"><bounds>{self.min_extent.tostring()}{self.max_extent.tostring()}</bounds><mode>{self.mode}</mode>{self.texcoords.tostring()}{self.normals.tostring()}{self.vertices.tostring()}<end>{self.indices_end}</end>{self.indices.tostring()}</geometry></entry>'''


@dataclass(kw_only=True)
class SkinnedPrimitive(Primitive):
    '''
    Skinned geometry primitive. Features automatic min/max extent calculation.
    - self.tag and self.texture: Point to the material this primitive uses. (Both have to match)
    - self.mode: Selects geometry mode. Possible values are: LINES, TRIANGLES, QUADS, POLYGONS
    
    Other attribs are self-explanatory.

    Can be converted to SkinnedPrimitive with PrimitiveAddSkin method.
    '''
    bones: Bones
    vertex_attribs: VertexAttribArray
    geom_class: str = 'com.threerings.opengl.geometry.config.GeometryConfig$SkinnedIndexedStored'

    def tostring(self):
        return f'''<entry><texture>{self.texture}</texture><tag>{self.tag}</tag><geometry class="{self.geom_class}"><bounds>{self.min_extent.tostring()}{self.max_extent.tostring()}</bounds><mode>{self.mode}</mode>{self.vertex_attribs.tostring()}{self.texcoords.tostring()}{self.normals.tostring()}{self.vertices.tostring()}<end>{self.indices_end}</end>{self.indices.tostring()}{self.bones.tostring()}</geometry></entry>'''


def PrimitiveAddSkin(primitive: Primitive, bones: Bones, vertex_attribs: VertexAttribArray):
    '''
    Adds skinning information to a primitive and returns a SkinnedPrimitive object.

    Args:
        primitive (Primitive): The original primitive object.
        bones (Bones): The bones object containing bone information.
        vertex_attribs (VertexAttribArray): The vertex attributes array with bone weights and indices.

    Returns:
        SkinnedPrimitive: The skinned primitive object with added skinning information.
    '''
    return SkinnedPrimitive(
        vertices=primitive.vertices,
        normals=primitive.normals,
        texcoords=primitive.texcoords,
        indices=primitive.indices,
        mode=primitive.mode,
        tag=primitive.tag,
        texture=primitive.texture,
        bones=bones,
        vertex_attribs=vertex_attribs
    )

@dataclass
class PrimitiveWrapper:
    '''
    Container for Primitive and SkinnedPrimitive objects. 
    Can check whether any of its members is a skinned primitive. 
    Features automatic min/max extent calculation.
    '''
    visible: list[Primitive | SkinnedPrimitive]
    tag_name: str = 'node'

    def __post_init__(self):
        self._calculate_extents()
        self._visible = EntryArray(self.visible, tag_name='visible')
        self.visible = self._visible.entry_list	 # link by reference

    def _calculate_extents(self):
        vertex_size = 3

        max_extent = [-math.inf]*vertex_size
        for i in range(vertex_size):
            max_extent[i] = max(prim.max_extent[i] for prim in self.visible)
        self.max_extent = DataSimple(max_extent, 'maxExtent')

        min_extent = [math.inf]*vertex_size
        for i in range(vertex_size):
            min_extent[i] = min(prim.min_extent[i] for prim in self.visible)
        self.min_extent = DataSimple(min_extent, 'minExtent')

    def isskinned(self):
        '''
        Returns True if any primitive within visible is skinned
        '''
        return any(type(primitive) is SkinnedPrimitive for primitive in self.visible)

    def tostring(self):
        return f'<{self.tag_name}><bounds>{self.min_extent.tostring()}{self.max_extent.tostring()}</bounds>{self._visible.tostring()}</{self.tag_name}>'

    def __iter__(self):
        for entry in self.visible:
            yield entry

    def __getitem__(self, i):
        return self.visible[i]
    
    def __setitem__(self, i, new_value):
        self.visible[i] = new_value

    def __len__(self):
        return len(self.visible)


######################
# Materials
######################

@dataclass
class Material:
    '''
    Basic material information.
    - self.tag and self.texture: If both match the same pair of tags in any primitive, this material will be applied to it.
    '''
    texture:	str
    tag:		str
    name: str = 'Model/Opaque'

    def tostring(self):
        return f'<entry><outer rdepth="1"/><key class="java.lang.String">Pass Mode</key><value class="java.lang.String">Normal</value><texture>{self.texture}</texture><tag>{self.tag}</tag><material><name>{self.name}</name><arguments><key class="java.lang.String">Texture</key><value class="com.threerings.config.ConfigReference"><name>2D/File/Default</name><arguments><key class="java.lang.String">File</key><value class="java.lang.String">PressToSelectTextureFile.png</value><key class="java.lang.String">Magnify</key><value class="com.threerings.opengl.renderer.config.TextureConfig$MagFilter">LINEAR</value><key class="java.lang.String">Minify</key><value class="com.threerings.opengl.renderer.config.TextureConfig$MinFilter">LINEAR</value></arguments></value></arguments></material></entry>'


def MaterialAddSkin(material: Material):
    '''
    Creates a skinned material based on the given material.

    Args:
        material (Material): The material to create a skinned material from.

    Returns:
        material (Material): The material with name changed to a skinned material.
    '''
    material.name = 'Model/Skinned/Masked (Soft)'
    return material


@dataclass
class MaterialArray(EntryArray):
    '''
    Entry array for Materials
    '''
    entry_list: list[Material]
    tag_name: str = 'materialMappings'


######################
# Model Exportable
######################

@dataclass(kw_only=True)
class Model(Exportable):
    '''
    Entire model in Exportable format. Automatically gives all materials skinning properties
    in case any primitive has skinning information.
    - self.primitives: Using base PrimitiveWrapper is sufficient, as model mode gets converted
    in main regardless
    '''
    primitives: PrimitiveWrapper
    materials: 	MaterialArray
    armature: ArmatureNode | None = None
    template_file: str = 'template_model'
    mode: str = ''

    def __post_init__(self):
        self._skin_materials()

    def _skin_materials(self):
        if self.primitives.isskinned():
            for i, material in enumerate(self.materials):
                self.materials[i] = MaterialAddSkin(material)

    def _get_armature_str(self):
        if self.armature:
            return self.armature.tostring()
        return ' '

    def toargs(self):
        args = {}
        args['primitives'] = self.primitives.tostring()
        args['materials'] = self.materials.tostring()
        args['armature'] = self._get_armature_str()
        args['mode'] = self.mode
        return args