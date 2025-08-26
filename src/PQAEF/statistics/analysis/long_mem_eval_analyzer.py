# -*- coding: utf-8 -*-
from typing import Dict, Any, List
import pandas as pd
import json
import os
from collections import Counter

from .registry import register_analyzer
from .base_analysis import BaseAnalysis

def calculate_f1(prediction: str, ground_truth: str):
    """计算单个样本的 Precision, Recall, F1"""
    prediction_tokens = prediction.split()
    ground_truth_tokens = ground_truth.split()
    
    if not prediction_tokens and not ground_truth_tokens:
        return 1.0, 1.0, 1.0 # 都是空的，算完全匹配

    if not prediction_tokens or not ground_truth_tokens:
        return 0.0, 0.0, 0.0 # 其中一个是空的

    common = Counter(prediction_tokens) & Counter(ground_truth_tokens)
    num_same = sum(common.values())
    
    precision = 1.0 * num_same / len(prediction_tokens)
    recall = 1.0 * num_same / len(ground_truth_tokens)
    
    if (precision + recall) == 0:
        f1 = 0.0
    else:
        f1 = (2 * precision * recall) / (precision + recall)
        
    return precision, recall, f1

def calculate_recall(prediction: str, ground_truth: str):
    """专门计算 Recall 值"""
    """计算 F1 分数"""
    # 确保输入都是字符串类型
    if not isinstance(prediction, str):
        prediction = str(prediction)
    if not isinstance(ground_truth, str):
        ground_truth = str(ground_truth)
    
    prediction_tokens = prediction.split()
    ground_truth_tokens = ground_truth.split()
    
    if not ground_truth_tokens:
        return 1.0 if not prediction_tokens else 0.0
    
    if not prediction_tokens:
        return 0.0
    
    common = Counter(prediction_tokens) & Counter(ground_truth_tokens)
    num_same = sum(common.values())
    
    recall = 1.0 * num_same / len(ground_truth_tokens)
    return recall

@register_analyzer(name="long_mem_eval")
class LongMemEvalAnalyzer(BaseAnalysis):
    """
    为长程记忆生成任务计算 Recall 等指标。
    """
    def analyze(self, df: pd.DataFrame, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        print("INFO: [Analyzer] Running Long Memory Evaluation Analysis...")
        
        if not raw_data or not all('predicted_answer' in item and 'correct_answer' in item for item in raw_data):
            return {"title": "Long Memory Analysis", "summary": "Skipped: Input data is missing required keys."}

        total_recall = 0
        exact_match_count = 0
        
        for result in raw_data:
            pred = result.get('predicted_answer', '')
            truth = result.get('correct_answer', '')
            
            # 计算 Recall 值
            recall = calculate_recall(pred, truth)
            total_recall += recall
            
            if str(pred).strip() == str(truth).strip():
                exact_match_count += 1
        
        num_samples = len(raw_data)
        avg_recall = total_recall / num_samples if num_samples > 0 else 0
        exact_match_rate = exact_match_count / num_samples if num_samples > 0 else 0
        
        # 构建指标字典，专注于 Recall
        metrics = {
            'recall': avg_recall,
            'exact_match_rate': exact_match_rate,
            'total_samples': num_samples
        }
        
        # 将指标写入JSON文件
        self._write_metrics_to_json(metrics)
        
        summary_text = (
            f"Evaluation completed over {num_samples} samples.\n"
            f"  - Average Recall: {avg_recall:.4f}\n"
            f"  - Exact Match Rate: {exact_match_rate:.2%}"
        )
        
        data_table = pd.DataFrame([{
            'Recall': avg_recall,
            'Exact Match': exact_match_rate,
            'Total Samples': num_samples
        }])
        
        return {
            "title": "Long Memory Generation Task Analysis",
            "summary": summary_text,
            "plots": [],
            "data_tables": {"Overall Metrics": data_table}
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