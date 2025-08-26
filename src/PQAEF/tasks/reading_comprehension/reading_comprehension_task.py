import os
from typing import List, Dict, Any, TYPE_CHECKING

from typing_extensions import override
from tqdm import tqdm
import re

from ..base_task import BaseTask
from ...utils.extract_answer import extract_reading_comprehension_answer
from ...utils.utils import get_model_response_content
from ...utils.metrics import calculate_rouge

if TYPE_CHECKING:
    from ...models.base_model import BaseModel

class ReadingComprehensionTask(BaseTask):
    def __init__(self, task_config: Dict[str, Any], llm_model: "BaseModel"):
        super().__init__(task_config)
        self.llm_model = llm_model
        
        prompt_path = self.task_config["prompt_path"]
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.prompt_template = f.read()
    
    def _calculate_score(self, responses: List[Any], batch: List[Dict[str, Any]]):
        results = []
        
        for response, sample in zip(responses, batch):
            response_content = get_model_response_content(response)
            predicted_answer = extract_reading_comprehension_answer(response_content)
            correct_answer = sample.get('correct_answer', '')
            
            # 计算ROUGE分数
            rouge_score = calculate_rouge(predicted_answer, correct_answer)
            
            result = {
                'question_id': sample.get('question_id', ''),
                'scene': sample.get('scene', ''),
                'question_text': sample.get('question_text', ''),
                'correct_answer': correct_answer,
                'predicted_answer': predicted_answer,
                'raw_answer': response_content,
                'category': sample.get('category', ''),
                'rouge_score': rouge_score
            }
            
            results.append(result)
        
        return results
    
    @override
    def process_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        all_prompts = []

        # 从prompt模板中提取所有占位符
        placeholders = re.findall(r'\{([^}]+)\}', self.prompt_template)
        
        for sample in batch:
            format_kwargs = {}
            
            for placeholder in placeholders:
                if placeholder in sample:
                    format_kwargs[placeholder] = sample[placeholder]
                else:
                    # 处理其他可能的映射关系
                    value = ''
                    if placeholder == 'scene':
                        value = sample.get('scene', '')
                    elif placeholder == 'question_text':
                        value = sample.get('question_text', sample.get('question', ''))
                    
                    format_kwargs[placeholder] = value
            
            prompt = self.prompt_template.format(**format_kwargs)
            all_prompts.append(prompt)
        
        print('one sample prompt:\n', all_prompts[0] if all_prompts else '')
        responses = self.llm_model.process(all_prompts)
        return self._calculate_score(responses, batch)