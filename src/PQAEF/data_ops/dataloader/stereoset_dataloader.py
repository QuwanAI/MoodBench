# -*- coding: utf-8 -*-
import json
import logging
from pathlib import Path
from typing import Dict, Any, Iterator, List
import random

from .base_dataloader import BaseDataLoader, register_dataloader
from PQAEF.utils.template_registry import get_formatter, BaseFormatter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@register_dataloader("StereoSetLoader")
class StereoSetLoader(BaseDataLoader):
    """
    DataLoader specifically for loading StereoSet dataset.
    It directly reads JSON files and drills down to 'data.intersentence' or 'data.intrasentence' paths.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        path_config = self.config.get('path')
        if not isinstance(path_config, str):
            raise ValueError("'path' in StereoSetLoader config must be a single string.")
        self.file_path: Path = Path(path_config)

        self.data_path: List[str] = self.config.get('data_path')
        if not self.data_path:
            raise ValueError("'data_path' must be specified in StereoSetLoader config.")

        formatter_name = self.config['formatter_name']
        self.formatter: BaseFormatter = get_formatter(formatter_name)()
        
        self.num = config.get("num", -1)
        self.seed = config.get("seed", 42)
        random.seed(self.seed)
        
        self._samples: List[Dict[str, Any]] = []
        self._load_and_process_data()

    def _load_and_process_data(self):
        if not self.file_path.exists():
            logging.error(f"StereoSet file not found at: {self.file_path}")
            return

        logging.info(f"Loading StereoSet data from: {self.file_path}")
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logging.error(f"Failed to read or parse file {self.file_path}: {e}")
            return

        data_to_iterate = raw_data
        for key in self.data_path:
            if isinstance(data_to_iterate, dict):
                data_to_iterate = data_to_iterate.get(key)
            else:
                logging.error(f"Cannot access key '{key}' in non-dict structure in {self.file_path}")
                return
        
        if not isinstance(data_to_iterate, list):
            logging.error(f"Data at path '{'.'.join(self.data_path)}' is not a list. Cannot process.")
            return
        
        all_formatted_samples = []
        for i, raw_sample in enumerate(data_to_iterate):
            try:
                formatted_sample = self.formatter.format(raw_sample)
                if formatted_sample:
                    all_formatted_samples.append(formatted_sample)
            except Exception as e:
                logging.warning(f"Failed to format sample #{i+1} from {self.file_path}. Error: {e}. Skipping.")
                continue
        
        self._samples = all_formatted_samples
        
        if self.num != -1 and self.num < len(self._samples):
            self._samples = random.sample(self._samples, self.num)
        
        logging.info(f"Finished loading StereoSet. Total formatted samples: {len(self._samples)}")

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        return iter(self._samples)

    def __len__(self) -> int:
        return len(self._samples)