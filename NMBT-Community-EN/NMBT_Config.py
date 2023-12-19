import os


class GlobalConfig:
    OutputFolder = "C:/downloadXunlei/Zenless_Zone_Zero_(Beta)/Mods/output/"
    LoaderFolder = "C:/downloadXunlei/Zenless_Zone_Zero_(Beta)/"
    FrameAnalysisFolder = "latest"
    WorkFolder = ""

    FrameAnalysisFilenameList = []

    def __init__(self):

        # auto get latest FrameAnalysisFolder from LoaderFolder
        if self.FrameAnalysisFolder == "latest":
            filenames = os.listdir(self.LoaderFolder)
            frame_analysis_filename_list = []
            for filename in filenames:
                if filename.startswith("FrameAnalysis-"):
                    frame_analysis_filename_list.append(filename)

            frame_analysis_filename_list.sort()
            self.FrameAnalysisFolder = frame_analysis_filename_list[-1]
        # set WorkFolder
        self.WorkFolder = self.LoaderFolder + self.FrameAnalysisFolder + "/"

        # read every filename.
        self.FrameAnalysisFilenameList = os.listdir(self.WorkFolder)

    def find_filename_by_condition(self, contain_str, suffix_str, search_dir=""):
        filename_list = []
        if search_dir == "":
            filename_list = os.listdir(self.WorkFolder)
        else:
            filename_list = os.listdir(search_dir)
        search_filename_list = []
        for filename in filename_list:
            if filename.find(contain_str) != -1 and filename.endswith(suffix_str):
                search_filename_list.append(filename)
        return search_filename_list



class VertexDataLine:
    pass


class D3D11Element:
    pass


class IndexBufferFile:
    # Attributes in filename
    FileName = ""
    Index = ""
    Hash = ""

    # Attributes in file content,we usually don't use all of them but preserved for compatible reason.
    ByteOffset = "preserved"
    FirstIndex = ""
    IndexCount = ""
    Topology = ""
    Format = "preserved"

    def __init__(self, file_path):
        filename = str(file_path).split("/")[-1].strip()
        self.FileName = filename
        self.Index = filename[0:6]
        self.Hash = filename[11:19]

        with open(file_path, "r") as ib_file:
            lines = ib_file.readlines()
            # parse line by line, python is designed for readable not for show off you skill,so we keep it simple.
            count = 0
            for line in lines:
                topology_str = "topology:"
                first_index_str = "first index:"
                index_count_str = "index count:"
                if line.startswith(topology_str):
                    self.Topology = line[len(topology_str):-1].strip()
                elif line.startswith(first_index_str):
                    self.FirstIndex = line[len(first_index_str):-1].strip()
                elif line.startswith(index_count_str):
                    self.IndexCount = line[len(index_count_str):-1].strip()
                count = count + 1
                if count > 6:
                    break

    def show(self):
        print("FileName: " + self.FileName)
        print("Index: " + self.Index)
        print("Hash: " + self.Hash)
        print("ByteOffset: " + self.ByteOffset)
        print("FirstIndex: " + self.FirstIndex)
        print("IndexCount: " + self.IndexCount)
        print("Topology: " + self.Topology)
        print("Format: " + self.Format)


class VertexBufferFile:
    FileName = ""
    Index = ""
    Hash = ""
    Stride = ""
    VertexCount = ""
    Topology = ""


class FmtFile:
    pass





