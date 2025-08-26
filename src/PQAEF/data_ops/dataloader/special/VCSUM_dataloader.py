import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Iterator, List, Union
import random

from ..base_dataloader import BaseDataLoader, register_dataloader
from PQAEF.utils.template_registry import get_formatter, BaseFormatter
from PQAEF.utils.utils import read_jsonl

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@register_dataloader("VCSUMLoader")
class VCSUMLoader(BaseDataLoader):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        """
            可接受的 config 参数
                context_path: 存放 context 路径
                long_path: 存放数据的 long 路径
                formatter_name: formatter 的名称
                num: 限制数据数量，默认为 -1 即全部加载
                seed: 采样种子
        """
        
        # Paths can be a single string or a list of strings
        self.context_path = self.config.get('context_path')
        self.long_path = self.config.get('long_path')
        
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

    
    def _load_and_process_data(self):
        context = read_jsonl(self.context_path)
        long = read_jsonl(self.long_path)
        print(context[0].keys())
        # print("="*20)
        print(long[0].keys())
        
        for d in long:
            id = d["id"]
            for c in context:
                if c["id"] == id:
                    d["context"] = c["context"]
                    break
            
            formatted_sample = self.formatter.format(d)
            self._samples.append(formatted_sample)
            
        del context
        
        
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