from Util import *

texture_check_slots = preset_config["Slot"]["texture_check_slots"].split(",")
ignore_tangent = preset_config["Split"].getboolean("ignore_tangent")
part_names = tmp_config["Ini"]["part_names"].split(",")

# calculate the stride,here must use tmp_element_list from tmp.ini
tmp_element_list = tmp_config["Ini"]["tmp_element_list"].split(",")

# 因为下面这两个dict只有分割和生成配置文件时会用到，所以不放在Tailor_Util中
# Calculate every replace_vb_slot's element_list,used in config file generate step and Split step.
category_element_list = {}
# format: {'vb0': ['POSITION'],'vb1':['NORMAL','TANGENT'],...}
for element_name in tmp_element_list:
    # You need to put it back to the slot which slot it been extract from,so here we use [extract_vb_file]
    category = vertex_config[element_name]["category"]
    slot_element_list = category_element_list.get(category)
    if slot_element_list is None:
        category_element_list[category] = [element_name]
    else:
        slot_element_list.append(element_name)
        category_element_list[category] = slot_element_list

# 根据vb_slot_element_list 获取一个步长字典，例如: {"vb0":40,"vb1":12,"vb2":24}
category_stride_dict = {}
categories = list(category_element_list.keys())
for categpory in categories:
    slot_elements = category_element_list.get(categpory)
    slot_stride = 0
    for slot_element in slot_elements:
        slot_stride_single = vertex_config[slot_element].getint("byte_width")
        slot_stride = slot_stride + slot_stride_single
    category_stride_dict[categpory] = slot_stride

# 获取所有的vb槽位
category_list = list(category_element_list.keys())

category_hash_dict = dict(tmp_config.items("category_hash"))
category_slot_dict = dict(tmp_config.items("category_slot"))

resource_ib_partnames = []
for part_name in part_names:
    name = "Resource_" + mod_name + "_" + part_name
    resource_ib_partnames.append(name)

position_category = preset_config["Category"]["position_category"]
texcoord_category = preset_config["Category"]["texcoord_category"]
blend_category = preset_config["Category"]["blend_category"]


class TextureOverride:
    OverrideName = None
    OverrideHash = None
    SlotResource = None
    Draw = None


def get_vb_override_str():
    print("生成VB override")
    # 自动拼接vb部分的TextureOverride
    texture_override_list = []
    print(category_list)
    print(category_hash_dict)
    print(category_slot_dict)
    for category in category_list:
        vb_hash = category_hash_dict.get(category)
        vb_slot = category_slot_dict.get(category)
        print(category)
        print(vb_hash)
        print(vb_slot)

        texture_override = TextureOverride()
        texture_override.OverrideName = "[TextureOverride_" + mod_name + "_" + category + "_VertexBuffer]" + "\n"
        texture_override.OverrideHash = "hash = " + vb_hash + "\n"
        # 这里要提前生成Resource的名称才行
        texture_override.SlotResource = vb_slot + " = " + "Resource_VB_" + category + "\n"

        # 如果是vb2,还需要控制draw call的数量
        # 这里我们需要两个变量来控制VertexLimitRaise特性，一个是开关用于是否生成，一个是需要skip并重新draw的槽位。
        if category == position_category:
            draw_str = ""
            draw_str = draw_str + "handling = skip\n"
            draw_numbers = tmp_config["Ini"]["draw_numbers"]
            draw_str = draw_str + "draw = " + draw_numbers + ",0\n"
            texture_override.Draw = draw_str

        texture_override_list.append(texture_override)
        # vb_override_str = vb_override_str + "\n"

    # 添加VertexLimitRaise支持
    break_vertex_limit = preset_config["Split"]["break_vertex_limit"]
    vertex_limit_vb = tmp_config["Ini"]["vertex_limit_vb"]
    if break_vertex_limit == "NicoMico":
        texture_override = TextureOverride()
        texture_override.OverrideName = "[TextureOverride_" + mod_name + "_c4]" + "\n"
        texture_override.OverrideHash = "hash = " + vertex_limit_vb + "\n"
        texture_override.SlotResource = "match_priority = -2\n"
        texture_override_list.append(texture_override)

    if break_vertex_limit == "Silent":
        texture_override = TextureOverride()
        texture_override.OverrideName = "[TextureOverride_" + mod_name + "_VertexLimitRaise]" + "\n"
        texture_override.OverrideHash = "hash = " + vertex_limit_vb + "\n"
        texture_override_list.append(texture_override)

    # specify blend_slot
    blend_slot = preset_config["Slot"]["blend_slot"]
    blend_original_slot = preset_config["Slot"]["blend_original_slot"]

    new_texture_override_list = []
    if blend_slot != "default":
        print("Detect blend slot change")
        # find blend_slot_resource
        blend_slot_resource = ""
        for texture_override in texture_override_list:
            if texture_override.SlotResource is not None and texture_override.OverrideName.endswith(blend_original_slot + "_VertexBuffer]\n"):
                blend_slot_resource = texture_override.SlotResource
                break

        # move blend_slot_resource
        for texture_override in texture_override_list:
            new_texture_override = texture_override
            if texture_override.SlotResource is not None and texture_override.OverrideName.endswith(blend_slot + "_VertexBuffer]\n"):
                new_texture_override.SlotResource += blend_slot_resource
                print(new_texture_override.SlotResource)
            if texture_override.SlotResource is not None and texture_override.OverrideName.endswith(blend_original_slot + "_VertexBuffer]\n"):
                new_texture_override.SlotResource = None

            new_texture_override_list.append(new_texture_override)

    # combine vb_override_str
    vb_override_str = ""
    for texture_override in new_texture_override_list:
        if texture_override.OverrideName is not None:
            vb_override_str += texture_override.OverrideName

        if texture_override.OverrideHash is not None:
            vb_override_str += texture_override.OverrideHash

        if texture_override.SlotResource is not None:
            vb_override_str += texture_override.SlotResource

        if texture_override.Draw is not None:
            vb_override_str += texture_override.Draw

        vb_override_str += "\n"

    print(vb_override_str)
    return vb_override_str


