"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import configparser
import os
import glob
import shutil
import re


global_config = configparser.ConfigParser()
global_config.read("Configs/global_config.ini", "utf-8")
config_folder = global_config["Global"]["config_folder"]

preset_config = configparser.ConfigParser()
preset_config.read(config_folder + "/preset.ini", "utf-8")

OutputFolder = preset_config["General"]["OutputFolder"]
LoaderFolder = preset_config["General"]["LoaderFolder"]
FrameAnalyseFolder = preset_config["General"]["FrameAnalyseFolder"]
mod_name = preset_config["General"]["mod_name"]


draw_ibs = preset_config["Merge"]["draw_ibs"].split(",")

basic_check = preset_config["Split"]["basic_check"]

def get_latest_folder():
    filenames = os.listdir(LoaderFolder)
    FA_filenames = []
    for filename in filenames:
        if filename.startswith("FrameAnalysis-"):
            FA_filenames.append(filename)

    FA_filenames.sort()
    return FA_filenames[-1]


if FrameAnalyseFolder == "latest":
    FrameAnalyseFolder = get_latest_folder()

WorkFolder = LoaderFolder + FrameAnalyseFolder
print("FrameAnalyseFolder: " + FrameAnalyseFolder)


def get_filter_filenames(in_str, end_str,target_folder=WorkFolder):
    filtered_filenames = []
    filenames = os.listdir(target_folder)
    for filename in filenames:
        if in_str in filename and filename.endswith(end_str):
            filtered_filenames.append(filename)
    return filtered_filenames


def get_basic_check_str():
    vertex_shader_list = []
    # all VertexShader will show in IndexBuffer related files.
    for draw_ib in draw_ibs:
        ib_files = get_filter_filenames(draw_ib, ".txt")
        # Get all VertexShader need to check

        for filename in ib_files:
            vs = filename.split("-vs=")[1][0:16]
            if vs not in vertex_shader_list:
                vertex_shader_list.append(vs)

    print(vertex_shader_list)

    # Add texcoord VertexShader check
    texcoord_check_slots = ["vb1", "ib"]
    action_check_slots = ["vb0"]

    # output str
    output_str = ""
    output_str = output_str + ";Texcoord Check List:" + "\n" + "\n"
    for vs in sorted(vertex_shader_list):
        section_name = "[ShaderOverride_VS_" + vs + "_Test_]"
        print("add section :" + section_name)

        output_str = output_str + section_name + "\n"
        output_str = output_str + "hash = " + vs + "\n"
        output_str = output_str + "if $costume_mods" + "\n"
        for slot in texcoord_check_slots:
            output_str = output_str + "  checktextureoverride = " + slot + "\n"
        output_str = output_str + "endif" + "\n"
        output_str = output_str + "\n"
    return output_str

def generate_basic_check():
    # Use a extra basic_check.ini is troublesome,but global check will get a huge FPS decrease in some game.
    basic_check_filename = LoaderFolder + "Mods/basic_check.ini"

    # Create a new basic_check.ini
    file = open(basic_check_filename, "w+")
    file.write("")
    file.close()

    output_str = get_basic_check_str()

    # Finally save the config file.
    output_file = open(basic_check_filename, "w")
    output_file.write(output_str)
    output_file.close()

