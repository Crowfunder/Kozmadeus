###############################################################
# by Crowfunder                                               #
# Copyright my ass but also the GPL-3.0 License               #
# Github: https://github.com/Crowfunder                       #
###############################################################

import gc
import re
import math
import collada
import xml.etree.ElementTree as ET

from components.model_classes import *


module_data = {
    'Name'       : 'Collada',
    'Author'     : 'Crowfunder',
    'Mesh'       : True,
    'Armature'   : True,
    'Animations' : False,
    'Multimesh'  : True
}



def ListFlatten(input_list):
    """
    Flattens a nested list into a single-level list.

    Args:
        input_list (list[list]): The nested list to be flattened.

    Returns:
        list: The flattened list.
    """
    while type(input_list[0]) is list:
        input_list = [item for sublist in input_list for item in sublist]

    return input_list



def EulerToQuaternion(euler_rotations):
    """
    Function for converting Euler Angles to Quaternions
    TAKES DEGREES AS INPUT, NOT RADIANS
    Credit: https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles

    Args:
        euler_rotations (dict): Dictionary containing Euler rotation angles in degrees.

    Returns:
        dict: Dictionary containing quaternion values (x, y, z, w).
    """
    
    # Initalize output quaternion dict
    quaternion = dict.fromkeys(['x', 'y', 'z', 'w'])
    
    # Simplify input dict data
    x = euler_rotations['x']
    y = euler_rotations['y']
    z = euler_rotations['z']
    
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
    quaternion['x'] = sx * cy * cz - cx * sy * sz
    quaternion['y'] = cx * sy * cz + sx * cy * sz
    quaternion['z'] = cx * cy * sz - sx * sy * cz
    quaternion['w'] = cx * cy * cz + sx * sy * sz
    
    return quaternion



def ApproximateUniformScale(scale_matrix):
    """
    Approximates uniform scale from scale matrix, 
    rewritten directly from the Clyde engine.
    "The cube root of the signed volume of the 
     parallelepiped spanned by the axis vectors"

    Args:
        scale_matrix (list): A 3x3 scale matrix.

    Returns:
        float: The approximate uniform scale factor.

    """
    
    # Simplify name
    m = scale_matrix
    
    # Calculate elements of the volume
    vol1 = m[0][0] * (m[1][1] * m[2][2] - m[2][1] * m[1][2])
    vol2 = m[1][0] * (m[2][1] * m[0][2] - m[0][1] * m[2][2])
    vol3 = m[2][0] * (m[0][1] * m[1][2] - m[1][1] * m[0][2])

    scale = float(vol1 + vol2 + vol3) ** float(1/3)
    return scale



