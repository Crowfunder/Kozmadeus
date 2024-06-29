###############################################################
# by Crowfunder                                               #
# Copyright my ass but also the GPL-3.0 License               #
# Github: https://github.com/Crowfunder                       #
###############################################################

from dataclasses import dataclass
import xml.etree.ElementTree as ET


@dataclass
class ModelDataSimple:
	data: 		list
	tag_name: 	str

	def _tostring(self):
		return str(self.data)[1:-1]
	
	def tostring(self):
		return f'<{self.tag_name}>{self._tostring()}</{self.tag_name}>'


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
		return f'<{self.tag_name}><size>{self.size}</size><type>FLOAT</type><floatArray>{self._tostring()}</floatArray></{self.tag_name}>'


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
		return f'<{self.tag_name}><size>{self.size}</size><type>FLOAT</type><floatArray>{self._tostring()}</floatArray><name>{self.name}</name></{self.tag_name}>'
	 

@dataclass
class BoneIndices(VertexAttribData):
	name: str = 'boneIndices'
	size: int = 4


@dataclass
class BoneWeights(VertexAttribData):
	name: str = 'boneWeights'
	size: int = 4


@dataclass
class ModelDataArray:
	entry_list: list[ModelData]
	tag_name:   str

	def _tostring(self):
		entry_list_str = ''
		for entry in self.entry_list:
			entry_list_str += entry.tostring()
		return entry_list_str
	
	def tostring(self):
		return f'<{self.tag_name}>{self._tostring()}</{self.tag_name}>'


@dataclass
class TexcoordsArray(ModelDataArray):
	tag_name: str = 'texCoordArrays'	


@dataclass
class VertexAttribArray(ModelDataArray):
	tag_name: str = 'vertexAttribArrays'


@dataclass(kw_only=True)
class Primitive:
	vertices: 	 Vertices
	normals: 	 Normals
	texcoords: 	 TexcoordsArray
	indices: 	 Indices
	min_extent:  MinExtent
	max_extent:  MaxExtent
	mode:		 str
	tag: 		 str
	texture: 	 str
	indices_end: int
	geom_class:  str = 'com.threerings.opengl.geometry.config.GeometryConfig$IndexedStored'

	def tostring(self):
		return f'''<entry><texture>{self.texture}</texture><tag>{self.tag}</tag><geometryclass="{self.geom_class}"><bounds>{self.min_extent.tostring()}{self.max_extent.tostring()}</bounds><mode>{self.mode}</mode>{self.texcoords.tostring()}{self.normals.tostring()}{self.vertices.tostring()}<end>{self.indices_end}</end>{self.indices.tostring()}</geometry></entry>'''


@dataclass(kw_only=True)
class SkinnedPrimitive(Primitive):
	bones: Bones
	vertex_attribs: VertexAttribArray
	geom_class = 'com.threerings.opengl.geometry.config.GeometryConfig$SkinnedIndexedStored'

	def tostring(self):
		return f'''<entry><texture>{self.texture}</texture><tag>{self.tag}</tag><geometryclass="{self.geom_class}"><bounds>{self.min_extent.tostring()}{self.max_extent.tostring()}</bounds><mode>{self.mode}</mode>{self.vertex_attribs.tostring()}{self.texcoords.tostring()}{self.normals.tostring()}{self.vertices.tostring()}<end>{self.indices_end}</end>{self.indices.tostring()}{self.bones.tostring()}</geometry></entry>'''


@dataclass
class Material:

	name = 'Model/Opaque'
	texture:	str
	tag:		str

	def tostring(self):
		return f'<entry><outer rdepth="1"/><texture>{self.texture}</texture><tag>{self.tag}</tag><material><name>{self.name}</name></material></entry>'


@dataclass
class SkinnedMaterial(Material):
	name = 'Model/Skinned/Masked (Soft)'


@dataclass
class Model:
	primitives: list[Primitive | SkinnedPrimitive]
	materials: 	list[Material]
	min_extent: MinExtent
	max_extent: MaxExtent
	bone_tree_xml: ET.Element | None
