# -*- coding: utf-8 -*-
import json
import logging
from pathlib import Path
from typing import Dict, Any, Iterator, List
import random

from .base_dataloader import BaseDataLoader, register_dataloader
from PQAEF.utils.template_registry import get_formatter, BaseFormatter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@register_dataloader("PersonaFeedbackLoader")
class PersonaFeedbackLoader(BaseDataLoader):
    """
    DataLoader specifically for loading PersonaFeedback dataset.
    - First loads all persona files.
    - Then samples specified number of samples from each data a.jsonl file according to configuration.
    - Finally, associates persona information with Q&A samples.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.persona_dir = Path(config['persona_dir'])
        self.data_dir = Path(config['data_dir'])
        
        self.num_per_file = config.get('num_per_file', -1)
        
        formatter_name = config['formatter_name']
        self.formatter: BaseFormatter = get_formatter(formatter_name)()
        
        self.seed = config.get("seed", 42)
        random.seed(self.seed)
        
        self._samples: List[Dict[str, Any]] = []
        self._load_and_process_data()

    def _load_and_process_data(self):
        personas = {}
        if not self.persona_dir.is_dir():
            logging.error(f"Persona directory not found: {self.persona_dir}")
            return
            
        for persona_file in self.persona_dir.glob("*.json"):
            user_id = persona_file.stem
            with open(persona_file, 'r', encoding='utf-8') as f:
                personas[user_id] = json.load(f)
        logging.info(f"Loaded {len(personas)} personas.")

        target_files = list(self.data_dir.glob("general/*.jsonl")) + \
                       list(self.data_dir.glob("specific/*.jsonl"))
        
        if not target_files:
            logging.error(f"No .jsonl files found in {self.data_dir}/general or {self.data_dir}/specific")
            return

        all_q_samples = []
        for file_path in target_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if self.num_per_file != -1 and self.num_per_file < len(lines):
                sampled_lines = random.sample(lines, self.num_per_file)
            else:
                sampled_lines = lines
            
            for line in sampled_lines:
                all_q_samples.append(json.loads(line))
        
        logging.info(f"Sampled a total of {len(all_q_samples)} questions from {len(target_files)} files.")

        for q_sample in all_q_samples:
            user_id = q_sample.get("user_id")
            if user_id in personas:
                combined_sample = {
                    "persona": personas[user_id],
                    "question_data": q_sample
                }
                formatted_sample = self.formatter.format(combined_sample)
                if formatted_sample:
                    self._samples.append(formatted_sample)
            else:
                logging.warning(f"Persona for user_id '{user_id}' not found. Skipping sample.")
        
        logging.info(f"Finished loading. Total formatted samples: {len(self._samples)}")

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        return iter(self._samples)

    def __len__(self) -> int:
        return len(self._samples)