from graphs.curriculum.graph import build_curriculum_graph

graph = build_curriculum_graph()


def run_curriculum_graph(topic: str) -> dict:
    initial_state = {
        "topic": topic,
        "total_days": None,
        "syllabus": [],
    }

    print("\n🚀 Running Curriculum Graph...\n")

    result = graph.invoke(initial_state)

    print("\n✅ Graph execution completed\n")

    return result
