# -*- coding: utf-8 -*-
from typing import Dict, Any, List
import pandas as pd
import json
import os

from .registry import register_analyzer
from .base_analysis import BaseAnalysis
from PQAEF.constant import constant


@register_analyzer(name="TruthfulQA")
class TestTruthfulQAAnalyzer(BaseAnalysis):
    """
    TruthfulQA任务的分析器，计算MC1和MC2的准确率并求平均值。
    """

    def analyze(self, df: pd.DataFrame, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        print("INFO: [Analyzer] Running TruthfulQA Analysis...")
        
        # 检查原始数据是否包含预期的键
        if not raw_data or not all(isinstance(item, dict) and ('MC1' in item or 'MC2' in item) for item in raw_data if isinstance(item, dict)):
            return {
                "title": "TruthfulQA Analysis",
                "summary": "Skipped: Input data does not contain the required 'MC1' or 'MC2' keys for this analysis.",
                "plots": [],
                "data_tables": {}
            }
        
        # 过滤出包含MC1或MC2字段的数据项
        results = [item for item in raw_data if isinstance(item, dict) and ('MC1' in item or 'MC2' in item)]
        
        if not results:
            return {
                "title": "TruthfulQA Analysis",
                "summary": "No valid results found for analysis.",
                "plots": [],
                "data_tables": {}
            }
        
        # 计算MC1和MC2的准确率
        metrics = self._calculate_truthfulqa_metrics(results)
        
        # 将指标写入JSON文件
        self._write_metrics_to_json(metrics)
        
        return {
            "title": "TruthfulQA Analysis",
            "summary": f"Calculated TruthfulQA metrics: {metrics}",
            "plots": [],
            "data_tables": {}
        }
    
    def _calculate_truthfulqa_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算TruthfulQA的MC1和MC2准确率指标
        """
        mc1_scores = []
        mc2_scores = []
        
        # 提取MC1和MC2分数
        for result in results:
            if 'MC1' in result:
                try:
                    mc1_score = float(result['MC1'])
                    mc1_scores.append(mc1_score)
                except (ValueError, TypeError):
                    print(f"Warning: Invalid MC1 score: {result['MC1']}")
            
            if 'MC2' in result:
                try:
                    mc2_score = float(result['MC2'])
                    mc2_scores.append(mc2_score)
                except (ValueError, TypeError):
                    print(f"Warning: Invalid MC2 score: {result['MC2']}")
        
        # 计算平均准确率
        mc1_accuracy = sum(mc1_scores) / len(mc1_scores) if mc1_scores else 0.0
        mc2_accuracy = sum(mc2_scores) / len(mc2_scores) if mc2_scores else 0.0
        
        # 计算总体平均准确率（MC1和MC2的平均值）
        overall_accuracy = 0.0
        if mc1_scores and mc2_scores:
            overall_accuracy = (mc1_accuracy + mc2_accuracy) / 2
        elif mc1_scores:
            overall_accuracy = mc1_accuracy
        elif mc2_scores:
            overall_accuracy = mc2_accuracy
        
        metrics = {
            'overall_accuracy': overall_accuracy,
            'MC1_accuracy': mc1_accuracy,
            'MC2_accuracy': mc2_accuracy,
            'MC1_count': len(mc1_scores),
            'MC2_count': len(mc2_scores),
            'total_samples': len(results)
        }
        
        print(f"MC1准确率: {mc1_accuracy:.4f} ({len(mc1_scores)} samples)")
        print(f"MC2准确率: {mc2_accuracy:.4f} ({len(mc2_scores)} samples)")
        print(f"总体准确率: {overall_accuracy:.4f}")
        
        return metrics
            
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