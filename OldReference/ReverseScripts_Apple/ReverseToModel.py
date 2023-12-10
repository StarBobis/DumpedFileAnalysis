from ReverseConfig import *


def get_ib_filename_minnum_maxnum_dict_from_ib_file(fc_tmp_ib_file_list):
    # 读取ib文件，并在格式转换后全部堆叠到一起来输出到一个完整的ib文件
    total_num = 0

    tmp_ib_filename_minnum_dict = {}
    tmp_ib_filename_maxnum_dict = {}

    for ib_num in range(len(fc_tmp_ib_file_list)):
        ib_filename = fc_tmp_ib_file_list[ib_num]
        print(ib_filename)
        tmp_ib_file = open(reverse_mod_path + ib_filename, "rb")
        tmp_ib_bytearray = bytearray(tmp_ib_file.read())
        tmp_ib_file.close()

        total_num += len(tmp_ib_bytearray)

        i = 0
        max_count = 0
        min_count = 9999999
        while i < len(tmp_ib_bytearray):
            tmp_byte = struct.pack(write_pack_sign,
                                   struct.unpack(read_pack_sign, tmp_ib_bytearray[i:i + read_pack_stride])[0])
            now_count = int.from_bytes(tmp_byte, "little")
            if now_count >= max_count:
                max_count = now_count
            if now_count <= min_count:
                min_count = now_count
            i += read_pack_stride
        tmp_ib_filename_minnum_dict[ib_filename] = min_count
        tmp_ib_filename_maxnum_dict[ib_filename] = max_count
    return tmp_ib_filename_minnum_dict, tmp_ib_filename_maxnum_dict


def collect_ib_subtract_offset(filename, offset):
    ib = bytearray()
    with open(filename, "rb") as f:
        data = f.read()
        data = bytearray(data)
        i = 0
        while i < len(data):
            ib += struct.pack(write_pack_sign, struct.unpack(read_pack_sign, data[i:i + read_pack_stride])[0] - offset)
            i += read_pack_stride
    return ib


def get_stride_from_element_list():
    fc_tmp_stride = 0
    for num in range(len(element_list)):
        element_name = element_list[num]
        byte_width = vertex_config[element_name].getint("byte_width")
        fc_tmp_stride += byte_width
    return fc_tmp_stride


def get_fmt_str_from_element_list():
    # 开始组装fmt文件内容
    fc_tmp_fmt_str = ""

    fc_tmp_aligned_byte_offset = 0
    element_str = ""
    for num in range(len(element_list)):
        element_name = element_list[num]
        semantic_name = vertex_config[element_name]["semantic_name"]
        semantic_index = vertex_config[element_name]["semantic_index"]
        format = vertex_config[element_name]["format"]
        input_slot = vertex_config[element_name]["input_slot"]
        byte_width = vertex_config[element_name].getint("byte_width")
        aligned_byte_offset = str(fc_tmp_aligned_byte_offset)
        fc_tmp_aligned_byte_offset += byte_width
        input_slot_class = vertex_config[element_name]["input_slot_class"]
        instance_data_step_rate = vertex_config[element_name]["instance_data_step_rate"]

        element_str = element_str + "element[" + str(num) + "]:\n"
        element_str = element_str + "  SemanticName: " + semantic_name + "\n"
        element_str = element_str + "  SemanticIndex: " + semantic_index + "\n"
        element_str = element_str + "  Format: " + format + "\n"
        element_str = element_str + "  InputSlot: " + input_slot + "\n"
        element_str = element_str + "  AlignedByteOffset: " + aligned_byte_offset + "\n"
        element_str = element_str + "  InputSlotClass: " + input_slot_class + "\n"
        element_str = element_str + "  InstanceDataStepRate: " + instance_data_step_rate + "\n"

    # combine final fmt str.
    fc_tmp_fmt_str = fc_tmp_fmt_str + "stride: " + str(fc_tmp_aligned_byte_offset) + "\n"
    fc_tmp_fmt_str = fc_tmp_fmt_str + "topology: " + "trianglelist" + "\n"
    fc_tmp_fmt_str = fc_tmp_fmt_str + "format: " + read_dxgi_format + "\n"
    fc_tmp_fmt_str = fc_tmp_fmt_str + element_str

    return fc_tmp_fmt_str


