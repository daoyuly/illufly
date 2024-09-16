import re
from typing import Any, Set, Union


class Knowledge:
    def __init__(self, text: str):
        self.text = text

    def __str__(self):
        return self.text

    def __repr__(self):
        return f"Knowledge(text={self.text})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Knowledge) and self.text == other.text

    def __hash__(self) -> int:
        return hash(self.text)


class KnowledgeManager:
    def __init__(self, knowledge: Union[Set[str], Set[Knowledge]] = None):
        """
        知识库在内存中以集合的方式保存，确保了其具有唯一性。
        """
        if isinstance(knowledge, set):
            for text in knowledge:
                if not isinstance(text, str):
                    raise ValueError("Knowledge must be a set of strings")
            self._knowledge: Set[Knowledge] = set(Knowledge(text) for text in knowledge)
        elif isinstance(knowledge, set):
            self._knowledge: Set[Knowledge] = knowledge
        else:
            self._knowledge: Set[Knowledge] = set()

    def add_knowledge(self, text: str):
        self._knowledge.add(Knowledge(text))

    def get_knowledge(self, filter: str = None):
        if filter:
            return [kg.text for kg in self._knowledge if re.search(filter, kg.text)]
        else:
            return [kg.text for kg in self._knowledge]

    def clear_knowledge(self):
        self._knowledge.clear()