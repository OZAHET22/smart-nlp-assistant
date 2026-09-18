try:
    from .pos_tagger import pos_tag_sentence
    from .dependency_parser import (
        dependency_parse,
        TokenAnalysis,
        SentenceParse,
    )
    from .grammar import GRAMMAR_RULES, CFGGrammar, DEFAULT_GRAMMAR
    from .cyk_parser import CYKParser, build_parse_tree_string, render_tree
except ImportError:
    from pos_tagger import pos_tag_sentence
    from dependency_parser import dependency_parse, TokenAnalysis, SentenceParse
    from grammar import GRAMMAR_RULES, CFGGrammar, DEFAULT_GRAMMAR
    from cyk_parser import CYKParser, build_parse_tree_string, render_tree
