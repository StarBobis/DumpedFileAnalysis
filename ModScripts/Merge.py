from TailorUtil import *


def get_first_real_index_from_trianglelist_indices(element_name_test, input_trianglelist_indices, tmp_max_vertex_count):
    print("当前查找的数量：" + str(tmp_max_vertex_count))
    print("从trianglelist中找到含有此element的第一个索引")
    # 从input_trianglelist_indices中选出VertexCount最大的
    # 按顺序找第一个含有此element真实数据的索引
    print("按顺序找第一个含有此element真实数据的索引")
    print("当前查找的ELEMENT元素名称为：" + str(element_name_test))
    print(input_trianglelist_indices)
    find_ib_index = ""
    for ib_index in input_trianglelist_indices:
        print("当前测试的索引为：" + str(ib_index))
        extract_vb_file = vertex_config[element_name_test.decode()]["extract_vb_file"]
        print("当前提取的槽位为：" + str(extract_vb_file))
        filter_vb_filenames = get_filter_filenames(ib_index + "-" + extract_vb_file, ".txt")
        print("正在匹配文件：" + str(filter_vb_filenames))
        if len(filter_vb_filenames) == 0:
            continue
        trianglelist_file_name = filter_vb_filenames[0]
        # print(trianglelist_file_name)

        file_vertex_count = get_attribute_from_txtfile(trianglelist_file_name, "vertex count")
        # print("file_vertex_count")
        # print(file_vertex_count)
        if file_vertex_count != tmp_max_vertex_count:
            continue

        vb_file = open(WorkFolder + trianglelist_file_name, "rb")
        vb_file_lines = vb_file.readlines()
        # 读取第一个VertexDataChunk,并去除相同值

        meet_first_vertex_data = False
        element_name_vertex_data_dict = {}
        data_time_dict = {}
        # 要顺便统计每个Data出现的频率
        for line in vb_file_lines:
            if line.startswith(extract_vb_file.encode()):
                meet_first_vertex_data = True

            if meet_first_vertex_data and line == b"\r\n":
                break

            if meet_first_vertex_data:
                line_vertex_data = VertexData(line)
                element_name_vertex_data_dict[line_vertex_data.element_name] = line_vertex_data.data
                if data_time_dict.get(line_vertex_data.data) is None:
                    data_time_dict[line_vertex_data.data] = 1
                else:
                    data_time_dict[line_vertex_data.data] = data_time_dict.get(line_vertex_data.data) + 1
        print("oooooooooo")
        print(element_name_vertex_data_dict)
        print(data_time_dict)

        real_element_list = []
        for element_name in element_name_vertex_data_dict:
            data = element_name_vertex_data_dict.get(element_name)
            if data_time_dict.get(data) == 1:
                real_element_list.append(element_name)

            if data_time_dict.get(data) == 2 and element_name.startswith(b"TEXCOORD"):
                real_element_list.append(element_name)

        # print(real_element_list)

        if element_name_test in real_element_list:
            # print("find real value")
            find_ib_index = ib_index
            break
    print("最终找到的索引为：" + str(find_ib_index))
    if find_ib_index is None or "" == find_ib_index:
        print("Error! 无法找到此ELEMENT所在trianglelist文件的索引！")

    return find_ib_index


def get_pointlist_and_trianglelist_info_location(info_location):
    print(split_str)
    print("Execute: {get_pointlist_and_trianglelist_info_location}")
    print("The elements need to read is: " + str(info_location.keys()))
    pointlist_info_location = {}
    trianglelist_info_location = {}

    element_names = list(info_location.keys())
    # 这里应该使用生成的info_location的，而不是直接读取的

    for element_name in element_names:
        if vertex_config[element_name.decode()]["extract_tech"] == "pointlist":
            pointlist_info_location[element_name] = vertex_config[element_name.decode()]["extract_vb_file"]

        if vertex_config[element_name.decode()]["extract_tech"] == "trianglelist":
            trianglelist_info_location[element_name] = vertex_config[element_name.decode()]["extract_vb_file"]

    # Convenient for us to observe the processing result
    print("pointlist_info_location: ")
    print(pointlist_info_location)
    print("trianglelist_info_location: ")
    print(trianglelist_info_location)
    print(split_str)

    return pointlist_info_location, trianglelist_info_location


