import os
import re
import tempfile
from typing import List, Dict, Any, TYPE_CHECKING
from typing_extensions import override
from tqdm import tqdm

from ..base_task import BaseTask
from ...utils.utils import get_model_response_content
from .metric import compute_metrics

if TYPE_CHECKING:
    from ...models.base_model import BaseModel


class ESConvTask(BaseTask):
    """
    ESConv情感支持对话任务 - 支持多策略回应生成
    """
    
    def __init__(self, task_config: Dict[str, Any], llm_model: "BaseModel"):
        super().__init__(task_config)
        self.llm_model = llm_model
        
        # 加载prompt模板
        prompt_path = self.task_config["prompt_path"]
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.prompt_template = f.read()
            
        # 策略列表
        self.strategies = self.task_config.get('strategies', [
            'Question', 'Restatement or Paraphrasing', 'Reflection of feelings',
            'Self-disclosure', 'Affirmation and Reassurance', 'Providing Suggestions',
            'Information', 'Others'
        ])
        
        # 评估配置
        self.eval_config = self.task_config.get('eval_config', {
            'weights': {
                'semantic_similarity': 0.3,
                'emotional_support': 0.3,
                'fluency': 0.2,
                'length_appropriateness': 0.2
            }
        })
        
    def _extract_strategy_responses(self, response_content: str) -> Dict[str, str]:
        """
        从模型的多策略回应中提取各个策略的具体回应
        """
        strategy_responses = {}
        
        # 定义策略模式匹配 - 适配实际模型回复格式
        strategy_patterns = {
            'Question': r'1\. \*\*Question[^：:]*[：:]\s*([^\n]+(?:\n(?!\d+\. \*\*)[^\n]*)*)',
            'Restatement or Paraphrasing': r'2\. \*\*Restatement or Paraphrasing[^：:]*[：:]\s*([^\n]+(?:\n(?!\d+\. \*\*)[^\n]*)*)',
            'Reflection of feelings': r'3\. \*\*Reflection of feelings[^：]*：\s*([^\n]+(?:\n(?!\d+\. \*\*)[^\n]*)*)',
            'Self-disclosure': r'4\. \*\*Self-disclosure[^：]*：\s*([^\n]+(?:\n(?!\d+\. \*\*)[^\n]*)*)',
            'Affirmation and Reassurance': r'5\. \*\*Affirmation and Reassurance[^：]*：\s*([^\n]+(?:\n(?!\d+\. \*\*)[^\n]*)*)',
            'Providing Suggestions': r'6\. \*\*Providing Suggestions[^：]*：\s*([^\n]+(?:\n(?!\d+\. \*\*)[^\n]*)*)',
            'Information': r'7\. \*\*Information[^：]*：\s*([^\n]+(?:\n(?!\d+\. \*\*)[^\n]*)*)',
            'Others': r'8\. \*\*Others[^：]*：\s*([^\n]+(?:\n(?!\d+\. \*\*)[^\n]*)*)',
        }
        
        for strategy, pattern in strategy_patterns.items():
            match = re.search(pattern, response_content, re.MULTILINE | re.DOTALL)
            if match:
                strategy_responses[strategy] = match.group(1).strip()
            else:
                strategy_responses[strategy] = ""  # 如果没有找到，设为空字符串
                print(f"WARNING: Could not extract response for strategy: {strategy}")
        
        return strategy_responses
    
    def _format_dialog_history(self, dialog_history: List[Dict[str, str]]) -> str:
        """
        格式化对话历史
        """
        if not dialog_history:
            return "（无对话历史）"
        
        formatted_history = []
        for turn in dialog_history:
            speaker = "求助者" if turn['speaker'] == 'seeker' else "支持者"
            formatted_history.append(f"{speaker}：{turn['content']}")
        
        return "\n".join(formatted_history)
        
    @override
    def process_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        处理批次数据 - 单策略回应生成
        """
        print(f"\nINFO: Processing batch of {len(batch)} ESConv samples...")
        
        # 构建prompts
        prompts = []
        for sample in batch:
            scene = sample.get('scene', '')
            question_text = sample.get('question_text', '')
            
            # 获取对话历史
            other_info = sample.get('other_info', {})
            dialog_history = other_info.get('dialog_history', [])
            formatted_history = self._format_dialog_history(dialog_history)
            
            prompt = self.prompt_template.format(
                scene=scene,
                question=question_text,
                dialog_history=formatted_history
            )
            prompts.append(prompt)
            
        # 打印示例prompt
        print('one sample prompt:\n', prompts[0] if prompts else 'No prompts generated')
        
        # 调用模型生成响应
        print(f"INFO: Calling {self.llm_model.model_name} for {len(prompts)} prompts...")
        responses = self.llm_model.process(prompts)
        
        # 处理响应并计算评分
        results = []
        for i, (response, sample) in enumerate(zip(responses, batch)):
            response_content = get_model_response_content(response)
            
            # 获取参考答案和策略信息
            other_info = sample.get('other_info', {})
            reference_response = other_info.get('reference_response', '')
            target_strategy = other_info.get('strategy', '')
            
            # 直接计算模型回复与标准答案的评分
            if response_content and reference_response:
                scores = self._calculate_esconv_scores(
                    response_content, 
                    reference_response, 
                    target_strategy,
                    sample
                )
            else:
                scores = {
                    'semantic_similarity': 0.0,
                    'emotional_support': 0.0,
                    'fluency': 0.0,
                    'length_appropriateness': 0.0,
                    'weighted_score': 0.0,
                    'error': 'Empty response or reference'
                }
            
            # 构建结果
            result = {
                'question_id': sample.get('question_id', ''),
                'scene': sample.get('scene', ''),
                'question_text': sample.get('question_text', ''),
                'target_strategy': target_strategy,
                'reference_response': reference_response,
                'model_response': response_content,
                'scores': scores,
                'other_info': other_info
            }
            
            results.append(result)
            
        return results
        
    def _compute_metrics_from_strings(self, hypothesis: str, reference: str) -> Dict[str, Any]:
        """
        直接从字符串计算指标，通过创建临时文件
        """
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as hyp_file:
                hyp_file.write(hypothesis.strip() + '\n')
                hyp_path = hyp_file.name
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as ref_file:
                ref_file.write(reference.strip() + '\n')
                ref_path = ref_file.name
            
            # 调用原始的compute_metrics函数
            metrics_result = compute_metrics(hyp_path, [ref_path], no_glove=True)
            
            # 清理临时文件
            os.unlink(hyp_path)
            os.unlink(ref_path)
            
            return metrics_result
            
        except Exception as e:
            print(f"Error computing metrics: {e}")
            return {
                'Bleu': {'Bleu_1': 0.0, 'Bleu_2': 0.0, 'Bleu_3': 0.0, 'Bleu_4': 0.0},
                'ROUGE_L': 0.0,
                'CIDEr': 0.0
            }
    
    def _calculate_esconv_scores(self, response: str, reference: str, strategy: str, sample: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算ESConv任务的综合评分
        """
        try:
            # 使用修改后的指标计算方法
            metrics_result = self._compute_metrics_from_strings(response, reference)
            
            # 提取各项指标（移除METEOR）
            bleu_scores = metrics_result.get('Bleu', {})
            rouge_l = metrics_result.get('ROUGE_L', 0.0)
            cider = metrics_result.get('CIDEr', 0.0)
            
            # 语义相似度 (使用BLEU-4和ROUGE-L的平均值)
            bleu_4 = bleu_scores.get('Bleu_4', 0.0) if isinstance(bleu_scores, dict) else 0.0
            semantic_similarity = (bleu_4 + rouge_l) / 2.0
            
            # 情感支持质量 (仅使用CIDEr，因为移除了METEOR)
            emotional_support = cider
            
            # 流畅性 (使用BLEU-1和BLEU-2的平均值)
            bleu_1 = bleu_scores.get('Bleu_1', 0.0) if isinstance(bleu_scores, dict) else 0.0
            bleu_2 = bleu_scores.get('Bleu_2', 0.0) if isinstance(bleu_scores, dict) else 0.0
            fluency = (bleu_1 + bleu_2) / 2.0
            
            # 长度合理性
            response_len = len(response.strip())
            reference_len = len(reference.strip())
            length_ratio = min(response_len, reference_len) / max(response_len, reference_len) if max(response_len, reference_len) > 0 else 0.0
            length_appropriateness = length_ratio
            
            # 加权综合评分
            weights = self.eval_config['weights']
            weighted_score = (
                semantic_similarity * weights['semantic_similarity'] +
                emotional_support * weights['emotional_support'] +
                fluency * weights['fluency'] +
                length_appropriateness * weights['length_appropriateness']
            )
            
            return {
                'semantic_similarity': semantic_similarity,
                'emotional_support': emotional_support,
                'fluency': fluency,
                'length_appropriateness': length_appropriateness,
                'weighted_score': weighted_score,
                'raw_metrics': metrics_result
            }
            
        except Exception as e:
            print(f"Error calculating ESConv scores: {e}")
            return {
                'semantic_similarity': 0.0,
                'emotional_support': 0.0,
                'fluency': 0.0,
                'length_appropriateness': 0.0,
                'weighted_score': 0.0,
                'raw_metrics': {},
                'error': str(e)
            }