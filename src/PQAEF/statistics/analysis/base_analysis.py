# # -*- coding: utf-8 -*-
# from abc import ABC, abstractmethod
# from typing import Dict, Any, List
# import pandas as pd
# import os
# from matplotlib.font_manager import FontProperties

# class BaseAnalysis(ABC):
#     """
#     所有分析器类的抽象基类。
#     定义了分析器必须实现的通用接口。
#     """
#     def __init__(self, config: Dict[str, Any], output_dir: str, font_props: FontProperties, file_prefix: str):
#         """
#         初始化分析器。

#         Args:
#             config (Dict[str, Any]): 全局配置字典。
#             output_dir (str): 用于保存图表等文件的输出目录。
#             font_props (FontProperties): 用于绘图的字体属性。
#             file_prefix (str): 文件名前缀。
#         """
#         self.config = config
#         self.output_dir = output_dir
#         self.font_props = font_props
#         self.file_prefix = file_prefix

#     @abstractmethod
#     def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
#         """
#         执行分析的核心方法。

#         Args:
#             df (pd.DataFrame): 预处理过的、包含所有数据的DataFrame。

#         Returns:
#             Dict[str, Any]: 一个包含分析结果的字典。
#                            必须遵循以下结构，以便报告生成器可以统一处理：
#                            {
#                                "title": str,           # 报告中此部分的标题
#                                "summary": str,         # 对结果的文本描述
#                                "plots": List[str],     # 生成的图表文件的绝对路径列表
#                                "data_tables": Dict[str, pd.DataFrame] # 要在报告中显示的DataFrame
#                            }
#         """
#         pass

#     def _get_safe_filename(self, base_name: str) -> str:
#         """辅助函数，创建安全的文件名。"""
#         import re
#         return re.sub(r'[^a-zA-Z0-9_-]', '_', base_name)

# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pandas as pd
import os
from matplotlib.font_manager import FontProperties
import json

class BaseAnalysis(ABC):
    """
    所有分析器类的抽象基类。
    定义了分析器必须实现的通用接口。
    """
    def __init__(self, config: Dict[str, Any], output_dir: str, font_props: FontProperties, file_prefix: str):
        self.config = config
        self.output_dir = output_dir
        self.font_props = font_props
        self.file_prefix = file_prefix
        self.title = "Abstract Analysis"

    @abstractmethod
    def analyze(self, df: pd.DataFrame, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]: # <--- MODIFIED
        """
        执行分析的核心方法。

        Args:
            df (pd.DataFrame): 预处理过的、包含所有数据的DataFrame。
                               适用于通用统计分析。
            raw_data (List[Dict[str, Any]]): 原始、未处理的数据列表。
                                             适用于需要原始嵌套结构的特定评估分析。

        Returns:
            Dict[str, Any]: 一个包含分析结果的字典。
        """
        pass

    def _get_safe_filename(self, base_name: str) -> str:
        import re
        return re.sub(r'[^a-zA-Z0-9_-]', '_', base_name)
    
    
    def _write_metrics_to_json(self, metrics: Dict[str, Any]):
        """
        将指标写入JSON文件
        """
        try:
            # 构建输出文件路径（与statistical_analysis目录同级）
            output_file = os.path.join(self.output_dir, 'result_stats.json')
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, ensure_ascii=False, indent=2)
            
            print(f"Metrics saved to: {output_file}")
        except Exception as e:
            print(f"Error writing metrics to JSON: {e}")