def calculate_category_hash_and_slot(pointlist_info_location, trianglelist_info_location, input_trianglelist_indices):
    # (1) split the info_location based on config file element's extract_tech.
    # 这里根据pointlist_indices索引和pointlist_info_location，得到对应vb的hash值。
    unique_pointlist_vb_list = list(set(list(pointlist_info_location.values())))
    unique_trianglelist_vb_list = list(set(list(trianglelist_info_location.values())))
    pointlist_vb_slot_hash_dict = {}
    trianglelist_vb_slot_hash_dict = {}

    print("pointlist_vb_slot hash:")
    for pointlist_vb_slot in unique_pointlist_vb_list:
        prefix = pointlist_indices[0] + "-" + pointlist_vb_slot
        filenames = get_filter_filenames(prefix, ".txt")
        if len(filenames) == 0:
            continue
        pointlist_vb_file = filenames[0]
        vb_slot_hash = pointlist_vb_file[len(prefix + "="):len(prefix + "=") + 8]
        print(pointlist_vb_slot + " :" + vb_slot_hash)
        pointlist_vb_slot_hash_dict[pointlist_vb_slot] = vb_slot_hash

    print("trianglelist_vb_slot hash:")
    for trianglelist_vb_slot in unique_trianglelist_vb_list:
        print(trianglelist_vb_slot)
        filenames = []
        for index in input_trianglelist_indices:
            prefix = index + "-" + trianglelist_vb_slot
            filenames = get_filter_filenames(prefix, ".txt")
            # print(filenames)
            if len(filenames) == 0:
                continue
            else:
                break

        print(filenames)

        trianglelist_vb_file = filenames[0]
        vb_slot_hash = trianglelist_vb_file[len(prefix + "="):len(prefix + "=") + 8]
        print(trianglelist_vb_slot + " :" + vb_slot_hash)
        trianglelist_vb_slot_hash_dict[trianglelist_vb_slot] = vb_slot_hash

    pointlist_category_vb_dict = {}
    # 计算得到每个vb0,vb1对应的category
    for element_name in pointlist_info_location.keys():
        category = vertex_config[element_name.decode()]["category"]
        extract_vb_file = vertex_config[element_name.decode()]["extract_vb_file"]
        pointlist_category_vb_dict[extract_vb_file] = category

    print(pointlist_category_vb_dict)
    trianglelist_category_vb_dict = {}
    for element_name in trianglelist_info_location.keys():
        category = vertex_config[element_name.decode()]["category"]
        extract_vb_file = vertex_config[element_name.decode()]["extract_vb_file"]
        trianglelist_category_vb_dict[extract_vb_file] = category
    print(trianglelist_category_vb_dict)

    print(pointlist_vb_slot_hash_dict)
    print(trianglelist_vb_slot_hash_dict)
    # 随后将这些值保存到配置文件
    for vb_slot, vb_hash in pointlist_vb_slot_hash_dict.items():
        category = pointlist_category_vb_dict.get(vb_slot)
        print(category)
        tmp_config.set("category_hash", category, vb_hash)
        tmp_config.set("category_slot", category, vb_slot)
        tmp_config.write(open(config_folder + "/tmp.ini", "w"))

    for vb_slot, vb_hash in trianglelist_vb_slot_hash_dict.items():
        category = trianglelist_category_vb_dict.get(vb_slot)
        print(category)
        tmp_config.set("category_hash", category, vb_hash)
        tmp_config.set("category_slot", category, vb_slot)
        tmp_config.write(open(config_folder + "/tmp.ini", "w"))

    # 将修改后的配置信息写回 .ini 文件


