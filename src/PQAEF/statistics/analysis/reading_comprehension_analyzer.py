# -*- coding: utf-8 -*-
from typing import Dict, Any, List
import pandas as pd
import json
import os

from .registry import register_analyzer
from .base_analysis import BaseAnalysis
from PQAEF.constant import constant


@register_analyzer(name="reading_comprehension")
class ReadingComprehensionAnalyzer(BaseAnalysis):
    """
    阅读理解任务的分析器，计算平均ROUGE分数等指标。
    """

    def analyze(self, df: pd.DataFrame, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        print("INFO: [Analyzer] Running Reading Comprehension Analysis...")
        
        # 检查原始数据是否包含预期的键
        if not raw_data or not all('rouge_score' in item for item in raw_data if isinstance(item, dict)):
            return {
                "title": "Reading Comprehension Analysis",
                "summary": "Skipped: Input data does not contain the required 'rouge_score' key for this analysis.",
                "plots": [],
                "data_tables": {}
            }
        
        # 过滤出包含rouge_score字段的数据项（排除第一个统计项）
        results = [item for item in raw_data if isinstance(item, dict) and 'rouge_score' in item]
        
        if not results:
            return {
                "title": "Reading Comprehension Analysis",
                "summary": "No valid results found for analysis.",
                "plots": [],
                "data_tables": {}
            }
        # 尝试从第一个结果中获取eval_tool信息
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
        
        # 如果没有指定的评估工具，默认使用准确率
        if not metrics:
            metrics = self._calculate_average_rouge(results)
        
        # 将指标写入JSON文件
        self._write_metrics_to_json(metrics)
        
        return {
            "title": "Reading Comprehension Analysis",
            "summary": f"Calculated average ROUGE metrics: {metrics}",
            "plots": [],
            "data_tables": {}
        }
    
    def _calculate_average_rouge(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算平均ROUGE分数
        """
        rouge_scores = [item['rouge_score'] for item in results]
        total_count = len(results)
        
        if total_count > 0:
            avg_rouge_1_f = sum(score['rouge-1']['f'] for score in rouge_scores) / total_count
            avg_rouge_2_f = sum(score['rouge-2']['f'] for score in rouge_scores) / total_count
            avg_rouge_l_f = sum(score['rouge-l']['f'] for score in rouge_scores) / total_count
            
            metrics = {
                    'rouge-1-f': avg_rouge_1_f,
                    'rouge-2-f': avg_rouge_2_f,
                    'rouge-l-f': avg_rouge_l_f,
                    'total_count': total_count
            }
            
            print(f"处理了 {total_count} 个阅读理解样本")
            print(f"平均ROUGE-1 F1分数: {avg_rouge_1_f:.4f}")
            print(f"平均ROUGE-2 F1分数: {avg_rouge_2_f:.4f}")
            print(f"平均ROUGE-L F1分数: {avg_rouge_l_f:.4f}")
        else:
            metrics = {
                'overall': {
                    'rouge-1-f': 0.0,
                    'rouge-2-f': 0.0,
                    'rouge-l-f': 0.0,
                    'total_count': 0
                }
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