import os
from pathlib import Path

from .kbase_service import KBaseService, DirKnowledgeConfig


class DirKnowledgeService(KBaseService):
    def __init__(self, config: DirKnowledgeConfig) -> None:
        super().__init__(config)
        self.knowledge: dict[str, str] = {}
        self.opened: set[str] = set()

        for root, dirs, files in os.walk(config['location']):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            files = [f for f in files if not f.startswith('.')]
            for file in files:
                name = Path(file).stem
                file_path = os.path.join(root, file)
                self.knowledge[name.lower()] = file_path
                self.knowledge[root.lower()] = self.knowledge.get(file, '') + '\n\n'+ self.knowledge[name.lower()]

    def load_context(self, request: str) -> list[str]:
        words = request.lower().split()

        context = []
        for word in words:
            if word in self.knowledge and word not in self.opened:
                path = self.knowledge[word]

                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()

                self.knowledge[word] = content
                self.opened.add(word)

                context.append(word)
            elif word in self.knowledge:
                context.append(self.knowledge[word])

        return context
