import configparser


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


if __name__ == "__main__":
    pass
    # Test for GlobalConfig class
    # GlobalConfig = GlobalConfig()
    # GlobalConfig.show()

    # Test for


