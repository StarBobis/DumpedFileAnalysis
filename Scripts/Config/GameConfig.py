import os


class GameConfig:
    OutputFolder = ""
    LoaderFolder = ""
    FrameAnalysisFolder = "latest"
    WorkFolder = ""

    FrameAnalysisFilenameList = []

    def __init__(self, game_name):
        # TODO read setting from GameSetting.json based on game_name

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