def get_ib_override_str():
    ib_override_str = ""
    # 首先把原本的IndexBuffer Skip掉
    ib_override_str = ib_override_str + "[TextureOverride_" + mod_name + "_IndexBuffer]" + "\n"
    ib_override_str = ib_override_str + "hash = " + draw_ib + "\n"
    ib_override_str = ib_override_str + "handling = skip\n\n"
    match_first_index = tmp_config["Ini"]["match_first_index"].split(",")

    # 然后补齐要添加的资源
    for i in range(len(part_names)):
        part_name = part_names[i]
        first_index = match_first_index[i]
        ib_override_str = ib_override_str + "[TextureOverride_" + mod_name + "_" + part_name + "_IndexBuffer]\n"
        ib_override_str = ib_override_str + "hash = " + draw_ib + "\n"
        ib_override_str = ib_override_str + "match_first_index = " + first_index + "\n"
        ib_override_str = ib_override_str + "ib = " + resource_ib_partnames[i] + "\n"

        # 加入贴图替换矩阵
        for texture_slot in texture_dict:
            ib_override_str = ib_override_str + texture_slot +" = Resource_" + texture_dict.get(texture_slot).split(".")[0] +"\n"

        ib_override_str = ib_override_str + "drawindexed = auto\n\n"

    return ib_override_str


def get_texture_resource_str():
    # Auto generate the ps slot we possibly will use from texture.ini.
    texture_resource_str = ""
    for texture_slot in texture_dict:
        texture_resource_str = texture_resource_str + "[Resource_" + texture_dict.get(texture_slot).split(".")[0] + "]\n"
        texture_resource_str = texture_resource_str + "filename = " + texture_dict.get(texture_slot) + "\n" + "\n"

    return texture_resource_str


def get_vb_resource_str():
    vb_resource_str = ""
    # 循环生成对应的VertexBuffer Resource文件
    for category in category_list:
        vb_resource_str = vb_resource_str + "[Resource_VB_" + category + "]\n"
        vb_resource_str = vb_resource_str + "type = Buffer\n"
        vb_slot_stride = category_stride_dict.get(category)
        vb_resource_str = vb_resource_str + "stride = " + str(vb_slot_stride) + "\n"
        vb_resource_str = vb_resource_str + "filename = " + mod_name + "_" + category + ".buf\n\n"
    return vb_resource_str


def get_ib_resource_str():
    ib_resource_str = ""
    # 循环生成对应的IndexBuffer Resource文件
    for i in range(len(part_names)):
        part_name = part_names[i]
        resource_name = resource_ib_partnames[i]
        ib_resource_str = ib_resource_str + "[" + resource_name + "]\n"
        ib_resource_str = ib_resource_str + "type = Buffer\n"
        ib_resource_str = ib_resource_str + "format = " + write_ib_format + "\n"
        # compatible with GIMI script.
        ib_resource_str = ib_resource_str + "filename = " + part_name + "_new.ib\n\n"

    return ib_resource_str


