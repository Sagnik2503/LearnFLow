from graphs.newsletter_generator_graph import build_graph

# ✅ Build once (important)
newsletter_graph = build_graph()


def run_newsletter_graph(
    topic: str,
    item: dict,
    previous: str | None,
    day: int,
    total_days: int,
) -> str:
    """
    Executes newsletter graph and returns markdown content
    """

    state = {
        "topic": topic,
        "item": item,
        "previous_topic": previous,
        "day_number": day,
        "total_days": total_days,
        # 🔽 graph working state
        "plan": None,
        "research": [],
        "research_summary": [],
        "draft": "",
        "feedback": "",
        "feedbacks": [],
        "revision_count": 0,
        "approved": False,
        # 🔽 final output
        "newsletter": "",
    }

    print("\n🧠 Running Newsletter Graph...")
    print("📌 Day:", day)

    result = newsletter_graph.invoke(state)

    newsletter = result.get("newsletter")

    if not newsletter:
        raise ValueError("Newsletter graph did not return content")

    print("✅ Newsletter generated\n")

    return newsletter
