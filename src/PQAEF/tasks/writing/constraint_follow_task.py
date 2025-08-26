import os
from typing import List, Dict, Any, TYPE_CHECKING
from collections import defaultdict
from pprint import pprint
import sys

from typing_extensions import override
from tqdm import tqdm

from ..base_task import BaseTask
# 假设你的原始脚本和工具类在以下路径
# 请根据你的实际项目结构调整这些导入路径
from .scripts import (
    Content_Keywords, Length_Words, Length_Sentences, Length_Paragraphs,
    Format_Table, Content_Punctuation, Language_English, Format_Markdown,
    Format_Json, Language_Chinese, Content_Others, Format_Others
)
from ...utils.utils import get_model_response_content

if TYPE_CHECKING:
    from ...models.base_model import BaseModel


# 将原始脚本中的全局映射和函数放入类中或作为辅助函数
# 这样可以更好地封装逻辑

# 1. 定义检查器类的映射
CLASS_MAPPING = {
    'Content_Keywords': Content_Keywords(),
    'Content_Keywords: Must include': Content_Keywords(),
    'Length_Words': Length_Words(),
    'Length_Words: At most': Length_Words(),
    'Length_Words: At least': Length_Words(),
    'Length_Words: Range': Length_Words(),
    'Length_Sentences': Length_Sentences(),
    'Length_Sentences: At least': Length_Sentences(),
    'Length_Sentences: At most': Length_Sentences(),
    'Length_Sentences: Range': Length_Sentences(),
    'Length_Paragraphs': Length_Paragraphs(),
    'Length_Paragraphs: At most': Length_Paragraphs(),
    'Length_Paragraphs: At least': Length_Paragraphs(),
    'Length_Paragraphs: Range': Length_Paragraphs(),
    'Paragraphs_At most': Length_Paragraphs(),
    'Format_Table': Format_Table(),
    'Table_Row limit': Format_Table(),
    'Table_Column limit': Format_Table(),
    'Format_Table: Row limit': Format_Table(),
    'Format_Table: Column limit': Format_Table(),
    'Punctuation_Ending punctuation': Content_Punctuation(),
    'Content_Punctuation: Ending punctuation': Content_Punctuation(),
    'Content_Punctuation': Content_Punctuation(),
    'Language_English': Language_English(),
    'Language_English: Capitalized': Language_English(),
    'Language_English: All Uppercase': Language_English(),
    'Format_Markdown': Format_Markdown(),
    'Markdown_Heading levels': Format_Markdown(),
    'Format_Markdown: Heading levels': Format_Markdown(),
    'Markdown_Block quotes': Format_Markdown(),
    'Json_Object nesting levels': Format_Json(),
    'Format_Json': Format_Json(),
    'Language_Chinese': Language_Chinese(),
    'Language_Chinese: Simplified': Language_Chinese(),
    'Language_Chinese: Traditional': Language_Chinese(),
    'Content_Identifiers': Content_Others(),
    'Content_Length': Content_Others(),
    'Citations_In-text': Content_Others(),
    'Content_Quotes': Content_Others(),
    'Content_Sources': Content_Others(),
    'Content_Mention': Content_Others(),
    'Format_Markdown: Block quotes': Format_Others(),
    'Format_Text': Format_Others(),
    'XML_Number of attributes': Format_Others(),
    'References_Format': Format_Others(),
    'Format_Bullet Points': Format_Others(),
    'Format_XML': Format_Others(),
    'Format_Blurb': Format_Others(),
    'Table_Table': Format_Others(),
    'Sentences_At most': Length_Sentences(),
    'Sentences_At least': Length_Sentences(),
    'Words_At most': Length_Words(),
    'Json_Number of attributes': Format_Json(),
    'Format_Word Count': Length_Words(),
    'Format_Length': Format_Others(),
}

