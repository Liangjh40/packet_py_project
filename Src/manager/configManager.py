import datetime
import json
import os


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            print("MyEncoder-datetime.datetime")
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        if isinstance(obj, int):
            return int(obj)
        elif isinstance(obj, float):
            return float(obj)
        #elif isinstance(obj, array):
        #    return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)

class ConfigManager:
    def __init__(self):
        self.work_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        self.config = {}
        self.env_dict = {}
        self.project_dict = {}
        self.settings = {}
        self.load_config()

    def load_config(self):
        self.config = self.read_config(os.path.join(self.work_path, "config.json"))
        self.env_dict = self.config.get("env", {})
        self.project_dict = self.config.get("project", {})
        self.settings = self.config.get("settings", {})
        if "compile_threads" not in self.settings:
            self.settings["compile_threads"] = max(1, os.cpu_count() or 4)
            self.config["settings"] = self.settings
            self.write_config(self.config, os.path.join(self.work_path, "config.json"))

    def update_env(self):
        self.config["env"] = self.env_dict
        self.write_config(self.config, os.path.join(self.work_path, "config.json"))

    def update_project(self):
        self.config["project"] = self.project_dict
        self.write_config(self.config, os.path.join(self.work_path, "config.json"))



    @staticmethod
    def write_config(config_dict, config_path):
        print(config_dict)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, cls=MyEncoder, ensure_ascii=False, indent=4)
        print(f"写入配置文件 {config_dict} 写入路径 {config_path}")

    @staticmethod
    def read_config(config_path):
        if not os.path.exists(config_path):
            print(f"配置文件不存在，自动创建默认配置: {config_path}")
            default_config = {"env": {}, "project": {}, "settings": {"compile_threads": max(1, os.cpu_count() or 4)}}
            ConfigManager.write_config(default_config, config_path)
            return default_config
            
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_dict = json.load(f)
                print(f"读取配置文件  {config_dict} 写入路径 {config_path}")
                return config_dict
        except Exception as e:
            print(f"读取配置文件失败 {e}")
            return {}

config_manager = ConfigManager()
