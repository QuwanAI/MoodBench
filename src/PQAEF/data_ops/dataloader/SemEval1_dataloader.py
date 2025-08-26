# -*- coding: utf-8 -*-
"""
Provides a flexible DataLoader for reading data from JSON/JSONL files.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Iterator, List, Union
import random
import sys

from .base_dataloader import BaseDataLoader, register_dataloader
from PQAEF.utils.template_registry import get_formatter, BaseFormatter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@register_dataloader("SemEval1Loader")
class SemEval1Loader(BaseDataLoader):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Paths can be a single string or a list of strings
        paths_config = self.config.get('paths')
        if isinstance(paths_config, str):
            self.paths: List[Path] = [Path(paths_config)]
        elif isinstance(paths_config, list):
            self.paths: List[Path] = [Path(p) for p in paths_config]
        else:
            raise ValueError("'paths' in config must be a string or a list of strings.")

        self.recursive: bool = self.config.get('recursive', False)
        
        formatter_name = self.config['formatter_name']
        self.num = self.config.get("num", -1)
        formatter_class = get_formatter(formatter_name)
        self.formatter: BaseFormatter = formatter_class()
        
        self._samples: List[Dict[str, Any]] = []
        
        self._load_and_process_data()

    def _get_file_paths(self) -> List[Path]:
        all_files = set()
        for path in self.paths:
            if not path.exists():
                logging.warning(f"Path does not exist: {path}")
                continue
            
            if path.is_file():
                all_files.add(path)
            elif path.is_dir():
                glob_pattern = '**/*.txt' if self.recursive else '*.txt'
                all_files.update(path.glob(glob_pattern))
        
        return sorted(list(all_files))
    
    def _load_and_process_data(self):
        file_paths = self._get_file_paths()
        if not file_paths:
            logging.warning(f"No files found to process for the given paths.")
            return
        emotions = ['anger','anticipation','disgust','fear','joy','love','optimism','pessimism','sadness','surprise','trust']
        for file_path in file_paths:
            logging.info(f"Processing file: {file_path}")

            with open(file_path, 'r', encoding='utf-8') as file:
                count = 0
                for line in file:
                    if count == 0:
                        count = count + 1
                        continue
                    raw_data = line.strip().split('\t')[1:]
                    text = raw_data[0]
                    item = {}
                    for index, label in enumerate(raw_data[1:]):
                        item['text'] = text
                        item['emotion'] = [emotions[index], label]
                        formatted_sample = self.formatter.format(item)
                        self._samples.append(formatted_sample)

        # 采样
        if self.num != -1:
            if self.num > len(self._samples):
                logging.warning(f"Requested sample size ({self.num}) is larger than available data ({len(self._samples)}). Using all available data.")
                # 不进行采样，使用全部数据
            else:
                self._samples = random.sample(self._samples, self.num)
        
        logging.info(f"Finished loading. Total formatted samples: {len(self._samples)}")

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        # 直接迭代已经加载和格式化好的样本列表
        return iter(self._samples)

    def __len__(self) -> int:
        return len(self._samples)