def calculate_tmp_element_list(header_info_input_element_list):
    tmp_element_list_str = ""
    for element in header_info_input_element_list:
        tmp_element_list_str = tmp_element_list_str + element.decode() + ","
    tmp_element_list_str = tmp_element_list_str[0:-1]
    tmp_config.set("Ini", "tmp_element_list", tmp_element_list_str)
    tmp_config.write(open(config_folder + "/tmp.ini", "w"))


def merge_pointlist_trianglelist_files(pointlist_indices, input_trianglelist_indices, max_vertex_count):
    # -------------------------------------读取区域-----------------------------------------------------------
    print("Start to merge pointlist and trianglelist files: ")
    # (1) split the info_location based on config file element's extract_tech.
    pointlist_info_location, trianglelist_info_location = get_pointlist_and_trianglelist_info_location(info_location)

    calculate_category_hash_and_slot(pointlist_info_location, trianglelist_info_location, input_trianglelist_indices)

    # (2) Read pointlist element vertexdata list dict.
    print(split_str)
    pointlist_vertex_count = 0
    pointlist_element_vertex_data_list_dict = {}
    if len(pointlist_info_location) != 0:
        pointlist_element_list = []
        for element_name in list(pointlist_info_location.keys()):
            pointlist_element_list.append(element_name.decode())
        pointlist_vertex_count, pointlist_element_vertex_data_list_dict = read_element_vertex_data_list_dict(pointlist_indices[0], pointlist_element_list)
    # print("len(pointlist_element_vertex_data_list_dict.get(BLENDINDICES)) :")
    # print(len(pointlist_element_vertex_data_list_dict.get("BLENDINDICES")))

    # (3) Read trianglelist element vertexdata list dict.
    # 根据element_name,在给出的trianglelist_indices中找到第一个含有真实对应element数据的index
    # TODO 这里不能只收集一个trianglelist的数据，而是要多个一起收集，对每个ib文件来说
    #  它们都应该有对应的vb文件来进行使用，这里我们要不直接将max_vertex_count强行替换为18391试试？
    print("Read trianglelist element vertexdata list dict.")
    trianglelist_vertex_count = 0
    trianglelist_element_vertex_data_list_dict = {}
    if len(trianglelist_info_location) != 0:
        element_real_index_dict = {}
        for element_name in list(trianglelist_info_location.keys()):
            # index = get_first_real_index_from_trianglelist_indices(element_name, input_trianglelist_indices, max_vertex_count)
            # TODO 这里只是测试
            index = get_first_real_index_from_trianglelist_indices(element_name, input_trianglelist_indices, b"18391")

            element_real_index_dict[element_name] = index
        print(element_real_index_dict)

        for element_name in element_real_index_dict:
            index = element_real_index_dict.get(element_name)
            vertex_data_list = get_vertex_data_list(index, element_name.decode())
            trianglelist_element_vertex_data_list_dict[element_name.decode()] = vertex_data_list
            trianglelist_vertex_count = len(vertex_data_list)

    # print(trianglelist_element_vertex_data_list_dict)
    # print("len(trianglelist_element_vertex_data_list_dict.get(TEXCOORD)) :")
    # print(len(trianglelist_element_vertex_data_list_dict.get("TEXCOORD")))

    # Calculate final vertex count depends on pointlist
    vb0_vertex_count = trianglelist_vertex_count
    print("vb0_vertex_count: " + str(vb0_vertex_count))
    if len(trianglelist_info_location) == 0:
        vb0_vertex_count = pointlist_vertex_count

    # -------------------------------------生成区域-----------------------------------------------------------
    # (4) Get header_info_str
    header_info_input_element_list = list(info_location.keys())

    header_info_str = get_header_info_str(vb0_vertex_count, header_info_input_element_list)
    # print(split_str)
    # print("Header info str: ")
    # print(header_info_str)

    # 这里我们需要把最终使用的element_list列表写到tmp.ini里,然后在Split的时候来读取
    calculate_tmp_element_list(header_info_input_element_list)

    # (5) Merge pointlist and trianglelist together.
    # print(trianglelist_element_vertex_data_list_dict)
    pointlist_element_vertex_data_list_dict.update(trianglelist_element_vertex_data_list_dict)

    # 对于9684c4091fc9e35a缺失BLENDWEIGTHS的情况，需要额外添加一个默认的vertex_data_dict来装载默认的BLENDWEIGHTS值。
    if root_vs == "9684c4091fc9e35a" and auto_completion_blendweights:
        # 1.构建VertexData
        # 2.构建符合vertex_count的长度的列表，并装入字典
        blendweight_list = []
        for i in range(vb0_vertex_count):
            vertex_data = VertexData(b"vb0[" + str(i).encode() +b"]+666 BLENDWEIGHTS: 1, 0, 0, 0\r\n")
            blendweight_list.append(vertex_data)
        blendweight_dict = {"BLENDWEIGHTS": blendweight_list}
        pointlist_element_vertex_data_list_dict.update(blendweight_dict)

    merged_element_vertex_data_list_dict = pointlist_element_vertex_data_list_dict
    # TODO 这里整个的收集逻辑都是错的！！！！！！！！
    '''
    假如有如下索引，而pointlist的最大值为18491，而trianglist里的18491缺失了vb1时，现有的收集体系会导致全部无法收集
    而根据分析脚本的结果，这个皮肤有4个部位，依次推理为：
    16079,18391,18425,18491
    如果还用之前的18491作为所有部件的属性，则由于18491缺失vb1槽位，会导致其它的也无法正常输出嘛
    {'000036': b'16079', '000037': b'18391', '000038': b'18425', '000039': b'18491', '000052': b'18391', 
    '000053': b'16079', '000057': b'18391', '000058': b'16079', '000063': b'18391', '000064': b'16079'}
    
    1.我们先尝试在计算的时候进行忽略处理，如果忽略处理有用吗，则推迟修改底层逻辑，先解决燃眉之急
    
    '''

    # print(split_str)
    # print(len(merged_element_vertex_data_list_dict.get("BLENDINDICES")))


    # Order by info_location.keys()
    print(info_location.keys())
    ordered_element_vertex_data_list_dict = {}
    for element_name in info_location.keys():
        values = merged_element_vertex_data_list_dict.get(element_name.decode())
        ordered_element_vertex_data_list_dict[element_name.decode()] = values

    merged_element_vertex_data_list_dict = ordered_element_vertex_data_list_dict
    print(merged_element_vertex_data_list_dict.keys())

    # (6) 获取唯一的ib的index
    ib_file_bytes, ib_file_first_index_list,unique_ib_indices = get_unique_ib_bytes_by_indices(input_trianglelist_indices)
    unique_trianglelist_ib_indices_list = []
    # 遍历ib_file_bytes，读取每一个trianglelist索引的ib文件进行对比，满足就把第一个满足的索引添加到列表
    for ib_file_byte in ib_file_bytes:
        for ib_index in input_trianglelist_indices:
            trianglelist_ib_file = open(WorkFolder + get_filter_filenames(ib_index + "-ib", ".txt")[0], "rb")
            trianglelist_ib_file_byte = trianglelist_ib_file.read()
            trianglelist_ib_file.close()
            if trianglelist_ib_file_byte == ib_file_byte:
                unique_trianglelist_ib_indices_list.append(ib_index)
                break

    print("ib_file_first_index_list: ")
    print(ib_file_first_index_list)

    # 这里需要将ib_file_first_inex_list写到tmp.ini中
    match_first_index_str = ""
    for first_index in ib_file_first_index_list:
        match_first_index_str = match_first_index_str + first_index.decode() + ","
    match_first_index_str = match_first_index_str[0:-1]
    tmp_config.set("Ini", "match_first_index", match_first_index_str)
    tmp_config.write(open(config_folder + "/tmp.ini", "w"))

    print("unique_trianglelist_ib_indices_list: ")
    print(unique_trianglelist_ib_indices_list)



    part_names = []
    for order_number in range(len(unique_trianglelist_ib_indices_list)):
        part_names.append(part_name + "_part" + str(order_number))

        trianglelist_ib_index = unique_trianglelist_ib_indices_list[order_number]
        print(split_str)

        print(vb0_vertex_count)
        print(split_str)
        model_file_data = ModelFileData(trianglelist_ib_index, order_number, merged_element_vertex_data_list_dict,
                                        header_info_str, vb0_vertex_count)

        model_file_data.calculate_vertex_data_str()

        model_file_data.save_to_file()
        print(str(trianglelist_ib_index) + " process over")

    # 记录part_names到tmp.ini方便后续使用
    part_names_str = ""
    for name in part_names:
        part_names_str = part_names_str + name + ","
    part_names_str = part_names_str[0:-1]
    tmp_config.set("Ini", "part_names", part_names_str)
    tmp_config.write(open(config_folder + "/tmp.ini", "w"))


