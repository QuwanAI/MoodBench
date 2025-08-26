import csv
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Iterator, List, Union
import random
import pandas as pd
import os

from ..base_dataloader import BaseDataLoader, register_dataloader
from .cped_datasets import CpedDataset
from PQAEF.utils.template_registry import get_formatter, BaseFormatter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@register_dataloader("CPEDDataLoader")
class CPEDDataLoader(BaseDataLoader):
    """
    CSV数据加载器
    
    支持加载CSV文件并通过注册的格式化器转换为标准格式
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化CSV数据加载器
        
        Args:
            config: 配置字典，包含以下字段：
                - path: 具体到 CPED 文件的路径，以 .csv
                - formatter_name: 格式化器名称（可选）
                - encoding: 文件编码，默认utf-8（可选）
                - skip_header: 是否跳过表头行，默认True（可选）
        """
        super().__init__(config)
        
        # Paths can be a single string or a list of strings
        paths_config = self.config.get('paths')
        self.suffix = self.config.get("suffix", "csv")
        if isinstance(paths_config, str):
            self.paths: List[Path] = [Path(paths_config)]
        elif isinstance(paths_config, list):
            self.paths: List[Path] = [Path(p) for p in paths_config]
        else:
            raise ValueError("'paths' in config must be a string or a list of strings.")

        self.recursive: bool = self.config.get('recursive', False)
        self.formatter_name = config.get('formatter_name')
        self.encoding = config.get('encoding', 'utf-8')
        self.skip_header = config.get('skip_header', True)  # 默认跳过表头
        self.formatter = None
        
        # 如果指定了格式化器，则获取格式化器实例
        if self.formatter_name:
            formatter_class = get_formatter(self.formatter_name)
            self.formatter = formatter_class()
        
        self.num = config.get("num", -1)
        self._samples: List[Dict[str, Any]] = []
        
        self.max_history = config.get("max_history", 5)
        
        assert len(self.paths) == 1, "Only support 1 path"

        
        self._load_and_process_data()
        
        # print(json.dumps(self._samples,indent=4))
        # sys.exit(0)
    

    def _load_and_process_data(self) -> Iterator[Dict[str, Any]]:
        file_path = self.paths[0]
        
        df = pd.read_csv(file_path)
        self._samples = CpedDataset(df, max_history=self.max_history, lm_labels=True)
            
            
        # 采样
        if self.num != -1:
            if self.num > len(self._samples):
                logging.warning(f"Requested sample size ({self.num}) is larger than available data ({len(self._samples)}). Using all available data.")
                # 不进行采样，使用全部数据
            else:
                self._samples.keys = random.sample(self._samples.keys, self.num)
        
        logging.info(f"Finished loading. Total formatted samples: {self.__len__()}")

    
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        # 直接迭代已经加载和格式化好的样本列表
        return iter(self._samples)

    def __len__(self) -> int:
        return len(self._samples.keys)
    
    def get_total_count(self) -> int:
        """
        获取数据总数（可选实现）
        
        Returns:
            int: 数据总数，如果无法确定则返回-1
        """
        return self.__len__()