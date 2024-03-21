# Extract Model from FrameAnalyseFolder.
from Config.GameConfig import *
from Config.IndexBufferFile import *

if __name__ == "__main__":
    game_config = GameConfig()

    pointlist_indices = []
    trianglelist_indices = []
    for filename in game_config.FrameAnalysisFilenameList:
        if filename.endswith(".txt"):
            index = filename[0:6]
            if filename.find("-vb0") != -1:
                search_list = game_config.find_filename_by_condition(index + "-ib", ".txt")
                if len(search_list) == 0:
                    print("Error: Can't find -ib file when -vb0 file exists.")
                    continue
                else:
                    print(search_list[0])
                    ib_file = IndexBufferFile(file_path=game_config.WorkFolder + search_list[0])
                    if ib_file.Topology == "pointlist":
                        pointlist_indices.append(index)
                        continue
                        # ib_file.show()
            if filename.find("-ib") != -1:
                # TODO trianglelist index
                pass



