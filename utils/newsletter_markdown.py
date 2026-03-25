from graphs.newsletter_generator_graph import build_graph


def generate_newsletter_markdown(
    topic: str,
    concepts: list[str],
    previous: str | None,
    day: int,
    total_days: int,
) -> str:
    """
    Generate markdown newsletter using your graph.
    """

    # Prepare input for graph
    graph_input = {
        "topic": topic,
        "concepts": concepts,
        "previous_topic": previous,
        "day": day,
        "total_days": total_days,
    }

    # Call graph
    result = build_graph.invoke(graph_input)

    # Extract markdown content
    content = result.get("content")

    if not content:
        raise ValueError("Newsletter graph did not return content")

    return content
