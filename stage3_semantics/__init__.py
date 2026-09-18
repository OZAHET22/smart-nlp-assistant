try:
    from .ner import Entity, extract_entities
    from .srl import SemanticFrame, extract_semantic_roles, semantic_analysis
    from .wsd import disambiguate, lesk_wsd, simplified_lesk
except ImportError:
    from ner import Entity, extract_entities
    from srl import SemanticFrame, extract_semantic_roles, semantic_analysis
    from wsd import disambiguate, lesk_wsd, simplified_lesk
