"""
Artifact tools for the Content Creation Studio.

Artifacts are named, versioned binary/text data stored alongside sessions.
They let agents save and retrieve generated content (blog posts, social media, etc.)

Key concepts:
  - Artifacts are saved per session by default
  - Use "user:" prefix in filename for cross-session artifacts
  - Each save returns an incremented version number
  - InMemoryArtifactService for dev, GcsArtifactService for production
"""

from google.adk.tools import ToolContext
from google.genai import types


async def save_content_artifact(
    tool_context: ToolContext,
    filename: str,
    content: str,
) -> dict:
    """Saves generated content as a versioned artifact.

    Args:
        tool_context: Provided automatically by ADK.
        filename: Name for the artifact (e.g. 'blog_post.md').
        content: The text content to save.

    Returns:
        Dict with filename and version number.
    """
    print(f"🔧 Tool: Saving artifact '{filename}'...")
    artifact = types.Part.from_text(text=content)
    version = await tool_context.save_artifact(filename=filename, artifact=artifact)
    print(f"   Saved: {filename} (version {version})")
    return {"filename": filename, "version": version}


async def list_content_artifacts(tool_context: ToolContext) -> list:
    """Lists all artifact filenames saved in the current session.

    Returns:
        List of artifact filenames.
    """
    print(f"🔧 Tool: Listing artifacts...")
    filenames = await tool_context.list_artifacts()
    print(f"   Found: {filenames}")
    return filenames


async def load_content_artifact(
    tool_context: ToolContext,
    filename: str,
) -> str:
    """Loads a previously saved artifact by filename.

    Args:
        tool_context: Provided automatically by ADK.
        filename: Name of the artifact to load.

    Returns:
        The artifact text content, or an error message if not found.
    """
    print(f"🔧 Tool: Loading artifact '{filename}'...")
    artifact = await tool_context.load_artifact(filename=filename)
    if artifact and artifact.text:
        print(f"   Loaded: {filename} ({len(artifact.text)} chars)")
        return artifact.text
    print(f"   Not found: {filename}")
    return f"Artifact '{filename}' not found."
