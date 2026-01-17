"""Interactive REPL for prompt engineering sessions."""

import os
import sys
import subprocess
import shlex
from pathlib import Path
from typing import Optional

from ..prompt.models import AnimationPrompt, PromptSession
from ..session.manager import SessionManager
from ..suggest.engine import SuggestionEngine
from ..compare.diff import diff_prompts, diff_code, format_prompt_diff, format_code_diff, compare_results


class InteractiveSession:
    """Interactive REPL for prompt engineering."""

    def __init__(self, session: PromptSession, manager: SessionManager):
        """Initialize interactive session."""
        self.session = session
        self.manager = manager
        self.suggestion_engine = SuggestionEngine()
        self.running = True

    def print_header(self) -> None:
        """Print session header."""
        print("\n" + "=" * 60)
        print("         Animation Prompt Engineering Lab")
        print("=" * 60)
        print(f"  Session: {self.session.session_id}")
        if self.session.current_prompt:
            print(f"  Topic:   {self.session.current_prompt.topic}")
        print("=" * 60 + "\n")

    def print_prompt(self) -> None:
        """Print current prompt state."""
        prompt = self.session.current_prompt
        if not prompt:
            print("No prompt set.")
            return

        print("\n--- PROMPT " + "-" * 49)
        print(f"Topic: {prompt.topic}")
        if prompt.requirements:
            print("Requirements:")
            for i, req in enumerate(prompt.requirements, 1):
                print(f"  {i}. {req}")
        else:
            print("Requirements: (none)")
        print(f"Style: {prompt.style} | Audience: {prompt.audience}", end="")
        if prompt.pacing:
            print(f" | Pacing: {prompt.pacing}")
        else:
            print()
        print("-" * 60 + "\n")

    def print_help(self) -> None:
        """Print help message."""
        print("""
Commands:
  prompt              Show current prompt
  add <text>          Add a requirement
  remove <n>          Remove requirement #n
  topic <text>        Change the topic
  style <dark|light>  Change animation style
  pacing <slow|medium|fast>  Set animation pacing

  generate            Generate code and render video
  generate --no-render  Generate code only (skip rendering)
  show [version]      Show generated code
  play [version]      Open video in player
  render [version]    Render a version that wasn't rendered

  ask <question>      Get suggestions (e.g., "ask how to make it slower")
  suggest             Get general improvement suggestions

  versions            List all versions
  compare <n> <m>     Compare two versions (e.g., "compare 1 2")
  diff <n> <m>        Show code diff between versions

  export [file]       Export current code to file
  history             Show prompt history

  help                Show this help
  quit                Exit (session is auto-saved)
""")

    def run(self) -> None:
        """Run the interactive session."""
        self.print_header()
        self.print_prompt()
        print("Type 'help' for commands, 'generate' to create animation.\n")

        while self.running:
            try:
                user_input = input("prompt> ").strip()
                if not user_input:
                    continue

                self.handle_command(user_input)

            except KeyboardInterrupt:
                print("\n\nUse 'quit' to exit.")
            except EOFError:
                self.running = False
                print("\nSession saved.")

        print(f"\nSession saved. Resume with: math-lab resume {self.session.session_id}")

    def handle_command(self, user_input: str) -> None:
        """Handle a single command."""
        parts = shlex.split(user_input)
        if not parts:
            return

        cmd = parts[0].lower()
        args = parts[1:]

        commands = {
            "help": self.cmd_help,
            "quit": self.cmd_quit,
            "exit": self.cmd_quit,
            "prompt": self.cmd_prompt,
            "add": self.cmd_add,
            "remove": self.cmd_remove,
            "topic": self.cmd_topic,
            "style": self.cmd_style,
            "pacing": self.cmd_pacing,
            "generate": self.cmd_generate,
            "show": self.cmd_show,
            "play": self.cmd_play,
            "render": self.cmd_render,
            "ask": self.cmd_ask,
            "suggest": self.cmd_suggest,
            "versions": self.cmd_versions,
            "compare": self.cmd_compare,
            "diff": self.cmd_diff,
            "export": self.cmd_export,
            "history": self.cmd_history,
        }

        handler = commands.get(cmd)
        if handler:
            handler(args)
        else:
            # Check if it might be a question
            if user_input.endswith("?") or user_input.startswith("how"):
                self.cmd_ask([user_input])
            else:
                print(f"Unknown command: {cmd}. Type 'help' for available commands.")

    def cmd_help(self, args: list[str]) -> None:
        """Show help."""
        self.print_help()

    def cmd_quit(self, args: list[str]) -> None:
        """Exit the session."""
        self.manager.save_session(self.session)
        self.running = False

    def cmd_prompt(self, args: list[str]) -> None:
        """Show current prompt."""
        self.print_prompt()

    def cmd_add(self, args: list[str]) -> None:
        """Add a requirement."""
        if not args:
            print("Usage: add <requirement text>")
            return

        requirement = " ".join(args)
        prompt = self.session.current_prompt
        if not prompt:
            prompt = AnimationPrompt(topic="Untitled")
            self.session.set_working_prompt(prompt)

        prompt.add_requirement(requirement)
        self.manager.save_session(self.session)
        print(f"✓ Added: \"{requirement}\"")

    def cmd_remove(self, args: list[str]) -> None:
        """Remove a requirement by number."""
        if not args:
            print("Usage: remove <number>")
            return

        try:
            index = int(args[0]) - 1  # Convert to 0-based
            prompt = self.session.current_prompt
            if prompt:
                removed = prompt.remove_requirement(index)
                if removed:
                    self.manager.save_session(self.session)
                    print(f"✓ Removed: \"{removed}\"")
                else:
                    print(f"Invalid requirement number: {args[0]}")
            else:
                print("No prompt set.")
        except ValueError:
            print("Please provide a valid number.")

    def cmd_topic(self, args: list[str]) -> None:
        """Change the topic."""
        if not args:
            print("Usage: topic <new topic>")
            return

        new_topic = " ".join(args)
        prompt = self.session.current_prompt
        if prompt:
            prompt.topic = new_topic
        else:
            prompt = AnimationPrompt(topic=new_topic)
            self.session.set_working_prompt(prompt)

        self.manager.save_session(self.session)
        print(f"✓ Topic changed to: \"{new_topic}\"")

    def cmd_style(self, args: list[str]) -> None:
        """Change animation style."""
        if not args or args[0].lower() not in ["dark", "light"]:
            print("Usage: style <dark|light>")
            return

        prompt = self.session.current_prompt
        if prompt:
            prompt.style = args[0].lower()
            self.manager.save_session(self.session)
            print(f"✓ Style set to: {prompt.style}")
        else:
            print("No prompt set. Use 'topic' to create one first.")

    def cmd_pacing(self, args: list[str]) -> None:
        """Set animation pacing."""
        valid_pacing = ["slow", "medium", "fast"]
        if not args or args[0].lower() not in valid_pacing:
            print(f"Usage: pacing <{'/'.join(valid_pacing)}>")
            return

        prompt = self.session.current_prompt
        if prompt:
            prompt.pacing = args[0].lower()
            self.manager.save_session(self.session)
            print(f"✓ Pacing set to: {prompt.pacing}")
        else:
            print("No prompt set. Use 'topic' to create one first.")

    def cmd_generate(self, args: list[str]) -> None:
        """Generate code and optionally render."""
        prompt = self.session.current_prompt
        if not prompt:
            print("No prompt set. Use 'topic' to set a topic first.")
            return

        render = "--no-render" not in args
        quality = "l"  # Default to low quality for fast preview

        for i, arg in enumerate(args):
            if arg in ["-q", "--quality"] and i + 1 < len(args):
                quality = args[i + 1]

        print(f"\nGenerating v{self.session.next_version}...")

        result = self.manager.generate(self.session, render=render, quality=quality)

        if result.success:
            print(f"✓ Code generated: {result.scene_name} ({len(result.code.splitlines())} lines)")
            if result.video_path:
                print(f"✓ Rendered in {result.render_time_ms / 1000:.1f}s → {result.video_path}")
            elif render:
                print("⚠ Render failed. Use 'show' to see the code.")
        else:
            print(f"✗ Generation failed: {result.error}")

    def cmd_show(self, args: list[str]) -> None:
        """Show generated code."""
        version = None
        if args:
            try:
                version = int(args[0].replace("v", ""))
            except ValueError:
                print("Usage: show [version]")
                return

        if version:
            result = self.session.get_version(version)
        else:
            result = self.session.current

        if not result:
            print("No code generated yet. Use 'generate' first.")
            return

        print(f"\n--- CODE v{result.version}: {result.scene_name} ({len(result.code.splitlines())} lines) ---")
        print(result.code)
        print("-" * 60)

    def cmd_play(self, args: list[str]) -> None:
        """Open video in player."""
        version = None
        if args:
            try:
                version = int(args[0].replace("v", ""))
            except ValueError:
                print("Usage: play [version]")
                return

        if version:
            result = self.session.get_version(version)
        else:
            result = self.session.current

        if not result:
            print("No video generated yet. Use 'generate' first.")
            return

        if not result.video_path:
            print(f"v{result.version} was not rendered. Use 'render {result.version}' first.")
            return

        video_path = Path(result.video_path)
        if not video_path.exists():
            print(f"Video file not found: {video_path}")
            return

        print(f"Opening: {video_path}")

        # Open with system default player
        if sys.platform == "darwin":
            subprocess.run(["open", str(video_path)], check=False)
        elif sys.platform == "win32":
            os.startfile(str(video_path))
        else:
            subprocess.run(["xdg-open", str(video_path)], check=False)

    def cmd_render(self, args: list[str]) -> None:
        """Render a specific version."""
        version = None
        if args:
            try:
                version = int(args[0].replace("v", ""))
            except ValueError:
                pass

        if version is None:
            result = self.session.current
            if result:
                version = result.version
            else:
                print("No version to render. Use 'generate' first.")
                return

        quality = "l"
        for i, arg in enumerate(args):
            if arg in ["-q", "--quality"] and i + 1 < len(args):
                quality = args[i + 1]

        print(f"Rendering v{version}...")

        video_path = self.manager.render_version(self.session, version, quality)

        if video_path:
            result = self.session.get_version(version)
            print(f"✓ Rendered → {video_path}")
        else:
            print("✗ Render failed")

    def cmd_ask(self, args: list[str]) -> None:
        """Ask for suggestions on how to change the animation."""
        if not args:
            print("Usage: ask <question>")
            print("Example: ask how do I make it slower?")
            return

        question = " ".join(args)
        prompt = self.session.current_prompt

        print("\n--- SUGGESTIONS ---")
        suggestions = self.suggestion_engine.suggest_from_request(question, prompt)

        if not suggestions:
            print("No specific suggestions found for that request.")
            print("Try describing what you want to change (e.g., 'slower', 'more colors', 'one at a time')")
            return

        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n{i}. {suggestion.description}")
            for req in suggestion.requirements_to_add:
                print(f"   + \"{req}\"")
            if suggestion.pacing:
                print(f"   (Sets pacing to: {suggestion.pacing})")

        print(f"\nApply suggestion? [1-{len(suggestions)}/none]: ", end="")
        try:
            choice = input().strip()
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(suggestions):
                    suggestion = suggestions[idx]
                    if prompt:
                        new_prompt = suggestion.apply_to(prompt)
                        self.session.set_working_prompt(new_prompt)
                        self.manager.save_session(self.session)
                        print("✓ Suggestion applied!")
                        self.print_prompt()
                else:
                    print("No changes made.")
            elif choice.lower() not in ["", "none", "n", "no"]:
                print("No changes made.")
        except (EOFError, KeyboardInterrupt):
            print("\nNo changes made.")

    def cmd_suggest(self, args: list[str]) -> None:
        """Get general improvement suggestions."""
        prompt = self.session.current_prompt
        if not prompt:
            print("No prompt set. Use 'topic' to create one first.")
            return

        code = None
        if self.session.current:
            code = self.session.current.code

        print("\n--- IMPROVEMENT SUGGESTIONS ---")
        suggestions = self.suggestion_engine.suggest_improvements(prompt, code)

        if not suggestions:
            print("No suggestions at this time.")
            return

        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n{i}. {suggestion.description}")
            for req in suggestion.requirements_to_add:
                print(f"   + \"{req}\"")

        print(f"\nApply suggestion? [1-{len(suggestions)}/none]: ", end="")
        try:
            choice = input().strip()
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(suggestions):
                    suggestion = suggestions[idx]
                    new_prompt = suggestion.apply_to(prompt)
                    self.session.set_working_prompt(new_prompt)
                    self.manager.save_session(self.session)
                    print("✓ Suggestion applied!")
                    self.print_prompt()
        except (EOFError, KeyboardInterrupt):
            print("\nNo changes made.")

    def cmd_versions(self, args: list[str]) -> None:
        """List all versions."""
        if not self.session.history:
            print("No versions yet. Use 'generate' to create one.")
            return

        print("\n--- VERSIONS ---")
        print(f"{'Ver':<5} {'Lines':<7} {'Rendered':<10} {'Requirements'}")
        print("-" * 60)

        current_ver = self.session.current.version if self.session.current else None

        for result in self.session.history:
            marker = "*" if result.version == current_ver else " "
            lines = len(result.code.splitlines())
            rendered = "✓" if result.video_path else "-"
            reqs = ", ".join(result.prompt.requirements[:2])
            if len(result.prompt.requirements) > 2:
                reqs += "..."

            print(f"v{result.version}{marker:<3} {lines:<7} {rendered:<10} {reqs[:40]}")

        print("-" * 60)
        print("* = current version")

    def cmd_compare(self, args: list[str]) -> None:
        """Compare two versions."""
        if len(args) < 2:
            print("Usage: compare <v1> <v2>")
            print("Example: compare 1 2")
            return

        try:
            v1 = int(args[0].replace("v", ""))
            v2 = int(args[1].replace("v", ""))
        except ValueError:
            print("Please provide valid version numbers.")
            return

        result1 = self.session.get_version(v1)
        result2 = self.session.get_version(v2)

        if not result1 or not result2:
            print(f"Version not found. Available: 1-{len(self.session.history)}")
            return

        comparison = compare_results(result1, result2)

        print(f"\n--- COMPARISON: v{v1} → v{v2} ---")

        print("\nPrompt changes:")
        print(format_prompt_diff(comparison["prompt_diff"]))

        print(f"\nCode: {comparison['v1_lines']} → {comparison['v2_lines']} lines", end="")
        if comparison["lines_diff"] > 0:
            print(f" (+{comparison['lines_diff']})")
        elif comparison["lines_diff"] < 0:
            print(f" ({comparison['lines_diff']})")
        else:
            print(" (no change)")

        if comparison["v1_video"] and comparison["v2_video"]:
            print(f"\nVideos: v{v1}={comparison['v1_render_time']/1000:.1f}s, v{v2}={comparison['v2_render_time']/1000:.1f}s")

        print("-" * 60)

    def cmd_diff(self, args: list[str]) -> None:
        """Show code diff between versions."""
        if len(args) < 2:
            print("Usage: diff <v1> <v2>")
            return

        try:
            v1 = int(args[0].replace("v", ""))
            v2 = int(args[1].replace("v", ""))
        except ValueError:
            print("Please provide valid version numbers.")
            return

        result1 = self.session.get_version(v1)
        result2 = self.session.get_version(v2)

        if not result1 or not result2:
            print(f"Version not found. Available: 1-{len(self.session.history)}")
            return

        diff = diff_code(result1.code, result2.code)
        print(f"\n--- CODE DIFF: v{v1} → v{v2} ---")
        print(format_code_diff(diff))

    def cmd_export(self, args: list[str]) -> None:
        """Export code to file."""
        output_path = None
        if args:
            output_path = Path(args[0])

        try:
            path = self.manager.export_code(self.session, output_path=output_path)
            print(f"✓ Exported → {path}")
        except ValueError as e:
            print(f"Error: {e}")

    def cmd_history(self, args: list[str]) -> None:
        """Show prompt history across versions."""
        if not self.session.history:
            print("No history yet.")
            return

        print("\n--- PROMPT HISTORY ---")
        for result in self.session.history:
            print(f"\nv{result.version}: {result.prompt.topic}")
            if result.prompt.requirements:
                for req in result.prompt.requirements:
                    print(f"  - {req}")
            else:
                print("  (no requirements)")
        print()