def Extract(file_name):

    # Initalize constants
    tag = 'default'

    print('[MODULE][INFO]: Reading input model file...')
    with open(file_name, 'rb') as file:
        geometries     = list()
        mesh           = collada.Collada(file)

    if any(geometry.primitives == [] for geometry in mesh.geometries):
        print('[MODULE][INFO]: Removing empty geometries...')
        mesh.geometries = filter(lambda geometry: geometry.primitives != [], mesh.geometries)
        
    geometries_num = len(mesh.geometries)
    if geometries_num >= 1:
        print(f'[MODULE][INFO]: Found {geometries_num} valid geometries!')
    else:
        raise Exception('Missing model geometry')
        

    # Iterate through all geometries
    for geometry in mesh.geometries:
        
        print(f'[MODULE][INFO]: Processing geometry: "{geometry.id}"')

        ##########################################
        # Materials Library Section
        #
        # - Extract existing materials info
        ##########################################

        materials_list = []
        for material in mesh.materials:
            texture = material.id
            materials_list.append(Material(texture=texture, tag=tag))
        materials = MaterialArray(materials_list)


        ##############################################
        # Geometry Library Section
        #  
        # - Extract vertices, indices and normals
        # - Fix normals if necessary
        # - Calculate min/max extents
        # - Extract connected material name
        # - Initiate primitives
        #
        ##############################################

        def PrimitiveReorder(prim_list, old_indices, new_indices):
            """
            Reorders the primitive data based on the given old and new indices.

            Args:
                prim_list (list): The list of primitive data to be reordered.
                old_indices (list): The list of old indices.
                new_indices (list): The list of new indices.

            Returns:
                list: The reordered primitive data.
            """

            # Don't reorder if indices are the same
            if old_indices == new_indices:
                return prim_list

            # Transitional indices used for reordering data
            indices_trans = dict()
            for i in range(0, len(new_indices)):
                indices_trans[old_indices[i]] = new_indices[i]

            # Initalize output data with empty vertices array
            data = list()
            for _ in range(0, len(prim_list)):
                data.append([0.0] * len(prim_list[0]))

            # Reorder data in separate lists
            for key_old, key_new in indices_trans.items():
                data[key_new] = prim_list[key_old]
            return data


        # Get v, vn and vt, merge all primitives if multiple found
        primitives_list = []
        print('[MODULE][INFO]: Calculating indices...')
        for primitives in geometry.primitives:
            
            if primitives.normal is None or len(primitives.normal) != len(primitives.vertex):
                if type(primitives) is collada.lineset.LineSet:
                    print('[MODULE][WARNING]: Cannot generate normals for LineSet, this set of primitives will be skipped.')
                    continue

                print('[MODULE][INFO]: Generating normals...')
                primitives.generateNormals()

            # Initalize temporary primitives
            v  = primitives.vertex.tolist()
            vn = primitives.normal.tolist()

            vt_list = []
            for texcoords in primitives.texcoordset:
                vt_list.append(texcoords.tolist())

            # Calculate min/max extent for vertices
            print('[MODULE][INFO]: Calculating min/max extents...')

            # Collapse indices subgeometries
            indices_v  = ListFlatten(primitives.vertex_index.tolist())
            indices_vn = ListFlatten(primitives.normal_index.tolist())

            indices_vt_list = []
            for indices in primitives.texcoord_indexset:
                indices_vt_list.append(ListFlatten(indices.tolist()))

            # Select the best candidate for general indices
            indices = sorted([indices_v,indices_vn]+indices_vt_list, key=len, reverse=True)[0]

            print('[MODULE][INFO]: Generalizing indices...')
            v = Vertices(PrimitiveReorder(v, indices_v, indices))
            vn = Normals(PrimitiveReorder(vn, indices_vn, indices))
            for i, vt in enumerate(vt_list):
                vt_list[i] = Texcoords(PrimitiveReorder(vt, indices_vt_list[i], indices))
            vt_list = TexcoordsArray(vt_list)

            indices_end = max(indices)

            # Determine the model mode
            if type(primitives) is collada.lineset.LineSet:
                mode = 'LINES'
                print('[MODULE][WARNING]: Experimental geometry mode: ', type(primitives),
                        ' The results may be faulty.')
                
            elif type(primitives) is collada.triangleset.TriangleSet:
                mode = 'TRIANGLES'
                #print('[MODULE][INFO]: Geometry mode: ', type(primitives))
                
            elif type(primitives) is collada.polylist.Polygon:
                mode = 'POLYGON'
                print('[MODULE][WARNING]: Experimental geometry mode: ', type(primitives),
                        ' The results may be faulty.')
                
            elif type(primitives) is collada.polylist.Polylist:
                mode = 'POLYGON'
                print('[MODULE][WARNING]: Experimental Geometry Mode: ', type(primitives),
                        ' The results may be faulty.')

            else:
                raise Exception(f'Unrecognized geometry mode! '
                                f'Found: {type(primitives)}')

            # Extract connected material
            texture = primitives.material

            # Finalize Primitive
            primitives_list.append(Primitive(vertices=v,
                                             normals=vn,
                                             texcoords=vt_list,
                                             indices=Indices(indices),
                                             mode=mode,
                                             tag=tag,
                                             texture=texture,
                                             indices_end=indices_end))


        ################################################
        # Controllers Library Section
        #
        # - Extract bone indices, weights and names
        # - Limit the bone weights to 4 per vertex
        #   and normalize them
        # - Fetch the controller to be used by armature
        #   hierarchy later on.
        #
        ################################################          


        # Thanks the algorithm Xan
        def WeightNormalize(weights):
            """
            Normalize a list of weights. (Make them add up to 1)

            Parameters:
            weights (list): A list of weights.

            Returns:
            list: A list of normalized weights.
            """
            output_weights = list()

            for weight in weights:
                output_weights.append(weight / sum(weights))

            return output_weights


        # Extract armature data from existing controllers
        # (if they exist)
        if mesh.controllers:
            
            # Look for controllers related to the current geometry
            for geom_ctrl in mesh.controllers:
                if type(geom_ctrl) == collada.controller.Skin and \
                geom_ctrl.geometry.id == geometry.id:

                    print(f'[MODULE][INFO]: Armature found! Processing: "{geom_ctrl.id}"...')

                    # Extract bone names
                    for bone in geom_ctrl.weight_joints.data.tolist():
                        args['bones'] += str(bone)[2:-2] + ', '
                    args['bones'] = args['bones'][:-2]
                    
                    # Extract bone indices and weights
                    bone_slots = list()
                    bone_weight_warn = False
                    for bone_vertex in geom_ctrl.index:
                        bone_indices = list()
                        bone_weights = list()

                        # Extract bone weights and indices for single vertex
                        for bone_index, weight_index in bone_vertex.tolist():
                            bone_indices.append(float(bone_index))

                            for weight in geom_ctrl.weights.data.tolist()[weight_index]:
                                bone_weights.append(float(weight))

                        if len(bone_weights) > 4:

                            # Remove len(bone_vertex)-4 smallest bone weights
                            extra_args = len(bone_vertex) - 4
                            for weight in sorted(bone_weights)[:extra_args]:
                                index = bone_weights.index(weight)
                                del bone_weights[index]
                                del bone_indices[index]
                                
                            # Bone weights need to be normalized, so that they add up to 1
                            bone_weights = WeightNormalize(bone_weights) 

                            if not bone_weight_warn:
                                bone_weight_warn = True
                                print('[MODULE][WARNING]: Unable to handle more than 4 bone '
                                        'weights per vertex. Will cut the extra ones, '
                                        'but the armature may not work properly. '
                                        'Refer to the documentation.')

                        # Fill out the remaining bone slots with 0.0
                        zeros_num = 4 - len(bone_weights)
                        for i in range(0, zeros_num):
                            bone_indices.append(0.0)
                            bone_weights.append(0.0)

                        bone = bone_indices + bone_weights
                        bone_slots.append(bone)
                    
                    # No need to look for more controllers 
                    break



        ###################################################
        # Vertices Finalize Section
        #
        # - Glue Geometry Library and Controllers Library
        #   data together 
        #
        ###################################################


        # List used for triangle data iteration
        iterable_primitives = [vertices_vt, vertices_vn, vertices_v]

        # Append bones to iterable_primitives if they exist
        if args['bones'] != '':
            iterable_primitives.insert(0, bone_slots)

        # Extract vertices, normals and texcoords groups
        # to a single list
        print('[MODULE][INFO]: Calculating vertices, normals, texcoords...')

        points  = list()
        for i in range(0, len(vertices_v)):

            point = str()

            for primitive in iterable_primitives:

                # Raise an exception if any primitive is empty
                if len(primitive) == 0:
                    raise Exception('Data missing in: ', primitive)

                point += str(primitive[i])[1:-1] + ', '

            points.append(point)

        # Del obsolete vars
        del vertices_vt, vertices_vn, vertices_v
        del indices_vn, indices_vt, indices_v
        del min_extent, max_extent
        del iterable_primitives
        
        print('[MODULE][INFO]: Creating vertices array...')
        args['vertices'] = ''.join(points)[:-2]
        del points
        
        if args['bones'] != '':
            del bone_slots



        ##########################################
        # Scenes Library Section
        #
        # - Extract Armature Hierarchy
        # - Create an Armature Hierarchy XML tree
        # - Fix "args['bones']" if possible
        #
        ##########################################


        # ArmatureNodeFinder supports two search modes:
        # - search by connected controllers
        # - search by node name
        #
        # It depends on whether armature_node_name gets passed on
        # If not, controller mode is used
        #
        # This function is a necessity since reading <skeleton>
        # requires manual xml read relying on strings since 
        # PyCollada refuses to read that single node
        # <skeleton> points to the node containing
        # the, as the name sugests, armature/skeleton.
        # Refer to https://github.com/pycollada/pycollada/issues/129
        
        def ArmatureNodeFinder(main_node, funct_mode, armature_node_name=None):
            """
            Recursively searches for an armature node in a Collada scene graph.

            Args:
                main_node (collada.scene.Node): The main node to start the search from.
                funct_mode (str): The mode of operation. Can be 'name' or 'controller'.
                armature_node_name (str, optional): The name of the armature node to search for. Required if funct_mode is 'name'.

            Returns:
                collada.scene.Node or None: The found armature node, or None if not found.
            """

            nonlocal output_node

            # Void all further recursions from this node
            # if found the correct armature node
            if funct_mode == 'name':
                if main_node.id == armature_node_name:
                    output_node = main_node

            if not output_node:

                # Iterate over all children
                for child in main_node.children:

                    # Look for nodes with ControllerNode as a child
                    if funct_mode == 'controller':
                        if type(child) is collada.scene.ControllerNode:
                            if child.controller == geom_ctrl:
                                output_node = main_node

                    # Apply recursion if child is an armature node
                    if type(child) is collada.scene.Node:
                        ArmatureNodeFinder(child, funct_mode, armature_node_name)

        ### BEGIN ArmatureNodeToXML
        def ArmatureNodeToXML(main_node, path=list(), xml_path=list()):
            """
            Converts a Collada armature node to an XML representation.

            Args:
                main_node (collada.scene.Node): The main node of the armature.
                path (list, optional): The path of the current node in the armature hierarchy. Defaults to an empty list.
                xml_path (list, optional): The XML path corresponding to the current node in the XML hierarchy. Defaults to an empty list.

            Returns:
                None (Implied return of the XML tree through nonlocal "root_xml_node" variable)
            """

            # Create a new entry from main_node data
            # Initiate the tree if path is empty
            if xml_path == list():
                xml_entr_node = ET.Element('root')
                nonlocal root_xml_node
                root_xml_node = xml_entr_node
            else:
                xml_entr_node = ET.SubElement(xml_path[-1], 'entry')

            # "sid" is the common reference name for the bones
            # the other attributes are used as a fallback
            # Also, handle an edge case, where for some reason
            # bone nodes lack any name or id
            nonlocal bones_list
            xml_name_node = ET.SubElement(xml_entr_node, 'name')
            
            if 'sid' in main_node.xmlnode.keys():
                xml_name_node.text = main_node.xmlnode.get('sid')
            elif 'name' in main_node.xmlnode.keys():
                xml_name_node.text = main_node.xmlnode.get('name')
            elif 'id' in main_node.xmlnode.keys():
                xml_name_node.text = main_node.id
                
            else:
                nonlocal unnamed_bone_num
                xml_name_node.text = 'UnnamedBone' + str(unnamed_bone_num)
                bones_list.append(xml_name_node.text)
                unnamed_bone_num += 1
                
            # Attempt to use names instead of sid's if possible
            # replacing the names in "bones".
            # It's a necessity since SK often uses names instead of sid's
            # Should be separate from the previous elif's in case the name
            # is not even within the "bones" list.
            if 'name' in main_node.xmlnode.keys():
                
                bone_name = main_node.xmlnode.get('name')

                # I firmly hope that's how these names are created
                bone_sid_from_name = re.sub('[^0-9a-zA-Z]+', '_', bone_name)

                if bone_sid_from_name in bones_list:
                    bone_name_index = bones_list.index(bone_sid_from_name)
                    bones_list[bone_name_index] = bone_name
                    xml_name_node.text = bone_name

            # Handle bone transforms
            xml_trfm_node = ET.SubElement(xml_entr_node, 'transform')
            xml_trfm_node.text = ' '
            
            # Define dict that may or may not be used
            # Used to store Euler XYZ rotation data in angles
            # If the model is using decomposed transforms
            # Default value: 0
            euler_rotations = dict.fromkeys(['x', 'y', 'z'], 0)
            
            # Marker that will signify that Euler rotations
            # need to be converted to quaternion
            euler_rotations_exist = False

            # Handle various transform types
            # It feels redundant but some tags' data 
            # requires additional handling and I'd rather 
            # have them separately if it's ever necessary
            for node_transform in main_node.transforms:

                if type(node_transform) is collada.scene.MatrixTransform:
                    xml_trfm_chld_node = ET.SubElement(xml_trfm_node, 'matrix')
                    xml_trfm_chld_data = node_transform.xmlnode.text.replace(' ', ', ')
                    xml_trfm_chld_node.text = xml_trfm_chld_data

                # Decomposed transforms data below
                elif type(node_transform) is collada.scene.TranslateTransform:
                    xml_trfm_chld_node = ET.SubElement(xml_trfm_node, 'translation')
                    xml_trfm_chld_data = node_transform.xmlnode.text.replace(' ', ', ')
                    xml_trfm_chld_node.text = xml_trfm_chld_data
                
                elif type(node_transform) is collada.scene.ScaleTransform:
                    xml_trfm_chld_node = ET.SubElement(xml_trfm_node, 'scale')

                    nonlocal scale_approx_warn
                    if not scale_approx_warn:
                        print('[MODULE][WARNING]: Uniform scale approximation detected, '
                                'it is not accurate and may break the armature, '
                                'instead of decomposed, use matrix transforms.')
                        scale_approx_warn = True

                    xml_trfm_chld_node.text = str(ApproximateUniformScale(node_transform.matrix))
                    
                # Support only for Blender-specific decomposed transformations
                elif type(node_transform) is collada.scene.RotateTransform:
                    euler_rotations_exist = True
                    
                    # Get rotation element letter in lowercase
                    # Checks the rotation tag SID
                    # Accepts format "rotationX", "rotationY" etc
                    # THAT'S WHY IT'S BLENDER-ONLY, IT SUCKS ASS
                    rotation_elem = node_transform.xmlnode.get('sid')[-1].lower()
                    
                    # Emergency check if it even makes sense
                    if rotation_elem not in euler_rotations.keys():
                        raise Exception(f'Unsupported rotation type: '
                                        f'{node_transform.xmlnode.get("sid")}')
                        
                    # Throw the angle into the euler dict
                    # later it'll get transformed into an xml tag
                    euler_rotations[rotation_elem] = node_transform.angle

                else:
                    raise Exception(f'Unhandled transform type, found: {type(node_transform)}')

                
            # Convert Euler rotation angles to Quaternions
            # If they are found
            if euler_rotations_exist:
                xml_rotn_node = ET.SubElement(xml_trfm_node, 'rotation')
                qtrnon = EulerToQuaternion(euler_rotations)

                # Convert to data from list in XYZW order
                xml_rotn_data = str([qtrnon[x] for x in ['x','y','z','w']])[1:-1]
                
                xml_rotn_node.text = xml_rotn_data


            # There needs to be just any value in the tag, or SK xml parser
            # will commit die instantly with little to no elaboration.
            xml_chld_node = ET.SubElement(xml_entr_node, 'children')
            xml_chld_node.text = ' '   

            if any(isinstance(val, collada.scene.Node) for val in main_node.children):
                
                path.append(main_node)
                xml_path.append(xml_chld_node)
                
                for child in main_node.children:
                    if type(child) is collada.scene.Node:
                        ArmatureNodeToXML(child, path, xml_path)
                    
                path.pop(-1)
                xml_path.pop(-1)
        ### END ArmatureNodeToXML

        # Try to extract the armature hierarchy
        # only if bones were exported previously.
        if args['bones'] != '':
                
            # Requires two separate loops
            # First, find the parent node of <skeleton> xml node
            # Second, find the aforementioned
            # armature starting node by its name.
            mode_order = ['controller', 'name']
            armature_node_name = None
            print('[MODULE][INFO]: Extracting armature hierarchy...')

            for funct_mode in mode_order:

                output_node = None
                
                # Since main scene node may have multiple children
                # we'll have to blanket-iterate over them all
                for scene_node in mesh.scenes[0].nodes:
                    ArmatureNodeFinder(scene_node, funct_mode, armature_node_name)
                    if output_node:
                        break

                if not output_node:
                    args['bones'] = ''
                    print('[MODULE][WARNING]: Unable to locate the armature '
                            'starting joint node, file may be corrupted. '
                            'Armature will not be imported.')
                    break

                # Read the <skeleton> xml node data manually.
                if funct_mode == 'controller':
                    for xml_node in output_node.xmlnode.iter():
                        if 'skeleton' in xml_node.tag:
                            armature_node_name = xml_node.text.replace('#','')
                            break
                

            # root_xml_node, bones_list and unnamed_bone_num
            # need to be accessible outside and inside
            # the recursions, as the root_xml_node is practically
            # the xmltree output, bones_list contains fixed args['bones']
            # unnamed_bone_num has to retain its value over recursions
            # to prevent repetitions in generated bone names
            root_xml_node = None
            bones_list = args['bones'].split(', ')
            armature_node = output_node
            unnamed_bone_num = 0

            # Warning issued if uniform scale approximation is detected
            # It sucks, it seriously, seriously sucks, so the user should know
            # Var has to be defined outside of the function so that 
            # it can be sent just once
            scale_approx_warn = False


            if args['bones'] != '':
                print('[MODULE][INFO]: Creating armature xml tree...')
                ArmatureNodeToXML(armature_node)
                args['bones'] = str(bones_list)[1:-1].replace("'", "")
                args['bone_tree'] = ET.tostring(root_xml_node, encoding='unicode')


        geometries_num -= 1
        print(f'[MODULE][INFO]: Done! {geometries_num} remaining.')
        gc.collect()
        geometries.append(args)

    return geometries
