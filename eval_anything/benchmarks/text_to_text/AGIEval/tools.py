from eval_anything.evaluate_tools.t2t_tools import RegexMatch
from typing import Union, List, Iterable

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