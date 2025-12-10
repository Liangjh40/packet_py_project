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
        self.load_config()

    def load_config(self):
        self.config = self.read_config("./config.json")
        self.env_dict = self.config.get("env", {})
        self.project_dict = self.config.get("project", {})

    def update_env(self):
        self.config["env"] = self.env_dict
        self.write_config(self.config, "./config.json")

    def update_project(self):
        self.config["project"] = self.project_dict
        self.write_config(self.config, "./config.json")



    @staticmethod
    def write_config(config_dict, config_path):
        print(config_dict)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, cls=MyEncoder, ensure_ascii=False, indent=4)
        print(f"写入配置文件 {config_dict} 写入路径 {config_path}")

    @staticmethod
    def read_config(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_dict = json.load(f)
                print(f"读取配置文件  {config_dict} 写入路径 {config_path}")
                return config_dict
        except Exception as e:
            print(f"读取配置文件失败 {e}")
            return {}

config_manager = ConfigManager()
