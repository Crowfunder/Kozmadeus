###############################################################
# by Crowfunder                                               #
# Copyright my ass but also the GPL-3.0 License               #
# Github: https://github.com/Crowfunder                       #
###############################################################

import gc
import re
import collada

from components.model import *


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



def Extract(file_name):

    # I'm still not sure how the tag works in the engine, it can stay as default
    # since it checks both texture name and tag to connect primitives to materials
    # tag itself *probably* shouldn't affect anything.
    # TODO: Check the engine source if it *really* doesn't affect anything
    material_tag = 'default'

    print('[MODULE][INFO]: Reading input model file...')
    models     = []
    mesh           = collada.Collada(file_name)

    geometries = mesh.geometries
    if any(geometry.primitives == [] for geometry in mesh.geometries):
        print('[MODULE][INFO]: Removing empty geometries...')
        geometries = [geometry for geometry in geometries if geometry.primitives != []]

    geometries_num = len(geometries)
    if geometries_num > 0:
        print(f'[MODULE][INFO]: Found {geometries_num} valid geometries!')
    else:
        raise Exception('Missing model geometry')


    # Iterate through all geometries
    for geometry in geometries:

        print(f'[MODULE][INFO]: Processing geometry: "{geometry.id}"')
        materials = ExtractMaterials(material_tag, mesh)
        primitives, old_vertex_indices = ExtractGeometries(geometry, material_tag)
        if mesh.controllers:
            controller = ExtractControllers(mesh, geometry, primitives, old_vertex_indices)
        else:
            controller = None

        if mesh.scenes and controller is not None:
            armature = ExtractArmature(mesh=mesh, primitives=primitives, controller=controller)
        else:
            armature = None

        geometries_num -= 1
        print(f'[MODULE][INFO]: Done! {geometries_num} remaining.')
        gc.collect()
        models.append(Model(primitives=primitives, materials=materials, armature=armature))

    return models



def ExtractMaterials(material_tag, mesh):
    '''
    Materials Library Section

    - Extract existing materials info
    '''
    print(f'[MODULE][INFO]: Found {len(mesh.materials)} materials, extracting...')
    materials_list = []
    for material in mesh.materials:
        texture = material.id
        materials_list.append(Material(texture=texture, tag=material_tag))
    return MaterialArray(materials_list)


def ExtractGeometries(geometry, material_tag):
    '''
    Geometry Library Section
    
    - Extract vertices, indices and normals
    - Fix normals if necessary
    - Generalize indices
    - Extract connected material name
    - Initiate primitives
    '''
    primitives_list = []
    old_vertex_indices = []

    for collada_primitive in geometry.primitives:
        if collada_primitive.normal is None or len(collada_primitive.normal) != len(collada_primitive.vertex):

            if type(collada_primitive) is collada.lineset.LineSet or type(collada_primitive) is collada.polylist.Polylist:
                print('[MODULE][WARNING]: Cannot generate normals for LineSet/PolyList, this set of primitives will be skipped.')
                continue

            print('[MODULE][INFO]: Generating normals...')
            collada_primitive.generateNormals()

        # Initalize temporary primitives
        v  = collada_primitive.vertex.tolist()
        vn = collada_primitive.normal.tolist()

        vt_list = []
        for texcoords in collada_primitive.texcoordset:
            vt_list.append(texcoords.tolist())

        # Collapse indices subgeometries
        indices_v  = ListFlatten(collada_primitive.vertex_index.tolist())
        indices_vn = ListFlatten(collada_primitive.normal_index.tolist())

        indices_vt_list = []
        for indices in collada_primitive.texcoord_indexset:
            indices_vt_list.append(ListFlatten(indices.tolist()))

        # Save old vertex indices to use when reordering bone weight/index data
        old_vertex_indices.append(indices_v)

        # Select the best candidate for general indices
        indices = sorted([indices_v,indices_vn]+indices_vt_list, key=len, reverse=True)[0]

        #print('[MODULE][INFO]: Generalizing indices...')   # TODO: would be great to have a LogOnce method...
        v = Vertices(ListFlatten(PrimitiveReorder(v, indices_v, indices)))
        vn = Normals(ListFlatten(PrimitiveReorder(vn, indices_vn, indices)))
        for i, vt in enumerate(vt_list):
            vt_list[i] = Texcoords(ListFlatten(PrimitiveReorder(vt, indices_vt_list[i], indices)))
        vt_list = TexcoordsArray(vt_list)

        # Determine the primitive mode
        if type(collada_primitive) is collada.lineset.LineSet:
            mode = 'LINES'
            print('[MODULE][WARNING]: Experimental geometry mode: ', type(collada_primitive),
                        ' The results may be faulty.')
                
        elif type(collada_primitive) is collada.triangleset.TriangleSet:
            mode = 'TRIANGLES'
            #print('[MODULE][INFO]: Geometry mode: ', type(collada_primitive))
                
        elif type(collada_primitive) is collada.polylist.Polygon:
            mode = 'POLYGON'
            print('[MODULE][WARNING]: Experimental geometry mode: ', type(collada_primitive),
                        ' The results may be faulty.')
                
        elif type(collada_primitive) is collada.polylist.Polylist:
            mode = 'POLYGON'
            print('[MODULE][WARNING]: Experimental Geometry Mode: ', type(collada_primitive),
                        ' The results may be faulty.')

        else:
            raise Exception(f'Unrecognized geometry mode! '
                            f'Found: {type(collada_primitive)}')

        # Extract connected material
        texture = collada_primitive.material

        # Finalize Primitive
        primitives_list.append(Primitive(vertices=v,
                                         normals=vn,
                                         texcoords=vt_list,
                                         indices=Indices(indices),
                                         mode=mode,
                                         tag=material_tag,
                                         texture=texture))

    if not primitives_list:
        raise Exception('No valid primitives found in the model')

    return PrimitiveWrapper(primitives_list), old_vertex_indices