def move_modfiles():
    final_output_folder = OutputFolder + mod_name + "/"
    # Make sure the final mod folder exists.
    if not os.path.exists(final_output_folder):
        os.mkdir(final_output_folder)
    print("move mod files to final output mod folder.")
    mod_file_list = []
    part_names = tmp_config["Ini"]["part_names"].split(",")
    for num in range(len(part_names)):
        mod_file_list.append(part_names[num] + "_new.ib")

    # mod_file_list.append(mod_name + ".ini")

    for vb_slot in category_list:
        mod_file_list.append(mod_name + "_" + vb_slot + ".buf")

    # copy file.
    for file_path in mod_file_list:
        original_file_path = OutputFolder + file_path
        dest_file_path = final_output_folder + file_path
        if os.path.exists(original_file_path):
            shutil.copy2(original_file_path, dest_file_path)
    # move ini file.
    ini_filename = mod_name + ".ini"
    shutil.move(OutputFolder + ini_filename,final_output_folder + ini_filename)


def collect_ib(filename, offset):
    # 默认打包为DXGI_FORMAT_R16_UINT格式
    read_pack_sign = 'H'
    read_pack_stride = 2
    write_pack_sign = 'H'

    if read_ib_format == "DXGI_FORMAT_R16_UINT":
        read_pack_sign = 'H'
        read_pack_stride = 2

    if read_ib_format == "DXGI_FORMAT_R32_UINT":
        read_pack_sign = 'I'
        read_pack_stride = 4

    if write_ib_format == "DXGI_FORMAT_R16_UINT":
        write_pack_sign = 'H'

    if write_ib_format == "DXGI_FORMAT_R32_UINT":
        write_pack_sign = 'I'

    ib = bytearray()
    with open(filename, "rb") as f:
        data = f.read()
        data = bytearray(data)
        i = 0
        while i < len(data):
            ib += struct.pack(write_pack_sign, struct.unpack(read_pack_sign, data[i:i + read_pack_stride])[0] + offset)
            i += read_pack_stride
    return ib


def collect_vb_UE4(vb_file_name, collect_stride):
    print(split_str)
    print("Start to collect vb info from: " + vb_file_name)
    print("Collect_stride: " + str(collect_stride))
    print(category_element_list)
    print(category_stride_dict)

    normal_width = vertex_config["NORMAL"].getint("byte_width")
    tangent_width = vertex_config["TANGENT"].getint("byte_width")

    print("Prepare normal_width: " + str(normal_width))
    print("Prepare tangent_width: " + str(tangent_width))

    # 这里定义一个dict{vb0:bytearray(),vb1:bytearray()}类型，来依次装载每个vb中的数据
    # 其中vb0需要特殊处理TANGENT部分
    collect_vb_slot_bytearray_dict = {}
    with open(vb_file_name, "rb") as vb_file:
        data = bytearray(vb_file.read())

        i = 0

        while i < len(data):
            # 遍历vb_slot_stride_dict，依次处理
            for category_stride_slot in category_stride_dict:
                category_stride = category_stride_dict.get(category_stride_slot)

                vb_slot_bytearray = bytearray()
                # UE4的Normal需要结尾+1
                # 由于3Dmigoto脚本会自动补齐为0，即0x00所以我们需要手动将他改为1，因为UE4中的Normal最后一位总为1.
                # print(category_stride_slot)
                if category_stride_slot == "tangent":
                    # print("处理NORMAL和TANGENT")
                    normal_data = data[i:i + normal_width]
                    normal_data[-1] = 0x01
                    # print(bytearray(struct.pack("f", 1)))
                    # normal_data += bytearray(struct.pack("f", 1))
                    tangent_data = data[i + normal_width: i + normal_width + tangent_width]

                    vb_slot_bytearray += normal_data
                    vb_slot_bytearray += tangent_data
                else:
                    vb_slot_bytearray += data[i:i + category_stride]

                # 追加到收集的vb信息中
                original_vb_slot_bytearray = collect_vb_slot_bytearray_dict.get(category_stride_slot)
                if original_vb_slot_bytearray is None:
                    original_vb_slot_bytearray = bytearray()
                collect_vb_slot_bytearray_dict[category_stride_slot] = original_vb_slot_bytearray + vb_slot_bytearray

                # 更新步长
                i += category_stride
    return collect_vb_slot_bytearray_dict


