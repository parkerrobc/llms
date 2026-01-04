from .dir_knowledge_service import DirKnowledgeService

from .kbase_service import KBaseService, KBaseConfig, KBaseType

def get_kbase_service(config: KBaseConfig) -> KBaseService:
    kbase_type = KBaseType[config['type'].upper()]

    match kbase_type:
        case KBaseType.DIRECTORY:
            return DirKnowledgeService(config)
