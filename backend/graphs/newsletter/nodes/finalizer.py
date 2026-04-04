from schema.schemas import ContentState


def finalizer_node(state: ContentState) -> dict:
    return {"newsletter": state["draft"]}
