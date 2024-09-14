###############################################################
# by Crowfunder                                               #
# Copyright my ass but also the GPL-3.0 License               #
# Github: https://github.com/Crowfunder                       #
###############################################################

#########################################
# Credits: Puzovoz                      #
# Based on:                             #
# https://github.com/Puzovoz/Bootshuze  #
#########################################

import gc
from components.model import *


module_data = {
    'Name'       : 'Wavefront',
    'Author'     : 'Crowfunder',
    'Mesh'       : True,
    'Armature'   : False,
    'Animations' : False,
    'Multimesh'  : False
}


def Extract(file_name):
    with open(file_name, 'r') as file:
        tag = 'default'
        texture = 'texture.png'
        faces      = list()
        indices    = list()
        vertices   = list()
        geometries = list()
        lines = file.readlines()
    
        print('[MODULE][INFO]: Reading input model file.')
        print('[MODULE][INFO]: Calculating indices...')
        print('[MODULE][INFO]: Calculating min/max extents...')
        
        for line in lines:
            # Store faces that determine the numbers for indices
            if line[0] == 'f':
                indices_count = len(line.split()[1:])
                if indices_count == 2: mode = 'LINES'
                if indices_count == 3: mode = 'TRIANGLES'
                if indices_count == 4: mode = 'QUADS'

                for face in line.split()[1:]:
                    if face not in faces: faces.append(face.replace('\n', ''))
                    indices.append(faces.index(face))
        
        print('[MODULE][INFO]: Geometry mode: ', mode)
            
        vt = list(filter(lambda x: x[:2] == 'vt', lines))
        vn = list(filter(lambda x: x[:2] == 'vn', lines))
        v  = list(filter(lambda x: x[:2] == 'v ', lines))
        
        if len(vt) == 0:
            raise Exception('Input model lacks UV mapping. '
                            'Model cannot be correctly created.')
        
        print('[MODULE][INFO]: Calculating vertices...')

        # Generate vertices list based on indices from input file
        vertices = []
        texcoords = []
        normals = []
        for face in faces:
            face_indices = face.split('/')
            
            # Texture coordinates, UV
            texcoords.extend([float(val) for val in vt[int(face_indices[1])-1].split()[1:]])
            
            # Face normals
            normals.extend([float(val) for val in vn[int(face_indices[2])-1].split()[1:]])
            
            # Position coordinates, XYZ
            vertices.extend([float(val) for val in v[int(face_indices[0])-1].split()[1:]])

        material = Material(tag=tag, texture=texture)
        primitive = Primitive(vertices=Vertices(vertices), normals=Normals(normals), texcoords=TexcoordsArray([Texcoords(texcoords)]),
                              indices=Indices(indices), mode=mode, tag=tag, texture=texture)

        model = Model(primitives=PrimitiveWrapper([primitive]), 
                      materials=MaterialArray(entry_list=[material]))

        del faces
        del lines
        del v, vn, vt
        del indices
        del vertices
        gc.collect()
        geometries.append(model)
        return geometries