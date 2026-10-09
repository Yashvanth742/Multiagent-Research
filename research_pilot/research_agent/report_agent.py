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

### Clickable Links and Images

- Always format source URLs as Markdown hyperlinks:
  [Source Page](https://example.com/article)

- For image references, use:
  [View Original Image](https://example.com/image.jpg)

- Never put URLs inside inline code or fenced code blocks.
- Do not output raw URLs when a Markdown hyperlink can be used.
- When an image URL is valid and accessible, render it using:
  ![Image description](https://example.com/image.jpg)

- Keep the original source page link alongside each image.

### Images and Visual References

- Display relevant images as small, visually balanced thumbnails within the research report.
- Each image should appear at approximately one-sixth to one-quarter of the report's content width, similar to images in a professional research article.
- Maintain the original aspect ratio without stretching or distortion.
- Place the image title above or beside the thumbnail.
- Make each thumbnail clickable so users can open the original image in a new tab.
- Include a clickable **Source Page** link below each image.
- Display images in a compact gallery when multiple images are available, with consistent spacing and alignment.
- Show only 3–5 relevant images, prioritizing the most useful results.
- Never allow an image to expand to the full report width by default.
- Do not embed full-size images directly into Markdown using `![title](url)` if the renderer displays them at excessive size.
- Preserve the original image URLs and source page URLs returned by SerpApi. Never invent or modify URLs.
- If the current interface cannot control image dimensions, display compact clickable image links instead of embedding the images.
- Keep the section clean, responsive, and consistent with a professional AI research report.
""",
)