def calculate_and_save_vertex_limit_vb(ib_index):
    vertex_limit_raise_index = ib_index
    print(ib_index)
    # Get vb0 filename, normally it always use vb0 to store POSITION info,so we use vb0 by default.
    first_draw_vb_filename = get_filter_filenames(str(vertex_limit_raise_index) + "-vb0=", ".txt")[0]
    index_vb_prefix = vertex_limit_raise_index + "-vb0="
    vertex_limit_vb = first_draw_vb_filename[len(index_vb_prefix):len(index_vb_prefix) + 8]
    # Save to tmp.ini for future split script use.
    tmp_config.set("Ini", "vertex_limit_vb", vertex_limit_vb)
    tmp_config.write(open(config_folder + "/tmp.ini", "w"))
    print("Calculated VertexLimitRaise hash value: " + vertex_limit_vb)
    print(split_str)


def read_element_vertex_data_list_dict(ib_index, read_element_list, convert_normal=False):
    vertex_count = 0
    element_vertex_data_list_dict = {}
    # {"POSITION":[xxx,xxx]}
    for element_name in read_element_list:
        vertex_data_list = get_vertex_data_list(ib_index, element_name, convert_normal=convert_normal)
        element_vertex_data_list_dict[element_name] = vertex_data_list

        vertex_count = len(vertex_data_list)
    # print(element_vertex_data_list_dict.get("POSITION")[0].element_name)
    return vertex_count, element_vertex_data_list_dict


