import os
import re
import json
import sys
from typing import List, Dict, Any, TYPE_CHECKING
from concurrent.futures import ThreadPoolExecutor

from typing_extensions import override
from tqdm import tqdm

from ..base_task import BaseTask
# 假设您的框架中有这些工具函数
# from ...utils.metrics import some_metric_if_needed #
from ...utils.utils import get_model_response_content, read_json

if TYPE_CHECKING:
    # 假设您的模型基类在这里
    from ...models.base_model import BaseModel


class AlignBenchTask(BaseTask):
    """
    一个用于执行 AlignBench 评估流程的任务。
    
    这个任务封装了以下步骤：
    1. 使用待评估模型 (llm_model) 对输入问题生成回答。
    2. 使用一个强大的裁判模型 (judge_model) 对生成的回答进行多维度评估。
    3. 解析裁判模型的输出，提取结构化的评分。
    
    任务配置 (task_config) 需要包含 AlignBench 所需的各种路径和设置。
    """
    
    def __init__(self, task_config: Dict[str, Any], llm_model: "BaseModel", judge_model: "BaseModel"):
        """
        初始化 AlignBench 任务。

        Args:
            llm_model (BaseModel): 需要被评估的语言模型实例。
            judge_model (BaseModel): 用作裁判的语言模型实例 (例如 GPT-4)。
            
            
            "judge_prompt_template_path": 裁判模型的提示词模板文件路径。
            "dimension_set_filepath": 类别到维度的映射文件路径。
            "dimension_def_filepath": 各个维度的定义文件路径。
            "subcategory_mapping_filepath": 子类别到类别的映射文件路径。
            "chosen_categories"
        """
        super().__init__(task_config)
        self.llm_model = llm_model
        self.judge_model = judge_model
        self.chosen_categories = task_config.get("chosen_categories", ["文本写作"])
        self.valid_categories = ["数学计算", "逻辑推理", "角色扮演", "文本写作", "专业能力", "中文理解", "综合问答", "基本任务"]
        
        if not all(category in self.valid_categories for category in self.chosen_categories):
            raise ValueError(f"Support categories include {self.valid_categories}, but got {self.chosen_categories}")
        
        # 加载所有必要的配置文件
        self._load_configs()

    def _load_configs(self):
        """从 task_config 中加载所有必要的配置文件。"""
        try:
            # 加载裁判提示词模板
            with open(self.task_config["judge_prompt_template_path"], 'r', encoding='utf-8') as f:
                self.judge_prompt_template = f.read()
            
            # 加载维度映射
            # with open(self.task_config["dimension_set_filepath"], 'r', encoding='utf-8') as f:
                # self.category_dimension_map = json.load(f)
            self.category_dimension_map = read_json(self.task_config["dimension_set_filepath"])
            
            # 加载维度定义
            # with open(self.task_config["dimension_def_filepath"], 'r', encoding='utf-8') as f:
            #     self.dimension_def_map = json.load(f)
            self.dimension_def_map = read_json(self.task_config["dimension_def_filepath"])

            # 加载子类别映射
            # with open(self.task_config["subcategory_mapping_filepath"], 'r', encoding='utf-8') as f:
            #     self.subcategory_type_map = json.load(f)
            self.subcategory_type_map = read_json(self.task_config["subcategory_mapping_filepath"])
            
            self.temperature_map = read_json(self.task_config["temperature_map"])
            
        except KeyError as e:
            raise ValueError(f"任务配置 (task_config) 中缺少必要的键: {e}")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"配置文件未找到: {e}")

    def _construct_judge_prompt(self, sample: Dict[str, Any]) -> str:
        """
        根据样本信息，构建用于裁判模型的完整提示词。
        此方法直接复用了 judge.py 中的 prompt_construct 逻辑。
        """
        # 1. 获取评估维度
        ques_type = self.subcategory_type_map.get(sample["subcategory"], None)
        dimensions = self.category_dimension_map.get(ques_type, [])
        
        dim_description = ""
        for index, dim in enumerate(dimensions):
            dim_def = self.dimension_def_map.get(dim, "无定义")
            dim_description += f"{index+1}. {dim}: {dim_def}\n"
        
        # 2. 填充模板
        prompt = self.judge_prompt_template.format(
            category=sample["category"],
            dimensions=dim_description,
            question=sample["question"],
            reference=sample.get("reference", ""), # 参考答案可能不存在
            answer=sample["model_answer"]
        )
        # 记录使用了哪些维度进行评估
        sample["dimensions"] = dimensions
        return prompt

    def _parse_judgment(self, judgment_text: str) -> Dict[str, Any]:
        """
        解析裁判模型的自然语言输出，提取评分。
        此方法直接复用了 judge.py 中的 post_process 逻辑。
        """
        # 提取花括号中的所有评分
        rating = {}
        # 匹配最后一个花括号内的内容，避免匹配到模板中的示例
        pattern = r'{(.*?)}(?![^{]*{)'
        match = re.search(pattern, judgment_text, re.DOTALL)
        if match:
            dictionary_str = match.group(1)
            # 匹配 "'key': value" 格式的键值对
            kv_pattern = r"['\"](.*?)['\"]\s*:\s*(\d+)"
            matches = re.findall(kv_pattern, dictionary_str)
            rating = {key: int(value) for key, value in matches}

        # 提取综合得分作为备用方案
        score = rating.get("综合得分", -1)
        if score == -1:
            score_match = re.search(r"['\"]综合得分['\"]\s*:\s*(\d+)", judgment_text)
            if score_match:
                score = int(score_match.group(1))

        return {"rating": rating, "score": score, "judgment": judgment_text}

    @override
    def process_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        处理一个批次的评估数据。

        Args:
            batch (List[Dict[str, Any]]): 一批数据样本，每个样本是一个字典，
                                         必须包含 'question', 'category', 'subcategory' 等键。

        Returns:
            List[Dict[str, Any]]: 处理完成的批次，每个样本字典中都增加了
                                  'model_answer', 'judgment', 'rating', 'score' 等字段。
        """
        # --- 步骤 1: 使用待评估模型生成回答 ---
        print(f"INFO: Number of items before filtering: {len(batch)}")
        new_batch = list(filter(lambda x: x["category"] in self.chosen_categories, batch))
        print(f"INFO: Data filtering completed. Number of items after filtering: {len(new_batch)}")
        
        prompts_for_model = [{"prompt": sample["question"], "temperature": self.temperature_map[sample["category"]]} for sample in new_batch]
        # print(prompts_for_model)
        # sys.exit(0)
        responses = self.llm_model.process(prompts_for_model)
        
        for sample, response in zip(new_batch, responses):
            sample["model_answer"] = get_model_response_content(response)

        # --- 步骤 2: 为每个样本构建裁判提示词 ---
        judge_prompts = []
        for sample in tqdm(new_batch, desc="构建裁判提示词"):
            prompt = self._construct_judge_prompt(sample)
            # judge_prompts.append(prompt)
            judge_prompts.append(prompt)
            # 同时将提示词存入样本，方便调试
            sample["judge_prompt"] = prompt

        # --- 步骤 3: 使用裁判模型获取评估结果 ---
        judgments = self.judge_model.process(judge_prompts)
        
        # --- 步骤 4: 解析评估结果并更新样本 ---
        for sample, judgment_text in tqdm(zip(new_batch, judgments), desc="解析裁判结果", total=len(new_batch)):
            parsed_results = self._parse_judgment(get_model_response_content(judgment_text))
            sample.update(parsed_results)
            
        return new_batch