def ExtractControllers(mesh, geometry, primitives, old_vertex_indices):
    '''
    Controllers Library Section
    - Extract bone indices, weights and names
    - Limit the bone weights to 4 per vertex
      and normalize them
    - Fetch the controller to be used for finding armature
      hierarchy later on.
    '''

    # TODO: So basically, there are two options how this is supposed to work
    # A - Separate bone data based on indices_end primitive offsets into their primitives (present)
    # B - If all primitives indeed use the same set of vertices (both have 524 in this case) just copypaste bone data into all primitives with matching vertices
    #     Can be sanity-checked while iterating over all primitives by comparing to their original vertex indices (if they align with bone vertices)

    bones = []
    controller = None

    primitive_bone_indices = []
    primitive_bone_weights = []
    primitive_vertex_indices = []

    # Look for controllers related to the current geometry
    for controller in mesh.controllers:
        if isinstance(controller, collada.controller.Skin) and \
                controller.geometry.id == geometry.id:
            print(f'[MODULE][INFO]: Controller found! Processing: "{controller.id}"...')

            # Extract bone names, stored in a fairly weird way so has to be retrieved like that
            bones = ListFlatten(controller.weight_joints.data.tolist())

            bone_weight_warn = False
            for bone_vertex in controller.index:
                bone_indices = []
                bone_weights = []

                # Extract bone weights and indices for single vertex
                for bone_index, bone_weight_index in bone_vertex:
                    bone_indices.append(float(bone_index))

                    for weight in controller.weights.data[bone_weight_index]:
                        bone_weights.append(float(weight))

                    primitive_vertex_indices.append(bone_weight_index)

                if len(bone_weights) > 4:
                    # Remove len(bone_vertex)-4 smallest bone weights
                    for weight in sorted(bone_weights)[:len(bone_vertex)-4]:
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
                for _ in range(zeros_num):
                    bone_indices.append(0.0)
                    bone_weights.append(0.0)

                primitive_bone_indices.append(bone_indices)
                primitive_bone_weights.append(bone_weights)

            # No need to look for more controllers
            break

    if not controller:
        return None

    for i, primitive in enumerate(primitives):
        if len(primitive.vertices) == len(primitive_bone_indices) \
                and len(primitive.vertices) == len(primitive_bone_weights):
            old_indices = old_vertex_indices[i]
            new_indices = primitive.indices.data
            primitive_bone_indices = ListFlatten(PrimitiveReorder(primitive_bone_indices, old_indices, new_indices))
            primitive_bone_weights = ListFlatten(PrimitiveReorder(primitive_bone_weights, old_indices, new_indices))
            primitives[i] = PrimitiveAddSkin(primitive=primitive, bones=Bones(bones), vertex_attribs=VertexAttribArray([BoneIndices(primitive_bone_indices), BoneWeights(primitive_bone_weights)]))

    return controller


