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
from BasicConfig import *


def get_topology_vertexcount(filename):
    ib_file = open(filename, "rb")
    ib_file_size = os.path.getsize(filename)
    get_topology = None
    get_vertex_count = None
    count = 0
    while ib_file.tell() <= ib_file_size:
        line = ib_file.readline()
        # Because topology only appear in the first 5 line,so if count > 5 ,we can stop looking for it.
        count = count + 1
        if count > 5:
            break
        if line.startswith(b"vertex count: "):
            get_vertex_count = line[line.find(b"vertex count: ") + b"vertex count: ".__len__():line.find(b"\r\n")]

        if line.startswith(b"topology: "):
            topology = line[line.find(b"topology: ") + b"topology: ".__len__():line.find(b"\r\n")]
            if topology == b"pointlist":
                get_topology = b"pointlist"
                break
            if topology == b"trianglelist":
                get_topology = b"trianglelist"
                break

    # Safely close the file.
    ib_file.close()

    return get_topology, get_vertex_count


def get_pointlit_and_trianglelist_indices(input_ib_hash, root_vs="", use_root_vs=True):
    # The index number at the front of every file's filename.
    indices = sorted([re.findall('^\d+', x)[0] for x in glob.glob('*-vb0*txt')])

    pointlist_indices_dict = {}
    trianglelist_indices_dict = {}
    trianglelist_vertex_count = None
    # 1.First, grab all vb0 file's indices.
    for index in range(len(indices)):
        ib_filename = glob.glob(indices[index] + '-ib*txt')[0]

        # 优化，仅处理相关ib，其余不处理
        if input_ib_hash not in ib_filename:
            continue

        vb0_filename = glob.glob(indices[index] + '-vb0*txt')[0]
        topology, vertex_count = get_topology_vertexcount(vb0_filename)
        if topology == b"pointlist":
            if use_root_vs:
                # Filter, vb0 filename must have ROOT VS.
                if root_vs in vb0_filename:
                    pointlist_indices_dict[indices[index]] = vertex_count
            else:
                pointlist_indices_dict[indices[index]] = vertex_count


        topology, vertex_count = get_topology_vertexcount(ib_filename)
        if topology == b"trianglelist":
            # Filter,ib filename must include input_ib_hash.
            topology, vertex_count = get_topology_vertexcount(vb0_filename)
            trianglelist_indices_dict[(indices[index])] = vertex_count
            trianglelist_vertex_count = vertex_count

    # Based on vertex count, remove the duplicated pointlist indices.
    pointlist_indices = []
    trianglelist_indices = []
    for pointlist_index in pointlist_indices_dict:
        if pointlist_indices_dict.get(pointlist_index) == trianglelist_vertex_count:
            pointlist_indices.append(pointlist_index)

    for trianglelist_index in trianglelist_indices_dict:
        trianglelist_indices.append(trianglelist_index)

    print("----------------------------------------------------------")
    print("Pointlist vb indices: " + str(pointlist_indices))
    if len(pointlist_indices) == 0:
        print("This game don't use pointlist tech.")
    print("Trianglelist vb indices: " + str(trianglelist_indices))

    return pointlist_indices, trianglelist_indices


def get_unique_ib_bytes_by_indices(indices):
    ib_filenames = []
    for index in range(len(indices)):
        indexnumber = indices[index]
        ib_filename = sorted(glob.glob(str(indexnumber) + '-ib*txt'))[0]
        ib_filenames.append(ib_filename)

    ib_file_info = {}
    ib_file_bytes = []
    for ib_filename in ib_filenames:
        with open(ib_filename, "rb") as ib_file:
            bytes = ib_file.read()
            if bytes not in ib_file_bytes:
                ib_file_bytes.append(bytes)
                ib_file_info[ib_filename] = bytes

    return ib_file_info


def get_all_first_index(input_ib_hash):
    """
    List all ib file's first index for an input ib hash.
    So you can test which part of a single index buffer could be removed correctly.
    Especially for the games that put a large number of object in a single index buffer.
    """

    pointlist_indices, trianglelist_indices = get_pointlit_and_trianglelist_indices(input_ib_hash, use_root_vs=False)
    ib_file = get_unique_ib_bytes_by_indices(trianglelist_indices)
    count = 0

    output_strs = ""
    for ib_file_name in ib_file:
        ib_bytes = ib_file.get(ib_file_name)
        header = ib_bytes[0:100]
        first_index = header[header.find(b"first index: ") + 13:header.find(b"\r\nindex count:")]
        output_strs = output_strs + ";" + str(ib_file_name) + "\n"
        output_strs = output_strs + "[TextureOverride_test_" + str(count) + "]" + "\n"
        output_strs = output_strs + "hash = " + input_ib_hash + "\n"
        output_strs = output_strs + "match_first_index = " + first_index.decode() + "\n"
        output_strs = output_strs + "handling = skip" + "\n" + "\n"
        count = count + 1

    return output_strs


if __name__ == "__main__":
    """
    Normally used for UE4 games..
    If multi part in a single Index Buffer ,this tool will be very helpful to test.
    """

    # 设置工作目录
    os.chdir(WorkFolder)

    # 设置要分析的IB
    ib_hash = draw_ibs[0]

    # 生成TextureOverride列表
    output_str = get_all_first_index(ib_hash)

    # 设置输出的文件名字
    output_filename = mod_name + ".ini"

    # 设置输出的目录
    output_folder = LoaderFolder + "Mods/"

    # 生成输出的文件名
    output_filename_final = output_folder + output_filename

    output_file = open(output_filename_final, "w+")
    output_file.write(output_str)
    output_file.close()