def collect_vb_unity(vb_file_name, collect_stride):
    print(split_str)
    print("Start to collect vb info from: " + vb_file_name)
    print("Collect_stride: " + str(collect_stride))
    print(category_element_list)
    print(category_stride_dict)

    position_width = vertex_config["POSITION"].getint("byte_width")
    normal_width = vertex_config["NORMAL"].getint("byte_width")
    print("Prepare position_width: " + str(position_width))
    print("Prepare normal_width: " + str(normal_width))

    # 读取配置文件里的厚度信息，值为0-255之间

    rgb_r = preset_config["Color"]["rgb_r"]
    rgb_g = preset_config["Color"]["rgb_g"]
    rgb_b = preset_config["Color"]["rgb_b"]
    rgb_a = preset_config["Color"]["rgb_a"]


    # 这里定义一个dict{vb0:bytearray(),vb1:bytearray()}类型，来依次装载每个vb中的数据
    # 其中vb0需要特殊处理TANGENT部分
    collect_vb_slot_bytearray_dict = {}

    # 这里需要额外收集一个只有POSITION的bytearray和一个只有TANGENT的数组，里面是turple类型，turple里面装着float类型的数
    position_float_list = []
    tangent_float_list = []

    with open(vb_file_name, "rb") as f:
        data = bytearray(f.read())
        i = 0
        while i < len(data):
            # print(vb_slot_stride_dict)  {'vb0': 40, 'vb1': 20, 'vb2': 32}

            # 遍历vb_slot_stride_dict，依次处理
            for vb_category in category_stride_dict:
                vb_stride = category_stride_dict.get(vb_category)

                vb_slot_bytearray = bytearray()
                # vb0一般装的是POSITION数据，所以需要特殊处理
                if vb_category == position_category:
                    # 先收集正常的所需的三个元素
                    if ignore_tangent:
                        # 先添加POSITION和NORMAL
                        vb_slot_bytearray += data[i:i + position_width + normal_width]

                        # 这里的忽略Tangent机制，原理是使用Normal替代TANGENT以达到更加近似的效果,但效果远不如KDTree修复
                        vb_slot_bytearray += data[i + position_width:i + position_width + normal_width] + bytearray(
                            struct.pack("f", 1))
                    else:
                        # 否则就全部添加上，暂时不管TANGENT了
                        vb_slot_bytearray += data[i:i + vb_stride]

                    # 再专门收集position和tangent,同时要转换成List<Turple(float,float,float)>的形式
                    pox = struct.unpack("f", data[i:i+4])[0]
                    poy = struct.unpack("f", data[i+4:i+8])[0]
                    poz = struct.unpack("f", data[i+8:i+normal_width])[0]
                    position_turple = (pox, poy, poz)
                    position_float_list.append(position_turple)

                    tox = struct.unpack("f", data[i + position_width + normal_width:i + position_width + normal_width + 4])[0]
                    toy = struct.unpack("f", data[i + position_width + normal_width + 4:i + position_width + normal_width + 8])[0]
                    toz = struct.unpack("f", data[i + position_width + normal_width + 8:i + position_width + normal_width + 12])[0]
                    toa = struct.unpack("f", data[i + position_width + normal_width + 12:i + position_width + normal_width + 16])[0]
                    tangent_float_list.append((tox, toy, toz, toa))

                else:
                    if vb_category == texcoord_category:
                        # 进行COLOR的替换逻辑处理
                        # 首先依次判断每个color值是否为default，如果是则无需处理
                        if rgb_r != "default":
                            vb_slot_bytearray += bytearray([int(rgb_r)])
                        else:
                            vb_slot_bytearray += data[i:i+1]

                        if rgb_g != "default":
                            vb_slot_bytearray += bytearray([int(rgb_g)])
                        else:
                            vb_slot_bytearray += data[i+1:i+2]

                        if rgb_b != "default":
                            vb_slot_bytearray += bytearray([int(rgb_b)])
                        else:
                            vb_slot_bytearray += data[i+2:i+3]

                        if rgb_a != "default":
                            vb_slot_bytearray += bytearray([int(rgb_a)])
                        else:
                            vb_slot_bytearray += data[i+3:i+4]

                        vb_slot_bytearray += data[i+4:i+vb_stride]

                    else:
                        # 这里必须考虑到9684c4091fc9e35a的情况，所以我们需要在这里不读取BLENDWEIGHTS信息，不读取BLENDWEIGHTS必须满足自动补全的情况
                        blendweights_extract_vb_file = ""
                        if "BLENDWEIGHTS" in element_list:
                            # 仅在有blend信息时进行读取
                            blendweights_extract_vb_file = vertex_config["BLENDWEIGHTS"]["extract_vb_file"]

                        if root_vs == "9684c4091fc9e35a" and vb_category == blendweights_extract_vb_file and auto_completion_blendweights:
                            print("读取时，并不读取BLENDWEIGHTS部分")
                            stride_blendweights = vertex_config["BLENDWEIGHTS"].getint("byte_width")
                            vb_slot_bytearray += data[i:i + vb_stride - stride_blendweights]
                        else:
                            # print("在处理不为vb0时,vb_stride,实际值: " + str(vb_stride))
                            vb_slot_bytearray += data[i:i + vb_stride]



                # print("collecting vb_slot:")
                # print(vb_stride_slot)
                #
                # print("collected vb_slot_bytearray: ")
                # print(len(vb_slot_bytearray))

                # 追加到收集的vb信息中
                original_vb_slot_bytearray = collect_vb_slot_bytearray_dict.get(vb_category)
                if original_vb_slot_bytearray is None:
                    original_vb_slot_bytearray = bytearray()
                collect_vb_slot_bytearray_dict[vb_category] = original_vb_slot_bytearray + vb_slot_bytearray

                # 更新步长
                i += vb_stride
    return collect_vb_slot_bytearray_dict, position_float_list, tangent_float_list