def ExtractArmature(mesh, primitives, controller):
    '''
    Scenes Library Section

    - Extract ArmatureNode Hierarchy
    - Fix Bones if possible
    '''

    # These functions are a necessity since reading <skeleton>
    # requires manual xml read relying on strings, as
    # PyCollada refuses to read that single node
    # <skeleton> points to the node containing
    # the, as the name sugests, armature/skeleton.
    # Refer to https://github.com/pycollada/pycollada/issues/129        
    def ArmatureFindNodeByController(main_node, controller):
        """
        Recursively searches for an armature node connected to specified controller in a Collada scene graph.

        Args:
            main_node (collada.scene.Node): The main collada node to start the search from.
            controller (collada.controller.Skin): Current geometry controller.

        Returns:
            None (Implied return of collada.scene.Node or None (if not found) in located_armature_node_ctrl nonlocal var)
        """

        nonlocal collada_controller_node
        if not collada_controller_node:
            for child in main_node.children:

                # Look for nodes with ControllerNode as a child and 
                # check if it's the current geometry controller
                if type(child) is collada.scene.ControllerNode \
                    and child.controller == controller:
                    collada_controller_node = main_node

                # Apply recursion if child is an armature node
                if type(child) is collada.scene.Node:
                    ArmatureFindNodeByController(child, controller)


    def ArmatureFindNodeByName(main_node, armature_node_name):
        """
        Recursively searches for an armature node with a specified name in a Collada scene graph.

        Args:
            main_node (collada.scene.Node): The main collada node to start the search from.
            armature_node_name (str, optional): The name of the armature node to search for.

        Returns:
            None (Implied return of collada.scene.Node or None (if not found) in collada_main_node nonlocal var)
        """

        nonlocal collada_main_node

        # Void all further recursions from this node
        # if found the correct armature node
        if armature_node_name and main_node.id == armature_node_name:
            collada_main_node = main_node

        if not collada_main_node:

            # Iterate over all children
            for child in main_node.children:

                # Apply recursion if child is an armature node
                if type(child) is collada.scene.Node:
                    ArmatureFindNodeByName(child, armature_node_name)


    def ColladaNodeToObj(collada_node, collada_path=[], obj_path=[]):
        """
        Converts a Collada armature node to a unified ArmatureNode object representation.

        Args:
            collada_node (collada.scene.Node): The main node of the armature in collada.
            collada_path (list, optional): The path of the current node in the armature hierarchy. Defaults to an empty list.
            obj_path (list, optional): The  path corresponding to the current node in the XML hierarchy. Defaults to an empty list.

        Returns:
            None (Implied return of the ArmatureNode tree through nonlocal "armature_root_node" variable)
        """

        # "sid" is the common reference name for the bones
        # the other attributes are used as a fallback
        # Also, handle an edge case, where for some reason
        # bone nodes lack any name or id
        nonlocal bones_list

        if 'sid' in collada_node.xmlnode.keys():
            obj_name = collada_node.xmlnode.get('sid')
        elif 'name' in collada_node.xmlnode.keys():
            obj_name = collada_node.xmlnode.get('name')
        elif 'id' in collada_node.xmlnode.keys():
            obj_name = collada_node.id

        else:
            nonlocal unnamed_bone_num
            obj_name = 'UnnamedBone' + str(unnamed_bone_num)
            bones_list.append(obj_name)
            unnamed_bone_num += 1

        # Attempt to use names instead of sid's if possible
        # replacing the names in "bones".
        # It's a necessity since SK often uses names instead of sid's
        # Should be separate from the previous elif's in case the name
        # is not even within the "bones" list.
        if 'name' in collada_node.xmlnode.keys():

            bone_name = collada_node.xmlnode.get('name')

            # I firmly hope that's how these names are created
            bone_sid_from_name = re.sub('[^0-9a-zA-Z]+', '_', bone_name)

            if bone_sid_from_name in bones_list:
                bone_name_index = bones_list.index(bone_sid_from_name)
                bones_list[bone_name_index] = bone_name
                obj_name = bone_name

        # Handle bone transforms
        transforms_list = []

        # Define dict that may or may not be used
        # Used to store Euler XYZ rotation data in angles
        # If the model is using decomposed transforms
        # Necessary since all rotation angles are stored as
        # separate tags in collada
        # Default value: 0
        euler_rotations = dict.fromkeys(['x', 'y', 'z'], 0)
        euler_rotations_exist = False

        # Handle various transform types
        for node_transform in collada_node.transforms:
            data = [float(i) for i in node_transform.xmlnode.text.split()]

            if type(node_transform) is collada.scene.MatrixTransform:
                transforms_list.append(Matrix(data))

        # Decomposed transforms data below
            elif type(node_transform) is collada.scene.TranslateTransform:
                transforms_list.append(Translation(data))

            elif type(node_transform) is collada.scene.ScaleTransform:
                transforms_list.append(Scale(data))
                nonlocal scale_approx_warn
                if not scale_approx_warn and len(data) != 1:
                    print('[MODULE][WARNING]: Uniform scale approximation detected, '
                            'it is not accurate and may break the armature, '
                            'instead of decomposed, use matrix transforms.')
                    scale_approx_warn = True

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
            transforms_list.append(Rotation([euler_rotations[i] for i in ['x','y','z']]))

        obj_transform = Transform(transforms_list)

        # Create a new entry from collada_node data
        # Initiate the tree if path is empty
        if obj_path == []:
            obj_node = ArmatureNode(transform=obj_transform, name=obj_name)
            nonlocal armature_root_node
            armature_root_node = obj_node
        else:
            obj_node = ArmatureNode(transform=obj_transform, parent=obj_path[-1], name=obj_name)

        if any(isinstance(val, collada.scene.Node) for val in collada_node.children):
            collada_path.append(collada_node)
            obj_path.append(obj_node)

            for child in collada_node.children:
                if isinstance(child, collada.scene.Node):
                    ColladaNodeToObj(child, collada_path, obj_path)

            collada_path.pop(-1)
            obj_path.pop(-1)


    # Requires two separate loops
    # First, find the parent node of <skeleton> xml node
    # Second, find the aforementioned
    # armature starting node by its name.
    print('[MODULE][INFO]: Searching for armature starting node...')

    collada_controller_node = None
    for scene in mesh.scenes:
        for scene_node in scene.nodes:
            ArmatureFindNodeByController(scene_node, controller)
            if collada_controller_node:
                break

    # Read the <skeleton> xml node data manually.
    collada_main_node_name = None
    for xml_node in collada_controller_node.xmlnode.iter():
        if 'skeleton' in xml_node.tag:
            collada_main_node_name = xml_node.text.replace('#','')
            break

    collada_main_node = None
    if collada_main_node_name:
        for scene in mesh.scenes:
            for scene_node in scene.nodes:
                ArmatureFindNodeByName(scene_node, collada_main_node_name)
                if collada_main_node:
                    break

    if not collada_controller_node or not collada_main_node:
        print('[MODULE][WARNING]: Unable to locate the armature '
                'starting joint node, file may be corrupted. '
                'Armature will not be imported.')
        return None

    # root_xml_node, bones_list and unnamed_bone_num
    # need to be accessible outside and inside
    # the recursions, as the root_xml_node is practically
    # the ArmatureNode tree output, bones_list contains fixed args['bones']
    # unnamed_bone_num has to retain its value over recursions
    # to prevent repetitions in generated bone names
    armature_root_node = None
    unnamed_bone_num = 0

    # Warning issued if uniform scale approximation is detected
    # It sucks, it seriously, seriously sucks, so the user should know
    scale_approx_warn = False

    # Any bones list will do as all skinned primitives share the same array of bones, thanks collada.
    bones_list = [primitive.bones.data for primitive in primitives if type(primitive) is SkinnedPrimitive][0]

    print('[MODULE][INFO]: Extracting armature tree...')
    ColladaNodeToObj(collada_main_node)
    for primitive in primitives:
        if type(primitive) is SkinnedPrimitive:
            primitive.bones = Bones(bones_list)

    return armature_root_node


