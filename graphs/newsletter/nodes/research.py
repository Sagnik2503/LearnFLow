from schema.schemas import ContentState, ExaResult
from exa_py import Exa
import os


def research_node(state: ContentState) -> dict:
    exa = Exa(api_key=os.getenv("EXA_API_KEY"))
    exa_queries_list = []
    for section in state["plan"].sections:
        for query in section.exa_queries:
            exa_queries_list.append(query)

    print(f"\n{'='*60}")
    print(f"🔍 RESEARCHER NODE")
    print(f"{'='*60}")
    print(f"📋 Total queries to run: {len(exa_queries_list)}")
    for i, q in enumerate(exa_queries_list, 1):
        print(f"   {i}. {q}")

    query_results = []
    seen_urls = set()
    for query in exa_queries_list:
        print(f"\n🔎 Searching: '{query}'")
        result = exa.search(
            query,
            type="auto",
            num_results=2,
            contents={
                "highlights": {"max_characters": 4000},
                "text": True,
                "summary": True,
            },
            include_domains=[
                "developers.google.com",
                "coursera.org",
                "arxiv.org",
                "datacamp.com",
                "baeldung.com",
                "wikipedia.org",
                "towardsdatascience.com",
            ],
        )
        for item in result.results:
            if item.url in seen_urls:
                continue

            seen_urls.add(item.url)
            exa_result = ExaResult(
                url=item.url,
                title=item.title,
                summary=item.summary if item.summary else "",
                snippet=item.highlights[0] if item.highlights else "",
            )
            query_results.append(exa_result)
            print(f"   ✅ {item.title}")
            print(f"      🔗 {item.url}")
            print(f"      📝 {exa_result.snippet[:100]}...")

    print(f"\n{'='*60}")
    print(f"✅ Research complete — {len(query_results)} results collected")
    print(f"{'='*60}\n")

    return {"research": query_results}
