from schema.schemas import ContentState


def finalizer_node(state: ContentState) -> dict:
    print(f"\n{'='*60}")
    print("🎨 FINALIZER NODE")
    print(f"{'='*60}")

    draft = state["draft"]
    day_num = state.get("day_number", 1)
    total_days = state.get("total_days", 30)

    print(f"   ✅ Newsletter finalized (Day {day_num}/{total_days})")
    print(f"{'='*60}\n")

    return {"newsletter": draft}
