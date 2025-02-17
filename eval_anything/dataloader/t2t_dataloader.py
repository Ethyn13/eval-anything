"""
t2t dataloader基类
输入：
    - 数据集路径
    - split
    - size
    - 模态
    - 预处理方式（是否pre-tokenize）
    - 模型路径（如果需要pre-tokenize）
    - shuffle
    - num_workers
    - chat_template
    - ...
输出：
    - InferenceInput类
"""

from typing import Any, Dict, List

from eval_anything.dataloader.base_dataloader import BaseDataLoader


# from eval_anything.utils.registry import TemplateRegistry as get_template_class
from eval_anything.utils.utils import MultiChoicePromptBuilder, DialoguePromptBuilder
from eval_anything.utils.data_type import InferenceInput
from datasets import load_dataset


class T2TDataLoader(BaseDataLoader):
    
    def build_multi_choice_prompt(self, data):
        few_shot_examples = self.few_shot_data[: self.num_shot] if self.num_shot else []
        # template = get_template_class(self.chat_template)
        prompt_builder = MultiChoicePromptBuilder(
            candidate_labels=self.task_info['candidate_labels'],
            few_shot_examples=few_shot_examples,
            cot=self.cot
        )
        prompts = [prompt_builder.build_prompt(item['question'], item['choices']) for item in data]
        
        return prompts

    def build_dialogue_prompt(self, data):
        few_shot_examples = self.few_shot_data[: self.num_shot] if self.num_shot else []
        prompt_builder = DialoguePromptBuilder(
            few_shot_examples=few_shot_examples,
            cot=self.cot
        )
        prompts = [InferenceInput(text=prompt_builder.build_prompt(item['question'])) for item in data]
        
        return prompts
