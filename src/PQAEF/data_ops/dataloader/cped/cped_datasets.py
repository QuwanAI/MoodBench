# coding=utf-8
# Copyright 2021 South China University of Technology and 
# Engineering Research Ceter of Ministry of Education on Human Body Perception.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# CPED Dataset data loading file
# File: cped_dataset.py
# Used for CPED dataset loading
# Author: Chen Yirong <eeyirongchen@mail.scut.edu.cn>
# Date: 2022.03.29

# 关键包版本说明：
# pytorch: 1.9.0+
import logging
from itertools import chain 
# import torch  # 移除Tensor相关的导入
import pandas as pd
from torch.utils.data import Dataset # 仅保留对Dataset的继承

# 假设这些常量和辅助函数在 cped_utils 中定义，但我们不再依赖它们来获取 ID，
# 而是直接使用字符串形式的角色和内容。

# 假设以下常量是可用的（即使我们不使用它们的ID或Token形式，但在逻辑中可能用于引用）
CPED_SPECIAL_TOKENS = ["[CLS]", "[SEP]", "[speaker1]", "[speaker2]"]
CPED_IGNORE_ID = -1

CPED_DA_TO_TOKENS = {'greeting': '[greeting]', 'question': '[question]', 'answer': '[answer]', 
                     'statement-opinion': '[statement-opinion]', 'statement-non-opinion': '[statement-non-opinion]', 
                     'apology': '[apology]', 'command': '[command]', 'agreement': '[agreement]', 
                     'disagreement': '[disagreement]', 'acknowledge': '[acknowledge]', 'appreciation': '[appreciation]', 
                     'interjection': '[interjection]', 'conventional-closing': '[conventional-closing]', 
                     'quotation': '[quotation]', 'reject': '[reject]', 'irony': '[irony]', 
                     'comfort': '[comfort]','thanking':'[thanking]', 'other': '[da-other]'}

CPED_EMOTION_TO_TOKENS = {'happy': '[happy]', 'grateful': '[grateful]', 'relaxed': '[relaxed]', 
                          'positive-other': '[positive-other]', 'anger': '[anger]', 'sadness': '[sadness]', 
                          'fear': '[fear]', 'depress': '[depress]', 'disgust': '[disgust]', 
                          'astonished': '[astonished]', 'worried': '[worried]', 'negative-other': '[negative-other]', 
                          'neutral': '[neutral]'}


logger = logging.getLogger(__name__)


def find_split_id_of_response(speaker_list, responder):
    """
    确定对话历史和回复内容的分割点。
    """
    split_id = -1
    for i in range(-2, -len(speaker_list), -1):
        if speaker_list[i] != responder:
            return split_id
        else:
            split_id = split_id - 1
    return -1

def create_speaker_type(speaker_list, responder=None):
    """
    将姓名列表转换为角色标识符（[speaker1] 或 [speaker2]）。
    """
    if responder == None: 
        speaker2 = speaker_list[-1] 
    else:
        speaker2 = responder
    
    speaker_type_list = []
    for speaker in speaker_list:
        if speaker == speaker2:
            speaker_type_list.append("[speaker2]")  # 回复者
        else:
            speaker_type_list.append("[speaker1]")
    return speaker_type_list


def convert_emotion_to_tokens(emotion_list, emotion_type="Emotion", SELECTED_EMOTION_TO_TOKENS=None):
    """
    将情感标签转换为对应的Token字符串。
    """
    if SELECTED_EMOTION_TO_TOKENS is None:
        SELECTED_EMOTION_TO_TOKENS = {"Emotion": CPED_EMOTION_TO_TOKENS, "Sentiment": {}}
    
    emotion_tokens_list = []
    for emo in emotion_list:
        if emo not in SELECTED_EMOTION_TO_TOKENS[emotion_type]:
            emotion_tokens_list.append("[neutral]")
        else:
            emotion_tokens_list.append(SELECTED_EMOTION_TO_TOKENS[emotion_type][emo])
    return emotion_tokens_list

def convert_da_to_tokens(da_list, da_type="DA", SELECTED_DA_TO_TOKENS=None):
    """
    将DA标签转换为对应的Token字符串。
    """
    if SELECTED_DA_TO_TOKENS is None:
        SELECTED_DA_TO_TOKENS = {"DA": CPED_DA_TO_TOKENS}
        
    da_tokens_list = [SELECTED_DA_TO_TOKENS[da_type][da] for da in da_list]
    return da_tokens_list


# 注意：set_da_in_speaker 和 set_emotion_in_speaker 等函数依赖于 token IDs 和 padding，
# 在这个只输出结构化文本的场景下不再适用或需要重写，因此此处省略。


