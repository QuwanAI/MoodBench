# -*- coding: utf-8 -*-
"""
Provides a specialized DataLoader for LogicNLI dataset.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Iterator, List, Union
import random

from .base_dataloader import BaseDataLoader, register_dataloader
from PQAEF.utils.template_registry import get_formatter, BaseFormatter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@register_dataloader("LogicNLIDataLoader")
class LogicNLIDataLoader(BaseDataLoader):
    """
    Specialized DataLoader for LogicNLI dataset.
    
    This loader handles the special structure of LogicNLI data where each sample
    contains facts, rules, statements, and labels, and generates individual samples
    for each statement-label pair.
    """
    
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
        
        self.seed = self.config.get("seed", 42)
        random.seed(self.seed)
        
        self._samples: List[Dict[str, Any]] = []
        
        self._load_and_process_data()

    def _get_file_paths(self) -> List[Path]:
        """Identifies all JSON files to be processed based on the configuration."""
        all_files = set()
        for path in self.paths:
            if not path.exists():
                logging.warning(f"Path does not exist: {path}")
                continue
            
            if path.is_file():
                if path.suffix == '.json':
                    all_files.add(path)
                else:
                    logging.warning(f"Skipping non-json file specified directly: {path}")
            elif path.is_dir():
                glob_pattern = '**/*.json' if self.recursive else '*.json'
                all_files.update(path.glob(glob_pattern))
        
        return sorted(list(all_files))
    
    def _load_and_process_data(self):
        """Load and process LogicNLI data, generating samples for each statement-label pair."""
        file_paths = self._get_file_paths()
        if not file_paths:
            logging.warning(f"No files found to process for the given paths.")
            return

        for file_path in file_paths:
            logging.info(f"Processing file: {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
            except (IOError, json.JSONDecodeError) as e:
                logging.error(f"Failed to read or parse file {file_path}: {e}")
                continue

            # Process each sample in the JSON data
            for sample_id, sample_data in raw_data.items():
                try:
                    # Add sample_id to the data for formatter
                    sample_data_with_id = sample_data.copy()
                    sample_data_with_id['id'] = sample_id
                    
                    try:
                        # Use formatter to process the original sample
                        formatted_result = self.formatter.format(sample_data_with_id)
                        
                        # Handle both single dict and list of dicts
                        if formatted_result is not None:
                            if isinstance(formatted_result, list):
                                # If formatter returns a list, extend our samples
                                self._samples.extend([sample for sample in formatted_result if sample is not None])
                            else:
                                # If formatter returns a single dict, append it
                                self._samples.append(formatted_result)
                        else:
                            logging.warning(f"Formatter returned None for sample {sample_id}")
                    except Exception as e:
                        logging.warning(
                            f"Failed to format sample {sample_id}. "
                            f"Error: {e}. Skipping sample."
                        )
                        continue
                        
                except Exception as e:
                    logging.warning(f"Error processing sample {sample_id}: {e}. Skipping sample.")
                    continue
                
        # Apply sampling if specified
        if self.num != -1 and len(self._samples) > self.num:
            self._samples = random.sample(self._samples, self.num)
        
        logging.info(f"Finished loading. Total formatted samples: {len(self._samples)}")

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Iterate over the loaded and formatted samples."""
        return iter(self._samples)

    def __len__(self) -> int:
        return len(self._samples)