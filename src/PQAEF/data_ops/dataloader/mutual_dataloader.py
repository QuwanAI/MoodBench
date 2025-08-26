import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Iterator, List
import random

from .base_dataloader import BaseDataLoader, register_dataloader
from PQAEF.utils.template_registry import get_formatter, BaseFormatter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@register_dataloader("MutualDataLoader")
class MutualDataLoader(BaseDataLoader):
    """
    DataLoader specifically for processing Mutual dataset
    Processes multiple files in dev_X.txt format in the dev directory, each containing one line of JSON content
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.dev_dir = Path(self.config.get('dev_dir'))
        if not self.dev_dir or not self.dev_dir.exists():
            raise ValueError(f"dev_dir '{self.dev_dir}' does not exist or is not specified.")
        
        formatter_name = self.config['formatter_name']
        formatter_class = get_formatter(formatter_name)
        self.formatter: BaseFormatter = formatter_class()
        
        self.num = config.get("num", -1)
        if not isinstance(self.num, int):
            raise ValueError(f"`num` must be int, but got {type(self.num)}")
        self.seed = config.get("seed", 42)
        random.seed(self.seed)
        
        self._samples: List[Dict[str, Any]] = []
        self._load_and_process_data()
    
    def _get_txt_files(self) -> List[Path]:
        """Get all txt files in the dev directory"""
        txt_files = list(self.dev_dir.glob("*.txt"))
        return sorted(txt_files)
    
    def _load_and_process_data(self):
        """Load and process JSON data from all txt files"""
        txt_files = self._get_txt_files()
        if not txt_files:
            logging.warning(f"No txt files found in directory: {self.dev_dir}")
            return
        
        logging.info(f"Found {len(txt_files)} txt files in {self.dev_dir}")
        
        for file_path in txt_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    line = f.readline().strip()
                    if not line:
                        logging.warning(f"Empty file: {file_path}")
                        continue
                    
                    try:
                        raw_sample = json.loads(line)
                        
                        formatted_sample = self.formatter.format(raw_sample)
                        if formatted_sample is not None:
                            self._samples.append(formatted_sample)
                        else:
                            logging.warning(f"Formatter returned None for file: {file_path}")
                            
                    except json.JSONDecodeError as e:
                        logging.warning(f"Failed to parse JSON in file {file_path}. Error: {e}")
                        continue
                        
            except IOError as e:
                logging.error(f"Failed to read file {file_path}: {e}")
                continue
        
        if self.num != -1 and len(self._samples) > self.num:
            self._samples = random.sample(self._samples, self.num)
        
        logging.info(f"Finished loading. Total formatted samples: {len(self._samples)}")
    
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Iterate over loaded and formatted samples"""
        return iter(self._samples)
    
    def __len__(self) -> int:
        return len(self._samples)