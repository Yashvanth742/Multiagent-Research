import logging

from google.adk.agents import LlmAgent
from google.adk.workflow import RetryConfig
from google.adk.models import LlmResponse
from google.adk.agents.callback_context import CallbackContext

from .schemas import ResearchPlan

logger = logging.getLogger(__name__)


def _save_plan_without_emitting_it(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> LlmResponse | None:
    """Save the research plan for the existing workflow."""

    if llm_response.partial or not llm_response.content:
        return None

    try:
        plan_text = "".join(
            part.text or ""
            for part in (llm_response.content.parts or [])
            if part.text is not None
        )

        if not plan_text.strip():
            logger.error("Research Manager returned an empty plan.")
            return None

        plan = ResearchPlan.model_validate_json(plan_text)

        # Ensure enabled searches always have queries.
        if plan.web and not plan.web_query.strip():
            plan.web_query = "Relevant information about the user's research topic"

        if plan.news and not plan.news_query.strip():
            plan.news_query = "Latest news about the user's research topic"

        if plan.images and not plan.image_query.strip():
            plan.image_query = "Images related to the user's research topic"

        callback_context.state["research_plan"] = plan.model_dump(
            mode="json"
        )

        logger.info(
            "Research plan stored: web=%s, news=%s, images=%s",
            plan.web,
            plan.news,
            plan.images,
        )
        logger.info(
            "Queries: web=%r, news=%r, images=%r",
            plan.web_query,
            plan.news_query,
            plan.image_query,
        )

        return llm_response.model_copy(
            update={
                "content": None,
                "partial": True,
                "turn_complete": True,
            }
        )

    except Exception:
        logger.exception("Failed to parse or store the research plan.")
        raise


research_manager = LlmAgent(
    name="research_manager",
    model="gemini-3.5-flash-lite",
    mode="single_turn",
    retry_config=RetryConfig(
        max_attempts=3,
        initial_delay=1,
        max_delay=4,
        exceptions=["ServerError"],
    ),
    description=(
        "Plans research and selects the necessary web, news, "
        "and image searches."
    ),
    instruction="""
You are ResearchPilot's general-purpose research planner.

Analyze the user's actual request and produce a structured ResearchPlan.
Do not answer the research question yourself.

SEARCH SELECTION

1. Web search:
Use it when factual information, background, statistics, explanations,
comparisons, or supporting sources are needed.

2. News search:
Enable it when the user requests the latest news, recent developments,
current events, recent announcements, or when recent developments are
an important part of the requested research.

3. Image search:
Enable it whenever the user explicitly requests images, photographs,
pictures, image URLs, or visual references. Also enable it when visual
evidence is clearly important to the requested deliverable.

Enable multiple search types when the request requires them. Do not
restrict a request to web search when the user explicitly asks for news
or images.

QUERIES

Create a focused, non-empty query for every enabled search.
Use separate queries appropriate to web, news, and image search.
Use the user's actual topic, entities, and location.
Do not hard-code any particular topic.

For disabled searches, use an empty query string.

OUTPUT

Return only a valid ResearchPlan matching the provided output schema.
Do not invent results or claim searches have already occurred.
""",
    output_schema=ResearchPlan,
    after_model_callback=_save_plan_without_emitting_it,
)