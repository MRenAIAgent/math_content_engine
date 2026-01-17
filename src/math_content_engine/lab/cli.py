"""CLI entry point for Animation Prompt Engineering Lab."""

import click
from pathlib import Path
from typing import Optional

from .prompt.models import AnimationPrompt
from .session.manager import SessionManager
from .session.storage import SessionStorage
from .interactive.repl import InteractiveSession


@click.group()
@click.pass_context
def main(ctx):
    """Animation Prompt Engineering Lab.

    Iteratively design math animations through prompt engineering.
    """
    ctx.ensure_object(dict)
    ctx.obj["storage"] = SessionStorage()
    ctx.obj["manager"] = SessionManager(storage=ctx.obj["storage"])


@main.command("new")
@click.argument("topic")
@click.option("-r", "--requirement", multiple=True, help="Add a requirement")
@click.option("-i", "--interactive", is_flag=True, help="Start interactive mode")
@click.option("--style", type=click.Choice(["dark", "light"]), default="dark", help="Animation style")
@click.option("--audience", default="high school", help="Target audience level")
@click.pass_context
def new_session(ctx, topic: str, requirement: tuple, interactive: bool, style: str, audience: str):
    """Create a new prompt engineering session.

    Example:
        math-lab new "Pythagorean theorem"
        math-lab new "Quadratic formula" -r "Show graphical solution" -i
    """
    manager: SessionManager = ctx.obj["manager"]

    session = manager.create_session(topic, list(requirement))
    session.current_prompt.style = style
    session.current_prompt.audience = audience
    manager.save_session(session)

    click.echo(f"Created session: {session.session_id}")
    click.echo(f"Topic: {topic}")

    if interactive:
        repl = InteractiveSession(session, manager)
        repl.run()
    else:
        click.echo(f"\nStart interactive mode with: math-lab resume {session.session_id}")


@main.command("resume")
@click.argument("session_id")
@click.pass_context
def resume_session(ctx, session_id: str):
    """Resume an existing session in interactive mode.

    Example:
        math-lab resume ses_abc123
    """
    manager: SessionManager = ctx.obj["manager"]

    session = manager.load_session(session_id)
    if not session:
        click.echo(f"Session not found: {session_id}")
        raise SystemExit(1)

    repl = InteractiveSession(session, manager)
    repl.run()


@main.command("list")
@click.option("-n", "--limit", default=10, help="Number of sessions to show")
@click.pass_context
def list_sessions(ctx, limit: int):
    """List recent sessions.

    Example:
        math-lab list
        math-lab list -n 20
    """
    manager: SessionManager = ctx.obj["manager"]

    sessions = manager.list_sessions(limit)

    if not sessions:
        click.echo("No sessions found.")
        return

    click.echo(f"\n{'ID':<15} {'Topic':<30} {'Versions':<10} {'Updated'}")
    click.echo("-" * 70)

    for s in sessions:
        topic = s["topic"][:28] + ".." if len(s["topic"]) > 30 else s["topic"]
        click.echo(f"{s['session_id']:<15} {topic:<30} {s['versions']:<10} {s['updated_at'][:10]}")

    click.echo()


@main.command("show")
@click.argument("session_id")
@click.pass_context
def show_session(ctx, session_id: str):
    """Show details of a session.

    Example:
        math-lab show ses_abc123
    """
    manager: SessionManager = ctx.obj["manager"]

    session = manager.load_session(session_id)
    if not session:
        click.echo(f"Session not found: {session_id}")
        raise SystemExit(1)

    click.echo(f"\nSession: {session.session_id}")
    click.echo(f"Created: {session.created_at}")
    click.echo(f"Updated: {session.updated_at}")

    prompt = session.current_prompt
    if prompt:
        click.echo(f"\nTopic: {prompt.topic}")
        click.echo(f"Style: {prompt.style} | Audience: {prompt.audience}")
        if prompt.requirements:
            click.echo("Requirements:")
            for i, req in enumerate(prompt.requirements, 1):
                click.echo(f"  {i}. {req}")

    click.echo(f"\nVersions: {len(session.history)}")
    for result in session.history:
        status = "✓" if result.video_path else "-"
        click.echo(f"  v{result.version}: {result.scene_name} [{status}]")


@main.command("delete")
@click.argument("session_id")
@click.option("--force", is_flag=True, help="Skip confirmation")
@click.pass_context
def delete_session(ctx, session_id: str, force: bool):
    """Delete a session.

    Example:
        math-lab delete ses_abc123
    """
    manager: SessionManager = ctx.obj["manager"]

    if not force:
        click.confirm(f"Delete session {session_id}?", abort=True)

    if manager.delete_session(session_id):
        click.echo(f"Deleted: {session_id}")
    else:
        click.echo(f"Session not found: {session_id}")


@main.command("generate")
@click.argument("session_id")
@click.option("-q", "--quality", type=click.Choice(["l", "m", "h"]), default="l",
              help="Video quality (l=480p, m=720p, h=1080p)")
@click.option("--no-render", is_flag=True, help="Generate code only, skip rendering")
@click.pass_context
def generate(ctx, session_id: str, quality: str, no_render: bool):
    """Generate animation for a session.

    Example:
        math-lab generate ses_abc123
        math-lab generate ses_abc123 -q h
    """
    manager: SessionManager = ctx.obj["manager"]

    session = manager.load_session(session_id)
    if not session:
        click.echo(f"Session not found: {session_id}")
        raise SystemExit(1)

    click.echo(f"Generating v{session.next_version}...")

    result = manager.generate(session, render=not no_render, quality=quality)

    if result.success:
        click.echo(f"✓ Generated: {result.scene_name} ({len(result.code.splitlines())} lines)")
        if result.video_path:
            click.echo(f"✓ Rendered: {result.video_path}")
    else:
        click.echo(f"✗ Failed: {result.error}")
        raise SystemExit(1)


@main.command("export")
@click.argument("session_id")
@click.option("-v", "--version", type=int, help="Version to export (default: latest)")
@click.option("-o", "--output", type=click.Path(), help="Output file path")
@click.pass_context
def export_code(ctx, session_id: str, version: Optional[int], output: Optional[str]):
    """Export generated code to a file.

    Example:
        math-lab export ses_abc123 -o my_animation.py
    """
    manager: SessionManager = ctx.obj["manager"]

    session = manager.load_session(session_id)
    if not session:
        click.echo(f"Session not found: {session_id}")
        raise SystemExit(1)

    output_path = Path(output) if output else None

    try:
        path = manager.export_code(session, version=version, output_path=output_path)
        click.echo(f"✓ Exported: {path}")
    except ValueError as e:
        click.echo(f"Error: {e}")
        raise SystemExit(1)


# Shortcut: math-lab "topic" is equivalent to math-lab new "topic" -i
@main.command("prompt", hidden=True)
@click.argument("topic")
@click.option("-r", "--requirement", multiple=True, help="Add a requirement")
@click.option("-i", "--interactive", is_flag=True, default=True, help="Start interactive mode")
@click.pass_context
def prompt_shortcut(ctx, topic: str, requirement: tuple, interactive: bool):
    """Shortcut for creating and starting interactive session."""
    ctx.invoke(new_session, topic=topic, requirement=requirement, interactive=interactive)


if __name__ == "__main__":
    main()