def split_vb_files(fc_tmp_vb_file_bytearray,
                   fc_tmp_category_output_name_dict, fc_tmp_stride):
    # 分割VB文件为多个vb文件
    left_offset_num = 0

    output_filename_outer_list = list(fc_tmp_category_output_name_dict.values())
    print(output_filename_outer_list)

    for output_filename_list in output_filename_outer_list:
        input_ib_filename = output_filename_list[3]
        output_vb_filename = output_filename_list[1]
        fc_tmp_category_maxnum = ib_filename_maxnum_dict.get(input_ib_filename)

        print("Processing: " + output_vb_filename)
        left_offset = left_offset_num
        right_offset = left_offset_num + fc_tmp_stride * (fc_tmp_category_maxnum + 1)

        print("Left: " + str(left_offset / fc_tmp_stride) + "  Right: " + str(right_offset / fc_tmp_stride))
        output_vb_bytearray = fc_tmp_vb_file_bytearray[left_offset:right_offset]

        output_vb_file = open(output_folder + output_vb_filename, "wb")
        output_vb_file.write(output_vb_bytearray)
        output_vb_file.close()

        left_offset_num = fc_tmp_stride * (fc_tmp_category_maxnum + 1)


def get_vb_byte_array():
    vertex_count = 0
    category_vb_bytearray_list_dict = {}

    for fc_tmp_data_vb_resource in sorted_data_vb_resource_list:
        # 获取buf文件名称
        vb_filename = fc_tmp_data_vb_resource.resource_filename
        # 读取buf文件数据
        tmp_vb_file = open(reverse_mod_path + vb_filename, "rb")
        data = bytearray(tmp_vb_file.read())
        tmp_vb_file.close()

        category_bytearray_list = []
        categorty_stride = int(fc_tmp_data_vb_resource.resource_stride)

        print(categorty_stride)
        i = 0
        while i < len(data):
            category_bytearray_list.append(data[i:i + categorty_stride])
            i += categorty_stride
        vertex_count = len(category_bytearray_list)
        category_vb_bytearray_list_dict[vb_filename] = category_bytearray_list

    # Merge them into a final bytearray
    tmp_vb_file_bytearray = bytearray()
    print(category_vb_bytearray_list_dict.keys())
    for i in range(vertex_count):
        for fc_tmp_data_vb_resource in sorted_data_vb_resource_list:
            bytearray_list = category_vb_bytearray_list_dict.get(fc_tmp_data_vb_resource.resource_filename)
            add_byte = bytearray_list[i]
            tmp_vb_file_bytearray += add_byte

    return tmp_vb_file_bytearray


def get_category_output_name_dict(fc_tmp_fmt_str):
    fc_tmp_category_output_name_dict = {}

    for num in range(len(ib_file_list)):
        category_name = "object_part" + str(num)
        input_ib_file_name = ib_file_list[num]
        output_vb_file_name = category_name + ".vb"
        output_ib_file_name = category_name + ".ib"
        output_fmt_file_name = category_name + ".fmt"
        fc_tmp_category_output_name_dict[category_name] = [output_ib_file_name, output_vb_file_name, output_fmt_file_name,input_ib_file_name]

        # 顺便输出fmt文件
        output_fmt_file = open(output_folder + output_fmt_file_name, "w")
        output_fmt_file.write(fc_tmp_fmt_str)
        output_fmt_file.close()
    return fc_tmp_category_output_name_dict


