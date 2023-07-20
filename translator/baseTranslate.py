import importlib
import Global


class BaseTsa:
    def __init__(self):
        self.now_use_trans = None
        self.trans_engine = None
        self.tsaMap = {"Baidu": "baiduApi", "Tencent": "tencentApi", "TencentImg": "tencentImg",
                       "ali": "ali", "bd": "baidu", "tx": "tencent", "ms": "microsoft", "cy": "caiyun",
                       "yd": "youdao", "sg": "sogou","gg":"google"}

    def return_engine(self):
        # 先判断翻译引擎是否存在，是否变更
        if self.trans_engine is not None and (Global.api_co == self.now_use_trans or Global.public_trans == self.now_use_trans):
            return self.trans_engine
        # 变更则重新创建对应的引擎
        if Global.api_co:
            tsa = self.tsaMap[Global.api_co]
        elif Global.public_trans:
            tsa = self.tsaMap[Global.public_trans]
        else:
            return None

        a_class = importlib.import_module('translator.' + tsa).Tsa # 类
        self.trans_engine = a_class()  # 类实例
        self.now_use_trans = Global.api_co if Global.api_co else Global.public_trans
        return self.trans_engine

    def get_target(self, text, fromLang):
        _engine = self.return_engine()
        if _engine is not None:
            return _engine.translate(text,fromLang)
        else:
            return "未选择翻译接口"
