"""
CLI for running the Video Retrieval API server.
"""

import click
from pathlib import Path


@click.group()
def main():
    """Math Content Engine - Video Retrieval API."""
    pass


@main.command()
@click.option(
    "--host",
    default="0.0.0.0",
    help="Host to bind to (default: 0.0.0.0)"
)
@click.option(
    "--port",
    default=8000,
    type=int,
    help="Port to bind to (default: 8000)"
)
@click.option(
    "--db-path",
    type=click.Path(path_type=Path),
    default=None,
    help="Path to SQLite database (default: ./data/videos.db)"
)
@click.option(
    "--reload",
    is_flag=True,
    help="Enable auto-reload for development"
)
def serve(host: str, port: int, db_path: Path, reload: bool):
    """Start the API server."""
    from .server import run_server

    click.echo(f"Starting Math Content Engine API server on {host}:{port}")
    if db_path:
        click.echo(f"Using database: {db_path}")

    run_server(
        host=host,
        port=port,
        db_path=db_path,
        reload=reload,
    )


@main.command()
@click.option(
    "--db-path",
    type=click.Path(path_type=Path),
    default=Path("./data/videos.db"),
    help="Path to SQLite database"
)
def stats(db_path: Path):
    """Show video storage statistics."""
    from .storage import VideoStorage

    storage = VideoStorage(db_path)
    stats = storage.get_stats()

    click.echo("\n=== Video Storage Statistics ===\n")
    click.echo(f"Total videos: {stats['total_videos']}")
    click.echo(f"Successful: {stats['successful_videos']}")
    click.echo(f"Failed: {stats['failed_videos']}")

    if stats['by_interest']:
        click.echo("\nBy Interest:")
        for interest, count in stats['by_interest'].items():
            click.echo(f"  {interest}: {count}")

    if stats['by_style']:
        click.echo("\nBy Style:")
        for style, count in stats['by_style'].items():
            click.echo(f"  {style}: {count}")

    click.echo()


@main.command()
@click.argument("video_id")
@click.option(
    "--db-path",
    type=click.Path(path_type=Path),
    default=Path("./data/videos.db"),
    help="Path to SQLite database"
)
def get(video_id: str, db_path: Path):
    """Get video metadata by ID."""
    from .storage import VideoStorage

    storage = VideoStorage(db_path)
    video = storage.get_by_id(video_id)

    if video is None:
        click.echo(f"Video not found: {video_id}", err=True)
        raise SystemExit(1)

    click.echo(f"\n=== Video: {video_id} ===\n")
    click.echo(f"Topic: {video.topic}")
    click.echo(f"Scene: {video.scene_name}")
    click.echo(f"Path: {video.video_path}")
    click.echo(f"Success: {video.success}")
    click.echo(f"Style: {video.style.value}")
    click.echo(f"Quality: {video.quality.value}")
    click.echo(f"Audience: {video.audience_level}")
    if video.interest:
        click.echo(f"Interest: {video.interest}")
    if video.llm_model:
        click.echo(f"Model: {video.llm_model}")
    click.echo(f"Created: {video.created_at}")
    click.echo()


@main.command("list")
@click.option(
    "--db-path",
    type=click.Path(path_type=Path),
    default=Path("./data/videos.db"),
    help="Path to SQLite database"
)
@click.option("--topic", default=None, help="Filter by topic")
@click.option("--interest", default=None, help="Filter by interest")
@click.option("--limit", default=20, type=int, help="Maximum results")
def list_videos(db_path: Path, topic: str, interest: str, limit: int):
    """List stored videos."""
    from .storage import VideoStorage
    from .models import VideoSearchParams

    storage = VideoStorage(db_path)
    params = VideoSearchParams(
        topic=topic,
        interest=interest,
        page_size=limit,
    )
    videos, total = storage.list_videos(params)

    click.echo(f"\n=== Videos ({len(videos)} of {total}) ===\n")
    for video in videos:
        status = "OK" if video.success else "FAIL"
        click.echo(f"[{status}] {video.id[:8]}... | {video.topic} | {video.scene_name}")

    click.echo()


if __name__ == "__main__":
    main()
