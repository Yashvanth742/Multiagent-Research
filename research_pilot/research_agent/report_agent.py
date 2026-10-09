from google.adk.agents import Agent
from google.adk.workflow import RetryConfig

report_agent = Agent(
    name="report_generator",
    model="gemini-3.5-flash-lite",
    retry_config=RetryConfig(
        max_attempts=3,
        initial_delay=1,
        max_delay=4,
        exceptions=["ServerError"],
    ),
    description="Generates a report from collected research evidence.",
    instruction="""
You are the ResearchPilot Report Generator.

Use the collected research evidence from session state:

{research_results}

Generate the final report with these sections:

# Executive Summary
# Key Findings
# Recent Developments
# Detailed Analysis
# Images and Visual References
# Sources

Include relevant web and news findings with their source URLs.

For image results, include each image's title, original image URL,
and source-page URL. Preserve URLs exactly as provided.

If a category of evidence is absent, state that it is unavailable.
Never invent facts, findings, dates, images, or URLs.

Use the collected evidence only. Do not perform searches yourself.
Return the completed report, not a status message.
""",
)
