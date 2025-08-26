# -*- coding: utf-8 -*-
from typing import Dict, Any, List
import pandas as pd
import json
import os
from sklearn.metrics import f1_score

from .registry import register_analyzer
from .base_analysis import BaseAnalysis
from PQAEF.constant import constant


@register_analyzer(name="liangbiao")
class LiangbiaoAnalyzer(BaseAnalysis):
    """
    量表分数计算
    """

    def analyze(self, df: pd.DataFrame, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        print("INFO: [Analyzer] Running liangbiao Analysis...")
        
        metrics = self._calculate_score(raw_data)
        
        # 将指标写入JSON文件
        self._write_metrics_to_json(metrics)
        
        return {
            "title": "Single Choice Analysis",
            "summary": f"Calculated liangbiao metrics",
            "plots": [],
            "data_tables": {}
        }
    
    def _calculate_score(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算量表分数
        """
        total_score = []
        res_score = 0
        
        for item in results:
            correct_answer = item['correct_answer']
            total_score = total_score + list(correct_answer.values())
            
            predicted = item['predicted_answer']
            # 检查predicted_answer是否在correct_answer的键中
            if predicted in correct_answer:
                score = correct_answer[predicted]
            else:
                # 对于UNKNOWN或其他无效回答，给予最低分数
                score = min(correct_answer.values())
                print(f"Warning: Invalid predicted_answer '{predicted}' found, assigning minimum score {score}")
            
            res_score = res_score + score
    
        total_count = len(results)
        min_value = min(total_score) * total_count
        max_value = max(total_score) * total_count
        score = (res_score - min_value) / (max_value - min_value)
    
        metric = {
            'overall': score,
            'total_count': total_count
        }
        print(f"量表指标: {metric['overall']:.2%}")
        return metric
            
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