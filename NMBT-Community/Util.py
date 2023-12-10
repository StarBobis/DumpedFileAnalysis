import configparser


# used for read config from Config.ini
class GlobalConfig:
    WorkingGame = ""
    AutoBackup = False
    BackUpFolder = ""
    VerboseLog = True
    WriteLog = False
    LogFolder = ""
    DeleteOutputFolder = True

    def __init__(self):
        global_config_path = "Config.ini"
        config = configparser.ConfigParser()
        config.read(global_config_path)

        self.WorkingGame = config["GameSetting"]["WorkingGame"]
        self.AutoBackup = config["BackupSetting"]["AutoBackUp"]
        self.BackUpFolder = config["BackupSetting"]["BackUpFolder"]
        self.VerboseLog = config["LogSetting"]["VerboseLog"]
        self.WriteLog = config["LogSetting"]["WriteLog"]
        self.LogFolder = config["LogSetting"]["LogFolder"]
        self.DeleteOutputFolder = config["BehaviourSetting"]["DeleteOutputFolder"]

    def show(self):
        print("WorkingGame: " + self.WorkingGame)
        print("AutoBackup: " + self.AutoBackup)
        print("BackUpFolder: " + self.BackUpFolder)
        print("VerboseLog: " + self.VerboseLog)
        print("WriteLog: " + self.WriteLog)
        print("LogFolder: " + self.LogFolder)
        print("DeleteOutputFolder: " + self.DeleteOutputFolder)


# used for wrap a single Element in every gametype.ini, eg:GIBody.ini
class D3D11Element:
    semantic = ""
    extract_semantic = ""
    semantic_index = 0
    format = ""
    byte_width = 0
    extract_slot = ""
    extract_tech = ""
    category = ""
    input_slot = 0
    input_slot_class = ""
    instance_data_step_rate = 0


# used for read Setting.ini at every game folder.
class SettingConfig:
    Engine = ""
    LoaderFolder = ""
    OutputFolder = ""
    FrameAnalyseFolder = ""
    ModName = ""
    DrawIB = ""


class TmpConfig:
    pass


if __name__ == "__main__":
    pass
    # Test for GlobalConfig class
    # GlobalConfig = GlobalConfig()
    # GlobalConfig.show()

    # Test for


