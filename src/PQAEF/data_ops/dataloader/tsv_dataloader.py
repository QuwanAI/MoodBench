import csv
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Iterator, List, Union
import random
import os

from .base_dataloader import BaseDataLoader, register_dataloader
from PQAEF.utils.template_registry import get_formatter, BaseFormatter


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@register_dataloader("TSVDataLoader")
class TSVDataLoader(BaseDataLoader):
    """
    TSV data loader

    Supports loading TSV files and converting them to standard format through registered formatters
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize TSV data loader

        Args:
            config: Configuration dictionary containing:
                - paths: TSV file path (string) or list of paths
                - formatter_name: Formatter name (optional)
                - encoding: File encoding, default utf-8 (optional)
                - skip_header: Whether to skip header row, default True (optional)
                - num: Sample count, -1 means load all data (optional)
        """
        super().__init__(config)

        paths_config = self.config.get('paths')
        self.suffix = self.config.get("suffix", "tsv")
        if isinstance(paths_config, str):
            self.paths: List[Path] = [Path(paths_config)]
        elif isinstance(paths_config, list):
            self.paths: List[Path] = [Path(p) for p in paths_config]
        else:
            raise ValueError("'paths' in config must be a string or a list of strings.")

        self.recursive: bool = self.config.get('recursive', False)
        self.formatter_name = config.get('formatter_name')
        self.encoding = config.get('encoding', 'utf-8')
        self.skip_header = config.get('skip_header', True)
        self.formatter = None

        if self.formatter_name:
            formatter_class = get_formatter(self.formatter_name)
            self.formatter = formatter_class()

        self.num = config.get("num", -1)
        self._samples: List[Dict[str, Any]] = []
        self._load_and_process_data()

    def _get_file_paths(self) -> List[Path]:
        """Find and return all TSV file paths that meet the criteria"""
        all_files = set()
        for path in self.paths:
            if not path.exists():
                logging.warning(f"Path does not exist: {path}")
                continue

            if path.is_file():
                if path.suffix == f".{self.suffix}":
                    all_files.add(path)
                else:
                    logging.warning(f"Skipping non-{self.suffix} file specified directly: {path}")
            elif path.is_dir():
                glob_pattern = f'**/*.{self.suffix}' if self.recursive else f'*.{self.suffix}'
                all_files.update(path.glob(glob_pattern))

        return sorted(list(all_files))

    def _load_and_process_data(self):
        """Load and process all found TSV files"""
        file_paths = self._get_file_paths()
        for data_path in file_paths:
            logging.info(f"Processing TSV file: {data_path}")
            try:
                with open(data_path, 'r', encoding=self.encoding, newline='') as tsvfile:
                    reader = csv.reader(tsvfile, delimiter='\t', quoting=csv.QUOTE_NONE)

                    if self.skip_header:
                        try:
                            next(reader)
                        except StopIteration:
                            logging.warning(f"File is empty or contains only a header: {data_path}")
                            continue

                    for row_idx, row in enumerate(reader):
                        try:
                            if not row or all(not cell.strip() for cell in row):
                                continue

                            cleaned_row = [cell.strip() if isinstance(cell, str) else cell for cell in row]

                            if self.formatter:
                                formatted_data = self.formatter.format(cleaned_row)
                            else:
                                formatted_data = {
                                    'raw_data': cleaned_row,
                                    '_source_file': str(data_path),
                                    '_row_index': row_idx
                                }
                            self._samples.append(formatted_data)

                        except Exception as e:
                            logging.error(f"Error processing row {row_idx} in {str(data_path)}: {e}")
                            continue

            except Exception as e:
                logging.error(f"Error reading file {str(data_path)}: {e}")
                continue

        # 进行健壮的采样
        if self.num != -1:
            if self.num > len(self._samples):
                logging.warning(
                    f"Requested sample size ({self.num}) is larger than available data ({len(self._samples)}). Using all available data."
                )
                # 不进行采样，使用全部数据
            else:
                self._samples = random.sample(self._samples, self.num)

        logging.info(f"Finished loading. Total formatted samples: {len(self._samples)}")

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """返回已加载和格式化好的样本迭代器"""
        return iter(self._samples)

    def __len__(self) -> int:
        """返回加载的样本总数"""
        return len(self._samples)

    def get_total_count(self) -> int:
        """
        获取数据总数

        Returns:
            int: 加载的数据总数
        """
        return self.__len__()