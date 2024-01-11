
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
