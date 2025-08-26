# -*- coding: utf-8 -*-
from typing import Dict, Any, List
import pandas as pd
import json
import os
from sklearn.metrics import f1_score

from .registry import register_analyzer
from .base_analysis import BaseAnalysis
from PQAEF.constant import constant


@register_analyzer(name="multi_choice")
class MultiChoiceAnalyzer(BaseAnalysis):
    """
    多选题任务的分析器，计算准确率、F1分数和EM等指标。
    """

    def analyze(self, df: pd.DataFrame, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        print("INFO: [Analyzer] Running Multi Choice Analysis...")
        
        # 检查原始数据是否包含预期的键
        if not raw_data or not all('predicted_answer' in item and 'correct_answer' in item for item in raw_data if isinstance(item, dict)):
            return {
                "title": "Multi Choice Analysis",
                "summary": "Skipped: Input data does not contain the required 'predicted_answer' and 'correct_answer' keys for this analysis.",
                "plots": [],
                "data_tables": {}
            }
        
        # 过滤出包含predicted_answer和correct_answer字段的数据项（排除第一个统计项）
        results = [item for item in raw_data if isinstance(item, dict) and 'predicted_answer' in item and 'correct_answer' in item]
        
        if not results:
            return {
                "title": "Multi Choice Analysis",
                "summary": "No valid results found for analysis.",
                "plots": [],
                "data_tables": {}
            }
        
        # 获取评估工具类型，默认为Accuracy
        eval_tool = self.config.get('eval_tool') or ['Accuracy']
        
        # 初始化metrics字典
        metrics = {}
        
        # 确保eval_tool是列表格式
        if isinstance(eval_tool, str):
            eval_tool = [eval_tool]
        
        # 遍历所有评估工具，计算相应指标
        for tool in eval_tool:
            if tool == 'Accuracy':
                accuracy_metrics = self._calculate_accuracy(results)
                metrics.update(accuracy_metrics)
            elif tool == 'F1':
                f1_metrics = self._calculate_f1(results)
                metrics.update(f1_metrics)
            elif tool == 'em':
                em_metrics = self._calculate_em(results)
                metrics.update(em_metrics)
        
        # 如果没有指定的评估工具，默认使用准确率
        if not metrics:
            metrics = self._calculate_accuracy(results)
        
        # 将指标写入JSON文件
        self._write_metrics_to_json(metrics)
        
        return {
            "title": "Multi Choice Analysis",
            "summary": f"Calculated {eval_tool} metrics: {metrics}",
            "plots": [],
            "data_tables": {}
        }
    
    def _calculate_accuracy(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算准确率指标
        """
        correct_count = 0
        total_count = len(results)
        
        for item in results:
            # 将预测答案和正确答案转换为集合（忽略顺序影响）
            predicted = set(item['predicted_answer'])
            correct = set(item['correct_answer'])
            
            # 检查两个集合是否完全相等
            if predicted == correct:
                correct_count += 1
        
        accuracy = {
            'overall': correct_count / total_count if total_count > 0 else 0,
            'correct_count': correct_count,
            'total_count': total_count
        }
        print(f"总体准确率: {accuracy['overall']:.2%}")
        return accuracy
    
    def _calculate_em(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算完全匹配(EM)指标
        """
        # 统计完全匹配的数量
        exact_matches = 0
        # 总样本数
        total = len(results)
        
        for item in results:
            # 将预测答案和正确答案转换为集合（忽略顺序影响）
            predicted = set(item['predicted_answer'])
            correct = set(item['correct_answer'])
            
            # 检查两个集合是否完全相等
            if predicted == correct:
                exact_matches += 1
        
        # 计算EM值（完全匹配数 / 总样本数）
        em_score = exact_matches / total if total > 0 else 0.0

        res = {
            'em': em_score,
            'total_count': total
        }
        print(f"em : {res['em']:.2%}")
        return res
    
    def _calculate_f1(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算F1分数指标
        """
        # 初始化统计变量
        total_tp = 0  # 真正例：预测正确且标准答案中存在
        total_fp = 0  # 假正例：预测存在但标准答案中不存在
        total_fn = 0  # 假负例：标准答案存在但未被预测
        
        for item in results:
            # 将答案列表转换为集合，方便计算交集和差集
            predicted = set(item['predicted_answer'])
            correct = set(item['correct_answer'])
            
            # 计算当前样本的TP、FP、FN
            tp = len(predicted & correct)  # 交集：预测正确的部分
            fp = len(predicted - correct)  # 预测有但不正确的部分
            fn = len(correct - predicted)  # 正确但未预测的部分
            
            # 累加到总数
            total_tp += tp
            total_fp += fp
            total_fn += fn
        
        # 计算精确率 (避免除以零)
        precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
        
        # 计算召回率 (避免除以零)
        recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
        
        # 计算F1值 (避免除以零)
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        total_count = len(results)
        res = {
            'F1': f1,
            'total_count': total_count
        }
        print(f"F1 : {res['F1']:.2%}")
        return res
            
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