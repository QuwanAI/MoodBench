# -*- coding: utf-8 -*-
from typing import Dict, Any, List
from collections import defaultdict
from pprint import pprint
import pandas as pd
import os
import json

from .registry import register_analyzer
from .base_analysis import BaseAnalysis
from PQAEF.tasks.writing.constraint_follow_task import CONSTRAINT_MAPPING


@register_analyzer(name="evaluation_aggregator")
class EvaluationAggregatorAnalysis(BaseAnalysis):
    """
    聚合评估任务的结果，计算准确率、F1分数等多维度指标。
    这个分析器直接处理原始数据列表，而不是扁平化的DataFrame。
    """

    def analyze(self, df: pd.DataFrame, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        print("INFO: [Analyzer] Running Evaluation Aggregator Analysis...")
        
        # 检查原始数据是否包含预期的键，以确定是否可以运行此分析
        if not raw_data or not all('constraints' in item and 'judges' in item for item in raw_data):
            return {
                "title": "Aggregated Evaluation Scores",
                "summary": "Skipped: Input data does not contain the required 'constraints' and 'judges' keys for this analysis.",
                "plots": [],
                "data_tables": {}
            }

        # 1. 映射约束（如果需要）
        # 将原始静态方法中的逻辑移到这里
        def map_constraint(data_to_map: List[Dict]) -> List[Dict]:
            new_data = []
            for d in data_to_map:
                new_constraints = []
                # 确保 'constraints' 是一个列表
                if not isinstance(d.get('constraints'), list):
                    continue
                for constraint in d['constraints']:
                    key = f"{constraint[0]}_{constraint[1]}"
                    value = CONSTRAINT_MAPPING.get(key)
                    if not value:
                        # print(f"Warning: Constraint mapping for '{key}' not found. Skipping.")
                        continue
                    first, second = value.split('_')
                    new_constraint = [first, second, constraint[-1]]
                    new_constraints.append(new_constraint)
                d['constraints'] = new_constraints
                new_data.append(d)
            return new_data

        data = map_constraint(raw_data)

        # 2. 计算各项分数 (直接从 aggregate_results 粘贴)
        num_data = len(data)
        num_constraint = sum(len(item['judges']) for item in data)
        total_acc = sum(1 for item in data if item.get('judges') and sum(item['judges']) == len(item['judges']))
        total_acc_macro = sum(sum(item['judges']) / len(item['judges']) for item in data if item.get('judges'))
        total_acc_micro = sum(sum(item['judges']) for item in data)

        # ... 这里应包含所有其他计算，例如 constraint_extension_list, constraint_type_list 等
        # 为了演示，我们只包含这几个
        
        # 3. 将结果格式化为DataFrame以便报告
        scores_data = {
            'Overall Accuracy (by sample)': f"{total_acc}/{num_data}",
            'Overall Accuracy Value': total_acc / num_data if num_data > 0 else 0,
            'Macro F1 (avg per sample)': f"{total_acc_macro:.2f}/{num_data}",
            'Macro F1 Value': total_acc_macro / num_data if num_data > 0 else 0,
            'Micro F1 (avg per constraint)': f"{total_acc_micro}/{num_constraint}",
            'Micro F1 Value': total_acc_micro / num_constraint if num_constraint > 0 else 0,
        }
        
        # 准备写入JSON的指标数据（只包含数值）
        metrics_for_json = {
            'macro_f1': total_acc_macro / num_data if num_data > 0 else 0,
            'micro_f1': total_acc_micro / num_constraint if num_constraint > 0 else 0,
            'overall_accuracy': total_acc / num_data if num_data > 0 else 0,
        }
        
        # 写入JSON文件
        self._write_metrics_to_json(metrics_for_json)
        
        # 转换为更适合报告的格式
        scores_df = pd.DataFrame([
            ["Overall Accuracy (by sample)", scores_data['Overall Accuracy (by sample)'], scores_data['Overall Accuracy Value']],
            ["Macro F1 (avg per sample)", scores_data['Macro F1 (avg per sample)'], scores_data['Macro F1 Value']],
            ["Micro F1 (avg per constraint)", scores_data['Micro F1 (avg per constraint)'], scores_data['Micro F1 Value']],
        ], columns=['Metric', 'Ratio', 'Value'])
        
        # 在控制台打印摘要
        print("\n--- Aggregated Evaluation Scores ---")
        pprint({k: v for k, v in scores_data.items() if 'Value' in k})
        print("----------------------------------\n")

        # 4. 返回符合标准接口的字典
        return {
            "title": "Aggregated Evaluation Scores",
            "summary": "This section provides aggregated scores based on evaluation results, such as constraint checking accuracy and F1 scores.",
            "plots": [],  # 此分析器不生成图表
            "data_tables": {"Final Evaluation Scores": scores_df}
        }
    
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