def generate_config_file():
    # 输出便于调试
    print(category_element_list)
    print(category_list)
    # 创建一个空白字符串
    output_str = ""

    output_str = output_str + get_vb_override_str()
    output_str = output_str + get_ib_override_str()
    output_str = output_str + get_texture_resource_str()
    print("get_vb_resource_str")
    output_str = output_str + get_vb_resource_str()
    print("get_ib_resource_str")
    output_str = output_str + get_ib_resource_str()

    # 写出到最终配置文件
    output_file = open(OutputFolder + mod_name + ".ini", "w")
    output_file.write(output_str)
    output_file.close()

    # Move to the final folder
    move_modfiles()


def generate_basic_check_ini():
    # We set this script as a single part instead of put it in Step2_Split.py
    # because some d3dx.ini use global check,so we can choose do not run this script to compatible with it.
    mod_folder = OutputFolder + mod_name + "/"
    basic_check_filename = mod_folder + "basic_check.ini"

    if not os.path.exists(mod_folder):
        os.mkdir(mod_folder)

    # Create a new basic_check.ini
    file = open(basic_check_filename, "w+")
    file.write("")
    file.close()

    # all VertexShader will show in IndexBuffer related files.
    ib_files = get_filter_filenames(draw_ib, ".txt")

    # Get all VertexShader need to check
    vertex_shader_list = []
    for filename in ib_files:
        vs = filename.split("-vs=")[1][0:16]
        if vs not in vertex_shader_list:
            vertex_shader_list.append(vs)
    print(vertex_shader_list)

    # Add texcoord VertexShader check



    # output str
    output_str = ""
    output_str = output_str + ";Texcoord Check List:" + "\n" + "\n"
    for vs in sorted(vertex_shader_list):
        section_name = "[ShaderOverride_VS_" + vs + "_Test_]"
        print("add section :" + section_name)

        output_str = output_str + section_name + "\n"
        output_str = output_str + "hash = " + vs + "\n"
        output_str = output_str + "if $costume_mods" + "\n"
        for slot in texture_check_slots:
            output_str = output_str + "  checktextureoverride = " + slot + "\n"
        output_str = output_str + "endif" + "\n"
        output_str = output_str + "\n"

    # Finally save the config file.
    output_file = open(basic_check_filename, "w")
    output_file.write(output_str)
    output_file.close()


