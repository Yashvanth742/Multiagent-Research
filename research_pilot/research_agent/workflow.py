import asyncio
import logging
from typing import Any

from google.adk import Workflow
from google.adk.agents import Context
from google.adk.workflow import START

from .research_manager import research_manager
from .schemas import ResearchPlan
from .searches.image_search import run_image_search
from .searches.news_search import run_news_search
from .searches.web_search import run_web_search
from .report_agent import report_agent


MAX_RESULTS_PER_SEARCH = 10
logger = logging.getLogger(__name__)


def _research_plan_from_input(node_input: Any) -> ResearchPlan:
    """Parse the structured research plan."""

    if isinstance(node_input, ResearchPlan):
        return node_input

    if isinstance(node_input, dict):
        return ResearchPlan.model_validate(node_input)

    if isinstance(node_input, str):
        return ResearchPlan.model_validate_json(node_input)

    parts = getattr(node_input, "parts", None)

    if parts is not None:
        text = "".join(
            part.text or ""
            for part in parts
            if getattr(part, "text", None) is not None
        )
        return ResearchPlan.model_validate_json(text)

    return ResearchPlan.model_validate(node_input)


def _format_search_evidence(
    title: str,
    query: str,
    records: list[dict[str, Any]],
) -> str:
    """Format web or news search results."""

    lines = [
        f"## {title}",
        f"Search query: {query}",
    ]

    if not records:
        lines.append("No readable results were returned.")
        return "\n".join(lines)

    for index, item in enumerate(
        records[:MAX_RESULTS_PER_SEARCH],
        start=1,
    ):
        lines.extend([
            "",
            f"### Result {index}: "
            f"{item.get('title') or 'Untitled result'}",
        ])

        for label, key in [
            ("Source", "source"),
            ("Publication date", "date"),
            ("Summary", "snippet"),
            ("URL", "url"),
        ]:
            value = item.get(key)
            if value:
                lines.append(f"{label}: {value}")

    return "\n".join(lines)


def _format_image_evidence(
    query: str,
    records: list[dict[str, Any]],
) -> str:
    """Format Google Images results with their URLs."""

    lines = [
        "## IMAGE RESULTS",
        f"Search query: {query}",
    ]

    if not records:
        lines.append("No image results were returned.")
        return "\n".join(lines)

    for index, item in enumerate(
        records[:MAX_RESULTS_PER_SEARCH],
        start=1,
    ):
        lines.extend([
            "",
            f"### Image {index}: "
            f"{item.get('title') or 'Image result'}",
        ])

        for label, key in [
            ("Source", "source_name"),
            ("Thumbnail URL", "thumbnail_url"),
            ("Original image URL", "original_url"),
            ("Source page URL", "source_page_url"),
        ]:
            value = item.get(key)
            if value:
                lines.append(f"{label}: {value}")

    return "\n".join(lines)


async def execute_research(
    node_input: Any,
    ctx: Context,
) -> None:
    """Execute each enabled search and store the combined evidence."""

    plan_data = ctx.state.get("research_plan")

    if plan_data is not None:
        plan = ResearchPlan.model_validate(plan_data)
    else:
        plan = _research_plan_from_input(node_input)

    logger.info("Research plan: %s", plan.model_dump_json())

    evidence_sections = []

    if plan.web:
        logger.info("Starting one Google web search")

        records = await asyncio.to_thread(
            run_web_search,
            plan.web_query,
        )

        logger.info("Web results extracted: %d", len(records))

        evidence_sections.append(
            _format_search_evidence(
                "WEB SEARCH",
                plan.web_query,
                records,
            )
        )

    if plan.news:
        logger.info("Starting one Google News search")

        records = await asyncio.to_thread(
            run_news_search,
            plan.news_query,
        )

        logger.info("News results extracted: %d", len(records))

        evidence_sections.append(
            _format_search_evidence(
                "NEWS SEARCH",
                plan.news_query,
                records,
            )
        )

    if plan.images:
        logger.info("Starting one Google Images search")

        records = await asyncio.to_thread(
            run_image_search,
            plan.image_query,
        )

        logger.info("Image results extracted: %d", len(records))

        evidence_sections.append(
            _format_image_evidence(
                plan.image_query,
                records,
            )
        )

    evidence = "\n\n".join(evidence_sections)

    if not evidence:
        evidence = (
            "No external research results were retrieved. "
            "Do not invent findings or claim searches were performed."
        )

    # Store the evidence for the report agent.
    ctx.state["research_results"] = evidence

    logger.info(
        "Research evidence stored: %d characters",
        len(evidence),
    )

    logger.info(
        "IMAGE EVIDENCE PRESENT: %s",
        "## IMAGE RESULTS" in evidence,
    )

    return None


root_agent = Workflow(
    name="research_pipeline",
    edges=[
        (START, research_manager, execute_research, report_agent),
    ],
)