def convert_and_output_ib_file(fc_tmp_category_output_name_dict, fc_tmp_category_minnum_dict):
    for category in fc_tmp_category_output_name_dict:
        input_ib_filename = fc_tmp_category_output_name_dict.get(category)[3]
        output_ib_filename = fc_tmp_category_output_name_dict.get(category)[0]

        category_minnum = fc_tmp_category_minnum_dict.get(input_ib_filename)

        # 因为mod格式的ib文件，值是从偏移量那里开始的，所以把原本的三个ib文件，分别减去其每个ib文件中最小的值
        # 使得新的ib文件的格式全部变成从0开始的值，这样才能导入blender
        original_ib_data = collect_ib_subtract_offset(reverse_mod_path + input_ib_filename, category_minnum)
        with open(output_folder + output_ib_filename, "wb") as output_ib_file:
            output_ib_file.write(original_ib_data)


# 获取该Mod的配置文件所有内容
reverse_ini_sections = reverse_ini_config.sections()
print(reverse_ini_sections)

# 解析配置文件内容，并放入list备用
ini_kv_pair_list = []
for section_name in reverse_ini_sections:
    options = reverse_ini_config.options(section_name)

    ini_kv_pair = IniKVPair()
    ini_kv_pair.section_name = section_name
    ini_kv_pair.kv_map = {}

    for option_name in options:
        option_value = reverse_ini_config.get(section_name, option_name)
        ini_kv_pair.kv_map[option_name] = option_value

    ini_kv_pair_list.append(ini_kv_pair)

    # print(ini_kv_pair)

# 解析资源文件
'''
这里注意分别计息TextureOverride部分和Resource部分
而且顺序必须为先解析Resource，再解析TextureOverride
'''

# 根据资源类型，将kv_pair分别装入TextureOverride list或Resource list
texture_override_kvpair_list = []
resource_kvpair_list = []

for ini_kv_pair in ini_kv_pair_list:
    section_name = ini_kv_pair.section_name
    if section_name.startswith("TextureOverride"):
        texture_override_kvpair_list.append(ini_kv_pair)
        continue

    if section_name.startswith("Resource"):
        resource_kvpair_list.append(ini_kv_pair)


# 构建对应的数据类型来装载Resource类型

data_ib_resource_list = []
data_vb_resource_list = []

for ini_kv_pair in resource_kvpair_list:

    # 先确定类型是ib文件还是buf文件
    find_stride = False
    find_format = False

    for option_name in ini_kv_pair.kv_map:
        if "stride" == str(option_name).lower():
            find_stride = True
            break

        if "format" == str(option_name).lower():
            find_format = True
            break

    if find_format:
        data_ib_resource = DataIBResource()
        # 设置名称
        data_ib_resource.resource_name = ini_kv_pair.section_name
        # 设置format和filename
        for option_name in ini_kv_pair.kv_map:
            option_value = ini_kv_pair.kv_map.get(option_name)

            if "format" == str(option_name).lower():
                data_ib_resource.resource_format = option_value

            if "filename" == str(option_name).lower():
                data_ib_resource.resource_filename = option_value
        data_ib_resource_list.append(data_ib_resource)
        continue

    if find_stride:
        data_vb_resource = DataVBResource()
        # 设置名称
        data_vb_resource.resource_name = ini_kv_pair.section_name
        # 设置stride和filename
        for option_name in ini_kv_pair.kv_map:
            option_value = ini_kv_pair.kv_map.get(option_name)

            if "stride" == str(option_name).lower():
                data_vb_resource.resource_stride = int(option_value)

            if "filename" == str(option_name).lower():
                data_vb_resource.resource_filename = option_value
        data_vb_resource_list.append(data_vb_resource)

# 接下来需要验证这些Resource文件是否在TextureOverride中使用到了。
# 理论上来讲，一个未混淆过的标准mod是不需要验证的，所以直接跳到下一步