def get_original_tangent_v2(points, tangents, position_input):
    position = position_input

    lookup = {}
    for x, y in zip(points, tangents):
        lookup[x] = y

    tree = KDTree(points, 3)

    i = 0
    while i < len(position):
        if len(points[0]) == 3:
            x, y, z = struct.unpack("f", position[i:i + 4])[0], struct.unpack("f", position[i + 4:i + 8])[0], \
                struct.unpack("f", position[i + 8:i + 12])[0]
            result = tree.get_nearest((x, y, z))[1]
            tx, ty, tz, ta = [struct.pack("f", a) for a in lookup[result]]
            position[i + 24:i + 28] = tx
            position[i + 28:i + 32] = ty
            position[i + 32:i + 36] = tz
            position[i + 36:i + 40] = ta
            i += 40
        else:
            x, y, z = struct.unpack("e", position[i:i + 2])[0], struct.unpack("e", position[i + 2:i + 4])[0], \
                struct.unpack("e", position[i + 4:i + 6])[0]
            result = tree.get_nearest((x, y, z))[1]
            tx, ty, tz, ta = [(int(a * 255)).to_bytes(1, byteorder="big") for a in lookup[result]]

            position[i + 24:i + 25] = tx
            position[i + 25:i + 26] = ty
            position[i + 26:i + 27] = tz
            position[i + 27:i + 28] = ta
            i += 28
    return position


def split_ib_vb_file():
    # 首先计算步长
    stride = 0
    for element in tmp_element_list:
        stride = stride + int(vertex_config[element].getint("byte_width"))

    # collect vb
    offset = 0

    # 这里定义一个总体的vb_slot_bytearray_dict
    vb0_slot_bytearray_dict = {}

    # vb filename
    for part_name in part_names:
        vb_filename = OutputFolder + part_name + ".vb"



        # 这里获取了vb0:bytearray() 这样的字典
        vb_slot_bytearray_dict = {}

        if Engine == "Unity":
            vb_slot_bytearray_dict, position_float_list, tangent_float_list = collect_vb_unity(vb_filename, stride)

        if Engine == "UE4":
            vb_slot_bytearray_dict = collect_vb_UE4(vb_filename, stride)

        print(split_str)
        for vb_slot_categpory in vb_slot_bytearray_dict:
            print("category:")
            print(vb_slot_categpory)
            vb_byte_array = vb_slot_bytearray_dict.get(vb_slot_categpory)

            # 获取总的vb_byte_array:
            vb0_byte_array = vb0_slot_bytearray_dict.get(vb_slot_categpory)
            # 如果为空就初始化一下
            if vb0_byte_array is None:
                vb0_byte_array = bytearray()

            vb0_byte_array = vb0_byte_array + vb_byte_array
            vb0_slot_bytearray_dict[vb_slot_categpory] = vb0_byte_array

        # calculate nearest TANGENT,we use GIMI's method
        # see: https://github.com/SilentNightSound/GI-Model-Importer/pull/84
        if repair_tangent:
            # 读取vb0文件
            position_hash = category_hash_dict.get(position_category)
            vb0_filename = get_filter_filenames("vb0=" + position_hash, ".txt")[0]

            # 获取position
            position_vb_array = vb0_slot_bytearray_dict.get(position_category)
            position_new = get_original_tangent_v2(position_float_list, tangent_float_list, position_vb_array)
            vb0_slot_bytearray_dict[position_category] = position_new

        # collect ib
        ib_filename = OutputFolder + part_name + ".ib"
        print("ib_filename: " + ib_filename)
        ib_buf = collect_ib(ib_filename, offset)
        with open(OutputFolder + part_name + "_new.ib", "wb") as ib_buf_file:
            ib_buf_file.write(ib_buf)

        # After collect ib, set offset for the next time's collect
        print(offset)
        offset = len(vb0_slot_bytearray_dict.get(position_category)) // 40

    # write vb buf to file.
    for categpory in vb0_slot_bytearray_dict:
        vb0_byte_array = vb0_slot_bytearray_dict.get(categpory)

        with open(OutputFolder + mod_name + "_" + categpory + ".buf", "wb") as byte_array_file:
            byte_array_file.write(vb0_byte_array)

    # set the draw number used in VertexLimitRaise
    draw_numbers = len(vb0_slot_bytearray_dict.get(position_category)) // 40
    tmp_config.set("Ini", "draw_numbers", str(draw_numbers))
    tmp_config.write(open(config_folder + "/tmp.ini", "w"))


if __name__ == "__main__":
    print("Start to split ib and vb file.")
    split_ib_vb_file()

    print("Start to generate final .ini file.")
    generate_config_file()

    # Do we need to generate basic_check.ini?
    if basic_check:
        print("Start to generate basic_check.ini.")
        generate_basic_check_ini()


