import os
from typing import List, Dict, Any, TYPE_CHECKING

from typing_extensions import override
from tqdm import tqdm

from ..base_task import BaseTask
from ...utils.metrics import calculate_rouge
from ...utils.utils import get_model_response_content


if TYPE_CHECKING:
    from ...models.base_model import BaseModel


class DialogueSummaryTask(BaseTask):
    def __init__(self, task_config: Dict[str, Any], llm_model: "BaseModel"):
        super().__init__(task_config)
        self.llm_model = llm_model
        
        prompt_path = self.task_config["prompt_path"]
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.prompt_template = f.read()
    
    # def _calculate_score(self, responses: List[Any], batch: List[Dict[str, Any]]) -> List[Any]:
    def _calculate_score(self, responses: List[Any], batch: List[Dict[str, Any]]):
        
        results = []
        
        for response, sample in zip(responses, batch):
            response_content = get_model_response_content(response)
            
            rouge_scores = calculate_rouge(response_content, sample["output"])
            sample["model_response"] = response
            for rouge_type, scores in rouge_scores.items():
                sample[rouge_type] = {
                    "F1-Score": f"{scores['f']:.4f}",
                    "Precision": f"{scores['p']:.4f}",
                    "Recall": f"{scores['r']:.4f}",
                }
            results.append(rouge_scores)
        # return results
        
            
    
    @override
    def process_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        
        all_prompts = []
        # gold_summarys = [sample["summary"] for sample in batch]
        
        for sample in batch:
        # for sample in tqdm(batch, desc="Dialogue Summary"):
            dialogue_text = sample["input"]
            prompt = self.prompt_template.format(dialogue_text=dialogue_text)
            all_prompts.append(prompt)
        
        # 打印一个示例prompt
        print('one sample prompt:\n', prompt)
        
        responses = self.llm_model.process(all_prompts)
        # scores = self._calculate_score(responses, batch)
        self._calculate_score(responses, batch)
        
        # for sample in 
        return batch
        
        