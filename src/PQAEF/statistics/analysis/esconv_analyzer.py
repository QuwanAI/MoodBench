from typing import Dict, Any, List
import pandas as pd
import json
import os
import numpy as np

from .registry import register_analyzer
from .base_analysis import BaseAnalysis
from PQAEF.constant import constant


@register_analyzer(name="esconv")
class ESConvAnalyzer(BaseAnalysis):
    """
    ESConv情感支持对话任务的分析器 - 支持多策略分析
    """

    def analyze(self, df: pd.DataFrame, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        print("INFO: [Analyzer] Running ESConv Multi-Strategy Analysis...")
        
        # 检查原始数据是否包含预期的键
        if not raw_data or not all('strategy_scores' in item for item in raw_data if isinstance(item, dict)):
            return {
                "title": "ESConv Multi-Strategy Analysis",
                "summary": "Skipped: Input data does not contain the required 'strategy_scores' key for this analysis.",
                "plots": [],
                "data_tables": {}
            }
        
        # 过滤出包含strategy_scores字段的数据项
        results = [item for item in raw_data if isinstance(item, dict) and 'strategy_scores' in item]
        
        if not results:
            return {
                "title": "ESConv Multi-Strategy Analysis",
                "summary": "No valid results found for analysis.",
                "plots": [],
                "data_tables": {}
            }
        
        # 计算整体指标
        overall_metrics = self._calculate_overall_metrics(results)
        
        # 按策略分组计算指标
        strategy_metrics = self._calculate_strategy_metrics(results)
        
        # 计算目标策略的表现
        target_strategy_metrics = self._calculate_target_strategy_metrics(results)
        
        # 合并所有指标
        all_metrics = {
            'overall': overall_metrics,
            'by_strategy': strategy_metrics,
            'target_strategy_performance': target_strategy_metrics
        }
        
        # 将指标写入JSON文件
        self._write_metrics_to_json(all_metrics)
        
        return {
            "title": "ESConv Multi-Strategy Analysis",
            "summary": f"Calculated ESConv multi-strategy metrics. Target strategy avg score: {target_strategy_metrics.get('avg_weighted_score', 0.0):.4f}",
            "plots": [],
            "data_tables": {}
        }
    
    def _calculate_overall_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算所有策略的整体平均指标
        """
        if not results:
            return {}
            
        all_scores = []
        strategy_counts = {}
        
        for result in results:
            strategy_scores = result.get('strategy_scores', {})
            for strategy, scores in strategy_scores.items():
                if isinstance(scores, dict) and 'weighted_score' in scores:
                    all_scores.append(scores['weighted_score'])
                    strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        metrics = {
            'avg_weighted_score': np.mean(all_scores) if all_scores else 0.0,
            'total_responses': len(all_scores),
            'total_samples': len(results),
            'strategy_counts': strategy_counts
        }
        
        return metrics
    
    def _calculate_strategy_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        按策略分组计算指标
        """
        strategy_groups = {}
        
        # 按策略分组收集分数
        for result in results:
            strategy_scores = result.get('strategy_scores', {})
            for strategy, scores in strategy_scores.items():
                if isinstance(scores, dict) and 'weighted_score' in scores:
                    if strategy not in strategy_groups:
                        strategy_groups[strategy] = []
                    strategy_groups[strategy].append(scores)
        
        # 为每个策略计算指标
        strategy_metrics = {}
        for strategy, scores_list in strategy_groups.items():
            if scores_list:
                semantic_scores = [s.get('semantic_similarity', 0.0) for s in scores_list]
                emotional_scores = [s.get('emotional_support', 0.0) for s in scores_list]
                fluency_scores = [s.get('fluency', 0.0) for s in scores_list]
                length_scores = [s.get('length_appropriateness', 0.0) for s in scores_list]
                weighted_scores = [s.get('weighted_score', 0.0) for s in scores_list]
                
                strategy_metrics[strategy] = {
                    'semantic_similarity': np.mean(semantic_scores),
                    'emotional_support': np.mean(emotional_scores),
                    'fluency': np.mean(fluency_scores),
                    'length_appropriateness': np.mean(length_scores),
                    'weighted_score': np.mean(weighted_scores),
                    'sample_count': len(scores_list)
                }
        
        return strategy_metrics
    
    def _calculate_target_strategy_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算目标策略（真实标签策略）的表现
        """
        target_scores = []
        strategy_performance = {}
        
        for result in results:
            target_strategy = result.get('target_strategy', '')
            target_strategy_score = result.get('target_strategy_score', {})
            
            if target_strategy and isinstance(target_strategy_score, dict) and 'weighted_score' in target_strategy_score:
                target_scores.append(target_strategy_score['weighted_score'])
                
                # 按目标策略分组
                if target_strategy not in strategy_performance:
                    strategy_performance[target_strategy] = []
                strategy_performance[target_strategy].append(target_strategy_score['weighted_score'])
        
        # 计算每个目标策略的平均表现
        avg_performance_by_strategy = {}
        for strategy, scores in strategy_performance.items():
            avg_performance_by_strategy[strategy] = np.mean(scores) if scores else 0.0
        
        metrics = {
            'avg_weighted_score': np.mean(target_scores) if target_scores else 0.0,
            'total_target_samples': len(target_scores),
            'performance_by_target_strategy': avg_performance_by_strategy
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