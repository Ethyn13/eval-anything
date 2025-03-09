"""
评估工具包（包括各种指标的计算以及指定pattern的提取）
"""
from abc import ABC, abstractmethod
from eval_anything.evaluate_tools.base_tools import BaseTool
from typing import Union, List, Iterable
import numpy as np

T2T_EXTRACTOR_MAP = {
    "regex_match_number": "RegexMatchNumber",
    "regex_match_letter": "RegexMatchLetter",
    "regex_match_multi_letter": "RegexMatchMultiLetter",
    "regex_match_code": "RegexMatchCode",
    "regex_match_math": "RegexMatchMath",
    "regex_match_dialogue": "RegexMatchDialogue",
}

T2T_JUDGER_MAP = {
    "judge_equal": "JudgeEqual",
    "judge_mc1": "JudgeMC1",
    "judge_mc2": "JudgeMC2",
}


class RegexMatch(BaseTool):
    def __init__(self, pattern: str, match_index: int = None):
        self.pattern = pattern
        self.match_index = match_index  

    def apply(self, data: Union[List, Iterable]) -> Union[List, None]:
        """
        Match the specified pattern in the text.
        Args:
            data (list/iterable): the text to be matched
        Returns:
            list/None: the matched result
        """
        def match_text(text):
            import re
            pattern = re.compile(self.pattern)
            match = list(pattern.finditer(text))
            if match:
                if self.match_index is not None:
                    return match[self.match_index].group()
                else:
                    return match.group()
            else:
                return None
        matches = [match_text(item) for item in data]
        return matches
    
    def __call__(self, data: Union[List, Iterable]) -> Union[List, None]:
        return self.apply(data)
    
class RegexMatchNumber(RegexMatch):
    def __init__(self, additional_pattern: str = None, match_index: int = None):
        pattern_match_number = r"(?:[+-]?(?:\d+/\d+|(?:\d*\.\d+)|\d+)|√(?:\([+-]?(?:\d+/\d+|(?:\d*\.\d+)|\d+)\)|[+-]?(?:\d+/\d+|(?:\d*\.\d+)|\d+)))"
        self.pattern = additional_pattern.format(original_pattern=pattern_match_number) if additional_pattern else pattern_match_number
        self.match_index = match_index
        
class RegexMatchText(RegexMatch):
    def __init__(self, additional_pattern: str = None, match_index: int = None):
        # Pattern to match single letter answers A, B, C, D (case insensitive)
        pattern_match_text = r"[A-Da-d]"
        self.pattern = additional_pattern.format(original_pattern=pattern_match_text) if additional_pattern else pattern_match_text
        self.match_index = match_index

    def apply(self, data: Union[List, Iterable]) -> Union[List, None]:
        """
        Match letter answers in the text and convert to uppercase.
        Args:
            data (list/iterable): the text to be matched
        Returns:
            list/None: the matched result in uppercase
        """
        matches = super().apply(data)
        # Convert matched letters to uppercase for consistency
        return [match.upper() if match else None for match in matches]

class JudgeEqual(BaseTool):
    def __init__(self):
        super().__init__()
    
    def apply(self, data_1, data_2) -> bool:
        return data_1 == data_2
    
    def __call__(self, data_1, data_2) -> bool:
        return self.apply(data_1, data_2)

class RegexMatchLetter(RegexMatch):
    def __init__(self, additional_pattern: str = None, match_index: int = None):
        # Base pattern to match letters in parentheses (A-Z)
        pattern_match_letter = r"\(([A-Za-z])\)"  # Capture the letter between parentheses
        self.pattern = additional_pattern.format(original_pattern=pattern_match_letter) if additional_pattern else pattern_match_letter
        self.match_index = match_index

    def apply(self, data: Union[List, Iterable]) -> Union[List, None]:
        def match_text(text):
            import re
            pattern = re.compile(self.pattern, re.IGNORECASE)
            match = list(pattern.finditer(text))
            if match:
                if self.match_index is not None:
                    # Extract just the letter part (group 1) and convert to uppercase
                    return match[self.match_index].group(1).upper()
                else:
                    return match.group(1).upper()
            else:
                return None
        matches = [match_text(item) for item in data]
        return matches

