from typing import Dict, Any
from ..utils import minify_text
import json
import uuid
import time
import random

class IDGenerator:
    def __init__(self):
        self.counter = 0

    def create_id(self):
        while True:
            timestamp = str(int(time.time()))[-4:]
            random_number = f'{random.randint(0, 999):03}'
            counter_str = f'{self.counter:03}'
            yield f'{timestamp}-{random_number}-{counter_str}'
            self.counter = 0 if self.counter == 999 else self.counter + 1

id_generator = IDGenerator()
id_gen = id_generator.create_id()

class Document():
    def __init__(self, text: str=None, index: str=None, meta: Dict[str, Any] = None):
        self.text = text or ""
        self.index = index or ""
        self.meta = {'source': 'unknown', **(meta or {})}
        if 'id' not in self.meta:
            self.meta['id'] = next(id_gen)

    def __repr__(self):
        return f"Document(text='{minify_text(self.text)}', meta='{minify_text(json.dumps(self.meta, ensure_ascii=False))}')"

    def __str__(self):
        return self.text
    
    def __len__(self):
        return len(self.text)
