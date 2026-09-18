try:
    from .coref import CorefChain, resolve_coreference, heuristic_coref_resolver
    from .discourse_relations import DiscourseRelation, detect_discourse_relations
    from .pragmatics import PragmaticNote, detect_indirect_request, detect_indirect_requests
except ImportError:
    from coref import CorefChain, resolve_coreference, heuristic_coref_resolver
    from discourse_relations import DiscourseRelation, detect_discourse_relations
    from pragmatics import PragmaticNote, detect_indirect_request, detect_indirect_requests
