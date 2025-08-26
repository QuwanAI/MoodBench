import json
import os
from typing import Dict, Any, Iterator
from .base_dataloader import BaseDataLoader, register_dataloader
from ...utils.template_registry import get_formatter


@register_dataloader("ESConvDataLoader")
class ESConvDataLoader(BaseDataLoader):
    """
    ESConv dataset data loader, extracts single-turn samples from multi-turn conversations for evaluation
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.path = self.config['path']
        self.formatter_name = self.config.get('formatter_name', 'ESConvFormatter')
        self.sample_size = self.config.get('sample_size', None)
        self.max_history_turns = self.config.get('max_history_turns', 3)
        self.strategies = self.config.get('strategies', [
            'Question', 'Restatement or Paraphrasing', 'Reflection of feelings',
            'Self-disclosure', 'Affirmation and Reassurance', 'Providing Suggestions',
            'Information', 'Others'
        ])
        
        self.data = self._load_data()
        
        formatter_class = get_formatter(self.formatter_name)
        self.formatter = formatter_class()
        
    def _load_data(self):
        """Load ESConv.json data"""
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"ESConv data file not found: {self.path}")
            
        with open(self.path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"INFO: Loaded {len(data)} conversations from {self.path}")
        return data
        
    def _merge_consecutive_turns(self, dialog):
        """Merge consecutive turns from the same speaker"""
        if not dialog:
            return []
        
        merged_dialog = []
        current_turn = None
        
        for turn in dialog:
            if current_turn is None:
                current_turn = {
                    'speaker': turn['speaker'],
                    'content': turn['content'].strip(),
                    'annotation': turn.get('annotation', {})
                }
            elif current_turn['speaker'] == turn['speaker']:
                current_turn['content'] += ' ' + turn['content'].strip()
                if turn.get('annotation'):
                    current_turn['annotation'].update(turn['annotation'])
            else:
                merged_dialog.append(current_turn)
                current_turn = {
                    'speaker': turn['speaker'],
                    'content': turn['content'].strip(),
                    'annotation': turn.get('annotation', {})
                }
        
        if current_turn:
            merged_dialog.append(current_turn)
        
        return merged_dialog
    
    def _extract_single_turn_samples(self):
        """Extract single-turn samples from multi-turn conversations"""
        samples = []
        
        for conv_idx, conversation in enumerate(self.data):
            dialog = conversation.get('dialog', [])
            
            merged_dialog = self._merge_consecutive_turns(dialog)
            
            dialog_history = []
            turn_count = 0
            
            for turn_idx, turn in enumerate(merged_dialog):
                if turn['speaker'] == 'supporter' and 'strategy' in turn.get('annotation', {}):
                    strategy = turn['annotation']['strategy']
                    
                    if strategy in self.strategies:
                        limited_history = dialog_history[-self.max_history_turns*2:] if self.max_history_turns > 0 else dialog_history
                        
                        sample = {
                            'conversation_id': conv_idx,
                            'turn_id': turn_idx,
                            'situation': conversation.get('situation', ''),
                            'emotion_type': conversation.get('emotion_type', ''),
                            'problem_type': conversation.get('problem_type', ''),
                            'experience_type': conversation.get('experience_type', ''),
                            'dialog_history': limited_history.copy(),
                            'strategy': strategy,
                            'supporter_response': turn['content'].strip(),
                            'survey_score': conversation.get('survey_score', {})
                        }
                        samples.append(sample)
                
                dialog_history.append({
                    'speaker': turn['speaker'],
                    'content': turn['content'].strip()
                })
                
        print(f"INFO: Extracted {len(samples)} single-turn samples")
        return samples
        
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Iterate and return formatted samples"""
        samples = self._extract_single_turn_samples()
        
        if self.sample_size and self.sample_size < len(samples):
            import random
            samples = random.sample(samples, self.sample_size)
            print(f"INFO: Sampled {self.sample_size} samples from {len(samples)} total samples")
            
        for sample in samples:
            formatted_sample = self.formatter.format(sample)
            if formatted_sample is not None:
                yield formatted_sample
                
    def __len__(self) -> int:
        """Return dataset size"""
        samples = self._extract_single_turn_samples()
        if self.sample_size:
            return min(self.sample_size, len(samples))
        return len(samples)