# Thanks the algorithm Xan
def WeightNormalize(weights):
    """
    Normalize a list of weights. (Make them add up to 1)

    Parameters:
    weights (list): A list of weights.

    Returns:
    list: A list of normalized weights.
    """
    output_weights = []

    for weight in weights:
        output_weights.append(weight / sum(weights))

    return output_weights


def GetPrimitiveIndexByIndex(primitive_wrapper: PrimitiveWrapper, index):
    """
    Retrieves index of primitive object from the list of visible primitives based on the given index in given PrimitiveWrapper, as if they were merged.

    Parameters:
        primitive_wrapper (PrimitiveWrapper): PrimitiveWrapper object to retireve from
        index (int): The index of the primitive to retrieve.

    Returns:
        int or None: The index of the primitive object corresponding to the given index in given PrimitiveWrapper, or None if not found.
    """
    offset = 0
    primitive_index = 0
    for primitive in primitive_wrapper.visible:
        primitive_offset = primitive.indices_end + offset
        if index <= primitive_offset:
            return primitive_index
        offset += primitive.indices_end
        primitive_index += 1
    return None


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
    indices_trans = {}
    for i in range(min(len(new_indices), len(old_indices))):
        indices_trans[old_indices[i]] = new_indices[i]

    # Initalize output data with empty vertices array
    data = []
    for _ in range(max(max(new_indices+old_indices), len(prim_list))):  # What is actually wrong with you
        data.append([0.0] * len(prim_list[0]))

    # Reorder data in separate lists
    for key_old, key_new in indices_trans.items():  # TODO: uwzględnij pomijane primitives
        data[key_new] = prim_list[key_old]
    return data