# 现在我们有了IB文件和Buffer文件，接下来要做的就是确定他们的顺序。
# 先输出看看格式是什么样的
# for data_ib_resource in data_ib_resource_list:
#     print(data_ib_resource.resource_filename)
#     print(data_ib_resource.resource_format)
#
# for data_vb_resource in data_vb_resource_list:
#     print(data_vb_resource.resource_filename)
#     print(data_vb_resource.resource_stride)

# 首先根据TextureOverride IB中的first index的大小，来确定对应的IB文件顺序排序。
# (1) 获取ib_override列表
data_ib_override_list = []
for ini_kv_pair in texture_override_kvpair_list:

    if "match_first_index" in ini_kv_pair.kv_map.keys():
        data_ib_override = DataIBOverride()
        data_ib_override.overide_name = ini_kv_pair.section_name

        for option_name in ini_kv_pair.kv_map:
            option_value = ini_kv_pair.kv_map.get(option_name)
            if option_name == "match_first_index":
                data_ib_override.match_first_index = int(option_value)
                print(data_ib_override.match_first_index)
            if option_name == "ib":
                data_ib_override.ib_resource_name = option_value
        data_ib_override_list.append(data_ib_override)
        print(data_ib_override.overide_name)
        print(data_ib_override.match_first_index)
        print(data_ib_override.ib_resource_name)
        print("---------------------------------------")
# (2) 根据ib_resource，给对应的ib_override添加对应的ib的文件名称
new_data_ib_override_list = []
for data_ib_override in data_ib_override_list:
    new_data_ib_override = data_ib_override

    for data_ib_resource in data_ib_resource_list:
        print(data_ib_override.ib_resource_name)
        print(data_ib_resource.resource_name)
        if str(data_ib_override.ib_resource_name).strip().lower() == str(data_ib_resource.resource_name).strip().lower():
            new_data_ib_override.ib_resource_filename = data_ib_resource.resource_filename
            print("找到了")
            break
    new_data_ib_override_list.append(new_data_ib_override)
    print(new_data_ib_override.match_first_index)
    print(new_data_ib_override.ib_resource_filename)
    print("---------------------------------------")

# (3) 直接获取按顺序排列好的ib文件列表
ib_file_list = []
from operator import attrgetter
new_data_ib_override_list_sorted = sorted(new_data_ib_override_list, key=attrgetter("match_first_index"))

for data_ib_override in new_data_ib_override_list_sorted:
    print(data_ib_override.match_first_index)
    print(data_ib_override.ib_resource_filename)
    print("---------------------------------------")
    if data_ib_override.ib_resource_filename is not None:
        ib_file_list.append(data_ib_override.ib_resource_filename)

print("输出查看一下排序完成的ib_file_list")
print(ib_file_list)

# 手动纠正
ib_file_list_flag = preset_config["ManuallyFix"]["ib_file_list"]
if ib_file_list_flag != "default":
    ib_file_list = ib_file_list_flag.split(",")

# 其次根据resource的步长，来确定VB文件的顺序，但是我觉得使用预设比较好


# TODO 增加配置文件解析的代码

# 根据预设，计算出正确顺序的列表

# 读取输入的ib文件的DXGI_FORMAT
format_count_dict = {}
for data_ib_resource in data_ib_resource_list:
    format_count = format_count_dict.get(data_ib_resource.resource_format)
    if format_count is None:
        format_count_dict[data_ib_resource.resource_format] = 1
    else:
        format_count_dict[data_ib_resource.resource_format] = format_count + 1

read_dxgi_format = ""
for dxgi_format in format_count_dict:
    format_count = format_count_dict.get(dxgi_format)
    if format_count == len(data_ib_resource_list):
        read_dxgi_format = dxgi_format
        break

print(read_dxgi_format)

read_pack_sign = 'H'
write_pack_sign = 'H'
read_pack_stride = 2