class RegexMatchMultiLetter(RegexMatch):
    def __init__(self, additional_pattern: str = None, match_index: int = None):
        pattern_match_letter = r"\(([A-Za-z])\)"
        self.pattern = additional_pattern.format(original_pattern=pattern_match_letter) if additional_pattern else pattern_match_letter
        self.match_index = match_index

    def apply(self, data: Union[List, Iterable]) -> Union[List, None]:
        def match_text(text):
            import re
            pattern = re.compile(self.pattern, re.IGNORECASE)
            match = list(pattern.finditer(text))
            if match:
                if self.match_index is not None:
                    return [match[self.match_index].group(1).upper()]
                else:
                    return [match.group(1).upper()]
            else:
                return None
        matches = [match_text(item) for item in data]
        return matches
    
class RegexMatchCode(RegexMatch):
    def __init__(self, additional_pattern: str = None, match_index: int = None, language: str = "python"):
        # Pattern to match code blocks between ```python ``` or ``` ```
        pattern_match_code = r"```(?:{language})?\s*([\s\S]*?)\s*```"
        self.pattern = additional_pattern.format(original_pattern=pattern_match_code) if additional_pattern else pattern_match_code
        self.match_index = match_index
        self.language = language

    def apply(self, data: Union[List, Iterable]) -> Union[List, None]:
        def match_text(text):
            import re
            # Find all positions of ```language and ``` markers
            language_pattern = r"```{}".format(self.language)
            close_pattern = r"```"
            language_positions = [m.start() for m in re.finditer(language_pattern, text)]
            close_positions = [m.start() for m in re.finditer(close_pattern, text)]
            
            if not language_positions or not close_positions:
                return ""
            
            # Match each ```language with its next ``` marker
            code_blocks = []
            for lang_start in language_positions:
                # Find the next closing marker after this language marker
                next_close = None
                for close_pos in close_positions:
                    if close_pos > lang_start:
                        next_close = close_pos
                        break
                
                if next_close is not None:
                    block_content = text[lang_start:next_close + 3]  # Include the closing ```
                    # Clean up the content
                    content = re.sub(r'^```{}\s*'.format(self.language), '', block_content)
                    content = re.sub(r'\s*```$', '', content)
                    code_blocks.append(content)
            
            if not code_blocks:
                return ""
            
            # Return the specific match based on index
            if self.match_index is not None:
                if self.match_index < 0:
                    self.match_index = len(code_blocks) + self.match_index
                if 0 <= self.match_index < len(code_blocks):
                    return code_blocks[self.match_index]
                return ""
            else:
                return code_blocks[0]  # Default to first match
            
        matches = [match_text(item) for item in data]
        return matches
    
class RegexMatchMath(RegexMatch):
    def __init__(self, additional_pattern: str = None, match_index: int = None):
        pass

    def apply(self, data: Union[List, Iterable]) -> Union[List, None]:
        from eval_anything.utils.utils import parse_math_answer
        matches = [parse_math_answer(item) for item in data]
        return matches
    
class RegexMatchDialogue(RegexMatch):
    def __init__(self, additional_pattern: str = None, match_index: int = None):
        pass

    def apply(self, data: Union[List, Iterable]) -> Union[List, None]:
        return data
    
class JudgeMC1(BaseTool):
    def __init__(self):
        super().__init__()
    
    def apply(self, scores, best_answer_index) -> bool:
        return True if scores['scores_true'][best_answer_index] > max(scores['scores_false']) else False
    
    def __call__(self, scores, best_answer_index) -> bool:
        return self.apply(scores, best_answer_index)
    
class JudgeMC2(BaseTool):
    def __init__(self):
        super().__init__()

    def apply(self, scores):
        scores_true = scores['scores_true']
        scores_false = scores['scores_false']

        probs_true = np.exp(scores_true)
        probs_false = np.exp(scores_false)
        probs_true = probs_true / (sum(probs_true) + sum(probs_false))
        
        return sum(probs_true)

    def __call__(self, scores):
        return self.apply(scores)