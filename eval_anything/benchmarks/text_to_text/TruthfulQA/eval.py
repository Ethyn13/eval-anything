"""
继承自eval-anything.pipeline.t2t_task
"""
from collections import defaultdict, namedtuple
import torch
from eval_anything.pipeline.t2t_benchmark import T2TBenchmark
from eval_anything.utils.data_type import InferenceInput, InferenceOutput
from eval_anything.models.base_model import BaseModel
from eval_anything.utils.logger import EvalLogger
from eval_anything.utils.register import BenchmarkRegistry
from eval_anything.utils.cache_manager import CacheManager

from eval_anything.benchmarks.text_to_text.TruthfulQA.dataloader import TruthfulQADataloader
from eval_anything.benchmarks.text_to_text.TruthfulQA.metrics import BLEURT, TruthJudge, InfoJudge, MC1, MC2
from eval_anything.benchmarks.text_to_text.TruthfulQA.tools import JudgeMC1, JudgeMC2
# Benchmark Registry
@BenchmarkRegistry.register('TruthfulQA')
class TruthfulQABenchmark(T2TBenchmark):
    def __init__(self, 
                 model: BaseModel, 
                 eval_cfgs: namedtuple, 
                 model_cfgs: namedtuple, 
                 infer_cfgs: namedtuple, 
                 output_path: str,
                 cache_manager: CacheManager,
                 logger: EvalLogger):
        super().__init__(model, eval_cfgs, model_cfgs, infer_cfgs, output_path, cache_manager, logger)
        self.benchmark_name = "TruthfulQA"
        self.benchmark_cfgs = self.get_benchmark_cfgs(self.benchmark_name)

    def to_InferenceOutput(self, inference_inputs: dict[str, list[InferenceInput]]) -> dict[str, list[InferenceOutput]]:
        """Convert a InferenceInput dict instances to a InferenceOutput dict instances with logprobs processing for TruthfulQA
        
        Args:
            inference_inputs (dict[str, list[InferenceInput]]): input data
            
        Returns:
            inference_outputs (dict[str, list[InferenceOutput]]): inference outputs with processed logprobs
        """
        inference_outputs = super().to_InferenceOutput(inference_inputs)
        task_list = inference_inputs.keys()
        for task in task_list:
            scores = defaultdict(list)
            for input, output in zip(inference_inputs[task], inference_outputs[task]):
                log_probs = torch.tensor([
                    list(token_probs.values())[0].logprob
                    for token_probs in output.response_logprobs[0]
                ])
                log_probs = log_probs[3:]
                text_id = input.metadata.get('text_id')
                scores[text_id].append(log_probs.sum().item())
                if text_id != 0 and text_id % 2 == 0:
                    output.response_logprobs = {
                        'scores_true': scores[text_id - 2],
                        'scores_false': scores[text_id - 1]
                    }
                else:
                    output.response_logprobs = None
        return inference_outputs
