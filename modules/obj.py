###############################################################
# by Crowfunder                                               #
# Copyright my ass but also the License                       #
# Github: https://github.com/Crowfunder                       #
###############################################################

#########################################
# Credits: Puzovoz                      #
# Based on:                             #
# https://github.com/Puzovoz/Bootshuze  #
#########################################

import gc

module_data = {
    'Name'       : 'Wavefront',
    'Mesh'       : True,
    'Armature'   : False,
    'Animations' : False,
    'Multimesh'  : False
}

def Extract(file_name):
    with open(file_name, 'r') as file:
        args       = dict()
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
                if 'mode' not in args:
                    indices_count = len(line.split()[1:])
                    if indices_count == 2: args['mode'] = 'LINES'
                    if indices_count == 3: args['mode'] = 'TRIANGLES'
                    if indices_count == 4: args['mode'] = 'QUADS'

                for face in line.split()[1:]:
                    if face not in faces: faces.append(face.replace('\n', ''))
                    indices.append(faces.index(face))
        
            # Calculate min/max extent for vertices
            if line[:2] == 'v ':
                
                # Initialize values with first vertex
                if 'min_extent' not in vars() and 'max_extent' not in vars():
                    min_extent = [float(val) for val in line.split()[1:]]
                    max_extent = [float(val) for val in line.split()[1:]]
                
                # And change values as we go through other vertices  
                for index, vertex in enumerate(line.split()[1:]):
                    min_extent[index] = min(min_extent[index], float(vertex))
                    max_extent[index] = max(max_extent[index], float(vertex))
            
        vt = list(filter(lambda x: x[:2] == 'vt', lines))
        vn = list(filter(lambda x: x[:2] == 'vn', lines))
        v  = list(filter(lambda x: x[:2] == 'v ', lines))
            
        if len(vt) == 0:
            raise Exception('Input model lacks UV mapping. '
                            'Model cannot be correctly created.')
            
        print('[MODULE][INFO]: Calculating vertices...')
            
        # Generate vertices list based on indices from input file
        for face in faces:
            face_indices = face.split('/')
            
            # Texture coordinates, UV
            vertices.extend(vt[int(face_indices[1])-1].split()[1:])
            
            # Face normals
            vertices.extend(vn[int(face_indices[2])-1].split()[1:])
            
            # Position coordinates, XYZ
            vertices.extend(v [int(face_indices[0])-1].split()[1:])


        del faces
        del lines
        del v, vn, vt

        args['min_extent'] = str(min_extent)[1:-1]
        del min_extent
        args['max_extent'] = str(max_extent)[1:-1]
        del max_extent
        args['indices']    = str(indices)[1:-1]
        args['indices_end'] = str(max(indices))
        del indices
        args['vertices']   = ', '.join(vertices)
        del vertices
        args['bones']      = ''

        gc.collect()
        geometries.append(args)
        return geometries