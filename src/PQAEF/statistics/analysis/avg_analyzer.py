# -*- coding: utf-8 -*-
from typing import Dict, Any, List
import pandas as pd
import json
import os
from sklearn.metrics import f1_score

from .registry import register_analyzer
from .base_analysis import BaseAnalysis
from PQAEF.constant import constant


class AvgAnalyzer(BaseAnalysis):
    def __init__(self, config, output_dir, font_props, file_prefix):
        super().__init__(config, output_dir, font_props, file_prefix)
        self.title = "Avg Analysis"
        self._avg_column = []
    
    def set_avg_column(self, avg_column: List[str]):
        self._avg_column = avg_column
        
    @staticmethod
    def _get_nested_value(data: Dict, key_path: str, default: Any = 0) -> Any:
        keys = key_path.split('.')
        current_level = data
        for key in keys:
            if isinstance(current_level, dict):
                current_level = current_level.get(key)
            else:
                return default
        
        if current_level is None:
            return default
            
        if isinstance(current_level, (int, float, bool)):
            return current_level
        else:
            return default
    
    def _path_exists(self, item):
        for key in self._avg_column:
            keys = key.split(".")
            current_level = item
            for k in keys:
                if not isinstance(current_level, dict) or k not in current_level:
                    return False
                current_level = current_level[k]
        return True
    
    def analyze(self, df: pd.DataFrame, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        print(f"INFO: [Analyzer] Running {self.title}...")
        
        if len(self._avg_column) == 0:
            raise NotImplementedError("avg_column is empty, please use `set_avg_column` first")
        
        # 检查原始数据是否包含预期的键
        if not raw_data or not all(self._path_exists(item) for item in raw_data if isinstance(item, dict)):
            return {
                "title": self.title,
                "summary": f"Skipped: Input data does not contain the required `{self._avg_column}` key for this analysis.",
                "plots": [],
                "data_tables": {}
            }
        
        results = [item for item in raw_data if isinstance(item, dict) and self._path_exists(item)]
        
        if not results:
            return {
                "title": self.title,
                "summary": "No valid results found for analysis.",
                "plots": [],
                "data_tables": {}
            }
        
        metrics = self._calculate_avg(results)
        self._write_metrics_to_json(metrics)
        
        return {
            "title": self.title,
            "summary": f"Metrics: {metrics}",
            "plots": [],
            "data_tables": {}
        }
    
    def _calculate_avg(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        
        total_count = len(results)
        averages = {}
        
        for column_name in self._avg_column:
            column_sum = sum(self._get_nested_value(result, column_name, 0) for result in results)
            
            averages[column_name] = column_sum / total_count

        return averages
            

@register_analyzer("cped_analyzer")
class CPEDAvgAnalyzer(AvgAnalyzer):
    def __init__(self, config, output_dir, font_props, file_prefix):
        super().__init__(config, output_dir, font_props, file_prefix)
        self.set_avg_column(["ppl_on_generated", "distinct_n", "bleu.BLEU-1", "bleu.BLEU-2", "bleu.BLEU-3", "bleu.BLEU-4"])