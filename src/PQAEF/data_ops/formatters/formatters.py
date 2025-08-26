# -*- coding: utf-8 -*-
"""
Contains specific formatters for different raw dataset structures.
To make a formatter available, simply import this file in your main script.
"""
import sys
from typing import Dict, Any, List
from abc import ABC, abstractmethod
import hashlib
import random
from typing_extensions import override

from PQAEF.constant import constant
from PQAEF.utils.template_registry import register_formatter
from PQAEF.utils.utils import calculate_hash
from PQAEF.utils.template_registry import BaseFormatter

def map_options_to_letters(options):
    # 生成对应的字母列表，超过Z时从a开始循环
    letters = []
    for i in range(len(options)):
        # 计算偏移量，26个大写字母后切换到小写字母循环
        offset = i % 52  # 52 = 26(大写) + 26(小写)
        if offset < 26:
            # 大写字母 A-Z
            letters.append(chr(ord('A') + offset))
        else:
            # 小写字母 a-z
            letters.append(chr(ord('a') + (offset - 26)))
    # 创建字母到选项的映射字典
    mapped_options = {letter: options[i] for i, letter in enumerate(letters)}
    return mapped_options

@register_formatter("empty_format")
@register_formatter("lcsts_format")
@register_formatter("TruthfulQA_format")
@register_formatter("MulDimIF_format")
@register_formatter("cped_format")
@register_formatter("AlignBench_format")
class EmptyFormatter(BaseFormatter):
    @override
    def format(self, raw_sample: Dict[str, Any]) -> Dict[str, Any]:
        hash_value = calculate_hash(raw_sample)
        raw_sample[constant.KEY_OTHER_INFO] = {}
        raw_sample[constant.KEY_OTHER_INFO][constant.KEY_HASH] = hash_value

        return raw_sample