class CpedDataset(Dataset):
    """
    用于将 CPED 数据集转换为结构化文本对话格式 {"role": role_name, "content": content}。
    不再依赖于Tokenizer来生成Token ID。
    """
    def __init__(self, 
                 data, 
                 # 移除 tokenizer 参数
                 emotion_type="Emotion", 
                 da_type="DA",
                 persona_type=["Gender","Neuroticism","Extraversion","Openness","Agreeableness","Conscientiousness","Age"],
                 max_history=25, 
                 lm_labels=True, 
                 with_current_speaker=False,
                 with_current_persona=False,
                 with_current_emotion=False,
                 with_current_da=False,
                 with_emotion=False, 
                 with_da=False,
                 use_speaker_name_as_speaker_list=False,
                 max_word_length=512): 
        self.data = data
        self.emotion_type = emotion_type 
        self.da_type = da_type          
        self.persona_type = persona_type
        self.with_current_speaker = with_current_speaker
        self.with_current_persona = with_current_persona
        self.with_current_emotion = with_current_emotion
        self.with_current_da = with_current_da
        self.with_emotion=with_emotion   
        self.with_da=with_da             
        self.max_history = max_history   
        self.max_history_utterances = 2*max_history 
        self.max_word_length = max_word_length
        self.use_speaker_name_as_speaker_list = use_speaker_name_as_speaker_list
        self.lm_labels = lm_labels
        
        # 假设 data 已经通过 cped_get_single_file 处理过，并且 Dialogue_ID 是可用的
        self.keys = list(set(self.data['Dialogue_ID']))
        self.len = len(self.keys)

    def __len__(self):
        return self.len

    def __getitem__(self, index):
        dialogue_id = self.keys[index]
        data_index = self.data[self.data['Dialogue_ID']==dialogue_id]
        
        # 确定历史对话的最大句子数
        if len(data_index["Speaker"].tolist()) > self.max_history_utterances:
            max_history_utterances = self.max_history_utterances
        else:
            max_history_utterances = len(data_index["Speaker"].tolist())
        
        # 获取说话人姓名列表和回复者姓名
        speaker_name_list = data_index["Speaker"].tolist()[-max_history_utterances:] 
        responder = speaker_name_list[-1] 
        
        # 找出回复内容与历史对话的分割id
        response_split_id = find_split_id_of_response(speaker_name_list, responder) 
        
        # 获取历史对话的原始文本
        history_utterance_texts = data_index["Utterance"].tolist()[-max_history_utterances:response_split_id]
        # 获取回复的原始文本
        if self.lm_labels:
            response_utterance_texts = data_index["Utterance"].tolist()[response_split_id:]
        else:
            response_utterance_texts = []
        
        # 获取历史对话的角色类型 ([speaker1] 或 [speaker2])
        if self.use_speaker_name_as_speaker_list: 
            # 如果使用真实姓名作为角色名，可以直接使用姓名
            history_speaker_types = speaker_name_list[-max_history_utterances:response_split_id]
            responder_role = responder
        else:
            # 使用抽象的角色类型 [speaker1], [speaker2]
            history_speaker_types = create_speaker_type(speaker_list=speaker_name_list[-max_history_utterances:response_split_id], responder=responder)
            responder_role = "[speaker2]"
        
        # ----------------------------------------------------
        # 核心修改：生成 {"role": role_name, "content": content} 格式
        # ----------------------------------------------------
        
        history_context = []
        for i, utt in enumerate(history_utterance_texts):
            role = history_speaker_types[i]
            # 可以在这里添加情感或DA信息到内容中，如果需要的话
            # 例如：content = f"{history_emotion_tokens[i]} {utt}"
            history_context.append({"role": role, "content": utt})
        
        response_context = []
        for utt in response_utterance_texts:
            # 假设回复者就是 [speaker2] 或其对应的名称
            response_context.append({"role": responder_role, "content": utt})

        # 将历史和回复合并，作为模型的完整输入
        full_dialogue = history_context + response_context

        # 返回结构化数据
        instance = {
            "dialogue_id": dialogue_id,
            "history": history_context,
            "response": response_context,
            "full_dialogue": full_dialogue
        }

        # 如果需要的话，添加其他元数据
        if self.with_current_emotion:
            current_emotion = data_index[self.emotion_type].tolist()[-1]
            instance["current_emotion"] = current_emotion
        # ... 可以添加其他的元数据，如 DA 或 Persona

        return instance

    # 移除 collate 函数，因为不再生成 Tensors 和 Padding

# --- 示例用法：如何获取结构化数据 ---
def example_usage_get_structured_data(data_path, max_history=5):
    # 假设你已经有了数据 DataFrame，通常是从 cped_util.cped_get_single_file 获取
    # 模拟一个 DataFrame 
    data = pd.DataFrame({
        'Dialogue_ID': ['27_000', '27_000', '27_000'],
        'Utterance_ID': ['27_000_000', '27_000_001', '27_000_002'],
        'Speaker': ['林宛瑜', '林宛瑜', '陆展博'],
        'Sentiment': ['neutral', 'neutral', 'negative'],
        'Emotion': ['neutral', 'neutral', 'worried'],
        'DA': ['statement-non-opinion', 'thanking', 'statement-non-opinion'],
        'Utterance': ['好了没事了', '谢谢你哦', '没关系'],
        # ... 其他列
    })

    # 实例化数据集
    dataset = CpedDataset(data, max_history=max_history, lm_labels=True)

    # 获取第一个对话样本
    sample = dataset[0]

    print("--- 格式化后的对话数据 ---")
    print(f"对话ID: {sample['dialogue_id']}")
    print("\n历史对话:")
    for turn in sample['history']:
        print(f"  {turn}")
    print("\n回复:")
    for turn in sample['response']:
        print(f"  {turn}")
    print("\n完整对话:")
    print(sample['full_dialogue'])

# 运行示例
if __name__ == '__main__':
    example_usage_get_structured_data("dummy_path")