def __getattr__(name):
    if name == 'root_agent':
        from .agent import root_agent
        return root_agent
    raise AttributeError(f"module 'content_creation_studio' has no attribute {name!r}")
