import os
from typing import List, Dict, Any, TYPE_CHECKING
from typing_extensions import override
from PQAEF.constant import constant
from ..base_task import BaseTask
from ...utils.utils import get_model_response_content

if TYPE_CHECKING:
    from ...models.base_model import BaseModel

class LongMemEvalTask(BaseTask):
    """
    一个处理开放式生成任务（如长程记忆问答）的 Task 类。
    """
    def __init__(self, task_config: Dict[str, Any], llm_model: "BaseModel"):
        super().__init__(task_config)
        self.llm_model = llm_model
        
        prompt_path = self.task_config["prompt_path"]
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.prompt_template = f.read()

    @override
    def process_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        all_prompts = []
        for sample in batch:
            prompt = self.prompt_template.format(
                scene=sample.get('scene', ''),
                question_text=sample.get('question_text', '')
            )
            all_prompts.append(prompt)

        # 调用模型获取生成结果
        responses = self.llm_model.process(all_prompts)
        
        # 整理结果，为后续分析做准备
        results = []
        for response, sample in zip(responses, batch):
            response_content = get_model_response_content(response).strip()
            
            result = {
                'question_id': sample.get('question_id'),
                'context': sample.get('scene'), # 完整的上下文
                'question': sample.get('question_text'),
                'correct_answer': sample.get('correct_answer'), # 标准答案
                'predicted_answer': response_content, # 模型预测的答案（简化后只保留内容）
                'model_response': response_content # 直接的模型回复内容，不包含其他冗杂数据
            }
            results.append(result)
            
        return results