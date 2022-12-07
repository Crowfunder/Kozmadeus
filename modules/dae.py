import gc
import collada
import xml.etree.ElementTree as ET

module_data = {
    'Name'       : 'Collada',
    'Mesh'       : True,
    'Armature'   : True,
    'Animations' : False,
    'Multimesh'  : True
}


# Function for list flattening, regardless of depth.
def ListFlatten(input_list):

    while type(input_list[0]) is list:
        input_list = [item for sublist in input_list for item in sublist]

    return input_list


def Extract(file_name):
    with open(file_name, 'rb') as file:
        geometries     = list()
        mesh           = collada.Collada(file)
        
        print('Reading input model file...')
        
        geometries_num = len(mesh.geometries)
        if geometries_num > 1:
            print(f'Found {geometries_num} geometries!')

        # Iterate through all geometries
        for geometry in mesh.geometries:
            
            print(f'Processing geometry: "{geometry.id}"')
            
            # Initalize some vars
            args        = dict()
            indices     = list()
            vertices_v  = list()
            vertices_vn = list()
            vertices_vt = list()
            args['bones']      = ''
            args['min_extent'] = list()
            args['max_extent'] = list()

            if len(geometry.primitives) > 1:
                print('Found ', len(geometry.primitives),
                      ' primitives, will try to merge...')
                print('Warning: Merging primitives may '
                      'cause several issues, it is '
                      'recommended to merge them manually.')

            
            ##############################################
            # Geometry Library Section
            # 
            # - Extract vertices, indices and normals
            # - Merge/triangulate primitives if necessary
            # - Fix normals if necessary
            #
            ##############################################

            # Function used for reordering data to comply
            # with new indices
            def PrimitiveReorder(prim_list, old_indices, new_indices):

                # Transitional indices used for reordering data
                indices_trans = dict()
                data = list()

                # Populate transitional indices and
                # data template
                for i in range(0, len(new_indices)):
                    indices_trans[old_indices[i]] = new_indices[i]
                    data.append((0.0, 0.0))

                # Reorder data in separate lists
                for key_old, key_new in indices_trans.items():
                    data[key_new] = prim_list[key_old]

                return data


            # Check if model modes are the same
            # if not triangulate or remove LineSets
            old_mode = type(geometry.primitives[0])
            flag_mode_convert = False
            
            for primitives in geometry.primitives:
                
                if primitives.normal is not None:
                    if len(primitives.normal) != len(primitives.vertex):
                        
                        print('Will triangulate geometries to fix '
                            'missing normals, if necessary...')
                        flag_mode_convert = True
                        break

                elif type(primitives) != old_mode:

                    flag_mode_convert = True
                    break
                
                old_mode = type(primitives)


            # Get v, vn and vt, merge all primitives if multiple found
            indices_end = -1
            print('Calculating indices...')
            for primitives in geometry.primitives:

                # Warnings for unlikely, albeit possible cases
                # that are not handled right now
                if len(primitives.texcoordset) > 1:
                    print('Warning: Unable to handle more than '
                          'one set of UV mappings, falling back '
                          'to the first one found.')

                if flag_mode_convert and type(primitives) is collada.lineset.LineSet:
                    print('Warning: Unable to triangulate a LineSet, ' 
                          'this set of primitives will be skipped.')

                else:

                    if flag_mode_convert and type(primitives) is not collada.triangleset.TriangleSet:
                        print('Triangulating geometries to merge...')
                        primitives = primitives.triangleset()

                    if len(primitives.normal) != len(primitives.vertex):
                        print('Generating normals...')
                        primitives.generateNormals()

                    # Initalize temporary primitives
                    v  = primitives.vertex.tolist()
                    vn = primitives.normal.tolist()
                    vt = primitives.texcoordset[0].tolist()

                    # Collapse indices subgeometries
                    indices_v  = ListFlatten(primitives.vertex_index.tolist())
                    indices_vn = ListFlatten(primitives.normal_index.tolist())
                    indices_vt = ListFlatten(primitives.texcoord_indexset[0].tolist())

                    # If primitives don't follow the same indices
                    # as vertices, reorder them
                    if indices_vn != indices_v:
                        print('Reordering normals to match vertex indices...')
                        vn = PrimitiveReorder(vn, indices_vn, indices_v)
                        
                    if indices_vt != indices_v:
                        print('Reordering texcoords to match vertex indices...')
                        vt = PrimitiveReorder(vt, indices_vt, indices_v)
                        
                    # Append the finished vertices to final primitives
                    vertices_v  += v
                    vertices_vn += vn
                    vertices_vt += vt
                    
                    # Calculate indices
                    for index in indices_v:
                        indices.append(index + indices_end + 1)

                    indices_end = max(indices)


            # Determine the model mode
            if type(primitives) is collada.lineset.LineSet:
                args['mode'] = 'LINES'
                print('Warning: Experimental geometry mode: ', type(primitives),
                      '\nThe results may be faulty.')
                
            elif type(primitives) is collada.triangleset.TriangleSet:
                args['mode'] = 'TRIANGLES'
                
            elif type(primitives) is collada.polylist.Polygon:
                args['mode'] = 'QUADS'
                print('Warning: Experimental geometry mode: ', type(primitives),
                      '\nThe results may be faulty.')
                
            elif type(primitives) is collada.polylist.Polylist:
                args['mode'] = 'QUADS'
                print('Warning: Experimental Geometry Mode: ', type(primitives),
                      '\nThe results may be faulty.')
                
            else:
                raise Exception('Unrecognized geometry mode!'
                                '\nFound:', type(primitives))
                
            # Finalize Indices
            args['indices']     = str(indices)[1:-1]
            args['indices_end'] = str(indices_end)


            ################################################
            # Controllers Library Section
            #
            # - Extract bone indices, weights and names
            # - Fetch the controller to be used by armature
            #   hierarchy later on.
            #
            ################################################          

            # Extract armature data from existing controllers
            # (if they exist)
            if mesh.controllers:
                
                # Look for controllers related to the current geometry
                for geom_ctrl in mesh.controllers:
                    if type(geom_ctrl) == collada.controller.Skin:
                        if geom_ctrl.geometry.id == geometry.id:
                            print(f'Armature found! Processing: "{geom_ctrl.id}"')

                            # Extract bone names
                            for bone in geom_ctrl.weight_joints.data.tolist():
                                args['bones'] += str(bone)[2:-2] + ', '
                            args['bones'] = args['bones'][:-2]
                            
                            # Extract bone indices and weights
                            bone_slots = list()
                            for bone_vertex in geom_ctrl.index:
                                bone_indices = list()
                                bone_weights = list()
                                zeros_num = 4 - len(bone_vertex)
                                if len(bone_vertex) > 4:
                                    zeros_num = 0
                                    bone_vertex = bone_vertex[0:4]
                                    print('Warning: Unable to handle more than 4 bone '
                                          'weights per vertex. Will cut the extra ones, '
                                          'but the armature may not work properly.')
                                   # raise Exception('Unable to handle more than 4 bone '
                                   #                 'weights per vertex.')

                                # Extract bone weights and indices for single vertex
                                for bone_index, weight_index in bone_vertex.tolist():
                                    bone_indices.append(float(bone_index))

                                    for weight in geom_ctrl.weights.data.tolist()[weight_index]:
                                        bone_weights.append(float(weight))

                                # Fill out the remaining bone slots with 0.0
                                for i in range(0, zeros_num):
                                    bone_indices.append(0.0)
                                    bone_weights.append(0.0)

                                bone = bone_indices + bone_weights
                                bone_slots.append(bone)
                                
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
            print('Calculating vertices, normals, texcoords...')

            points  = list()
            for i in range(0, len(vertices_v)):

                point = str()

                for primitive in iterable_primitives:

                    # Raise an exception if any primitive is empty
                    if len(primitive) == 0:
                        raise Exception('Data missing in\n', primitive)

                    point += str(primitive[i])[1:-1] + ', '

                points.append(point)

            # Calculate min/max extent for vertices
            print('Calculating min/max extents...')
            
            # Initialize values with first vertex
            # by creating a copy, not a reference
            min_extent = vertices_v[0][:]
            max_extent = vertices_v[0][:]

            # Iterate through vertices to find min/max
            for vertex in vertices_v:
                for index, point in enumerate(vertex):
                    min_extent[index] = min(min_extent[index], vertex[index])
                    max_extent[index] = max(max_extent[index], vertex[index])

            args['min_extent'] = str(min_extent)[1:-1]
            args['max_extent'] = str(max_extent)[1:-1]

            # Del obsolete vars
            del vertices_vt, vertices_vn, vertices_v
            del indices_vn, indices_vt, indices_v
            del min_extent, max_extent
            del iterable_primitives
            
            print('Creating vertices array...')
            args['vertices'] = ''.join(points)[:-2]
            del points
            
            if args['bones'] != '':
                del bone_slots
                
                
            ##########################################
            # Scenes Library Section
            #
            # - Extract Armature Hierarchy
            # - Create an Armature Hierarchy XML tree
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


            # Try to extract the armature hierarchy
            # only if bones were exported previously.
            if args['bones'] != '':
                    
                # Requires two separate loops
                # First, find the parent node of <skeleton> xml node
                # Second, find the aforementioned
                # armature starting node by its name.
                mode_order = ['controller', 'name']
                armature_node_name = None
                print('Extracting armature hierarchy...')

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
                        print('Warning: Unable to locate the armature '
                            'starting joint node, file may be corrupted.'
                            '\nArmature will not be imported.')
                        break

                    # Read the <skeleton> xml node data manually.
                    if funct_mode == 'controller':
                        for xml_node in output_node.xmlnode.iter():
                            if 'skeleton' in xml_node.tag:
                                armature_node_name = xml_node.text.replace('#','')
                                break
                    

                # root_xml_node and unnamed_bone_num
                # need to be accessible outside and inside
                # the recursions, as the former is practically
                # the ArmatureTreeToXML output, and the latter
                # has to retain its value over recursions
                # to prevent repetitions in generated bone names
                root_xml_node = None
                armature_node = output_node
                unnamed_bone_num = 0

                def ArmatureNodeToXML(main_node, path=list(), xml_path=list()):

                    # Create a new entry from main_node data
                    # Initiate the tree if path is empty
                    if xml_path == list():
                        xml_entr_node = ET.Element('entry')
                        nonlocal root_xml_node
                        root_xml_node = xml_entr_node
                    else:
                        xml_entr_node = ET.SubElement(xml_path[-1], 'entry')

                    # "sid" is the common reference name for the bones
                    # the other attributes are used as a fallback
                    # Also, handle an edge case, where for some reason
                    # bone nodes lack any name or id
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
                        args['bones'] += xml_name_node.text
                        unnamed_bone_num += 1

                    if xml_name_node.text == '%ROOT%':
                        xml_name_node.text = 'ROOT_renamed_bone_' + str(unnamed_bone_num)
                        args['bones'] += xml_name_node.text
                        unnamed_bone_num += 1

                    xml_trfm_node = ET.SubElement(xml_entr_node, 'transform')

                    # There shouldn't be more than a single transform
                    # but better safe than sorry
                    for node_transform in main_node.transforms:
                        if type(node_transform) is collada.scene.MatrixTransform:
                            
                            xml_mtrx_node = ET.SubElement(xml_trfm_node, 'matrix')
                            xml_mtrx_data = ListFlatten(node_transform.matrix.tolist())
                            xml_mtrx_data = str(xml_mtrx_data)[1:-1]
                            xml_mtrx_node.text = xml_mtrx_data
                            
                        else:
                            raise Exception('Unhandled transform type, found ', type(node_transform))

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


                if args['bones'] != '':
                    print('Creating armature xml tree...')
                    ArmatureNodeToXML(armature_node)
                    args['bone_tree'] = ET.tostring(root_xml_node, encoding='unicode')

            geometries_num -= 1
            print(f'Done! {geometries_num} remaining.')
            gc.collect()
            geometries.append(args)

        return geometries