@register_formatter("mmchat_m3ed_format")
class MMChatM3EDFormatter(BaseFormatter):
    """
    Formats raw data from datasets like mmchat and M3ED into the
    PQAEF standard format.
    """
    def format(self, raw_sample: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Create the standard skeleton for the output
        formatted_sample = {
            constant.KEY_DIALOGUES: [],
            constant.KEY_DIALOGUE_ANNOTATION: {},
            constant.KEY_OTHER_INFO: {}
        }

        # 2. Move top-level fields like 'ave_value' into 'other_info'
        if 'ave_value' in raw_sample:
            formatted_sample[constant.KEY_OTHER_INFO]['ave_value'] = raw_sample['ave_value']
        if 'sentiment_score' in raw_sample:
            formatted_sample[constant.KEY_OTHER_INFO]['sentiment_score'] = raw_sample['sentiment_score']

        # 3. Process the dialogue turns
        for turn in raw_sample.get(constant.KEY_DIALOGUES, []):
            formatted_turn = {
                constant.KEY_ROLE: turn.get(constant.KEY_ROLE),
                constant.KEY_CONTENT: turn.get(constant.KEY_CONTENT),
                constant.KEY_SENTENCE_ANNOTATION: {}  # Initialize empty annotation dict
            }
            # Note: We are intentionally ignoring 'normal_value' as it's not in the standard format.
            # If you wanted to keep it, you could add it to `sentence_annotation`.
            formatted_sample[constant.KEY_DIALOGUES].append(formatted_turn)

        # 4. Calculate and add the hash AFTER the sample is in standard format
        # This ensures the hash is consistent regardless of the raw format.
        hash_value = calculate_hash(formatted_sample)
        formatted_sample[constant.KEY_OTHER_INFO][constant.KEY_HASH] = hash_value

        return formatted_sample


@register_formatter("EmoBenchBFormatter")
class EmoBenchBFormatter(BaseFormatter):
    @override
    def format(self, raw_sample: Dict[str, Any]) -> Dict[str, Any]:
        # 处理None输入
        if raw_sample is None:
            return None
            
        # 确保输入是字典类型
        if not isinstance(raw_sample, dict):
            return None
        
        # 提取数据字段（忽略cause相关字段）
        qid = raw_sample.get('qid', '').strip()
        language = raw_sample.get('language', '').strip()
        coarse_category = raw_sample.get('coarse_category', '').strip()
        finegrained_category = raw_sample.get('finegrained_category', '').strip()
        scenario = raw_sample.get('scenario', '').strip()
        subject = raw_sample.get('subject', '').strip()
        emotion_choices = raw_sample.get('emotion_choices', [])
        emotion_label = raw_sample.get('emotion_label', '').strip()
        
        # 验证必要字段
        if not scenario or not emotion_choices or not emotion_label:
            return None
        
        # 验证emotion_label是否在emotion_choices中
        if emotion_label not in emotion_choices:
            return None
        
        # 构建场景描述
        scene = f"Scenario: {scenario}"
        if subject:
            scene += f"\n\nSubject: {subject}"
        
        # 构建问题文本
        question_text = "What emotion is the subject most likely experiencing in this situation?"
        
        # 构建选项字典（根据emotion_choices的数量动态生成）
        option_dict = {}
        option_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']  # 支持最多8个选项
        
        for i, choice in enumerate(emotion_choices):
            if i < len(option_labels):
                option_dict[option_labels[i]] = choice
        
        # 找到正确答案对应的字母
        correct_answer = ""
        for key, value in option_dict.items():
            if value == emotion_label:
                correct_answer = key
                break
        
        # 生成哈希值
        hash_content = f"{qid}_{scenario}_{emotion_label}"
        hash_value = hashlib.md5(hash_content.encode('utf-8')).hexdigest()
        
        # 添加其他信息
        other_info = {
            "dataset_name": "emobench_b",
            "qid": qid,
            "language": language,
            "coarse_category": coarse_category,
            "finegrained_category": finegrained_category,
            "subject": subject,
            "original_emotion_choices": emotion_choices,
            "original_emotion_label": emotion_label,
            constant.KEY_HASH: hash_value
        }
        
        formatted_sample = {
            constant.KEY_QUESTION_ID: str(qid),
            constant.KEY_SCENE: scene,
            constant.KEY_QUESTION_TEXT: question_text,
            constant.KEY_OPTIONS: option_dict,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_CATEGORY: "Emotion Recognition",
            constant.KEY_SUBCATEGORY: "Complex Emotion Understanding",
            constant.KEY_OTHER_INFO: other_info
        }
        
        return formatted_sample


@register_formatter("SAMSum_format")
class SAMSumFormatter(BaseFormatter):
    @override
    def format(self, raw_sample: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Create the standard skeleton for the output
        formatted_sample = {
            "id": raw_sample["id"],
            "input": raw_sample["dialogue"],
            "output": raw_sample["summary"],
            constant.KEY_OTHER_INFO: {}
        }
        

        hash_value = calculate_hash(formatted_sample)
        formatted_sample[constant.KEY_OTHER_INFO][constant.KEY_HASH] = hash_value

        return formatted_sample


@register_formatter("CNewSumFormatter")
class CNewSumFormatter(BaseFormatter):
    @override
    def format(self, raw_sample: Dict[str, Any]) -> Dict[str, Any]:
        formatted_sample = {
            "id": raw_sample["id"],
            "input": "".join(sentence.replace(" ", "") for sentence in raw_sample["article"]) ,
            "output": raw_sample["summary"].replace(" ", ""),
            constant.KEY_OTHER_INFO: {}
        }
        
        hash_value = calculate_hash(formatted_sample)
        formatted_sample[constant.KEY_OTHER_INFO][constant.KEY_HASH] = hash_value

        return formatted_sample

@register_formatter("VCSUM_format")
class VCSUMFormatter(BaseFormatter):
    @override
    def format(self, raw_sample: Dict[str, Any]) -> Dict[str, Any]:
        context = []
        for c in raw_sample["context"]:
            context.extend(c)
        formatted_sample = {
            "id": raw_sample["id"],
            "input": context ,
            "output": raw_sample["summary"],
            constant.KEY_OTHER_INFO: {}
        }
        
        hash_value = calculate_hash(formatted_sample)
        formatted_sample[constant.KEY_OTHER_INFO][constant.KEY_HASH] = hash_value

        return formatted_sample

@register_formatter("sharegpt_format")
class ShareGPTFormatter(BaseFormatter):
    @override
    def format(self, raw_sample: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Not implement sharegpt_format")
        formatted_sample = {
            "id": raw_sample["id"],
            "input": context ,
            "output": raw_sample["summary"],
            
        }
        
        hash_value = calculate_hash(formatted_sample)
        formatted_sample[constant.KEY_OTHER_INFO][constant.KEY_HASH] = hash_value

        return formatted_sample
    
@register_formatter("OCNLIFormatter")
class OCNLIFormatter(BaseFormatter):
    @override
    def format(self, raw_sample: Dict[str, Any]) -> Dict[str, Any]:
        sentence1 = raw_sample['sentence1'].strip()
        sentence2 = raw_sample['sentence2'].strip()
        label = raw_sample['label']
        if isinstance(label, str):
            label = int(label.strip())

        # 添加其他信息
        other_info = {}
        excluded_keys = {'sentence1', 'sentence2', 'label'}
        other_info = {key: value for key, value in raw_sample.items() if key not in excluded_keys}

        scene = f"前提句：{sentence1}" + '\n' + f"假设句：{sentence2}"
        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        options = {
            "A": "中立关系（无法根据前提句判断假设句的真假）",
            "B": "蕴含关系（如果前提句为真，则假设句一定为真）",
            "C": "矛盾关系（如果前提句为真，则假设句一定为假）", 
            
        }

        label_to_answer = {0: "A", 1: "B", 2: "C"}
        correct_answer = label_to_answer.get(label, "")
        
        formatted_sample = {
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }
        formatted_sample[constant.KEY_OTHER_INFO] = other_info

        return formatted_sample
    

@register_formatter("HellaSwagFormatter")
class HellaSwagFormatter(BaseFormatter):
    @override
    def format(self, raw_sample: Dict[str, Any]) -> Dict[str, Any]:
        ctx = raw_sample['ctx'].strip()
        endings = raw_sample['endings']
        label = raw_sample['label']
        if isinstance(label, str):
            label = int(label.strip())

        # 添加其他信息
        other_info = {}
        excluded_keys = {'ctx', 'endings', 'label'}
        other_info = {key: value for key, value in raw_sample.items() if key not in excluded_keys}

        scene = f"Scenario: {ctx}"
        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        options = {
            "A": endings[0],
            "B": endings[1],
            "C": endings[2],
            "D": endings[3],
        }

        label_to_answer = {0: "A", 1: "B", 2: "C", 3: "D"}
        correct_answer = label_to_answer.get(label, "")
        
        formatted_sample = {
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }
        formatted_sample[constant.KEY_OTHER_INFO] = other_info

        return formatted_sample
    

@register_formatter("CosmosFormatter")
class CosmosFormatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        ID, context, question, c0, c1, c2, c3, label = raw_sample
        if isinstance(label, str):
            label = int(label.strip())

        scene = f"Context: {context} \nQuestion: {question}"
        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        options = {
            "A": c0,
            "B": c1,
            "C": c2,
            "D": c3,
        }

        label_to_answer = {0: "A", 1: "B", 2: "C", 3: "D"}
        correct_answer = label_to_answer.get(label, "")
        
        formatted_sample = {
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }
        return formatted_sample


@register_formatter("AGNewsFormatter")
class AGNewsFormatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        # 处理CSV行数据
        if not isinstance(raw_sample, list) or len(raw_sample) < 3:
            return None
        
        try:
            label = int(raw_sample[0].strip())
            title = raw_sample[1].strip().strip('"')
            description = raw_sample[2].strip().strip('"')
        except (ValueError, IndexError):
            return None
        
        # 验证标签范围
        if label not in [1, 2, 3, 4] or not title or not description:
            return None
        
        # 构建场景描述
        scene = f"Title: {title}\nDescription: {description}"
        
        # 生成哈希值
        hash_value = hashlib.sha256(scene.encode('utf-8')).hexdigest()
        
        # 构建选项
        options = {
            "A": "World - International news, politics, and global events",
            "B": "Sports - Athletic events, games, and sports-related news", 
            "C": "Business - Economic news, corporate affairs, and financial markets",
            "D": "Sci/Tech - Science, technology, and innovation news"
        }
        
        # 映射标签到答案
        label_to_answer = {1: "A", 2: "B", 3: "C", 4: "D"}
        correct_answer = label_to_answer.get(label, "")
        
        # 添加其他信息
        other_info = {
            "dataset_name": "agnews",
            "title": title,
            "description": description,
            "original_label": label
        }
        
        formatted_sample = {
            constant.KEY_QUESTION_ID: hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_QUESTION_TEXT: "Please classify this news article into one of the following categories:",
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_CATEGORY: "AGNews",
            constant.KEY_SUBCATEGORY: "News Topic Classification",
            constant.KEY_OTHER_INFO: other_info
        }
        
        return formatted_sample


@register_formatter("C3Formatter")
class C3Formatter(BaseFormatter):
    @override
    def format(self, raw_sample: Dict[str, Any]) -> Dict[str, Any]:
        # 处理None输入
        if raw_sample is None:
            return None
            
        # 确保输入是字典类型
        if not isinstance(raw_sample, dict):
            return None
        
        # 提取数据字段
        id_val = raw_sample.get('id', 0)
        context = raw_sample.get('context', [])
        question = raw_sample.get('question', '').strip()
        choice = raw_sample.get('choice', [])
        answer = raw_sample.get('answer', '').strip()
        
        # 处理pandas数组 - 转换为Python列表
        if hasattr(context, 'tolist'):
            context = context.tolist()
        if hasattr(choice, 'tolist'):
            choice = choice.tolist()
        
        # 确保都是字符串列表
        if isinstance(context, list):
            context = [str(item) for item in context]
        if isinstance(choice, list):
            choice = [str(item) for item in choice]
        
        # 验证必要字段
        if not context or not question or not choice or not answer:
            return None
        
        # 验证答案是否在选项中
        answer_found = False
        try:
            for c in choice:
                if str(c) == str(answer):
                    answer_found = True
                    break
        except Exception:
            return None
            
        if not answer_found:
            return None
        
        # 构建场景描述 - 将对话上下文组合
        if isinstance(context, list):
            scene = "\n".join(context)
        else:
            scene = str(context)
        
        # 构建选项字典 - 使用A、B、C、D等标识
        options = {}
        option_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']  # 支持最多8个选项
        
        for i, choice_text in enumerate(choice):
            if i < len(option_labels):
                options[option_labels[i]] = choice_text
        
        # 找到正确答案对应的标签
        correct_answer = ""
        for label, choice_text in options.items():
            if choice_text == answer:
                correct_answer = label
                break
        
        if not correct_answer:
            return None
        
        # 生成哈希值
        hash_content = f"{id_val}_{scene}_{question}_{answer}"
        hash_value = hashlib.md5(hash_content.encode('utf-8')).hexdigest()
        
        # 添加其他信息
        other_info = {
            "dataset_name": "c3",
            "original_context": context,
            "original_question": question,
            "original_choices": choice,
            "original_answer": answer,
            "choice_count": len(choice)
        }
        
        formatted_sample = {
            constant.KEY_QUESTION_ID: str(id_val),
            constant.KEY_SCENE: scene,
            constant.KEY_QUESTION_TEXT: question,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_CATEGORY: "NLU",
            constant.KEY_SUBCATEGORY: "阅读理解",
            constant.KEY_OTHER_INFO: other_info
        }
        
        return formatted_sample


@register_formatter("COPAFormatter")
class COPAFormatter(BaseFormatter):
    @override
    def format(self, raw_sample: Dict[str, Any]) -> Dict[str, Any]:
        # 处理None输入
        if raw_sample is None:
            return None
            
        # 确保输入是字典类型
        if not isinstance(raw_sample, dict):
            return None
        
        # 提取数据字段
        premise = raw_sample.get('premise', '').strip()
        choice1 = raw_sample.get('choice1', '').strip()
        choice2 = raw_sample.get('choice2', '').strip()
        question = raw_sample.get('question', '').strip()  # "cause" 或 "effect"
        label = raw_sample.get('label', -1)  # 0: choice1, 1: choice2
        idx = raw_sample.get('idx', 0)
        
        # 验证必要字段
        if not premise or not choice1 or not choice2 or question not in ['cause', 'effect'] or label not in [0, 1]:
            return None
        
        # 构建场景描述
        scene = f"Premise: {premise}"
        
        # 根据问题类型构建问题文本
        if question == "effect":
            question_text = "What is the most plausible effect of the premise?"
        else:  # question == "cause"
            question_text = "What is the most plausible cause of the premise?"
        
        # 构建选项 - COPA是二分类任务
        options = {
            "A": choice1,
            "B": choice2
        }
        
        # 映射标签到答案
        label_to_answer = {0: "A", 1: "B"}  # 0表示choice1，1表示choice2
        correct_answer = label_to_answer.get(label, "")
        
        # 生成哈希值
        hash_content = f"{idx}_{premise}_{choice1}_{choice2}_{question}_{label}"
        hash_value = hashlib.md5(hash_content.encode('utf-8')).hexdigest()
        
        # 添加其他信息
        other_info = {
            "dataset_name": "copa",
            "premise": premise,
            "choice1": choice1,
            "choice2": choice2,
            "question_type": question,
            "original_label": label
        }
        
        formatted_sample = {
            constant.KEY_QUESTION_ID: str(idx),
            constant.KEY_SCENE: scene,
            constant.KEY_QUESTION_TEXT: question_text,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_CATEGORY: "NLI",
            constant.KEY_SUBCATEGORY: "Causal Reasoning",
            constant.KEY_OTHER_INFO: other_info
        }
        
        return formatted_sample


@register_formatter("LCQMCFormatter")
class LCQMCFormatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        # 处理None输入
        if raw_sample is None:
            return None
            
        # 如果输入是列表类型（TSV行数据）- 保持向后兼容
        if isinstance(raw_sample, (list, tuple)):
            return self._format_list(raw_sample)
        
        # 否则，假设输入是字典类型（JSON格式）
        return self._format_dict(raw_sample)
        
    def _format_dict(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        # 提取数据字段 - 支持新的JSON格式
        sentence1 = raw_data.get('sentence1', '').strip()
        sentence2 = raw_data.get('sentence2', '').strip()
        # 支持新格式的gold_label和旧格式的label
        label = str(raw_data.get('gold_label', raw_data.get('label', ''))).strip()
        # 获取ID字段
        sample_id = raw_data.get('ID', raw_data.get('id', ''))
        
        return self._create_formatted_data(sentence1, sentence2, label, sample_id)
    
    def _format_list(self, raw_sample: list) -> Dict[str, Any]:
        # 检查数据格式
        if not isinstance(raw_sample, (list, tuple)) or len(raw_sample) < 3:
            return None
        
        # 提取数据字段
        sentence1 = str(raw_sample[0]).strip() if len(raw_sample) > 0 else ''
        sentence2 = str(raw_sample[1]).strip() if len(raw_sample) > 1 else ''
        label = str(raw_sample[2]).strip() if len(raw_sample) > 2 else ''
        
        return self._create_formatted_data(sentence1, sentence2, label)
    
    def _create_formatted_data(self, sentence1: str, sentence2: str, label: str, sample_id: str = '') -> Dict[str, Any]:
        if not sentence1 or not sentence2 or label not in ['0', '1']:
            return None
        
        # 生成问题ID - 优先使用提供的ID
        if sample_id:
            question_id = f"lcqmc_{sample_id}"
        else:
            question_id = f"lcqmc_{hash(sentence1 + sentence2) % 100000}"
        
        # 构建场景描述
        scene = f"句子1：{sentence1}\n句子2：{sentence2}"
        
        # 构建问题文本
        question_text = "请判断以上两个句子的意图是否相同："
        
        # 构建选项
        options = {
            "A": "相同 - 两个句子表达的意图相同",
            "B": "不同 - 两个句子表达的意图不同"
        }
        
        # 确定正确答案
        correct_answer = "A" if label == "1" else "B"
        
        # 生成哈希值
        hash_content = f"{question_id}_{scene}_{correct_answer}"
        hash_value = hashlib.md5(hash_content.encode('utf-8')).hexdigest()
        
        # 添加其他信息
        other_info = {
            "dataset_name": "lcqmc",
            "sentence1": sentence1,
            "sentence2": sentence2,
            "original_label": label,
            "sample_id": sample_id,
            constant.KEY_HASH: hash_value
        }
        
        formatted_sample = {
            constant.KEY_QUESTION_ID: question_id,
            constant.KEY_SCENE: scene,
            constant.KEY_QUESTION_TEXT: question_text,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_CATEGORY: "LCQMC",
            constant.KEY_SUBCATEGORY: "语义相似度判断",
            constant.KEY_OTHER_INFO: other_info
        }
        
        return formatted_sample


@register_formatter("QQPFormatter")
class QQPFormatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        # 处理None输入
        if raw_sample is None:
            return None
            
        # 如果输入是列表类型（TSV行数据）
        if isinstance(raw_sample, (list, tuple)):
            return self._format_list(raw_sample)
        
        # 否则，假设输入是字典类型
        return self._format_dict(raw_sample)
        
    def _format_dict(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        # 提取数据字段
        question1 = raw_data.get('question1', '').strip()
        question2 = raw_data.get('question2', '').strip()
        is_duplicate = str(raw_data.get('is_duplicate', '')).strip()
        pair_id = raw_data.get('id', '')
        
        return self._create_formatted_data(question1, question2, is_duplicate, pair_id)
    
    def _format_list(self, raw_sample: list) -> Dict[str, Any]:
        # 检查数据格式
        if not isinstance(raw_sample, (list, tuple)) or len(raw_sample) < 6:
            return None
        
        # 提取数据字段 [id, qid1, qid2, question1, question2, is_duplicate]
        pair_id = str(raw_sample[0]).strip() if len(raw_sample) > 0 else ''
        question1 = str(raw_sample[3]).strip() if len(raw_sample) > 3 else ''
        question2 = str(raw_sample[4]).strip() if len(raw_sample) > 4 else ''
        is_duplicate = str(raw_sample[5]).strip() if len(raw_sample) > 5 else ''
        
        return self._create_formatted_data(question1, question2, is_duplicate, pair_id)
    
    def _create_formatted_data(self, question1: str, question2: str, is_duplicate: str, pair_id: str = '') -> Dict[str, Any]:
        if not question1 or not question2 or is_duplicate not in ['0', '1']:
            return None
        
        # 生成问题ID
        question_id = f"qqp_{pair_id}" if pair_id else f"qqp_{hash(question1 + question2) % 100000}"
        
        # 构建场景描述
        scene = f"Question 1: {question1}\nQuestion 2: {question2}"
        
        # 构建问题文本
        question_text = "Please determine whether the above two questions are asking about the same thing:"
        
        # 构建选项
        options = {
            "A": "Duplicate - The two questions are asking about the same thing",
            "B": "Not duplicate - The two questions are asking about different things"
        }
        
        # 确定正确答案
        correct_answer = "A" if is_duplicate == "1" else "B"
        
        # 生成哈希值
        hash_content = f"{question_id}_{scene}_{correct_answer}"
        hash_value = hashlib.md5(hash_content.encode('utf-8')).hexdigest()
        
        # 添加其他信息
        other_info = {
            "dataset_name": "qqp",
            "question1": question1,
            "question2": question2,
            "original_label": is_duplicate
        }
        
        formatted_sample = {
            constant.KEY_QUESTION_ID: question_id,
            constant.KEY_SCENE: scene,
            constant.KEY_QUESTION_TEXT: question_text,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_CATEGORY: "QQP",
            constant.KEY_SUBCATEGORY: "Question Duplicate Detection",
            constant.KEY_OTHER_INFO: other_info
        }
        
        return formatted_sample


@register_formatter("MNLIFormatter")
class MNLIFormatter(BaseFormatter):
    @override
    def format(self, raw_sample: Dict[str, Any]) -> Dict[str, Any]:
        # 处理None输入
        if raw_sample is None:
            return None
            
        # 确保输入是字典类型
        if not isinstance(raw_sample, dict):
            return None
        
        # 提取数据字段
        premise = raw_sample.get('premise', '').strip()
        hypothesis = raw_sample.get('hypothesis', '').strip()
        label = raw_sample.get('label', -1)
        idx = raw_sample.get('idx', 0)
        
        # 验证必要字段
        if not premise or not hypothesis or label not in [0, 1, 2]:
            return None
        
        # 构建场景描述
        scene = f"Premise: {premise}\nHypothesis: {hypothesis}"
        
        # 构建问题文本
        question_text = "Please determine the relationship between the premise and hypothesis:"
        
        # 构建选项
        options = {
            "A": "Entailment - The premise supports the hypothesis",
            "B": "Neutral - The premise is unrelated to the hypothesis", 
            "C": "Contradiction - The premise contradicts the hypothesis"
        }
        
        # 映射标签到答案
        label_to_answer = {0: "A", 1: "B", 2: "C"}
        correct_answer = label_to_answer.get(label, "")
        
        # 生成哈希值
        hash_content = f"{idx}_{premise}_{hypothesis}_{label}"
        hash_value = hashlib.md5(hash_content.encode('utf-8')).hexdigest()
        
        # 添加其他信息
        other_info = {
            "dataset_name": "mnli",
            "premise": premise,
            "hypothesis": hypothesis,
            "original_label": label
        }
        
        formatted_sample = {
            constant.KEY_QUESTION_ID: str(idx),
            constant.KEY_SCENE: scene,
            constant.KEY_QUESTION_TEXT: question_text,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_CATEGORY: "MNLI",
            constant.KEY_SUBCATEGORY: "Natural Language Inference",
            constant.KEY_OTHER_INFO: other_info
        }
        
        return formatted_sample


@register_formatter("RTEFormatter")
class RTEFormatter(BaseFormatter):
    @override
    def format(self, raw_sample: Dict[str, Any]) -> Dict[str, Any]:
        # 处理None输入
        if raw_sample is None:
            return None
            
        # 确保输入是字典类型
        if not isinstance(raw_sample, dict):
            return None
        
        # 提取数据字段
        premise = raw_sample.get('premise', '').strip()
        hypothesis = raw_sample.get('hypothesis', '').strip()
        label = raw_sample.get('label', -1)
        idx = raw_sample.get('idx', 0)
        
        # 验证必要字段
        if not premise or not hypothesis or label not in [0, 1]:
            return None
        
        # 构建场景描述
        scene = f"Premise: {premise}\nHypothesis: {hypothesis}"
        
        # 构建问题文本
        question_text = "Please determine whether the hypothesis can be logically inferred from the premise:"
        
        # 构建选项 - RTE是二分类任务
        options = {
            "A": "Entailment - The hypothesis can be logically inferred from the premise",
            "B": "Not Entailment - The hypothesis cannot be logically inferred from the premise"
        }
        
        # 映射标签到答案
        label_to_answer = {0: "A", 1: "B"}
        correct_answer = label_to_answer.get(label, "")
        
        # 生成哈希值
        hash_content = f"{idx}_{premise}_{hypothesis}_{label}"
        hash_value = hashlib.md5(hash_content.encode('utf-8')).hexdigest()
        
        # 添加其他信息
        other_info = {
            "dataset_name": "rte",
            "premise": premise,
            "hypothesis": hypothesis,
            "original_label": label
        }
        
        formatted_sample = {
            constant.KEY_QUESTION_ID: str(idx),
            constant.KEY_SCENE: scene,
            constant.KEY_QUESTION_TEXT: question_text,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_CATEGORY: "RTE",
            constant.KEY_SUBCATEGORY: "Textual Entailment",
            constant.KEY_OTHER_INFO: other_info
        }
        
        return formatted_sample


@register_formatter("WSCFormatter")
class WSCFormatter(BaseFormatter):
    @override
    def format(self, raw_sample: Dict[str, Any]) -> Dict[str, Any]:
        # 处理None输入
        if raw_sample is None:
            return None
            
        # 确保输入是字典类型
        if not isinstance(raw_sample, dict):
            return None
        
        # 提取数据字段
        text = raw_sample.get('text', '').strip()
        span1_text = raw_sample.get('span1_text', '').strip()  # 指代对象
        span2_text = raw_sample.get('span2_text', '').strip()  # 代词
        span1_index = raw_sample.get('span1_index', 0)  # 单词索引
        span2_index = raw_sample.get('span2_index', 0)  # 单词索引
        label = raw_sample.get('label', -1)  # 0: 不指代, 1: 指代
        idx = raw_sample.get('idx', 0)
        
        # 验证必要字段
        if not text or not span1_text or not span2_text or label not in [0, 1]:
            return None
        
        # 简化场景描述，避免复杂的文本高亮逻辑
        scene = f"Text: {text}\n\nEntity: {span1_text}\nPronoun: {span2_text}"
        
        # 构建问题文本
        question_text = f"Does the pronoun '{span2_text}' refer to '{span1_text}' in the given text?"
        
        # 构建选项 - WSC是二分类任务
        options = {
            "A": f"Yes, '{span2_text}' refers to '{span1_text}'",
            "B": f"No, '{span2_text}' does not refer to '{span1_text}'"
        }
        
        # 映射标签到答案
        label_to_answer = {1: "A", 0: "B"}  # 1表示指代关系成立，0表示不成立
        correct_answer = label_to_answer.get(label, "")
        
        # 生成哈希值
        hash_content = f"{idx}_{text}_{span1_text}_{span2_text}_{label}"
        hash_value = hashlib.md5(hash_content.encode('utf-8')).hexdigest()
        
        # 添加其他信息
        other_info = {
            "dataset_name": "wsc",
            "text": text,
            "span1_text": span1_text,
            "span2_text": span2_text,
            "span1_index": span1_index,
            "span2_index": span2_index,
            "original_label": label
        }
        
        formatted_sample = {
            constant.KEY_QUESTION_ID: str(idx),
            constant.KEY_SCENE: scene,
            constant.KEY_QUESTION_TEXT: question_text,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_CATEGORY: "WSC",
            constant.KEY_SUBCATEGORY: "Coreference Resolution",
            constant.KEY_OTHER_INFO: other_info
        }
        
        return formatted_sample

# 在文件末尾添加CMRCFormatter

@register_formatter("CMRCFormatter")
class CMRCFormatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        if not isinstance(raw_sample, dict):
            return None
        
        # 提取数据字段
        id_val = raw_sample.get('id', '')
        context = str(raw_sample.get('context', '')).strip()
        question = str(raw_sample.get('question', '')).strip()
        answers = raw_sample.get('answers', {})
        
        # 验证必要字段
        if not context or not question or not isinstance(answers, dict):
            return None
        
        # 处理答案文本
        answer_texts = answers.get('text', [])
        if hasattr(answer_texts, 'tolist'):
            answer_texts = answer_texts.tolist()
        elif not isinstance(answer_texts, list):
            answer_texts = [str(answer_texts)] if answer_texts else []
        
        if not answer_texts:
            return None
        
        # 获取第一个有效答案
        correct_answer = ''
        for answer in answer_texts:
            if answer and str(answer).strip():
                correct_answer = str(answer).strip()
                break
        
        if not correct_answer:
            return None
        
        # 生成哈希值
        hash_value = hashlib.sha256(f"{id_val}_{context}_{question}".encode('utf-8')).hexdigest()
        
        # 添加其他信息
        other_info = {
            "dataset_name": "cmrc",
            "original_context": context,
            "original_question": question,
            "original_answers": answers,
            constant.KEY_HASH: hash_value  # 添加这一行
        }
        
        formatted_sample = {
            constant.KEY_QUESTION_ID: str(id_val),
            constant.KEY_SCENE: context,
            constant.KEY_QUESTION_TEXT: question,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_CATEGORY: "NLU",
            constant.KEY_SUBCATEGORY: "阅读理解",
            constant.KEY_OTHER_INFO: other_info
        }
        
        return formatted_sample


@register_formatter("WiCFormatter")
class WiCFormatter(BaseFormatter):
    @override
    def format(self, raw_sample: Dict[str, Any]) -> Dict[str, Any]:
        # 处理None输入
        if raw_sample is None:
            return None
            
        # 确保输入是字典类型
        if not isinstance(raw_sample, dict):
            return None
        
        # 提取数据字段
        word = raw_sample.get('word', '').strip()
        sentence1 = raw_sample.get('sentence1', '').strip()
        sentence2 = raw_sample.get('sentence2', '').strip()
        start1 = raw_sample.get('start1', 0)
        end1 = raw_sample.get('end1', 0)
        start2 = raw_sample.get('start2', 0)
        end2 = raw_sample.get('end2', 0)
        label = raw_sample.get('label', -1)
        idx = raw_sample.get('idx', 0)
        
        # 验证必要字段
        if not word or not sentence1 or not sentence2 or label not in [0, 1]:
            return None
        
        # 构建场景描述 - 突出显示目标词
        highlighted_sentence1 = (sentence1[:start1] + 
                                f"{word}" + 
                                sentence1[end1:])
        highlighted_sentence2 = (sentence2[:start2] + 
                                f"{word}" + 
                                sentence2[end2:])
        
        scene = f"Target word: {word}\n\nSentence 1: {highlighted_sentence1}\nSentence 2: {highlighted_sentence2}"
        
        # 构建问题文本
        question_text = f"Does the word '{word}' have the same meaning in both sentences?"
        
        # 构建选项 - WiC是二分类任务
        options = {
            "A": f"Yes, '{word}' has the same meaning in both sentences",
            "B": f"No, '{word}' has different meanings in the two sentences"
        }
        
        # 映射标签到答案
        label_to_answer = {1: "A", 0: "B"}  # 1表示含义相同，0表示含义不同
        correct_answer = label_to_answer.get(label, "")
        
        # 生成哈希值
        hash_content = f"{idx}_{word}_{sentence1}_{sentence2}_{label}"
        hash_value = hashlib.md5(hash_content.encode('utf-8')).hexdigest()
        
        # 添加其他信息
        other_info = {
            "dataset_name": "wic",
            "word": word,
            "sentence1": sentence1,
            "sentence2": sentence2,
            "start1": start1,
            "end1": end1,
            "start2": start2,
            "end2": end2,
            "original_label": label,
            constant.KEY_HASH: hash_value  # 添加这一行
        }
        
        formatted_sample = {
            constant.KEY_QUESTION_ID: str(idx),
            constant.KEY_SCENE: scene,
            constant.KEY_QUESTION_TEXT: question_text,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_CATEGORY: "WiC",
            constant.KEY_SUBCATEGORY: "Word Sense Disambiguation",
            constant.KEY_OTHER_INFO: other_info
        }
        
        return formatted_sample

@register_formatter("PIQAFormatter")
class PIQAFormatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        goal = raw_sample['goal'].strip()
        sol1 = raw_sample['sol1'].strip()
        sol2 = raw_sample['sol2'].strip()
        label = raw_sample['label'].strip()
        if isinstance(label, str):
            label = int(label.strip())

        scene = f"Goal: {goal}"
        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        options = {
            "A": sol1,
            "B": sol2,
        }

        label_to_answer = {0: "A", 1: "B"}
        correct_answer = label_to_answer.get(label, "")
        
        formatted_sample = {
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }
        return formatted_sample


@register_formatter("MMLU-proFormatter")
class MMLUFormatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        question = raw_sample['question'].strip()
        options = raw_sample['options']
        label = raw_sample['answer_index']
        if isinstance(label, str):
            label = int(label.strip())

        scene = f"Question: {question}"
        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        # options = {
        #     "A": options[0],
        #     "B": options[1],
        #     "C": options[2],
        #     "D": options[3],
        #     "E": options[4],
        #     "F": options[5],
        #     "G": options[6],
        #     "H": options[7],
        #     "I": options[8]
        # }
        options = map_options_to_letters(options)
        keys = list(options.keys())
        correct_answer = keys[label]
        # label_to_answer = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E", 5: "F",6 : "G",7: "H",8 :"I"}
        # correct_answer = label_to_answer.get(label, "")
        
        formatted_sample = {
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }
        return formatted_sample
    

@register_formatter("AGIEvalFormatter")
class AGIEvalFormatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        def map_options_to_letters(options):
            # 生成对应的字母列表，从'A'开始，根据选项数量生成
            letters = [chr(ord('A') + i) for i in range(len(options))]
            # 创建字母到选项的映射字典
            mapped_options = {letter: options[i] for i, letter in enumerate(letters)}
            return mapped_options
        # print(raw_sample)
        question = raw_sample['question'].strip()
        passage = raw_sample['passage']
        options = raw_sample['options']
        label = raw_sample['label']

        # 添加其他信息
        other_info = {}
        excluded_keys = {'question', 'passage', 'options', 'label'}
        other_info = {key: value for key, value in raw_sample.items() if key not in excluded_keys}

        scene = f"Question: {question}"
        if passage:
            scene = f"Passage: {passage}\n" + scene
        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        options = map_options_to_letters(options)
        correct_answer = label
        
        formatted_sample = {
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }
        formatted_sample[constant.KEY_OTHER_INFO] = other_info

        return formatted_sample
    

@register_formatter("CMMLUFormatter")
class CMMLUFormatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        def map_options_to_letters(options):
            # 生成对应的字母列表，从'A'开始，根据选项数量生成
            letters = [chr(ord('A') + i) for i in range(len(options))]
            # 创建字母到选项的映射字典
            mapped_options = {letter: options[i] for i, letter in enumerate(letters)}
            return mapped_options
        # print(raw_sample)
        
        id, question, options1, options2, options3, options4, answer = raw_sample

        scene = f"问题：{question}"
        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        options = map_options_to_letters([options1, options2, options3, options4])
        correct_answer = answer
        
        formatted_sample = {
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }

        return formatted_sample


@register_formatter("CEvalFormatter")
class CEvalFormatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        def map_options_to_letters(options):
            # 生成对应的字母列表，从'A'开始，根据选项数量生成
            letters = [chr(ord('A') + i) for i in range(len(options))]
            # 创建字母到选项的映射字典
            mapped_options = {letter: options[i] for i, letter in enumerate(letters)}
            return mapped_options
        # print(raw_sample)
        id = str(raw_sample['id'])
        question = raw_sample['question'].strip()
        answer = raw_sample['answer']
        options = [raw_sample['A'], raw_sample['B'], raw_sample['C'], raw_sample['D']]
        # 添加其他信息
        other_info = {'id': id}

        scene = f"问题： {question}"
        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        options = map_options_to_letters(options)
        correct_answer = answer
        
        formatted_sample = {
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }
        formatted_sample[constant.KEY_OTHER_INFO] = other_info

        return formatted_sample
    
@register_formatter("FOLIOFormatter")
class FOLIOFormatter(BaseFormatter):
    @override
    def format(self, raw_sample: Dict[str, Any]) -> Dict[str, Any]:
        # 处理None输入
        if raw_sample is None:
            return None
            
        # 确保输入是字典类型
        if not isinstance(raw_sample, dict):
            return None
        
        # 提取数据字段
        premises = raw_sample.get('premises', [])
        premises_fol = raw_sample.get('premises-FOL', [])
        conclusion = raw_sample.get('conclusion', '').strip()
        conclusion_fol = raw_sample.get('conclusion-FOL', '').strip()
        label = raw_sample.get('label', '').strip()
        
        # 验证必要字段
        if not premises or not conclusion or label not in ['True', 'False', 'Uncertain']:
            return None
        
        # 构建场景描述 - 同时展示自然语言和FOL表示
        premises_text = "\n".join([f"{i+1}. {premise.strip()}" for i, premise in enumerate(premises)])
        
        # 如果有FOL表示，也包含进来
        if premises_fol:
            fol_text = "\n".join([f"   FOL: {fol.strip()}" for fol in premises_fol])
            scene = f"Given premises:\n{premises_text}\n\nFormal Logic Representation:\n{fol_text}"
        else:
            scene = f"Given premises:\n{premises_text}"
        
        # 构建问题文本 - 同时包含自然语言和FOL表示
        if conclusion_fol:
            question_text = f"Based on the given premises, what is the logical relationship of the following conclusion?\n\nConclusion: {conclusion}\nFOL: {conclusion_fol}"
        else:
            question_text = f"Based on the given premises, what is the logical relationship of the following conclusion?\n\nConclusion: {conclusion}"
        
        # 构建选项 - FOLIO是三分类任务
        options = {
            "A": "True (The conclusion logically follows from the premises)",
            "B": "False (The conclusion contradicts the premises)", 
            "C": "Uncertain (Cannot be determined from the given premises)"
        }
        
        # 映射标签到答案
        label_to_answer = {"True": "A", "False": "B", "Uncertain": "C"}
        correct_answer = label_to_answer.get(label, "")
        
        # 生成唯一ID（如果没有提供ID字段，使用哈希值）
        question_id = raw_sample.get('id', '')
        if not question_id:
            hash_content = f"{premises_text}_{conclusion}_{label}"
            question_id = hashlib.md5(hash_content.encode('utf-8')).hexdigest()[:8]
        
        # 生成哈希值
        hash_content = f"{question_id}_{premises_text}_{conclusion}_{label}"
        hash_value = hashlib.md5(hash_content.encode('utf-8')).hexdigest()
        
        # 添加其他信息
        other_info = {
            "dataset_name": "folio",
            "premises": premises,
            "premises_fol": premises_fol,
            "conclusion": conclusion,
            "conclusion_fol": conclusion_fol,
            "original_label": label,
            constant.KEY_HASH: hash_value
        }
        
        formatted_sample = {
            constant.KEY_QUESTION_ID: str(question_id),
            constant.KEY_SCENE: scene,
            constant.KEY_QUESTION_TEXT: question_text,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_CATEGORY: "NLI",
            constant.KEY_SUBCATEGORY: "Logical Reasoning",
            constant.KEY_OTHER_INFO: other_info
        }
        
        return formatted_sample


@register_formatter("MutualFormatter")
class MutualFormatter(BaseFormatter):
    @override
    def format(self, raw_sample: Dict[str, Any]) -> Dict[str, Any]:
        # 处理None输入
        if raw_sample is None:
            return None
            
        # 确保输入是字典类型
        if not isinstance(raw_sample, dict):
            return None
        
        # 提取数据字段
        article = raw_sample.get('article', '').strip()
        options = raw_sample.get('options', [])
        answers = raw_sample.get('answers', '').strip()
        sample_id = raw_sample.get('id', '')
        
        # 验证必要字段
        if not article or not options or len(options) != 4 or answers not in ['A', 'B', 'C', 'D']:
            return None
        
        # 构建场景描述
        scene = f"Dialogue Context:\n{article}"
        
        # 构建问题文本
        question_text = "Based on the dialogue context above, which of the following responses is the most logical and coherent continuation?"
        
        # 构建选项字典
        option_dict = {
            "A": options[0],
            "B": options[1], 
            "C": options[2],
            "D": options[3]
        }
        
        # 正确答案
        correct_answer = answers
        
        # 生成哈希值
        hash_content = f"{sample_id}_{article}_{answers}"
        hash_value = hashlib.md5(hash_content.encode('utf-8')).hexdigest()
        
        # 添加其他信息
        other_info = {
            "dataset_name": "mutual",
            "original_article": article,
            "original_options": options,
            "original_answers": answers,
            "sample_id": sample_id,
            constant.KEY_HASH: hash_value
        }
        
        formatted_sample = {
            constant.KEY_QUESTION_ID: str(sample_id),
            constant.KEY_SCENE: scene,
            constant.KEY_QUESTION_TEXT: question_text,
            constant.KEY_OPTIONS: option_dict,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_CATEGORY: "NLI",
            constant.KEY_SUBCATEGORY: "Multi-Turn Dialogue Reasoning",
            constant.KEY_OTHER_INFO: other_info
        }
        
        return formatted_sample



@register_formatter("IMDbFormatter")
class IMDbFormatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        def map_options_to_letters(options):
            # 生成对应的字母列表，从'A'开始，根据选项数量生成
            letters = [chr(ord('A') + i) for i in range(len(options))]
            # 创建字母到选项的映射字典
            mapped_options = {letter: options[i] for i, letter in enumerate(letters)}
            return mapped_options
        # print(raw_sample)
        text = str(raw_sample['text'])
        label = str(raw_sample['label'])
        options = ['Positive', 'Negative']

        # 添加其他信息
        scene = f"text: {text}"
        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        options = map_options_to_letters(options)
        
        label_to_answer = {"1": "A", "0": "B"}
        correct_answer = label_to_answer.get(label, "")
        
        formatted_sample = {
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }

        return formatted_sample


@register_formatter("EmoBenchAFormatter")
class EmoBenchAFormatter(BaseFormatter):
    @override
    def format(self, raw_sample: Dict[str, Any]) -> Dict[str, Any]:
        # 处理None输入
        if raw_sample is None:
            return None
            
        # 确保输入是字典类型
        if not isinstance(raw_sample, dict):
            return None
        
        # 提取数据字段
        qid = raw_sample.get('qid', '').strip()
        language = raw_sample.get('language', '').strip()
        category = raw_sample.get('category', '').strip()
        question_type = raw_sample.get('question type', '').strip()
        scenario = raw_sample.get('scenario', '').strip()
        subject = raw_sample.get('subject', '').strip()
        choices = raw_sample.get('choices', [])
        label = raw_sample.get('label', '').strip()
        
        # 验证必要字段
        if not scenario or not choices or len(choices) != 4 or not label:
            return None
        
        # 验证label是否在choices中
        if label not in choices:
            return None
        
        # 构建场景描述
        scene = f"Scenario: {scenario}"
        if subject:
            scene += f"\n\nSubject: {subject}"
        
        # 构建问题文本
        question_text = "What would be the most appropriate and empathetic action in this situation?"
        
        # 构建选项字典
        option_dict = {
            "A": choices[0],
            "B": choices[1], 
            "C": choices[2],
            "D": choices[3]
        }
        
        # 找到正确答案对应的字母
        correct_answer = ""
        for key, value in option_dict.items():
            if value == label:
                correct_answer = key
                break
        
        # 生成哈希值
        hash_content = f"{qid}_{scenario}_{label}"
        hash_value = hashlib.md5(hash_content.encode('utf-8')).hexdigest()
        
        # 添加其他信息
        other_info = {
            "dataset_name": "emobench_a",
            "qid": qid,
            "language": language,
            "category": category,
            "question_type": question_type,
            "subject": subject,
            "original_choices": choices,
            "original_label": label,
            constant.KEY_HASH: hash_value
        }
        
        formatted_sample = {
            constant.KEY_QUESTION_ID: str(qid),
            constant.KEY_SCENE: scene,
            constant.KEY_QUESTION_TEXT: question_text,
            constant.KEY_OPTIONS: option_dict,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_CATEGORY: "Emotional Intelligence",
            constant.KEY_SUBCATEGORY: "Empathy and Problem Solving",
            constant.KEY_OTHER_INFO: other_info
        }
        
        return formatted_sample


@register_formatter("EmoBenchCFormatter")
class EmoBenchCFormatter(BaseFormatter):
    @override
    def format(self, raw_sample: Dict[str, Any]) -> Dict[str, Any]:
        # 处理None输入
        if raw_sample is None:
            return None
            
        # 确保输入是字典类型
        if not isinstance(raw_sample, dict):
            return None
        
        # 提取数据字段（这次关注cause相关字段）
        qid = raw_sample.get('qid', '').strip()
        language = raw_sample.get('language', '').strip()
        coarse_category = raw_sample.get('coarse_category', '').strip()
        finegrained_category = raw_sample.get('finegrained_category', '').strip()
        scenario = raw_sample.get('scenario', '').strip()
        subject = raw_sample.get('subject', '').strip()
        emotion_label = raw_sample.get('emotion_label', '').strip()  # 作为已知信息
        cause_choices = raw_sample.get('cause_choices', [])
        cause_label = raw_sample.get('cause_label', '').strip()
        
        # 验证必要字段
        if not scenario or not cause_choices or not cause_label or not emotion_label:
            return None
        
        # 验证cause_label是否在cause_choices中
        if cause_label not in cause_choices:
            return None
        
        # 构建场景描述（包含已知情绪）
        scene = f"Scenario: {scenario}"
        if subject:
            scene += f"\n\nSubject: {subject}"
        scene += f"\n\nObserved Emotion: {emotion_label}"
        
        # 构建问题文本
        question_text = "What is the most likely cause of this emotion in the given scenario?"
        
        # 构建选项字典（根据cause_choices的数量动态生成）
        option_dict = {}
        option_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']  # 支持最多8个选项
        
        for i, choice in enumerate(cause_choices):
            if i < len(option_labels):
                option_dict[option_labels[i]] = choice
        
        # 找到正确答案对应的字母
        correct_answer = ""
        for key, value in option_dict.items():
            if value == cause_label:
                correct_answer = key
                break
        
        # 生成哈希值
        hash_content = f"{qid}_{scenario}_{emotion_label}_{cause_label}"
        hash_value = hashlib.md5(hash_content.encode('utf-8')).hexdigest()
        
        # 添加其他信息
        other_info = {
            "dataset_name": "emobench_c",
            "qid": qid,
            "language": language,
            "coarse_category": coarse_category,
            "finegrained_category": finegrained_category,
            "subject": subject,
            "emotion_label": emotion_label,
            "original_cause_choices": cause_choices,
            "original_cause_label": cause_label,
            constant.KEY_HASH: hash_value
        }
        
        formatted_sample = {
            constant.KEY_QUESTION_ID: str(qid),
            constant.KEY_SCENE: scene,
            constant.KEY_QUESTION_TEXT: question_text,
            constant.KEY_OPTIONS: option_dict,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_CATEGORY: "Emotion Cause Recognition",
            constant.KEY_SUBCATEGORY: "Causal Analysis of Emotions",
            constant.KEY_OTHER_INFO: other_info
        }
        
        return formatted_sample


@register_formatter("SST-2Formatter")
class SSTFormatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        def map_options_to_letters(options):
            # 生成对应的字母列表，从'A'开始，根据选项数量生成
            letters = [chr(ord('A') + i) for i in range(len(options))]
            # 创建字母到选项的映射字典
            mapped_options = {letter: options[i] for i, letter in enumerate(letters)}
            return mapped_options
        # print(raw_sample)
        idx = str(raw_sample['idx'])
        sentence = raw_sample['sentence'].strip()
        label = str(raw_sample['label'])
        options = ['Positive', 'Negative']

        # 添加其他信息
        other_info = {'idx': idx}

        scene = f"sentence: {sentence}"
        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        options = map_options_to_letters(options)
        label_to_answer = {"1": "A", "0": "B"}
        correct_answer = label_to_answer.get(label, "")
        
        formatted_sample = {
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }
        formatted_sample[constant.KEY_OTHER_INFO] = other_info

        return formatted_sample


@register_formatter("DianpingFormatter")
class DianpingFormatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        def map_options_to_letters(options):
            # 生成对应的字母列表，从'A'开始，根据选项数量生成
            letters = [chr(ord('A') + i) for i in range(len(options))]
            # 创建字母到选项的映射字典
            mapped_options = {letter: options[i] for i, letter in enumerate(letters)}
            return mapped_options
        # print(raw_sample)
        comment , label, _ = raw_sample
        options = ['正面', '负面']

        scene = f"评论： {comment}"
        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        options = map_options_to_letters(options)
        label_to_answer = {"1": "A", "0": "B"}
        correct_answer = label_to_answer.get(label, "")
        
        formatted_sample = {
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }

        return formatted_sample


@register_formatter("CPEDFormatter")
class CPEDFormatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        def map_options_to_letters(options):
            # 生成对应的字母列表，从'A'开始，根据选项数量生成
            letters = [chr(ord('A') + i) for i in range(len(options))]
            # 创建字母到选项的映射字典
            mapped_options = {letter: options[i] for i, letter in enumerate(letters)}
            return mapped_options
        # print(raw_sample)
        text = raw_sample[-1]
        Emotion = raw_sample[-3]
        options = ["happy", "sad", "angry", "feared", "depressed", "disgusted", "astonished", "worried", "grateful", "relaxed", "neutral", "other-positive", "other-negative"]

        scene = f"文本： {text}"
        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        options = map_options_to_letters(options)

        correct_answer = ''
        for k,v in options.items():
            if v == Emotion:
                correct_answer = k
                break
        
        formatted_sample = {
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }

        return formatted_sample


@register_formatter("EDOSFormatter")
class EDOSFormatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        def map_options_to_letters(options):
            # 生成对应的字母列表，超过Z时从a开始循环
            letters = []
            for i in range(len(options)):
                # 计算偏移量，26个大写字母后切换到小写字母循环
                offset = i % 52  # 52 = 26(大写) + 26(小写)
                if offset < 26:
                    # 大写字母 A-Z
                    letters.append(chr(ord('A') + offset))
                else:
                    # 小写字母 a-z
                    letters.append(chr(ord('a') + (offset - 26)))
            # 创建字母到选项的映射字典
            mapped_options = {letter: options[i] for i, letter in enumerate(letters)}
            return mapped_options
        # print(raw_sample)
        text = raw_sample[9]
        Emotion = raw_sample[10]
        options = ['afraid','angry','annoyed','anticipating','anxious','apprehensive','ashamed','caring',
    'confident','content','devastated','disappointed','disgusted','embarrassed','excited',
    'faithful','furious','grateful','guilty','hopeful','impressed','jealous','joyful',
    'lonely','nostalgic','prepared','proud','sad','sentimental','surprised','terrified',
    'trusting','agreeing','acknowledging','encouraging','consoling','sympathizing',
    'suggesting','questioning','wishing','neutral']

        scene = f"text: {text}"
        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        options = map_options_to_letters(options)

        correct_answer = ''
        for k,v in options.items():
            if v == Emotion:
                correct_answer = k
                break
        
        formatted_sample = {
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }

        return formatted_sample


@register_formatter("SemEval-2018_Task_3Formatter")
class SemEvalFormatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        def map_options_to_letters(options):
            # 生成对应的字母列表，超过Z时从a开始循环
            letters = []
            for i in range(len(options)):
                # 计算偏移量，26个大写字母后切换到小写字母循环
                offset = i % 52  # 52 = 26(大写) + 26(小写)
                if offset < 26:
                    # 大写字母 A-Z
                    letters.append(chr(ord('A') + offset))
                else:
                    # 小写字母 a-z
                    letters.append(chr(ord('a') + (offset - 26)))
            # 创建字母到选项的映射字典
            mapped_options = {letter: options[i] for i, letter in enumerate(letters)}
            return mapped_options
        # print(raw_sample)
        label = raw_sample[0]
        text = raw_sample[1].split('\t')[1]
        options = ['not ironic', 'ironic']

        scene = f"text: {text}"
        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        options = map_options_to_letters(options)

        label_to_answer = {"0": "A", "1": "B"}
        correct_answer = label_to_answer.get(label, "")

        formatted_sample = {
            # constant.KEY_EVALUATION_TOOL:'Accuracy',
            constant.KEY_EVALUATION_TOOL:'F1',
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }

        return formatted_sample

@register_formatter("VUA20Formatter")
class VUA20Formatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        def map_options_to_letters(options):
            # 生成对应的字母列表，超过Z时从a开始循环
            letters = []
            for i in range(len(options)):
                # 计算偏移量，26个大写字母后切换到小写字母循环
                offset = i % 52  # 52 = 26(大写) + 26(小写)
                if offset < 26:
                    # 大写字母 A-Z
                    letters.append(chr(ord('A') + offset))
                else:
                    # 小写字母 a-z
                    letters.append(chr(ord('a') + (offset - 26)))
            # 创建字母到选项的映射字典
            mapped_options = {letter: options[i] for i, letter in enumerate(letters)}
            return mapped_options
        # print(raw_sample)
        sentence = raw_sample[2]
        w_index = raw_sample[-1]
        POS = raw_sample[-3]
        FGPOS = raw_sample[-2]
        label = raw_sample[1]

        question_text = f"Pay attention to the word at position {w_index} in the sentence, which has the part-of-speech {POS} (fine-grained POS: {FGPOS}). Is this word used in a metaphorical way in the sentence?"
        options = ['Yes (metaphorical use)', 'No (non-metaphorical use)']
        scene = f"{sentence}"

        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        options = map_options_to_letters(options)

        label_to_answer = {"1": "A", "0": "B"}
        correct_answer = label_to_answer.get(label, "")

        formatted_sample = {
            constant.KEY_QUESTION_TEXT: question_text,
            # constant.KEY_EVALUATION_TOOL:'Accuracy',
            constant.KEY_EVALUATION_TOOL:'F1',
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }

        return formatted_sample


@register_formatter("PQEmotion1Formatter")
class PQEmotion1Formatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        def map_options_to_letters(options):
            # 生成对应的字母列表，超过Z时从a开始循环
            letters = []
            for i in range(len(options)):
                # 计算偏移量，26个大写字母后切换到小写字母循环
                offset = i % 52  # 52 = 26(大写) + 26(小写)
                if offset < 26:
                    # 大写字母 A-Z
                    letters.append(chr(ord('A') + offset))
                else:
                    # 小写字母 a-z
                    letters.append(chr(ord('a') + (offset - 26)))
            # 创建字母到选项的映射字典
            mapped_options = {letter: options[i] for i, letter in enumerate(letters)}
            return mapped_options
        # print(raw_sample)
        idx = raw_sample[0]
        text = raw_sample[1]
        label = raw_sample[-3]


        exclude_indices = {
            0,  # 第0个元素
            1,  # 第1个元素
            len(raw_sample)-1,  # -1对应的正索引
            len(raw_sample)-2,  # -2对应的正索引
            len(raw_sample)-3   # -3对应的正索引
        }
        options = [raw_sample[i] for i in range(len(raw_sample)) if i not in exclude_indices]

        scene = f"场景：{text}"
        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        options = map_options_to_letters(options)
        correct_answer = label

        formatted_sample = {
            # constant.KEY_QUESTION_TEXT: question_text,
            # constant.KEY_EVALUATION_TOOL:'Accuracy',
            constant.KEY_EVALUATION_TOOL:'F1',
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }

        return formatted_sample



@register_formatter("PQEmotion2Formatter")
class PQEmotion2Formatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        def map_options_to_letters(options):
            # 生成对应的字母列表，超过Z时从a开始循环
            letters = []
            for i in range(len(options)):
                # 计算偏移量，26个大写字母后切换到小写字母循环
                offset = i % 52  # 52 = 26(大写) + 26(小写)
                if offset < 26:
                    # 大写字母 A-Z
                    letters.append(chr(ord('A') + offset))
                else:
                    # 小写字母 a-z
                    letters.append(chr(ord('a') + (offset - 26)))
            # 创建字母到选项的映射字典
            mapped_options = {letter: options[i] for i, letter in enumerate(letters)}
            return mapped_options
        # print(raw_sample)
        idx = raw_sample[0]
        text = raw_sample[1]
        label = raw_sample[-3]


        exclude_indices = {
            0,  # 第0个元素
            1,  # 第1个元素
            len(raw_sample)-1,  # -1对应的正索引
            len(raw_sample)-2,  # -2对应的正索引
            len(raw_sample)-3   # -3对应的正索引
        }
        options = [raw_sample[i] for i in range(len(raw_sample)) if i not in exclude_indices]

        scene = f"场景：{text}"
        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        options = map_options_to_letters(options)
        correct_answer = label

        formatted_sample = {
            # constant.KEY_QUESTION_TEXT: question_text,
            # constant.KEY_EVALUATION_TOOL:'Accuracy',
            constant.KEY_EVALUATION_TOOL:'F1',
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }

        return formatted_sample


@register_formatter("PQEmotion3Formatter")
class PQEmotion3Formatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        def map_options_to_letters(options):
            # 生成对应的字母列表，超过Z时从a开始循环
            letters = []
            for i in range(len(options)):
                # 计算偏移量，26个大写字母后切换到小写字母循环
                offset = i % 52  # 52 = 26(大写) + 26(小写)
                if offset < 26:
                    # 大写字母 A-Z
                    letters.append(chr(ord('A') + offset))
                else:
                    # 小写字母 a-z
                    letters.append(chr(ord('a') + (offset - 26)))
            # 创建字母到选项的映射字典
            mapped_options = {letter: options[i] for i, letter in enumerate(letters)}
            return mapped_options
        # print(raw_sample)
        idx = raw_sample[0]
        text = raw_sample[1]
        label = raw_sample[-3]


        exclude_indices = {
            0,  # 第0个元素
            1,  # 第1个元素
            len(raw_sample)-1,  # -1对应的正索引
            len(raw_sample)-2,  # -2对应的正索引
            len(raw_sample)-3   # -3对应的正索引
        }
        options = [raw_sample[i] for i in range(len(raw_sample)) if i not in exclude_indices]

        scene = f"场景：{text}"
        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        options = map_options_to_letters(options)
        correct_answer = label

        formatted_sample = {
            # constant.KEY_QUESTION_TEXT: question_text,
            # constant.KEY_EVALUATION_TOOL:'Accuracy',
            constant.KEY_EVALUATION_TOOL:'F1',
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }

        return formatted_sample



@register_formatter("PQEmotion4Formatter")
class PQEmotion4Formatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        def map_options_to_letters(options):
            # 生成对应的字母列表，超过Z时从a开始循环
            letters = []
            for i in range(len(options)):
                # 计算偏移量，26个大写字母后切换到小写字母循环
                offset = i % 52  # 52 = 26(大写) + 26(小写)
                if offset < 26:
                    # 大写字母 A-Z
                    letters.append(chr(ord('A') + offset))
                else:
                    # 小写字母 a-z
                    letters.append(chr(ord('a') + (offset - 26)))
            # 创建字母到选项的映射字典
            mapped_options = {letter: options[i] for i, letter in enumerate(letters)}
            return mapped_options
        # print(raw_sample)
        idx = raw_sample[0]
        text = raw_sample[1]
        label = raw_sample[-2]


        exclude_indices = {
            0,  # 第0个元素
            1,  # 第1个元素
            len(raw_sample)-1,  # -1对应的正索引
            len(raw_sample)-2,  # -2对应的正索引
        }
        options = [raw_sample[i] for i in range(len(raw_sample)) if i not in exclude_indices]

        scene = f"场景：{text}"
        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        options = map_options_to_letters(options)
        correct_answer = label

        formatted_sample = {
            # constant.KEY_QUESTION_TEXT: question_text,
            # constant.KEY_EVALUATION_TOOL:'Accuracy',
            constant.KEY_EVALUATION_TOOL:'F1',
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }

        return formatted_sample


@register_formatter("PQEmotion5Formatter")
class PQEmotion5Formatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        def map_options_to_letters(options):
            # 生成对应的字母列表，超过Z时从a开始循环
            letters = []
            for i in range(len(options)):
                # 计算偏移量，26个大写字母后切换到小写字母循环
                offset = i % 52  # 52 = 26(大写) + 26(小写)
                if offset < 26:
                    # 大写字母 A-Z
                    letters.append(chr(ord('A') + offset))
                else:
                    # 小写字母 a-z
                    letters.append(chr(ord('a') + (offset - 26)))
            # 创建字母到选项的映射字典
            mapped_options = {letter: options[i] for i, letter in enumerate(letters)}
            return mapped_options
        # print(raw_sample)
        idx = raw_sample[0]
        text = raw_sample[1]
        label = raw_sample[-2]

        exclude_indices = {
            0,  # 第0个元素
            1,  # 第1个元素
            len(raw_sample)-1,  # -1对应的正索引
            len(raw_sample)-2,  # -2对应的正索引
        }
        options = [raw_sample[i] for i in range(len(raw_sample)) if i not in exclude_indices]

        scene = f"场景：{text}"
        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        options = map_options_to_letters(options)
        correct_answer = label

        formatted_sample = {
            # constant.KEY_QUESTION_TEXT: question_text,
            # constant.KEY_EVALUATION_TOOL:'Accuracy',
            constant.KEY_EVALUATION_TOOL:'F1',
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }

        return formatted_sample


@register_formatter("LogicNLIFormatter")
class LogicNLIFormatter(BaseFormatter):
    @override
    def format(self, raw_sample: Dict[str, Any]) -> List[Dict[str, Any]]:
        # 处理None输入
        if raw_sample is None:
            return []
            
        # 确保输入是字典类型
        if not isinstance(raw_sample, dict):
            return []
        
        # 提取数据字段
        facts = raw_sample.get('facts', [])
        rules = raw_sample.get('rules', [])
        statements = raw_sample.get('statements', [])
        labels = raw_sample.get('labels', [])
        
        # 验证必要字段
        if not facts or not rules or not statements or not labels:
            return []
            
        # 验证statements和labels数量一致
        if len(statements) != len(labels):
            return []
        
        # 为每个statement-label对创建一个样本
        formatted_samples = []
        
        for i, (statement, label) in enumerate(zip(statements, labels)):
            # 验证标签是否有效
            if label not in ['entailment', 'contradiction', 'neutral', 'self_contradiction']:
                continue
            
            # 构建场景描述
            facts_text = "\n".join([f"{j+1}. {fact.strip()}" for j, fact in enumerate(facts)])
            rules_text = "\n".join([f"{j+1}. {rule.strip()}" for j, rule in enumerate(rules)])
            
            scene = f"Given Facts:\n{facts_text}\n\nGiven Rules:\n{rules_text}"
            
            # 构建问题文本
            question_text = f"Based on the given facts and rules, what is the logical relationship of the following statement?\n\nStatement: {statement.strip()}"
            
            # 构建选项 - LogicNLI是四分类任务
            options = {
                "A": "Entailment (The statement logically follows from the facts and rules)",
                "B": "Contradiction (The statement contradicts the facts and rules)", 
                "C": "Neutral (Cannot be determined from the given facts and rules)",
                "D": "Self-contradiction (The facts and rules themselves are contradictory)"
            }
            
            # 映射标签到答案
            label_to_answer = {
                "entailment": "A", 
                "contradiction": "B", 
                "neutral": "C",
                "self_contradiction": "D"
            }
            correct_answer = label_to_answer.get(label, "")
            
            # 生成唯一ID
            question_id = f"{raw_sample.get('id', 'unknown')}_{i}"
            
            # 生成哈希值
            hash_content = f"{question_id}_{facts_text}_{rules_text}_{statement}_{label}"
            hash_value = hashlib.md5(hash_content.encode('utf-8')).hexdigest()
            
            # 添加其他信息
            other_info = {
                "dataset_name": "logic_nli",
                "facts": facts,
                "rules": rules,
                "statement": statement,
                "original_label": label,
                "statement_index": i,
                constant.KEY_HASH: hash_value
            }
            
            formatted_sample = {
                constant.KEY_QUESTION_ID: str(question_id),
                constant.KEY_SCENE: scene,
                constant.KEY_QUESTION_TEXT: question_text,
                constant.KEY_OPTIONS: options,
                constant.KEY_CORRECT_ANSWER: correct_answer,
                constant.KEY_CATEGORY: "NLI",
                constant.KEY_SUBCATEGORY: "Logical Reasoning",
                constant.KEY_OTHER_INFO: other_info
            }
            
            formatted_samples.append(formatted_sample)
        
        # 返回所有格式化的样本
        return formatted_samples


@register_formatter("BookSortFormatter")
class BookSortFormatter(BaseFormatter):
    @override
    def format(self, raw_sample: Dict[str, Any]) -> Dict[str, Any]:
        # 处理None输入
        if raw_sample is None:
            return None
            
        # 确保输入是字典类型
        if not isinstance(raw_sample, dict):
            return None
        
        # 提取数据字段
        segment_1 = raw_sample.get('segment_1', '').strip()
        segment_2 = raw_sample.get('segment_2', '').strip()
        present_seg1_first = raw_sample.get('present_seg1_first', -1)
        excerpt_text = raw_sample.get('excerpt_text', '').strip()
        book_title = raw_sample.get('book_title', '').strip()
        segment_length = raw_sample.get('segment_length', 0)
        excerpt_length = raw_sample.get('excerpt_length', 0)
        distance_bin = raw_sample.get('distance_bin', 0)
        
        # 验证必要字段
        if not segment_1 or not segment_2 or present_seg1_first not in [0, 1]:
            return None
        
        # 构建场景描述
        scene = f"Book: {book_title}\n\nContext Excerpt:\n{excerpt_text}\n\nTwo text segments to analyze:"
        scene += f"\nSegment 1: {segment_1}"
        scene += f"\nSegment 2: {segment_2}"
        
        # 构建问题文本
        question_text = "Based on the context excerpt, which segment appears first in the original text?"
        
        # 构建选项 - 这是二分类任务
        options = {
            "A": "Segment 1 appears first",
            "B": "Segment 2 appears first"
        }
        
        # 映射标签到答案
        # present_seg1_first = 1 表示segment_1在原文中先出现
        # present_seg1_first = 0 表示segment_2在原文中先出现
        correct_answer = "A" if present_seg1_first == 1 else "B"
        
        # 生成唯一ID
        question_id = f"{raw_sample.get('book_idx', 0)}_{raw_sample.get('excerpt_idx', 0)}_{raw_sample.get('segment_idx', 0)}"
        
        # 生成哈希值
        hash_content = f"{question_id}_{segment_1}_{segment_2}_{present_seg1_first}"
        hash_value = hashlib.md5(hash_content.encode('utf-8')).hexdigest()
        
        # 添加其他信息
        other_info = {
            "dataset_name": "booksort",
            "book_title": book_title,
            "segment_1": segment_1,
            "segment_2": segment_2,
            "excerpt_text": excerpt_text,
            "segment_length": segment_length,
            "excerpt_length": excerpt_length,
            "distance_bin": distance_bin,
            "original_label": present_seg1_first,
            constant.KEY_HASH: hash_value
        }
        
        formatted_sample = {
            constant.KEY_QUESTION_ID: str(question_id),
            constant.KEY_SCENE: scene,
            constant.KEY_QUESTION_TEXT: question_text,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_CATEGORY: "Reading Comprehension",
            constant.KEY_SUBCATEGORY: "Text Sequence Understanding",
            constant.KEY_OTHER_INFO: other_info
        }
        
        return formatted_sample


@register_formatter("MultiRCFormatter")
class MultiRCFormatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        def map_options_to_letters(options):
            # 生成对应的字母列表，超过Z时从a开始循环
            letters = []
            for i in range(len(options)):
                # 计算偏移量，26个大写字母后切换到小写字母循环
                offset = i % 52  # 52 = 26(大写) + 26(小写)
                if offset < 26:
                    # 大写字母 A-Z
                    letters.append(chr(ord('A') + offset))
                else:
                    # 小写字母 a-z
                    letters.append(chr(ord('a') + (offset - 26)))
            # 创建字母到选项的映射字典
            mapped_options = {letter: options[i] for i, letter in enumerate(letters)}
            return mapped_options
        
        options = []
        labels = []
        paragraph = raw_sample[0]['paragraph']
        question = raw_sample[0]['question']
        for item in raw_sample:
            options.append(item['answer'])
            labels.append(str(item['label']))

        scene = f"paragraph: {paragraph} \n question: {question}"
        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        options = map_options_to_letters(options)

        correct_answer = []
        keys = list(options.keys())
        for index, label in enumerate(labels):
            if label == '1':
                correct_answer.append(keys[index])

        formatted_sample = {
            # constant.KEY_QUESTION_TEXT: question_text,
            constant.KEY_EVALUATION_TOOL:'F1,em',
            # constant.KEY_EVALUATION_TOOL:'F1',
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }

        return formatted_sample

@register_formatter("ReCoRDFormatter")
class ReCoRDFormatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        def map_options_to_letters(options):
            # 生成对应的字母列表，超过Z时从a开始循环
            letters = []
            for i in range(len(options)):
                # 计算偏移量，26个大写字母后切换到小写字母循环
                offset = i % 52  # 52 = 26(大写) + 26(小写)
                if offset < 26:
                    # 大写字母 A-Z
                    letters.append(chr(ord('A') + offset))
                else:
                    # 小写字母 a-z
                    letters.append(chr(ord('a') + (offset - 26)))
            # 创建字母到选项的映射字典
            mapped_options = {letter: options[i] for i, letter in enumerate(letters)}
            return mapped_options
        # print(raw_sample)
        passage = raw_sample['passage']
        query = raw_sample['query']
        options = raw_sample['entities']
        answers = raw_sample['answers']

        scene = f"passage:{passage} \n Statement to complete: {query}"
        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        options = map_options_to_letters(options)
        correct_answer = []
        for answer in answers:
            for k,v in options.items():
                if v == answer:
                    correct_answer.append(k)
                    break
        correct_answer = sorted(correct_answer)

        formatted_sample = {
            # constant.KEY_QUESTION_TEXT: question_text,
            # constant.KEY_EVALUATION_TOOL:'Accuracy',
            constant.KEY_EVALUATION_TOOL:'F1,em',
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }

        return formatted_sample


@register_formatter("THUCNewsFormatter")
class THUCNewsFormatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        def map_options_to_letters(options):
            # 生成对应的字母列表，超过Z时从a开始循环
            letters = []
            for i in range(len(options)):
                # 计算偏移量，26个大写字母后切换到小写字母循环
                offset = i % 52  # 52 = 26(大写) + 26(小写)
                if offset < 26:
                    # 大写字母 A-Z
                    letters.append(chr(ord('A') + offset))
                else:
                    # 小写字母 a-z
                    letters.append(chr(ord('a') + (offset - 26)))
            # 创建字母到选项的映射字典
            mapped_options = {letter: options[i] for i, letter in enumerate(letters)}
            return mapped_options
        # print(raw_sample)
        text = raw_sample['text']
        options = ['education', 'entertainment', 'fashion', 'finance', 'game', 'politic', 'society', 'sport', 'stock', 'technology']
        label = options[int(raw_sample['label'])]

        scene = f"文本：{text}"
        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        options = map_options_to_letters(options)
        for k, v in options.items():
            if v == label:
                correct_answer = k
                break

        formatted_sample = {
            # constant.KEY_QUESTION_TEXT: question_text,
            # constant.KEY_EVALUATION_TOOL:'Accuracy',
            constant.KEY_EVALUATION_TOOL:'Accuracy,F1',
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }

        return formatted_sample

@register_formatter("GoEmotionsFormatter")
class GoEmotionsFormatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        def map_options_to_letters(options):
            # 生成对应的字母列表，超过Z时从a开始循环
            letters = []
            for i in range(len(options)):
                # 计算偏移量，26个大写字母后切换到小写字母循环
                offset = i % 52  # 52 = 26(大写) + 26(小写)
                if offset < 26:
                    # 大写字母 A-Z
                    letters.append(chr(ord('A') + offset))
                else:
                    # 小写字母 a-z
                    letters.append(chr(ord('a') + (offset - 26)))
            # 创建字母到选项的映射字典
            mapped_options = {letter: options[i] for i, letter in enumerate(letters)}
            return mapped_options
        # print(raw_sample)
        options = raw_sample[0]
        sample = raw_sample[1]
        text = sample[0]
        labels = sample[1].split(',')
        ans = []
        for label in labels:
            ans.append(options[int(label)])

        scene = f"text: {text}"
        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        options = map_options_to_letters(options)

        correct_answer = []
        for label in ans:
            for k,v in options.items():
                if v == label:
                    correct_answer.append(k)
                    break

        formatted_sample = {
            # constant.KEY_QUESTION_TEXT: question_text,
            # constant.KEY_EVALUATION_TOOL:'F1',
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }

        return formatted_sample
    

@register_formatter("SafetyBench1Formatter")
@register_formatter("SafetyBench2Formatter")
@register_formatter("SafetyBench3Formatter")
@register_formatter("SafetyBench4Formatter")
@register_formatter("SafetyBench5Formatter")
@register_formatter("SafetyBench6Formatter")
@register_formatter("SafetyBench7Formatter")
class SafetyBenchFormatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        def map_options_to_letters(options):
            # 生成对应的字母列表，超过Z时从a开始循环
            letters = []
            for i in range(len(options)):
                # 计算偏移量，26个大写字母后切换到小写字母循环
                offset = i % 52  # 52 = 26(大写) + 26(小写)
                if offset < 26:
                    # 大写字母 A-Z
                    letters.append(chr(ord('A') + offset))
                else:
                    # 小写字母 a-z
                    letters.append(chr(ord('a') + (offset - 26)))
            # 创建字母到选项的映射字典
            mapped_options = {letter: options[i] for i, letter in enumerate(letters)}
            return mapped_options
        # print(raw_sample)
        question = raw_sample['question']
        options = raw_sample['options']
        label = int(raw_sample['answer'])

        scene = f"question: {question}"
        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        options = map_options_to_letters(options)
        correct_answer = list(options.keys())[label]

        formatted_sample = {
            # constant.KEY_QUESTION_TEXT: question_text,
            # constant.KEY_EVALUATION_TOOL:'F1',
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }

        return formatted_sample

@register_formatter("liangbiaoFormatter")
@register_formatter("liangbiao1Formatter")
@register_formatter("liangbiao2Formatter")
@register_formatter("liangbiao8Formatter")
@register_formatter("liangbiao9Formatter")
class liangbiaoFormatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        # print(raw_sample)
        Question = raw_sample['Question']
        options = raw_sample['Choices']
        Score = raw_sample['Score']

        scene = f"问题： {Question}"
        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        options = map_options_to_letters(options)
        correct_answer = {}
        keys = list(options.keys())
        for index, key in enumerate(keys):
            correct_answer[key] = Score[index]
            

        formatted_sample = {
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }

        return formatted_sample


# @register_formatter("TruthfulQA2Formatter")
# class TruthfulQA2Formatter(BaseFormatter):
#     @override
#     def format(self, raw_sample) -> Dict[str, Any]:
#         print(raw_sample)
#         Type = raw_sample[0]
#         Category = raw_sample[1]
#         Question = raw_sample[2]
#         Best_Answer = raw_sample[3]
#         Correct_Answers = raw_sample[4]
#         Incorrect_Answers = raw_sample[5]
#         Source = raw_sample[6]

#         Question = raw_sample['Question']
#         options = raw_sample['Choices']
#         Score = raw_sample['Score']

#         scene = f"问题： {Question}"
#         hash_value = hashlib.sha256(scene.encode('utf-8'))
#         hash_value = hash_value.hexdigest()

#         options = map_options_to_letters(options)
#         correct_answer = {}
#         keys = list(options.keys())
#         for index, key in enumerate(keys):
#             correct_answer[key] = Score[index]
            

#         formatted_sample = {
#             constant.KEY_QUESTION_ID:hash_value,
#             constant.KEY_SCENE: scene,
#             constant.KEY_OPTIONS: options,
#             constant.KEY_CORRECT_ANSWER: correct_answer,
#             constant.KEY_OTHER_INFO: {}
#         }

#         return formatted_sample


@register_formatter("SemEval-2018_Task_1Formatter")
class SemEval2018Task1Formatter(BaseFormatter):
    @override
    def format(self, raw_sample) -> Dict[str, Any]:
        # print(raw_sample)
        text = raw_sample['text']
        emotion, label = raw_sample['emotion']

        scene = f"text: {text}"
        hash_value = hashlib.sha256(scene.encode('utf-8'))
        hash_value = hash_value.hexdigest()

        options = [emotion, f'not {emotion}']

        options = map_options_to_letters(options)
        if label == '1':
            correct_answer = 'A'
        else:
            correct_answer = 'B'

        formatted_sample = {
            # constant.KEY_QUESTION_TEXT: question_text,
            # constant.KEY_EVALUATION_TOOL:'Accuracy',
            constant.KEY_QUESTION_ID:hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_OTHER_INFO: {}
        }

        return formatted_sample


@register_formatter("BBQFormatter")
class BBQFormatter(BaseFormatter):
    """
    处理来自 BBQ (Bias Benchmark for Question Answering) 数据集的原始数据。
    输入是一个字典，格式为: {"context": ..., "question": ..., "ans0": ..., "ans1": ..., "ans2": ..., "label": ...}
    """
    @override
    def format(self, raw_sample: Dict[str, Any]) -> Dict[str, Any]:
        # 1. 验证和解析输入
        if not isinstance(raw_sample, dict):
            return None
        
        context = raw_sample.get('context', '').strip()
        question = raw_sample.get('question', '').strip()
        label = raw_sample.get('label') # label可以是整数0, 1, 2

        ans0 = raw_sample.get('ans0', '').strip()
        ans1 = raw_sample.get('ans1', '').strip()
        ans2 = raw_sample.get('ans2', '').strip()
        
        # 2. 验证必要字段
        if not context or not question or label is None or not ans0 or not ans1 or not ans2:
            return None

        # 3. 构建标准化的样本结构
        
        # 'scene' 字段是上下文
        scene = context
        
        # 'question_text' 字段是问题
        question_text = question
        
        # 'options' 字段定义了所有选项
        options = {
            "A": ans0,
            "B": ans1, 
            "C": ans2
        }
        
        # 将数字标签 (0, 1, 2) 映射到对应的选项字母 (A, B, C)
        label_to_answer = {0: "A", 1: "B", 2: "C"}
        correct_answer = label_to_answer.get(int(label))
        
        if correct_answer is None:
            return None # 如果label无效，则跳过此样本

        # 生成一个唯一的ID，用于追踪
        # 使用 context + question 的哈希值确保唯一性
        hash_content = f"{context}{question}"
        hash_value = hashlib.sha256(hash_content.encode('utf-8')).hexdigest()
        
        # 组装最终的字典
        formatted_sample = {
            constant.KEY_QUESTION_ID: hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_QUESTION_TEXT: question_text,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_CATEGORY: raw_sample.get("category", "BBQ"), # 使用原始的category字段
            constant.KEY_OTHER_INFO: { # 存放原始数据以便调试
                "original_label": label,
                "context_condition": raw_sample.get("context_condition"),
                "question_polarity": raw_sample.get("question_polarity")
            }
        }
        
        return formatted_sample

@register_formatter("StereoSetFormatter")
class StereoSetFormatter(BaseFormatter):
    @override
    def format(self, raw_sample: Dict[str, Any]) -> Dict[str, Any]:
        # (前面的代码保持不变)
        # 1. 验证和解析输入
        if not isinstance(raw_sample, dict):
            return None
        context = raw_sample.get('context', '').strip()
        sentences = raw_sample.get('sentences', [])
        if not context or not sentences or len(sentences) != 3:
            return None

        # 2. 梳理三个选项
        stereotype_sent, anti_stereotype_sent, unrelated_sent = None, None, None
        for sent_info in sentences:
            label = sent_info.get("gold_label")
            if label == "stereotype":
                stereotype_sent = sent_info.get("sentence", "").strip()
            elif label == "anti-stereotype":
                anti_stereotype_sent = sent_info.get("sentence", "").strip()
            elif label == "unrelated":
                unrelated_sent = sent_info.get("sentence", "").strip()
        if not all([stereotype_sent, anti_stereotype_sent, unrelated_sent]):
            return None

        # 3. 构建标准化的样本结构
        scene = context
        # 【修改点】我们不再使用这个通用的问题，而是让Prompt来定义
        # question_text = "..." 
        
        options = {
            "A": stereotype_sent,
            "B": anti_stereotype_sent,
            "C": unrelated_sent
        }
        
        correct_answer = "B" # 保持将“反刻板印象”作为正确答案的设定
        
        hash_content = f"{context}{stereotype_sent}{anti_stereotype_sent}"
        hash_value = hashlib.sha256(hash_content.encode('utf-8')).hexdigest()
        
        formatted_sample = {
            constant.KEY_QUESTION_ID: raw_sample.get("id", hash_value),
            constant.KEY_SCENE: scene,
            # 【新增】将bias_type明确传递出去
            "bias_type": raw_sample.get("bias_type", "general social"), 
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_CATEGORY: raw_sample.get("bias_type", "StereoSet"),
            constant.KEY_OTHER_INFO: { "target": raw_sample.get("target") }
        }
        
        return formatted_sample


@register_formatter("CrowS-PairsFormatter")
class CrowSPairsFormatter(BaseFormatter):
    """
    处理来自 CrowS-Pairs 数据集的原始数据。
    【版本3: 修正了正确答案的判断逻辑】
    """
    @override
    def format(self, raw_sample: List[str]) -> Dict[str, Any]:
        # 1. 验证和解析输入
        if not isinstance(raw_sample, list) or len(raw_sample) < 5:
            return None

        try:
            sent_more = raw_sample[1].strip()      # 句子1 (关于弱势群体)
            sent_less = raw_sample[2].strip()      # 句子2 (关于优势群体)
            stereo_type = raw_sample[3].strip()    # 偏见方向 ('stereo' 或 'antistereo')
            bias_type = raw_sample[4].strip()      # 偏见类型
        except IndexError:
            return None

        if not sent_more or not sent_less or not bias_type or stereo_type not in ['stereo', 'antistereo']:
            return None

        # 2. 【不再随机】采用固定的选项分配方式
        options = {
            "A": sent_more,
            "B": sent_less
        }
        
        # 3. 【关键修正】根据 stereo_type 动态确定正确答案
        correct_answer = ""
        if stereo_type == 'stereo':
            # 如果句子A是刻板印象，那么我们期望模型选择更中立的句子B
            correct_answer = "B"
        elif stereo_type == 'antistereo':
            # 如果句子A本身就是反刻板印象，那么它就是我们期望模型选择的句子
            correct_answer = "A"

        if not correct_answer:
            return None

        # 4. 构建标准化的样本结构
        scene = "" 
        question_text = "" # question_text 将完全由 prompt 定义
        
        hash_content = f"{sent_more}{sent_less}"
        hash_value = hashlib.sha256(hash_content.encode('utf-8')).hexdigest()
        
        formatted_sample = {
            constant.KEY_QUESTION_ID: hash_value,
            constant.KEY_SCENE: scene,
            constant.KEY_QUESTION_TEXT: question_text,
            "bias_type": bias_type,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_CATEGORY: bias_type,
            constant.KEY_OTHER_INFO: {
                "stereo_antistereo_type": stereo_type
            }
        }
        
        return formatted_sample


@register_formatter("ESConvFormatter")
class ESConvFormatter(BaseFormatter):
    @override
    def format(self, raw_sample: Dict[str, Any]) -> Dict[str, Any]:
        # Handle None input
        if raw_sample is None:
            return None
            
        # Ensure input is dictionary type
        if not isinstance(raw_sample, dict):
            return None
            
        # Extract data fields
        conversation_id = raw_sample.get('conversation_id', 0)
        turn_id = raw_sample.get('turn_id', 0)
        situation = raw_sample.get('situation', '').strip()
        emotion_type = raw_sample.get('emotion_type', '').strip()
        problem_type = raw_sample.get('problem_type', '').strip()
        experience_type = raw_sample.get('experience_type', '').strip()
        dialog_history = raw_sample.get('dialog_history', [])
        strategy = raw_sample.get('strategy', '').strip()
        supporter_response = raw_sample.get('supporter_response', '').strip()
        survey_score = raw_sample.get('survey_score', {})
        
        # Validate required fields
        if not situation or not emotion_type or not strategy or not supporter_response:
            return None
            
        # Build dialog history text
        dialog_text = ""
        if dialog_history:
            dialog_lines = []
            for turn in dialog_history:
                speaker = turn.get('speaker', '')
                content = turn.get('content', '').strip()
                if speaker and content:
                    role = "Help-seeker" if speaker == "seeker" else "Supporter"
                    dialog_lines.append(f"{role}: {content}")
            dialog_text = "\n".join(dialog_lines)
            
        # Build scene description
        scene_parts = []
        scene_parts.append(f"Situation Description: {situation}")
        scene_parts.append(f"Emotion Type: {emotion_type}")
        scene_parts.append(f"Problem Type: {problem_type}")
        scene_parts.append(f"Experience Type: {experience_type}")
        
        if dialog_text:
            scene_parts.append(f"\nDialogue History:\n{dialog_text}")
            
        scene = "\n".join(scene_parts)
        
        # Build question text - 使用具体策略而不是通用提示
        question_text = f"Based on the above situation and dialogue history, please use the '{strategy}' strategy to provide a one-sentence emotional support response for the help-seeker."
        
        # Generate unique ID
        question_id = f"esconv_{conversation_id}_{turn_id}"
        
        # Generate hash value
        hash_content = f"{question_id}_{situation}_{strategy}_{supporter_response}"
        hash_value = hashlib.md5(hash_content.encode('utf-8')).hexdigest()
        
        # Add other information
        other_info = {
            "dataset_name": "esconv",
            "conversation_id": conversation_id,
            "turn_id": turn_id,
            "strategy": strategy,
            "emotion_type": emotion_type,
            "problem_type": problem_type,
            "experience_type": experience_type,
            "reference_response": supporter_response,
            "survey_score": survey_score,
            constant.KEY_HASH: hash_value
        }
        
        formatted_sample = {
            constant.KEY_QUESTION_ID: question_id,
            constant.KEY_SCENE: scene,
            constant.KEY_QUESTION_TEXT: question_text,
            constant.KEY_CATEGORY: "Emotional Support",
            constant.KEY_SUBCATEGORY: strategy,
            constant.KEY_OTHER_INFO: other_info
        }
        
        return formatted_sample

def format_persona_to_text(persona: Dict[str, Any]) -> str:
    """一个辅助函数，将复杂的Persona字典格式化为人类可读的文本。"""
    parts = []
    # 添加基本信息
    demographics = persona.get("Demographics", {})
    parts.append(f"- Basic Info: {demographics.get('Age')} years old, {demographics.get('Gender', 'N/A')}, from {demographics.get('Nationality', 'N/A')}.")
    parts.append(f"- Career: {demographics.get('Career_Information', 'N/A')}.")
    
    # 添加性格和价值观
    personality = persona.get("Personality", {})
    mbti = "".join([
        personality.get("Extraversion_or_Introversion", ""),
        personality.get("Sensing_or_Intuition", ""),
        personality.get("Thinking_or_Feeling", ""),
        personality.get("Judging_or_Perceiving", "")
    ])
    if mbti:
        parts.append(f"- Personality (MBTI): {mbti}.")
    if personality.get("Values_and_Interests"):
        interests = ", ".join(personality["Values_and_Interests"])
        parts.append(f"- Values and Interests: {interests}.")

    # 添加偏好
    preference = persona.get("Preference", {})
    if preference.get("Content_Interests"):
        content = ", ".join(preference["Content_Interests"])
        parts.append(f"- Content Interests: {content}.")
    if preference.get("Social"):
        parts.append(f"- Social Habits: {preference['Social']}.")
        
    return "\n".join(parts)

@register_formatter("PersonaFeedbackFormatter")
class PersonaFeedbackFormatter(BaseFormatter):
    """
    处理来自 PersonaFeedbackLoader 合并后的数据。
    """
    @override
    def format(self, raw_sample: Dict[str, Any]) -> Dict[str, Any]:
        persona_data = raw_sample.get("persona", {})
        question_data = raw_sample.get("question_data", {})

        if not persona_data or not question_data:
            return None

        question = question_data.get("question")
        chosen_resp = question_data.get("chosen")
        rejected_resp = question_data.get("reject")
        
        if not all([question, chosen_resp, rejected_resp]):
            return None

        # 将 Persona 字典格式化为文本，作为场景 (scene)
        persona_text = format_persona_to_text(persona_data)
        
        # 随机化选项
        options = {}
        if random.choice([True, False]):
            options["A"] = chosen_resp
            options["B"] = rejected_resp
            correct_answer = "A"
        else:
            options["A"] = rejected_resp
            options["B"] = chosen_resp
            correct_answer = "B"

        hash_value = hashlib.sha256(f"{persona_text}{question}".encode('utf-8')).hexdigest()

        formatted_sample = {
            constant.KEY_QUESTION_ID: hash_value,
            constant.KEY_SCENE: persona_text,
            constant.KEY_QUESTION_TEXT: question,
            constant.KEY_OPTIONS: options,
            constant.KEY_CORRECT_ANSWER: correct_answer,
            constant.KEY_CATEGORY: "Persona Alignment",
            constant.KEY_OTHER_INFO: {
                "user_id": question_data.get("user_id"),
                "persona_name": persona_data.get("Name")
            }
        }
        return formatted_sample


import hashlib

@register_formatter("LongMemEvalFormatter")
class LongMemEvalFormatter(BaseFormatter):
    """
    处理 LongMemEval 数据集，将多段对话历史格式化为单一的上下文。
    """
    @override
    def format(self, raw_sample: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(raw_sample, dict):
            return None

        question = raw_sample.get("question")
        correct_answer = raw_sample.get("answer")
        haystack_sessions = raw_sample.get("haystack_sessions", [])
        haystack_dates = raw_sample.get("haystack_dates", [])

        if not all([question, correct_answer, haystack_sessions]):
            return None

        # --- 核心逻辑：将多段对话历史格式化为清晰的文本 ---
        context_parts = []
        for i, session in enumerate(haystack_sessions):
            session_date = haystack_dates[i] if i < len(haystack_dates) else "Unknown Date"
            context_parts.append(f"--- Conversation on {session_date} ---")
            for turn in session:
                role = turn.get("role", "unknown").capitalize()
                content = turn.get("content", "")
                context_parts.append(f"{role}: {content}")
            context_parts.append("--- End of Conversation ---\n")
        
        # 将所有部分连接成一个大的上下文 (scene)
        scene = "\n".join(context_parts)

        formatted_sample = {
            constant.KEY_QUESTION_ID: raw_sample.get("question_id"),
            constant.KEY_SCENE: scene,
            constant.KEY_QUESTION_TEXT: question,
            constant.KEY_CORRECT_ANSWER: correct_answer, # 这里是标准答案，用于后续计算指标
            constant.KEY_CATEGORY: "Long Context Understanding",
            constant.KEY_OTHER_INFO: {
                "question_type": raw_sample.get("question_type")
            }
        }
        return formatted_sample