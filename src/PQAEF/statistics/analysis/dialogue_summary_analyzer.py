# -*- coding: utf-8 -*-
from typing import Dict, Any, List
import pandas as pd
import json
import os

from .registry import register_analyzer
from .base_analysis import BaseAnalysis
from PQAEF.constant import constant


@register_analyzer(name="dialogue_summary")
class DialogueSummaryAnalyzer(BaseAnalysis):
    """
    对话摘要任务的分析器，计算平均ROUGE分数等指标。
    """

    def analyze(self, df: pd.DataFrame, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        print("INFO: [Analyzer] Running Dialogue Summary Analysis...")
        
        # 检查原始数据是否包含预期的键
        if not raw_data or not all(self._has_rouge_scores(item) for item in raw_data if isinstance(item, dict)):
            return {
                "title": "Dialogue Summary Analysis",
                "summary": "Skipped: Input data does not contain the required ROUGE score keys for this analysis.",
                "plots": [],
                "data_tables": {}
            }
        
        # 过滤出包含ROUGE分数字段的数据项
        results = [item for item in raw_data if isinstance(item, dict) and self._has_rouge_scores(item)]
        
        if not results:
            return {
                "title": "Dialogue Summary Analysis",
                "summary": "No valid results found for analysis.",
                "plots": [],
                "data_tables": {}
            }
        
        # 获取评估工具类型，默认为Rouge
        eval_tool = self.config.get('eval_tool') or ['Rouge']
        
        # 初始化metrics字典
        metrics = {}
        
        # 确保eval_tool是列表格式
        if isinstance(eval_tool, str):
            eval_tool = [eval_tool]
        
        # 遍历所有评估工具，计算相应指标
        for tool in eval_tool:
            if tool == 'Rouge':
                rouge_metrics = self._calculate_average_rouge(results)
                metrics.update(rouge_metrics)
        
        # 如果没有指定的评估工具，默认使用ROUGE
        if not metrics:
            metrics = self._calculate_average_rouge(results)
        
        # 将指标写入JSON文件
        self._write_metrics_to_json(metrics)
        
        return {
            "title": "Dialogue Summary Analysis",
            "summary": f"Calculated average ROUGE metrics: {metrics}",
            "plots": [],
            "data_tables": {}
        }
    
    def _has_rouge_scores(self, item: Dict[str, Any]) -> bool:
        """
        检查数据项是否包含所需的ROUGE分数字段
        """
        return ('rouge-1' in item and 'rouge-2' in item and 'rouge-l' in item and
                'F1-Score' in item.get('rouge-1', {}) and
                'F1-Score' in item.get('rouge-2', {}) and
                'F1-Score' in item.get('rouge-l', {}))
    
    def _calculate_average_rouge(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算平均ROUGE分数
        """
        total_count = len(results)
        
        if total_count > 0:
            # 计算ROUGE-1 F1分数平均值
            avg_rouge_1_f = sum(float(item['rouge-1']['F1-Score']) for item in results) / total_count
            # 计算ROUGE-2 F1分数平均值
            avg_rouge_2_f = sum(float(item['rouge-2']['F1-Score']) for item in results) / total_count
            # 计算ROUGE-L F1分数平均值
            avg_rouge_l_f = sum(float(item['rouge-l']['F1-Score']) for item in results) / total_count
            
            metrics = {
                'rouge-1-f': avg_rouge_1_f,
                'rouge-2-f': avg_rouge_2_f,
                'rouge-l-f': avg_rouge_l_f,
                'total_count': total_count
            }
            
            print(f"处理了 {total_count} 个对话摘要样本")
            print(f"平均ROUGE-1 F1分数: {avg_rouge_1_f:.4f}")
            print(f"平均ROUGE-2 F1分数: {avg_rouge_2_f:.4f}")
            print(f"平均ROUGE-L F1分数: {avg_rouge_l_f:.4f}")
        else:
            metrics = {
                'rouge-1-f': 0.0,
                'rouge-2-f': 0.0,
                'rouge-l-f': 0.0,
                'total_count': 0
            }
        
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