def merge_ue4():
    # 1.get uniqu ib_indices
    ib_indices = get_indices_by_draw_ib()
    ib_file_bytes, ib_file_first_index_list, unique_ordered_ib_indices = get_unique_ib_bytes_by_indices(ib_indices)

    print(ib_file_first_index_list)
    print(unique_ordered_ib_indices)
    # (3) Calculate vertex_limit_vb.
    calculate_and_save_vertex_limit_vb(unique_ordered_ib_indices[0])

    pointlist_info_location, trianglelist_info_location = get_pointlist_and_trianglelist_info_location(info_location)

    calculate_category_hash_and_slot(pointlist_info_location, trianglelist_info_location, unique_ordered_ib_indices)

    # element_list直接写回
    tmp_config.set("Ini", "tmp_element_list", preset_config["Merge"]["element_list"])
    tmp_config.write(open(config_folder + "/tmp.ini", "w"))

    # 这里需要将ib_file_first_inex_list写到tmp.ini中
    match_first_index_str = ""
    for first_index in ib_file_first_index_list:
        match_first_index_str = match_first_index_str + first_index.decode() + ","
    match_first_index_str = match_first_index_str[0:-1]
    tmp_config.set("Ini", "match_first_index", match_first_index_str)
    tmp_config.write(open(config_folder + "/tmp.ini", "w"))

    # partnames
    part_names = []
    for order_number in range(len(unique_ordered_ib_indices)):
        part_names.append(part_name + "_part" + str(order_number))
    # 记录part_names到tmp.ini方便后续使用
    part_names_str = ""
    for name in part_names:
        part_names_str = part_names_str + name + ","
    part_names_str = part_names_str[0:-1]
    tmp_config.set("Ini", "part_names", part_names_str)
    tmp_config.write(open(config_folder + "/tmp.ini", "w"))

    # 首先要找出VertexCount最大的那个order_number
    final_order_number = 0
    max_vertex_count = 0
    for order_number in range(len(unique_ordered_ib_indices)):
        # (1) read VertexData object list for every element_name.
        ib_index = unique_ordered_ib_indices[order_number]

        # 因为后面的方法接收的都是bytes类型的element，所以这里要做转换
        bytes_element_list = []
        for element in element_list:
            bytes_element_list.append(element.encode())

        # 这里的element_list用原始的
        vertex_count, element_vertex_data_list_dict = read_element_vertex_data_list_dict(ib_index, element_list, convert_normal=True)

        if vertex_count >= max_vertex_count:
            max_vertex_count = vertex_count
            final_order_number = order_number

    print("已找出最大的VertexCount")
    ib_index = unique_ordered_ib_indices[final_order_number]
    vb0_data = get_final_vb0_model(ib_index, final_order_number)

    # 复制移动ib数据
    for order_number in range(len(unique_ordered_ib_indices)):
        name = part_names[order_number]
        ib_index = unique_ordered_ib_indices[order_number]
        ib_filename = get_filter_filenames(ib_index + "-ib", ".txt")[0]
        shutil.copy2(WorkFolder + ib_filename, OutputFolder + draw_ib + "-" + name + "-ib.txt")

    # 写出VB0数据
    for name in part_names:
        vb0_data.target_vb0_filename = draw_ib + "-" + name + "-vb0.txt"
        vb0_data.save_to_file()

    print("All process over.")
        

