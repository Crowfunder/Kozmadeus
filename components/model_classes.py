###############################################################
# by Crowfunder                                               #
# Copyright my ass but also the GPL-3.0 License               #
# Github: https://github.com/Crowfunder                       #
###############################################################

from dataclasses import dataclass
import xml.etree.ElementTree as ET
import math

######################
# Base Model Data
######################

@dataclass
class ModelDataSimple:
	data: 		list
	tag_name: 	str

	def _tostring(self):
		return str(self.data)[1:-1]
	
	def tostring(self):
		return f'<{self.tag_name}>{self._tostring()}</{self.tag_name}>'
	
	def __iter__(self):
		for item in self.data:
			yield item

	def __getitem__(self, i):
		return self.data[i]

	def __len__(self):
		return len(self.data)


@dataclass
class Bones(ModelDataSimple):
	data: list[str]
	tag_name: str = 'bones'


@dataclass
class Indices(ModelDataSimple):
	data: list[int]
	tag_name: str = 'indices'


@dataclass
class MinExtent(ModelDataSimple):
	data: list[float]
	tag_name: str = 'minExtent'


@dataclass
class MaxExtent(ModelDataSimple):
	data: list[float]
	tag_name: str = 'maxExtent'


@dataclass
class ModelData(ModelDataSimple):
	size: int
	def tostring(self):
		return f'<{self.tag_name}><size>{self.size}</size><type>FLOAT</type><stride>{self.size*4}</stride><floatArray>{self._tostring()}</floatArray></{self.tag_name}>'
	
	def __iter__(self):
		for index in range(len(self.data)//self.size):
			yield self.data[index*self.size : index*self.size + self.size]


@dataclass
class Vertices(ModelData):
	size: 	  int = 3
	tag_name: str = 'vertexArray'


@dataclass
class Normals(ModelData):
	size: 	  int = 3
	tag_name: str = 'normalArray'


@dataclass
class Texcoords(ModelData):
	size: 	  int = 2
	tag_name: str = 'entry'


@dataclass
class VertexAttribData(ModelData):
	name: str
	def tostring(self):
		return f'<{self.tag_name}><size>{self.size}</size><stride>{self.size*4}</stride><type>FLOAT</type><floatArray>{self._tostring()}</floatArray><name>{self.name}</name></{self.tag_name}>'
	 

@dataclass
class BoneIndices(VertexAttribData):
	name: str = 'boneIndices'
	size: int = 4


@dataclass
class BoneWeights(VertexAttribData):
	name: str = 'boneWeights'
	size: int = 4


######################
# Model Data Wrappers
######################

@dataclass
class EntryArray:
	entry_list: list
	tag_name:   str

	def _tostring(self):
		entry_list_str = ''
		for entry in self.entry_list:
			entry_list_str += entry.tostring()
		return entry_list_str
	
	def tostring(self):
		return f'<{self.tag_name}>{self._tostring()}</{self.tag_name}>'
	
	def __iter__(self):
		for entry in self.entry_list:
			yield entry

	def __getitem__(self, i):
		return self.entry_list[i]

	def __len__(self):
		return len(self.entry_list)


@dataclass
class TexcoordsArray(EntryArray):
	entry_list: list[Texcoords]
	tag_name: str = 'texCoordArrays'


@dataclass
class VertexAttribArray(EntryArray):
	entry_list: list[BoneIndices | BoneWeights]
	tag_name: str = 'vertexAttribArrays'


######################
# Primitives
######################

@dataclass(kw_only=True)
class Primitive:
	vertices: 	 Vertices
	normals: 	 Normals
	texcoords: 	 TexcoordsArray
	indices: 	 Indices
	mode:		 str
	tag: 		 str
	texture: 	 str
	indices_end: int
	geom_class:  str = 'com.threerings.opengl.geometry.config.GeometryConfig$IndexedStored'

	def __post_init__(self):
		self._calculate_extents()

	def _calculate_extents(self):
		vertex_size=3
		min_extent = [math.inf]*vertex_size
		max_extent = [-math.inf]*vertex_size

		# Iterate through vertices to find min/max
		for vertex in self.vertices:
			for index, point in enumerate(vertex):
				min_extent[index] = min(min_extent[index], vertex[index])
				max_extent[index] = max(max_extent[index], vertex[index])

		self.min_extent = MinExtent(min_extent)
		self.max_extent = MaxExtent(max_extent)

	def tostring(self):
		return f'''<entry><texture>{self.texture}</texture><tag>{self.tag}</tag><geometry class="{self.geom_class}"><bounds>{self.min_extent.tostring()}{self.max_extent.tostring()}</bounds><mode>{self.mode}</mode>{self.texcoords.tostring()}{self.normals.tostring()}{self.vertices.tostring()}<end>{self.indices_end}</end>{self.indices.tostring()}</geometry></entry>'''


@dataclass(kw_only=True)
class SkinnedPrimitive(Primitive):
	bones: Bones
	vertex_attribs: VertexAttribArray
	geom_class: str = 'com.threerings.opengl.geometry.config.GeometryConfig$SkinnedIndexedStored'

	def tostring(self):
		return f'''<entry><texture>{self.texture}</texture><tag>{self.tag}</tag><geometry class="{self.geom_class}"><bounds>{self.min_extent.tostring()}{self.max_extent.tostring()}</bounds><mode>{self.mode}</mode>{self.vertex_attribs.tostring()}{self.texcoords.tostring()}{self.normals.tostring()}{self.vertices.tostring()}<end>{self.indices_end}</end>{self.indices.tostring()}{self.bones.tostring()}</geometry></entry>'''


def PrimitiveAddSkin(primitive: Primitive, bones: Bones, vertex_attribs: VertexAttribArray):
	"""
	Adds skinning information to a primitive and returns a SkinnedPrimitive object.

	Args:
		primitive (Primitive): The original primitive object.
		bones (Bones): The bones object containing bone information.
		vertex_attribs (VertexAttribArray): The vertex attributes array with bone weights and indices.

	Returns:
		SkinnedPrimitive: The skinned primitive object with added skinning information.
	"""
	return SkinnedPrimitive(
		vertices=primitive.vertices,
		normals=primitive.normals,
		texcoords=primitive.texcoords,
		indices=primitive.indices,
		mode=primitive.mode,
		tag=primitive.tag,
		texture=primitive.texture,
		indices_end=primitive.indices_end,
		bones=bones,
		vertex_attribs=vertex_attribs
	)


@dataclass
class PrimitiveArray(EntryArray):
	entry_list: list[Primitive | SkinnedPrimitive]
	tag_name: str = 'visible'


@dataclass
class PrimitiveWrapper:
	visible: PrimitiveArray
	tag_name: str = 'node'

	def __post_init__(self):
		self._calculate_extents()

	def _calculate_extents(self):
		vertex_size = 3

		max_extent = [-math.inf]*vertex_size
		for i in range(vertex_size):
			max_extent[i] = max([prim.max_extent[i] for prim in self.visible])
		self.max_extent = MaxExtent(max_extent)

		min_extent = [math.inf]*vertex_size
		for i in range(vertex_size):
			min_extent[i] = min([prim.min_extent[i] for prim in self.visible])
		self.min_extent = MinExtent(min_extent)

	def get_primitive_by_index(self, index):
		"""
		Retrieves a primitive object from the list of visible primitives based on the given index, as if they were merged.

		Parameters:
			index (int): The index of the primitive to retrieve.

		Returns:
			Primitive or None: The primitive object corresponding to the given index, or None if not found.
		"""
		offset = 0
		for primitive in self.visible:
			primitive_offset = primitive.indices_end + offset
			if index <= primitive_offset:
				return primitive
			offset += primitive.indices_end
		return None

	def tostring(self):
		return f'<{self.tag_name}><bounds>{self.min_extent.tostring()}{self.max_extent.tostring()}</bounds>{self.visible.tostring()}</{self.tag_name}>'


@dataclass
class ArticulatedPrimitiveWrapper(PrimitiveWrapper):
	tag_name: str = 'skin'


@dataclass
class StaticPrimitiveWrapper(PrimitiveWrapper):
	tag_name: str = 'meshes'


######################
# Materials
######################

@dataclass
class Material:

	texture:	str
	tag:		str
	name: str = 'Model/Opaque'

	def tostring(self):
		return f'<entry><outer rdepth="1"/><texture>{self.texture}</texture><tag>{self.tag}</tag><material><name>{self.name}</name><arguments><key class="java.lang.String">Texture</key><value class="com.threerings.config.ConfigReference"><name>2D/File/Default</name><arguments><key class="java.lang.String">File</key><value class="java.lang.String">PressToSelectTextureFile.png</value><key class="java.lang.String">Magnify</key><value class="com.threerings.opengl.renderer.config.TextureConfig$MagFilter">LINEAR</value><key class="java.lang.String">Minify</key><value class="com.threerings.opengl.renderer.config.TextureConfig$MinFilter">LINEAR</value></arguments></value></arguments></material></entry>'


@dataclass
class SkinnedMaterial(Material):
	name: str = 'Model/Skinned/Masked (Soft)'


def MaterialAddSkin(material: Material):
	"""
	Creates a skinned material based on the given material.

	Args:
		material (Material): The material to create a skinned material from.

	Returns:
		SkinnedMaterial: The skinned material created from the given material.
	"""
	return SkinnedMaterial(texture=material.texture, tag=material.tag)


@dataclass
class MaterialArray(EntryArray):
	entry_list: list[Material | SkinnedMaterial]
	tag_name: str = 'materialMappings'


######################
# Model
######################

@dataclass(kw_only=True)
class Model:
	primitives: ArticulatedPrimitiveWrapper | StaticPrimitiveWrapper | PrimitiveWrapper
	materials: 	MaterialArray
	bone_tree_xml: ET.Element | None
	mode: str = ''

	def _get_bone_tree_xml(self):
		if self.bone_tree_xml:
			return ET.tostring(self.bone_tree_xml, encoding='unicode')
		return ' '


	def toargs(self):
		args = {}

		args['primitives'] = self.primitives.tostring()
		args['materials'] = self.materials.tostring()
		args['bone_tree'] = self._get_bone_tree_xml()
		args['mode'] = self.mode

		return args


@dataclass(kw_only=True)
class StaticModel(Model):
	mode: str = 'Static'


@dataclass(kw_only=True)
class ArticulatedModel(Model):
	mode: str = 'Articulated'

	def _get_bone_tree_xml(self):
		if self.bone_tree_xml:
			return ET.tostring(self.bone_tree_xml, encoding='unicode')
		return '<root><name>%ROOT%</name><transform> </transform><children> </children></root>'


def SetModelType(model: Model, mode: str):
	"""
	Sets the model type based on the given mode.

	Args:
		model (Model): The model object to set the type for.
		mode (str): The mode to set the model type to. Valid values are 'Articulated' or 'Static'.

	Returns:
		Model: The model object with the updated type.

	Raises:
		Exception: If an unknown model mode is provided.
	"""
	if mode.capitalize() == 'Articulated':
		return ArticulatedModel(primitives=ArticulatedPrimitiveWrapper(visible=model.primitives.visible), 
								materials=model.materials, bone_tree_xml=model.bone_tree_xml)
	elif mode.capitalize() == 'Static':
		return StaticModel(primitives=StaticPrimitiveWrapper(visible=model.primitives.visible), 
						   materials=model.materials, bone_tree_xml=model.bone_tree_xml)
	else:
		raise Exception('Unknown model mode.')
