from graphs.newsletter.graph import build_graph

newsletter_graph = build_graph()


def run_newsletter_graph(
    topic: str,
    item: dict,
    day: int,
    total_days: int,
) -> str:
    state = {
        "topic": topic,
        "item": item,
        "day_number": day,
        "total_days": total_days,
        "plan": None,
        "research": [],
        "research_summary": [],
        "draft": "",
        "feedbacks": [],
        "revision_count": 0,
        "approved": False,
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
