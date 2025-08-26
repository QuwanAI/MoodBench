import os
import math
import torch
import logging
from typing import List, Dict, Any, Tuple, TYPE_CHECKING

from typing_extensions import override
from tqdm import tqdm

from PQAEF.utils.utils import merge_values, get_model_response_content
from PQAEF.tasks.base_task import BaseTask
from PQAEF.utils.metrics import calculate_distinct_n, calculate_bleu


if TYPE_CHECKING:
    from PQAEF.models.base_model import BaseModel


class CPEDPerplexityOnGeneratedResponseTask(BaseTask):
    """
    一个两阶段任务:
    1. 根据输入上下文生成回复。
    2. 计算模型对它自己生成的回复的困惑度 (PPL)。
    """
    def __init__(self, task_config: Dict[str, Any], llm_model: "BaseModel"):
        """
        初始化任务。
        
        Args:
            task_config (Dict[str, Any]): 任务配置。
            llm_model (BaseModel): 包装好的本地模型实例。
        """
        super().__init__(task_config)
        self.llm_model = llm_model
        self.tokenizer = self.llm_model.tokenizer # 从模型实例中获取分词器
        
        if not hasattr(llm_model, 'process'):
             raise AttributeError(f"模型 '{llm_model.model_name}' 必须有 'process' 方法用于生成文本。")
        if not hasattr(llm_model, 'forward_pass_with_loss'):
            raise AttributeError(f"模型 '{llm_model.model_name}' 必须有 'forward_pass_with_loss' 方法用于计算损失。")

    def _calculate_ppl_for_single_text(self, text: str) -> Tuple[float, float]:
        """
        为单段文本计算PPL和NLL。

        Args:
            text (str): 需要评估的文本。

        Returns:
            Tuple[float, float]: (ppl, nll)
        """
        # 对单段文本进行分词
        # 确保文本不为空，否则会引发错误
        if not text or not text.strip():
            return float('inf'), float('inf')
            
        inputs = self.tokenizer(text, return_tensors="pt")
        
        # 将张量移动到模型所在的设备
        # inputs = {k: v.to(self.llm_model.device) for k, v in inputs.items()}
        
        # 调用模型的损失计算方法
        outputs = self.llm_model.forward_pass_with_loss(
            input_ids=inputs.input_ids,
            attention_mask=inputs.attention_mask
        )

        if hasattr(outputs, 'loss') and outputs.loss is not None:
            nll = outputs.loss.item()
            ppl = math.exp(nll)
            return ppl, nll
        
        return float('inf'), float('inf')
    
    def _prepare_batch(self, batch: List[Dict[str, Any]]):
        for index, b in enumerate(batch):
            history, response = merge_values(b["history"], "role", "content"), merge_values(b["response"], "role", "content")
            assistant_role = response[0]["role"]
            
            response[0]["role"] = "assistant"
            for item in history:
                item["role"] = "assistant" if item["role"] == assistant_role else "user"
            
            batch[index]["history"] = history
            batch[index]["response"] = response[0]
            
            


    @override
    def process_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        处理一个批次的数据：先生成回复，然后对生成的回复计算PPL。

        Args:
            batch (List[Dict[str, Any]]): 一个样本列表，每个样本字典必须包含 'history' 键。

        Returns:
            List[Dict[str, Any]]: 带有'model_response', 'ppl', 'nll'评分的批次。
        """
        
        if not all("history" in sample for sample in batch):
            raise KeyError("批次中的某些样本缺少 'history' 键。")
        
        self._prepare_batch(batch)
            
        prompts = [sample["history"] for sample in batch]
        
        generated_responses = self.llm_model.process(prompts)
        
        # --- 阶段 2: 对每个生成的回复计算PPL ---
        for i, sample in enumerate(tqdm(batch, desc="Calculating PPL on Generated Responses")):
            # 假设 `generated_responses` 是一个与`batch`长度相同的字符串列表
            response_text = get_model_response_content(generated_responses[i])
            answer = sample["response"]["content"]
            
            # 计算这个回复的PPL和NLL
            ppl, nll = self._calculate_ppl_for_single_text(response_text)
            distinct_n = calculate_distinct_n([response_text, answer], 5)
            bleu = calculate_bleu(response_text, answer)
            
            # 更新样本信息
            sample["model_response"] = response_text
            # 保留原始的真实回复，以便对比
            sample["ground_truth_response"] = sample.get("response") # 可选
            sample["ppl_on_generated"] = ppl
            sample["nll_on_generated"] = nll
            sample["distinct_n"] = distinct_n
            sample["bleu"] = bleu

        return batch