def get_final_vb0_model(ib_index,final_order_number):
    # 因为后面的方法接收的都是bytes类型的element，所以这里要做转换
    bytes_element_list = []
    for element in element_list:
        bytes_element_list.append(element.encode())

    # 这里的element_list用原始的
    vertex_count, element_vertex_data_list_dict = read_element_vertex_data_list_dict(ib_index, element_list,
                                                                                     convert_normal=True)

    # (2) get header_info_str.
    # 这里要用bytes的
    header_info_str = get_header_info_str(vertex_count, bytes_element_list)

    # Initial a model_file_data.
    model_file_data = Ue4Vb0Data(ib_index, element_vertex_data_list_dict, header_info_str, vertex_count)

    # calculate vertex_data_str.
    model_file_data.calculate_vertex_data_str()

    return model_file_data


def merge_unity():
    # Calculate vertex_limit_vb.
    calculate_and_save_vertex_limit_vb(trianglelist_indices[0])

    # Start to merge vb0 files.
    merge_pointlist_trianglelist_files(pointlist_indices, trianglelist_indices, max_vertex_count)


if __name__ == "__main__":
    # Always delete the old output folder to create a new one.
    if os.path.exists(OutputFolder):
        shutil.rmtree(OutputFolder)

    # Make sure the {OutputFolder} exists.
    if not os.path.exists(OutputFolder):
        os.mkdir(OutputFolder)

    # (4) move trianglelist related texture files.
    move_related_files(trianglelist_indices, OutputFolder, move_dds=True)

    if Engine == "UE4":
        merge_ue4()
    
    if Engine == "Unity":
        merge_unity()

