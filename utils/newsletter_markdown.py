from graphs.builder.newsletter_builder import run_newsletter_graph


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

    item = {
        "day": day,
        "title": topic,
        "description": "",
        "concepts": concepts,
    }

    content = run_newsletter_graph(
        topic=topic,
        item=item,
        previous=previous,
        day=day,
        total_days=total_days,
    )

    return content
