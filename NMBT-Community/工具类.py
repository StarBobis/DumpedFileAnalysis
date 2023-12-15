import json
import os

class 日志类:
    def 输出(self, string):
        print(str(string))


class 全局配置类:
    游戏名称 = ""
    自动备份 = False
    备份文件夹 = ""
    繁琐日志 = True
    写出日志 = False
    日志文件夹 = ""
    自动删除输出文件夹 = True

    def __init__(self):
        全局配置路径 = "全局配置.json"
        with open(全局配置路径, 'r', encoding='utf-8') as file:
            全局配置数据 = json.load(file)

        self.游戏名称 = 全局配置数据["游戏名称"]
        self.自动备份 = 全局配置数据["自动备份"]
        self.备份文件夹 = 全局配置数据["备份文件夹"]
        self.繁琐日志 = 全局配置数据["繁琐日志"]
        self.写出日志 = 全局配置数据["写出日志"]
        self.日志文件夹 = 全局配置数据["日志文件夹"]
        self.自动删除输出文件夹 = 全局配置数据["自动删除输出文件夹"]

    def 让我康康(self):
        print("游戏名称: " + self.游戏名称)
        print("自动备份: " + str(self.自动备份))
        print("备份文件夹: " + self.备份文件夹)
        print("繁琐日志: " + str(self.繁琐日志))
        print("写出日志: " + str(self.写出日志))
        print("日志文件夹: " + self.日志文件夹)
        print("自动删除输出文件夹: " + str(self.自动删除输出文件夹))


# used for wrap a single Element in every gametype.ini, eg:GIBody.ini
class D3D11元素类:
    语义 = ""
    提取语义 = ""
    语义索引 = 0
    格式 = ""
    带宽 = 0
    提取槽位 = ""
    提取拓扑 = ""
    类别 = ""
    输入槽位 = 0
    输入槽位种类 = ""
    实例数据步长比例 = 0


# used for read Setting.ini at every game folder.
class 游戏配置类:
    引擎 = ""
    加载器文件夹 = ""
    输出文件夹 = ""
    帧分析文件夹 = ""
    工作目录 = ""

    模组名称 = ""
    绘制索引缓冲区哈希值与提取类型字典 = {}

    读入索引缓冲区格式 = ""
    输出索引缓冲区格式 = ""
    切线算法 = ""

    混合槽位 = ""
    原混合槽位 = ""
    顶点着色器检查 = False
    顶点着色器检查列表 = []

    红 = -1
    绿 = -1
    蓝 = -1
    阿尔法 = -1

    语义_D3D11元素类字典 = {}
    提取语义_D3D11元素类字典 = {}
    帧分析文件列表 = []
    纹理目录 = ""
    独特纹理目录 = ""

    def __init__(self, 游戏名称):
        游戏配置路径 = "游戏配置/" + 游戏名称 + "/配置.json"
        with open(游戏配置路径, 'r', encoding='utf-8') as file:
            游戏配置数据 = json.load(file)

        self.引擎 = 游戏配置数据["通用配置"]["引擎"]
        self.加载器文件夹 = 游戏配置数据["通用配置"]["加载器文件夹"]
        self.输出文件夹 = 游戏配置数据["通用配置"]["输出文件夹"]
        self.帧分析文件夹 = 游戏配置数据["通用配置"]["帧分析文件夹"]
        if self.帧分析文件夹 == "最新":
            filenames = os.listdir(self.加载器文件夹)
            fa_filenames = []
            for filename in filenames:
                if filename.startswith("FrameAnalysis-"):
                    fa_filenames.append(filename)

            fa_filenames.sort()
            self.帧分析文件夹 =fa_filenames[-1]
        self.工作目录 = self.加载器文件夹 + self.帧分析文件夹
        self.模组名称 = 游戏配置数据["通用配置"]["模组名称"]
        绘制索引缓冲区哈希值与提取类型列表 = str(游戏配置数据["通用配置"]["绘制索引缓冲区哈希值与提取类型"]).split(",")
        for 绘制索引缓冲区哈希值与提取类型 in 绘制索引缓冲区哈希值与提取类型列表:
            绘制索引缓冲区哈希值与提取类型对 = 绘制索引缓冲区哈希值与提取类型.split("_");
            self.绘制索引缓冲区哈希值与提取类型字典[绘制索引缓冲区哈希值与提取类型对[0]] = 绘制索引缓冲区哈希值与提取类型对[1]





    def 让我康康(self):
        print("引擎: " + self.引擎)
        print("加载器文件夹: " + self.加载器文件夹)
        print("输出文件夹: " + self.输出文件夹)
        print("帧分析文件夹: " + self.帧分析文件夹)
        print("工作目录: " + str(self.工作目录))

        print("模组名称: " + self.模组名称)
        print("绘制索引缓冲区哈希值与提取类型: " + str(self.绘制索引缓冲区哈希值与提取类型字典))

        print("读入索引缓冲区格式: " + self.读入索引缓冲区格式)
        print("输出索引缓冲区格式: " + self.输出索引缓冲区格式)
        print("切线算法: " + self.切线算法)

        print("混合槽位: " + self.混合槽位)
        print("原混合槽位: " + self.原混合槽位)
        print("顶点着色器检查: " + str(self.顶点着色器检查))
        print("顶点着色器检查列表: " + str(self.顶点着色器检查列表))

        print("红: " + str(self.红))
        print("绿: " + str(self.绿))
        print("蓝: " + str(self.蓝))
        print("阿尔法: " + str(self.阿尔法))


        print("语义_D3D11元素类字典: " + str(self.语义_D3D11元素类字典))
        print("提取语义_D3D11元素类字典: " + str(self.提取语义_D3D11元素类字典))
        print("帧分析文件列表: " + str(self.帧分析文件列表))
        print("纹理目录: " + str(self.纹理目录))
        print("独特纹理目录: " + str(self.独特纹理目录))


    def 根据条件查找文件名(self, search_str, suffix_str, search_folder=""):
        pass







class TmpConfig:
    pass

    def __init__(self):
        pass

    def show(self):
        pass

    def save(self):
        pass