if read_dxgi_format == "DXGI_FORMAT_R16_UINT":
    read_pack_stride = 2
    read_pack_sign = 'H'
    write_pack_sign = 'H'

if read_dxgi_format == "DXGI_FORMAT_R32_UINT":
    read_pack_stride = 4
    read_pack_sign = 'I'
    write_pack_sign = 'I'

sorted_data_vb_resource_list = []


# 从vertex_attr.ini中进行读取
vertex_element_list = vertex_config.sections()
element_list = []

for data_vb_resource in data_vb_resource_list:
    if 40 == int(data_vb_resource.resource_stride):
        sorted_data_vb_resource_list.append(data_vb_resource)
        element_list.append("POSITION")
        element_list.append("NORMAL")
        element_list.append("TANGENT")
        break


for data_vb_resource in data_vb_resource_list:
    if 20 == int(data_vb_resource.resource_stride):
        sorted_data_vb_resource_list.append(data_vb_resource)
        element_list.append("COLOR")
        element_list.append("TEXCOORD")
        element_list.append("TEXCOORD1")
        break
    if 12 == int(data_vb_resource.resource_stride):
        sorted_data_vb_resource_list.append(data_vb_resource)
        element_list.append("COLOR")
        element_list.append("TEXCOORD")
        break

    if 8 == int(data_vb_resource.resource_stride):
        sorted_data_vb_resource_list.append(data_vb_resource)
        element_list.append("TEXCOORD")
        break

for data_vb_resource in data_vb_resource_list:
    if 32 == int(data_vb_resource.resource_stride):
        sorted_data_vb_resource_list.append(data_vb_resource)
        if "BLENDWEIGHTS" in vertex_element_list:
            element_list.append("BLENDWEIGHTS")
            element_list.append("BLENDINDICES")
            break
        if "BLENDWEIGHT" in vertex_element_list:
            element_list.append("BLENDWEIGHT")
            element_list.append("BLENDINDICES")
            break

        break
print("----------------------------------------------")
print("查看一下element_list:")
print(element_list)
print("----------------------------------------------")

for data_vb_resource in sorted_data_vb_resource_list:
    print(data_vb_resource.resource_stride)
    print(data_vb_resource.resource_filename)



'''
有几个硬参数是灵活变化的，需要在逆向开始前提供
reverse_mod_path                mod文件所在文件夹
output_folder                   逆向结果文件输出到哪个目录
ib_file_list                    ib文件名称列表
category_vb_filename_dict       {类别:vb文件名称列表}
'''

output_folder = reverse_mod_path + "reverse/"
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# (1) 读取mod文件列表
mod_files = os.listdir(reverse_mod_path)
print(mod_files)

print("开始之前最后展示一遍ib_file_list")
print(ib_file_list)
# (2) 读取ib文件中，分别最小和最大的数，用于后续转换ib文件时和分割vb文件时提供坐标指示
ib_filename_minnum_dict, ib_filename_maxnum_dict = get_ib_filename_minnum_maxnum_dict_from_ib_file(ib_file_list)
print(ib_filename_minnum_dict)
print(ib_filename_maxnum_dict)

# (4) 获取最终要进行分割处理的vb文件内容
vb_file_bytearray = get_vb_byte_array()


# 根据元素列表获取输出的.fmt文件的内容
fmt_str = get_fmt_str_from_element_list()
# 根据元素列表获取总步长
stride = get_stride_from_element_list()

# (6) 组装出要输出的文件名的字典，用于后续处理,顺便还会输出fmt文件
category_output_name_dict = get_category_output_name_dict(fmt_str)
print(category_output_name_dict)

# (7) 把每个ib文件转换成特殊格式后再输出
convert_and_output_ib_file(category_output_name_dict, ib_filename_minnum_dict)

# (8) 将完整的vb文件分割为多个vb文件
split_vb_files(vb_file_bytearray, category_output_name_dict, stride)



