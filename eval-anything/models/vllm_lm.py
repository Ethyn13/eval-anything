"""
(t2t)支持vllm推理
"""

import json
import os
import re
from typing import Any, Dict, List

from vllm import LLM, SamplingParams
from vllm.utils import cuda_device_count_stateless

from eval_anything.utils.data_type import InferenceInput, InferenceOutput
from eval_anything.utils.utils import UUIDGenerator
from eval_anything.models.base_model import BaseModel

class vllmModel(BaseModel):
    def __init__(self, model_cfgs: Dict[str, Any], vllm_cfgs, **kwargs):
        self.vllm_cfgs_sp, self.vllm_cfgs_llm = vllm_cfgs.SamplingParams, vllm_cfgs.LLM
        self.model_cfgs = model_cfgs
        self.sp_n = self.vllm_cfgs_sp.n
        self.sp_top_k = self.vllm_cfgs_sp.top_k
        self.sp_top_p = self.vllm_cfgs_sp.top_p
        self.sp_temperature = self.vllm_cfgs_sp.temperature
        self.sp_max_tokens = self.model_cfgs.model_max_length
        self.sp_prompt_logprobs = self.vllm_cfgs_sp.prompt_logprobs
        self.sp_logprobs = self.vllm_cfgs_sp.logprobs

        self.llm_tokenizer_mode = self.vllm_cfgs_llm.tokenizer_mode
        self.llm_trust_remote_code = self.vllm_cfgs_llm.trust_remote_code
        self.llm_gpu_memory_utilization = self.vllm_cfgs_llm.gpu_memory_utilization
        self.llm_max_num_seqs = self.vllm_cfgs_llm.max_num_seqs
        tensor_ps = self.vllm_cfgs_llm.tensor_parallel_size
        self.llm_tensor_parallel_size = tensor_ps if tensor_ps else cuda_device_count_stateless()

        self.model_id = self.model_cfgs.model_id
        self.model_name_or_path = self.model_cfgs.model_name_or_path
        self.llm_trust_remote_code = self.model_cfgs.trust_remote_code
        self.sp_max_tokens = self.model_cfgs.model_max_length

        self.task2details = {}
        self.detailed_filename = f'{self.model_id}_detailed'
        self.brief_filename = f'{self.model_id}_brief'
        self.init_model()

    def init_model(self) -> None:
        self.samplingparams = SamplingParams(
            n=self.sp_n,
            top_k=self.sp_top_k,
            top_p=self.sp_top_p,
            temperature=self.sp_temperature,
            max_tokens=self.sp_max_tokens,
            prompt_logprobs=self.sp_prompt_logprobs,
            logprobs=self.sp_logprobs,
        )

        self.model = LLM(
            model=self.model_name_or_path,
            tokenizer=self.model_name_or_path,
            tokenizer_mode=self.llm_tokenizer_mode,
            trust_remote_code=self.llm_trust_remote_code,
            tensor_parallel_size=self.llm_tensor_parallel_size,
            gpu_memory_utilization=self.llm_gpu_memory_utilization,
            max_num_seqs=self.llm_max_num_seqs,
        )

    def generation(self, inputs: Dict[str, List[InferenceInput]]) -> Dict[str, List[InferenceOutput]]:
        return self._generation(inputs)

    def _generation(self, inputs: Dict[str, List[InferenceInput]]) -> Dict[str, List[InferenceOutput]]:
        input_list = []
        for task, data_list in inputs.items():
            for data in data_list:
                data.uuid = UUIDGenerator()(data)
                data.task = task
                input_list.append(data)

        outputs = self.model.generate(
            prompts=[input.text for input in input_list], sampling_params=self.samplingparams
        )
        InferenceOutputs = [
            InferenceOutput.from_vllm_output(task=input.task, uuid=input.uuid, vllm_output=output, store_raw=True)
            for input, output in zip(input_list, outputs)
        ]
        outputs = {task: [] for task in inputs.keys()}
        for output in InferenceOutputs:
            outputs[output.task].append(output)

        return outputs
    
    # TODO
    def shutdown_model(self):
        pass