# 2. 定义约束归一化的映射
CONSTRAINT_MAPPING = {
    'Content_Keywords': 'Content_Keywords',
    'Content_Keywords: Must include': 'Content_Keywords',
    'Length_Words': 'Length_Words',
    'Length_Words: At most': 'Length_Words',
    'Length_Words: At least': 'Length_Words',
    'Length_Words: Range': 'Length_Words',
    'Words_At most': 'Length_Words',
    'Length_Sentences': 'Length_Sentences',
    'Length_Sentences: At least': 'Length_Sentences',
    'Length_Sentences: At most': 'Length_Sentences',
    'Length_Sentences: Range': 'Length_Sentences',
    'Sentences_At most': 'Length_Sentences',
    'Sentences_At least': 'Length_Sentences',
    'Length_Paragraphs': 'Length_Paragraphs',
    'Length_Paragraphs: At most': 'Length_Paragraphs',
    'Length_Paragraphs: At least': 'Length_Paragraphs',
    'Length_Paragraphs: Range': 'Length_Paragraphs',
    'Paragraphs_At most': 'Length_Paragraphs',
    'Format_Table': 'Format_Table',
    'Table_Row limit': 'Format_Table',
    'Table_Column limit': 'Format_Table',
    'Format_Table: Row limit': 'Format_Table',
    'Format_Table: Column limit': 'Format_Table',
    'Punctuation_Ending punctuation': 'Content_Punctuation',
    'Content_Punctuation: Ending punctuation': 'Content_Punctuation',
    'Content_Punctuation': 'Content_Punctuation',
    'Language_English': 'Language_English',
    'Language_English: Capitalized': 'Language_English',
    'Language_English: All Uppercase': 'Language_English',
    'Format_Markdown': 'Format_Markdown',
    'Markdown_Heading levels': 'Format_Markdown',
    'Format_Markdown: Heading levels': 'Format_Markdown',
    'Markdown_Block quotes': 'Format_Markdown',
    'Json_Object nesting levels': 'Format_Json',
    'Format_Json': 'Format_Json',
    'Language_Chinese': 'Language_Chinese',
    'Language_Chinese: Simplified': 'Language_Chinese',
    'Language_Chinese: Traditional': 'Language_Chinese',
    'Content_Identifiers': 'Content_Identifiers',
    'Content_Length': 'Length_Words',
    'Citations_In-text': 'Content_Identifiers',
    'Content_Quotes': 'Content_Punctuation',
    'Content_Sources': 'Content_Identifiers',
    'Content_Mention': 'Content_Keywords',
    'Format_Markdown: Block quotes': 'Format_Markdown',
    'Format_Text': 'Content_Identifiers',
    'XML_Number of attributes': 'Format_XML',
    'References_Format': 'Content_Identifiers',
    'Format_Bullet Points': 'Content_Identifiers',
    'Format_XML': 'Format_XML',
    'Format_Blurb': 'Length_Words',
    'Table_Table': 'Format_Table',
    'Json_Number of attributes': 'Format_Json',
    'Format_Word Count': 'Length_Words',
    'Format_Length': 'Length_Words',
}

def get_instance(class_name):
    cls = CLASS_MAPPING.get(class_name)
    if cls:
        return cls
    else:
        raise ValueError(f"Class '{class_name}' not found")


