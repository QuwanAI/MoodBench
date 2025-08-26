# 文件：mutual_task.py (全新版本)

import os
from typing import List, Dict, Any, TYPE_CHECKING
import numpy as np
from typing_extensions import override
from tqdm import tqdm

from ..base_task import BaseTask

if TYPE_CHECKING:
    from ...models.base_model import BaseModel


class MutualTask(BaseTask):
    def __init__(self, task_config: Dict[str, Any], llm_model: "BaseModel"):
        super().__init__(task_config)
        self.llm_model = llm_model
        
        # 在新的逻辑中，我们不再需要 prompt_path
        # 因此，可以删除所有与 self.prompt_template 相关的代码
        print("INFO: Initialized MutualTask in logits scoring mode.")
    
    @override
    def process_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not hasattr(self.llm_model, 'score_options'):
            raise TypeError(
                f"The provided model '{self.llm_model.model_name}' "
                "does not have the required 'score_options' method for this task."
            )

        # 1. 在方法开头初始化所有需要的列表
        individual_results = []
        all_preds_scores = []
        all_labels = []

        print(f"\nINFO: Starting batch processing for {len(batch)} samples...")
        for i, sample in enumerate(tqdm(batch, desc=f"Scoring batch with {self.llm_model.model_name}")):
            context = sample.get('context', '')
            options_dict = sample.get('options', {})
            correct_answer_char = sample.get('correct_answer', '')

            # (可选) 打印第一个样本的格式以供调试
            if i == 0:
                print("\n--- DEBUG: First sample data format ---")
                print(f"Context length: {len(context)}")
                print(f"Options content: {options_dict}")
                print(f"Correct Answer content: '{correct_answer_char}'")
                print("-------------------------------------\n")

            # 数据格式校验
            if not isinstance(options_dict, dict) or len(options_dict) != 4:
                print(f"WARNING: Skipping sample {sample.get('question_id', 'N/A')} due to invalid options format or count.")
                continue

            options_keys = sorted(options_dict.keys())
            options_list = [options_dict[key] for key in options_keys]
            
            label_map = {label: idx for idx, label in enumerate(options_keys)}
            label_index = label_map.get(correct_answer_char, -1)
            
            if label_index == -1:
                print(f"WARNING: Skipping sample {sample.get('question_id', 'N/A')} because correct_answer '{correct_answer_char}' not found in option keys {list(label_map.keys())}.")
                continue
            print("context:", context)
            # sys.exit(0)
            # 调用模型进行评分
            scores = self.llm_model.score_options(context, options_list)
            
            all_preds_scores.append(scores)
            all_labels.append(label_index)

            # 2. 在循环中填充 individual_results 列表
            predicted_choice_index = np.argmax(scores)
            predicted_choice_char = options_keys[predicted_choice_index]
            individual_results.append({
                'question_id': sample.get('question_id', 'N/A'),
                'context': context,
                'options': options_dict,
                'scores': [float(s) for s in scores],
                'correct_answer': correct_answer_char,
                'predicted_answer': predicted_choice_char,
                'is_correct': predicted_choice_char == correct_answer_char
            })

        # ----- 指标计算 -----
        if not all_preds_scores:
            print("WARNING: No valid samples were processed. Returning empty list.")
            return []

        preds = np.array(all_preds_scores)
        out_label_ids = np.array(all_labels)

        preds_pos_1 = np.argmax(preds, axis=1)
        correct_count = np.sum(preds_pos_1 == out_label_ids)
        total_count = len(out_label_ids)
        r1_acc = correct_count / total_count if total_count > 0 else 0.0

        mrr = 0.0
        p2_count = 0
        for i in range(total_count):
            temp_ranks = np.argsort(preds[i])
            ranks = np.empty_like(temp_ranks)
            ranks[temp_ranks] = np.arange(len(preds[i]))
            correct_rank_from_bottom = ranks[out_label_ids[i]]
            correct_rank = len(preds[i]) - correct_rank_from_bottom
            mrr += 1.0 / correct_rank
            if correct_rank == 2:
                p2_count += 1
        
        final_mrr = mrr / total_count if total_count > 0 else 0.0
        final_r2 = (correct_count + p2_count) / total_count if total_count > 0 else 0.0

        summary_metrics = {
            'accuracy': r1_acc, 'recall@1': r1_acc, 'recall@2': final_r2,
            'mrr': final_mrr, 'correct_count': int(correct_count), 'total_count': total_count
        }

        print("\n" + "="*30)
        print(f"MutualTask 评价结果 (Logits Scoring):")
        print("="*30)
        for key, value in summary_metrics.items():
            print(f"{key}: {value:.4f}" if isinstance(value, float) else f"{key}: {value}")
        print("="*30)
        
        # 3. 在方法末尾返回被完整填充的列表
        return individual_results