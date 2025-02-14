from typing import Any, Dict, List
from eval_anything.utils.data_type import InferenceInput, InferenceOutput

# TODO 以注册表的形式管理模型

MODEL_MAP = {
    "vllm_LM": "vllm_lm",
    "vllm_MM": "vllm_mm",
    "hf_LM": "hf_lm",
    "hf_MM": "hf_mm",
    "api_LM": "api_lm",
    "api_MM": "api_mm",
}

class BaseModel:
    def __init__(self, model_cfgs: Dict[str, Any]):
        self.model_cfgs = model_cfgs
        self.init_model()

    def init_model(self):
        pass
    
    def generation(self, inputs: Dict[str, List[InferenceInput]]) -> Dict[str, List[InferenceOutput]]:
        pass
    
    def _generation(self, inputs: Dict[str, List[InferenceInput]]) -> Dict[str, List[InferenceOutput]]:
        pass

    def shutdown_model(self):
        pass
