import os
import configparser
import shutil
import struct
import math

# 读取配置文件
global_config = configparser.ConfigParser()
global_config.read("Configs/global_config.ini", "utf-8")
config_folder = global_config["Global"]["config_folder"]

preset_config = configparser.ConfigParser()
preset_config.optionxform = str  # 设置optionxform属性为str，保留原始大小写形式
preset_config.read(config_folder + "/preset.ini", "utf-8")

tmp_config = configparser.ConfigParser()
tmp_config.read(config_folder + "/tmp.ini", "utf-8")

vertex_config = configparser.ConfigParser()
vertex_config.read(config_folder + "/vertex_attr.ini", "utf-8")

# 只读取一个必须的路径参数
reverse_ini_path = preset_config["Reverse"]["reverse_ini_path"]

# 拆分这个路径参数 reverse_ini_path
# 原路径：C:/Users/Administrator/Desktop/fuhua-RosyBridesmaid-sfw-2/fuhua-RosyBridesmaid.ini
# reverse_mod_path： C:/Users/Administrator/Desktop/fuhua-RosyBridesmaid-sfw-2/
reverse_mod_path = os.path.dirname(reverse_ini_path) + "/"
# reverse_ini_name：fuhua-RosyBridesmaid.ini
reverse_ini_name = os.path.basename(reverse_ini_path)
# mod_name：fuhua-RosyBridesmaid
mod_name = reverse_ini_name.split(".")[0]

print("逆向Mod的Buffer文件所在路径：" + reverse_mod_path)
print("逆向Mod的主ini文件名称：" + reverse_ini_name)
print("逆向Mod的输出Mod名称：" + mod_name)

reverse_ini_config = configparser.ConfigParser()
reverse_ini_config.optionxform = str  # 设置optionxform属性为str，保留原始大小写形式
reverse_ini_config.read(reverse_ini_path, "utf-8")

class DataIBResource:
    resource_name = None
    resource_format = None
    resource_filename = None


class DataVBResource:
    resource_name = None
    resource_stride = None
    resource_filename = None


class DataIBOverride:
    overide_name = None
    match_first_index = None
    ib_resource_name = None
    ib_resource_filename = None


class IniKVPair:
    section_name = ""
    kv_map = {"": ""}

    def __str__(self):
        print_str = "SectionName: " + self.section_name + "\n"
        for option_name in self.kv_map:
            option_value = self.kv_map.get(option_name)
            print_str += "OptionName: " + option_name + "\n" + "OptionValue: " + option_value + "\n"
        print_str += "-----------------------------"
        return print_str


