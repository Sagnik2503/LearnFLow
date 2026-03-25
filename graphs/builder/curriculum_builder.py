from graphs.curriculum_graph import build_curriculum_graph

graph = build_curriculum_graph()


def run_curriculum_graph(topic: str) -> dict:
    """
    Executes the curriculum graph end-to-end.

    Returns:
    {
        "topic": str,
        "total_days": int,
        "syllabus": list[dict],
        "track_id": int
    }
    """

    # ✅ IMPORTANT: always pass dict (fixes your error)
    initial_state = {
        "topic": topic,
        "total_days": None,  # will be decided by graph
        "syllabus": [],
    }

    print("\n🚀 Running Curriculum Graph...\n")

    result = graph.invoke(initial_state)

    print("\n✅ Graph execution completed\n")

    return result