class ConstraintFollowTask(BaseTask):
    def __init__(self, task_config: Dict[str, Any], llm_model: "BaseModel"):
        super().__init__(task_config)
        self.llm_model = llm_model
    
    def _check_constraints(self, sample: Dict[str, Any], response_content: str):
        """检查单个样本的约束并更新 'judges' 字段。"""
        judges = []
        for constraint in sample['constraints']:
            cls_name = f"{constraint[0]}_{constraint[1]}"
            try:
                checker = get_instance(cls_name)
                judge_result = checker.check(constraint[-1], response_content)
                judges.append(1 if judge_result else 0)
            except ValueError as e:
                # 如果找不到检查器，可以记为0分并打印警告
                print(f"Warning: Checker for '{cls_name}' not found. Defaulting to 0. Error: {e}")
                judges.append(0)
        sample['judges'] = judges

    def _calculate_score(self, responses: List[Any], batch: List[Dict[str, Any]]):
        """
        计算分数并更新 batch 中每个 sample 的 'judges' 和 'model_response' 字段。
        此框架下，我们通常逐个样本处理，而不是返回聚合分数。
        聚合分数将在所有批次处理完后，在主流程中进行。
        """
        for response, sample in zip(responses, batch):
            # 假设 get_model_response_content 是一个工具函数，用于从各种模型输出格式中提取文本
            # response_content = get_model_response_content(response) # 如果需要
            response_content = response # 假设 self.llm_model.process 直接返回文本列表
            
            # 1. 预处理模型响应
            # clean_response = self._pre_process(response_content)
            
            # 2. 检查约束并获得 judges
            self._check_constraints(sample, response_content)
            
            # 3. 将模型原始响应和清理后的响应保存回 sample
            sample['model_raw_response'] = response_content
            # sample['model_clean_response'] = clean_response
            
    @override
    def process_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        处理一个批次的数据：获取模型响应，然后进行评测。
        """
        # 1. 准备模型的输入 prompt
        # 在这个任务中，prompt 就是数据中的 'prompt' 字段
        # all_prompts = [sample["prompt"] for sample in batch]

        # 2. 调用模型进行推理
        # 使用 tqdm 显示进度条
        responses = []
        for b in tqdm(batch, desc=f"Processing batch for {self.__class__.__name__}"):
             # 假设模型 process 方法可以处理单个字符串
             # 如果它只接受列表，需要调整
            prompt = b["conversations"][-1]["content"]
            response = self.llm_model.process(prompt) # 假设返回列表
            # print(response)
            # sys.exit(0)
            responses.append(get_model_response_content(response))

        # 3. 计算分数并更新 batch 数据
        self._calculate_score(responses, batch)
        
        # 4. 返回处理和评测后的 batch
        # 每个 sample 现在都包含了 'judges', 'model_response' 等新字段
        return batch

    @staticmethod
    def aggregate_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        在所有批次处理完毕后，对所有结果进行聚合，计算最终的多维度分数。
        这个方法是静态的，因为它不依赖于类的实例状态。
        """
        # 原始脚本中的 get_score 函数逻辑可以完整地移到这里
        
        # 1. 映射约束（如果需要）
        def map_constraint(data):
            # ... (这部分代码和原始脚本完全一样) ...
            new_data = []
            for d in data:
                new_constraints = []
                for constraint in d['constraints']:
                    key = f"{constraint[0]}_{constraint[1]}"
                    # 如果键不存在，可以给个默认值或跳过
                    value = CONSTRAINT_MAPPING.get(key)
                    if not value:
                        print(f"Warning: Constraint mapping for '{key}' not found. Skipping.")
                        continue
                    first, second = value.split('_')
                    new_constraint = [
                        first,
                        second,
                        constraint[-1]
                    ]
                    new_constraints.append(new_constraint)
                d['constraints'] = new_constraints
                new_data.append(d)
            return new_data

        data = map_constraint(results)

        # 2. 计算各项分数
        # ... (以下代码几乎是 get_score 函数的直接复制粘贴) ...
        num_data = len(data)
        num_constraint = sum(len(item['judges']) for item in data)
        total_acc = sum(1 for item in data if sum(item['judges']) == len(item['judges']))
        total_acc_macro = sum(sum(item['judges']) / len(item['judges']) for item in data if item['judges'])
        total_acc_micro = sum(sum(item['judges']) for item in data)
        
        # ... (此处省略 constraint_extension_list, constraint_type_list 等所有计算逻辑)
        # ... (请将原始 get_score 函数中从 'constraint_extension_list = defaultdict(int)' 开始的所有代码粘贴到这里)

        # 假设所有计算都已完成
        # 示例性地返回聚合分数
        final_scores = {
            'Overall_Acc': f"{total_acc}/{num_data}={total_acc/num_data if num_data > 0 else 0:.4f}",
            'Overall_Macro_F1': f"{total_acc_macro}/{num_data}={total_acc_macro/num_data if num_data > 0 else 0:.4f}",
            'Overall_Micro_F1': f"{total_acc_micro}/{num_constraint}={total_acc_micro/num_constraint if num_constraint > 0 else 0:.4f}",
            # 'constraint_pattern_list': constraint_extension_list,
            # 'constraint_category_list': constraint_type_list,
            # 'constraint_category_second_list': constraint_type_second_list,
            # 'constraint_difficulty_list': constraint_difficulty_list,
        }
        
        # 打印最终报告
        print("\n--- Final Aggregated Scores ---")
        pprint(final_scores)
        print("-----------------------------\n")

        return final_scores