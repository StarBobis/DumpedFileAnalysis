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
import os
import glob
import shutil
import datetime

from BasicConfig import *


if __name__ == "__main__":
    # 此脚本用于TextureOverride和ShaderOverride的规范化命名生成。
    # 首先确定mod文件输出位置
    output_folder = LoaderFolder + "Mods"

    # 然后确定输出的mod文件名称，这里名称示例为 mod_name.ini
    mod_file_name = mod_name + ".ini"

    # 然后确定最终写入的mod文件的完整路径
    output_filename = output_folder + "/" + mod_file_name

    # 一个变量用于装载最终文本内容
    mod_content = ""

    # 处理TextureOverride
    for override_hash in draw_ibs:
        texture_override_sect = ""
        texture_override_sect = texture_override_sect + "[TextureOverride_" + mod_name + "_" + override_hash + "]\n"
        texture_override_sect = texture_override_sect + "hash = " + override_hash + "\n"
        texture_override_sect = texture_override_sect + "handling = skip\n"
        texture_override_sect = texture_override_sect + "\n"
        mod_content = mod_content + texture_override_sect

    if basic_check:
        mod_content += get_basic_check_str()

    output_file = open(output_filename, "w+")
    output_file.write(mod_content)
    output_file.close()



