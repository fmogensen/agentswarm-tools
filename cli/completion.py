"""
Shell Auto-Completion for AgentSwarm CLI

Generates shell completion scripts for bash, zsh, and fish.
"""

import os
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel

console = Console()


class CompletionManager:
    """Manage shell auto-completion."""

    def __init__(self):
        """Initialize completion manager."""
        self.supported_shells = ["bash", "zsh", "fish"]

    def generate_bash_completion(self) -> str:
        """
        Generate bash completion script.

        Returns:
            Bash completion script
        """
        return """# AgentSwarm CLI bash completion

_agentswarm_completions() {
    local cur prev opts tools categories commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Main commands
    commands="list info run test validate config interactive workflow history completion"

    # Get tool names (dynamic - would be generated from actual tools)
    tools="web_search scholar_search image_search video_search product_search \
           google_product_search financial_report stock_price crawler \
           summarize_large_document url_metadata webpage_capture_screen \
           resource_discovery image_generation video_generation audio_generation \
           understand_images understand_video batch_understand_videos \
           analyze_media_content audio_transcribe merge_audio extract_audio_from_video \
           aidrive_tool file_format_converter onedrive_search onedrive_file_read \
           gmail_search gmail_read read_email_attachments email_draft \
           google_calendar_list google_calendar_create_event_draft phone_call \
           query_call_logs maps_search notion_search notion_read think \
           ask_for_clarification create_agent"

    # Tool categories
    categories="data communication media visualization content infrastructure utils integrations"

    # First argument - main command
    if [ $COMP_CWORD -eq 1 ]; then
        COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
        return 0
    fi

    # Second argument - context-specific
    case "${COMP_WORDS[1]}" in
        list)
            opts="--category --format --categories"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            ;;
        info|run|test)
            if [ $COMP_CWORD -eq 2 ]; then
                COMPREPLY=( $(compgen -W "${tools}" -- ${cur}) )
            else
                opts="--params --interactive --output --format --mock --verbose"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            fi
            ;;
        workflow)
            opts="create run list delete"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            ;;
        history)
            opts="list replay clear stats"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            ;;
        completion)
            opts="install show --shell"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            ;;
        config)
            opts="--show --set --get --reset --validate"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            ;;
        *)
            ;;
    esac

    # Handle --category flag
    if [ "${prev}" == "--category" ]; then
        COMPREPLY=( $(compgen -W "${categories}" -- ${cur}) )
        return 0
    fi

    # Handle --format flag
    if [ "${prev}" == "--format" ]; then
        COMPREPLY=( $(compgen -W "json yaml table text" -- ${cur}) )
        return 0
    fi

    # Handle --shell flag
    if [ "${prev}" == "--shell" ]; then
        COMPREPLY=( $(compgen -W "bash zsh fish" -- ${cur}) )
        return 0
    fi
}

complete -F _agentswarm_completions agentswarm
"""

    def generate_zsh_completion(self) -> str:
        """
        Generate zsh completion script.

        Returns:
            Zsh completion script
        """
        return """#compdef agentswarm

# AgentSwarm CLI zsh completion

_agentswarm() {
    local -a commands tools categories

    commands=(
        'list:List available tools'
        'info:Show tool information'
        'run:Run a tool'
        'test:Test a tool'
        'validate:Validate tools'
        'config:Manage configuration'
        'interactive:Launch interactive mode'
        'workflow:Manage workflows'
        'history:View command history'
        'completion:Manage shell completion'
    )

    tools=(
        'web_search:Search the web'
        'scholar_search:Search academic papers'
        'image_search:Search for images'
        'video_search:Search for videos'
        'product_search:Search for products'
        'image_generation:Generate images'
        'video_generation:Generate videos'
        'audio_generation:Generate audio'
        'crawler:Crawl web pages'
        'gmail_search:Search Gmail'
        'create_agent:Create AI agent'
    )

    categories=(
        'data:Search and information retrieval'
        'communication:Email and messaging'
        'media:Image, video, and audio'
        'visualization:Charts and graphs'
        'content:Documents and web content'
        'infrastructure:Code execution and storage'
        'utils:Utility tools'
        'integrations:External services'
    )

    if (( CURRENT == 2 )); then
        _describe -t commands 'agentswarm commands' commands
        return
    fi

    case "$words[2]" in
        list)
            _arguments \
                '(-c --category)'{-c,--category}'[Filter by category]:category:->categories' \
                '(-f --format)'{-f,--format}'[Output format]:format:(table json yaml)' \
                '--categories[List all categories]'
            ;;
        info|run|test)
            if (( CURRENT == 3 )); then
                _describe -t tools 'tools' tools
            else
                _arguments \
                    '(-p --params)'{-p,--params}'[Parameters as JSON]:params:' \
                    '(-i --interactive)'{-i,--interactive}'[Interactive mode]' \
                    '(-o --output)'{-o,--output}'[Output file]:file:_files' \
                    '(-f --format)'{-f,--format}'[Output format]:format:(json yaml text)' \
                    '(-m --mock)'{-m,--mock}'[Use mock mode]' \
                    '(-v --verbose)'{-v,--verbose}'[Verbose output]'
            fi
            ;;
        workflow)
            local -a workflow_cmds
            workflow_cmds=(
                'create:Create new workflow'
                'run:Run workflow'
                'list:List workflows'
                'delete:Delete workflow'
            )
            _describe -t workflow_commands 'workflow commands' workflow_cmds
            ;;
        history)
            local -a history_cmds
            history_cmds=(
                'list:List command history'
                'replay:Replay command'
                'clear:Clear history'
                'stats:Show statistics'
            )
            _describe -t history_commands 'history commands' history_cmds
            ;;
        completion)
            local -a completion_cmds
            completion_cmds=(
                'install:Install completion'
                'show:Show completion script'
            )
            _describe -t completion_commands 'completion commands' completion_cmds
            _arguments '--shell[Shell type]:shell:(bash zsh fish)'
            ;;
        config)
            _arguments \
                '--show[Show configuration]' \
                '--set[Set value]:value:' \
                '--get[Get value]:key:' \
                '--reset[Reset configuration]' \
                '--validate[Validate configuration]'
            ;;
    esac

    case "$state" in
        categories)
            _describe -t categories 'categories' categories
            ;;
    esac
}

_agentswarm "$@"
"""

    def generate_fish_completion(self) -> str:
        """
        Generate fish completion script.

        Returns:
            Fish completion script
        """
        return """# AgentSwarm CLI fish completion

# Main commands
complete -c agentswarm -f -n "__fish_use_subcommand" -a "list" -d "List available tools"
complete -c agentswarm -f -n "__fish_use_subcommand" -a "info" -d "Show tool information"
complete -c agentswarm -f -n "__fish_use_subcommand" -a "run" -d "Run a tool"
complete -c agentswarm -f -n "__fish_use_subcommand" -a "test" -d "Test a tool"
complete -c agentswarm -f -n "__fish_use_subcommand" -a "validate" -d "Validate tools"
complete -c agentswarm -f -n "__fish_use_subcommand" -a "config" -d "Manage configuration"
complete -c agentswarm -f -n "__fish_use_subcommand" -a "interactive" -d "Launch interactive mode"
complete -c agentswarm -f -n "__fish_use_subcommand" -a "workflow" -d "Manage workflows"
complete -c agentswarm -f -n "__fish_use_subcommand" -a "history" -d "View command history"
complete -c agentswarm -f -n "__fish_use_subcommand" -a "completion" -d "Manage shell completion"

# List command options
complete -c agentswarm -n "__fish_seen_subcommand_from list" -s c -l category -d "Filter by category"
complete -c agentswarm -n "__fish_seen_subcommand_from list" -s f -l format -a "table json yaml" -d "Output format"
complete -c agentswarm -n "__fish_seen_subcommand_from list" -l categories -d "List all categories"

# Categories
set -l categories data communication media visualization content infrastructure utils integrations
complete -c agentswarm -n "__fish_seen_subcommand_from list; and __fish_seen_argument -l category" -a "$categories"

# Tools (common ones)
set -l tools web_search scholar_search image_search video_search product_search image_generation video_generation audio_generation crawler gmail_search create_agent

complete -c agentswarm -n "__fish_seen_subcommand_from info run test" -a "$tools"

# Run/Test options
complete -c agentswarm -n "__fish_seen_subcommand_from run test" -s p -l params -d "Parameters as JSON"
complete -c agentswarm -n "__fish_seen_subcommand_from run test" -s i -l interactive -d "Interactive mode"
complete -c agentswarm -n "__fish_seen_subcommand_from run test" -s o -l output -d "Output file"
complete -c agentswarm -n "__fish_seen_subcommand_from run test" -s f -l format -a "json yaml text" -d "Output format"
complete -c agentswarm -n "__fish_seen_subcommand_from test" -s m -l mock -d "Use mock mode"
complete -c agentswarm -n "__fish_seen_subcommand_from test" -s v -l verbose -d "Verbose output"

# Workflow subcommands
complete -c agentswarm -n "__fish_seen_subcommand_from workflow" -a "create" -d "Create new workflow"
complete -c agentswarm -n "__fish_seen_subcommand_from workflow" -a "run" -d "Run workflow"
complete -c agentswarm -n "__fish_seen_subcommand_from workflow" -a "list" -d "List workflows"
complete -c agentswarm -n "__fish_seen_subcommand_from workflow" -a "delete" -d "Delete workflow"

# History subcommands
complete -c agentswarm -n "__fish_seen_subcommand_from history" -a "list" -d "List command history"
complete -c agentswarm -n "__fish_seen_subcommand_from history" -a "replay" -d "Replay command"
complete -c agentswarm -n "__fish_seen_subcommand_from history" -a "clear" -d "Clear history"
complete -c agentswarm -n "__fish_seen_subcommand_from history" -a "stats" -d "Show statistics"

# Completion subcommands
complete -c agentswarm -n "__fish_seen_subcommand_from completion" -a "install" -d "Install completion"
complete -c agentswarm -n "__fish_seen_subcommand_from completion" -a "show" -d "Show completion script"
complete -c agentswarm -n "__fish_seen_subcommand_from completion" -l shell -a "bash zsh fish" -d "Shell type"

# Config options
complete -c agentswarm -n "__fish_seen_subcommand_from config" -l show -d "Show configuration"
complete -c agentswarm -n "__fish_seen_subcommand_from config" -l set -d "Set value"
complete -c agentswarm -n "__fish_seen_subcommand_from config" -l get -d "Get value"
complete -c agentswarm -n "__fish_seen_subcommand_from config" -l reset -d "Reset configuration"
complete -c agentswarm -n "__fish_seen_subcommand_from config" -l validate -d "Validate configuration"
"""

    def detect_shell(self) -> Optional[str]:
        """
        Detect current shell.

        Returns:
            Shell name or None if cannot detect
        """
        shell_path = os.environ.get("SHELL", "")

        if "bash" in shell_path:
            return "bash"
        elif "zsh" in shell_path:
            return "zsh"
        elif "fish" in shell_path:
            return "fish"

        return None

    def get_completion_script(self, shell: str) -> str:
        """
        Get completion script for shell.

        Args:
            shell: Shell type (bash, zsh, fish)

        Returns:
            Completion script
        """
        if shell == "bash":
            return self.generate_bash_completion()
        elif shell == "zsh":
            return self.generate_zsh_completion()
        elif shell == "fish":
            return self.generate_fish_completion()
        else:
            raise ValueError(f"Unsupported shell: {shell}")

    def get_install_path(self, shell: str) -> Path:
        """
        Get installation path for completion script.

        Args:
            shell: Shell type

        Returns:
            Installation path
        """
        home = Path.home()

        if shell == "bash":
            # Try bash_completion.d directory
            bash_completion_dir = Path("/etc/bash_completion.d")
            if bash_completion_dir.exists() and os.access(bash_completion_dir, os.W_OK):
                return bash_completion_dir / "agentswarm"

            # Fall back to user directory
            return home / ".bash_completion.d" / "agentswarm"

        elif shell == "zsh":
            # Use user's zsh completions directory
            zsh_dir = home / ".zsh" / "completion"
            zsh_dir.mkdir(parents=True, exist_ok=True)
            return zsh_dir / "_agentswarm"

        elif shell == "fish":
            # Use fish completions directory
            fish_dir = home / ".config" / "fish" / "completions"
            fish_dir.mkdir(parents=True, exist_ok=True)
            return fish_dir / "agentswarm.fish"

        raise ValueError(f"Unsupported shell: {shell}")

    def install_completion(self, shell: Optional[str] = None) -> bool:
        """
        Install completion script for shell.

        Args:
            shell: Shell type (auto-detect if None)

        Returns:
            True if installed successfully
        """
        if not shell:
            shell = self.detect_shell()

        if not shell:
            console.print("[red]Could not detect shell type.[/red]")
            console.print("Please specify shell with --shell option (bash, zsh, or fish)")
            return False

        if shell not in self.supported_shells:
            console.print(f"[red]Unsupported shell: {shell}[/red]")
            return False

        try:
            # Get completion script
            script = self.get_completion_script(shell)

            # Get install path
            install_path = self.get_install_path(shell)

            # Create directory if needed
            install_path.parent.mkdir(parents=True, exist_ok=True)

            # Write script
            with open(install_path, "w") as f:
                f.write(script)

            console.print(f"[green]Completion script installed to {install_path}[/green]")

            # Show next steps
            self._show_install_instructions(shell, install_path)

            return True

        except Exception as e:
            console.print(f"[red]Error installing completion: {e}[/red]")
            return False

    def _show_install_instructions(self, shell: str, install_path: Path):
        """Show post-installation instructions."""
        instructions = ""

        if shell == "bash":
            instructions = f"""
To enable completion, add this to your ~/.bashrc:

    source {install_path}

Then reload your shell:

    source ~/.bashrc

Or start a new terminal session.
"""

        elif shell == "zsh":
            instructions = f"""
To enable completion, add this to your ~/.zshrc:

    fpath=({install_path.parent} $fpath)
    autoload -Uz compinit && compinit

Then reload your shell:

    source ~/.zshrc

Or start a new terminal session.
"""

        elif shell == "fish":
            instructions = """
Fish will automatically load completions from ~/.config/fish/completions/

Reload fish configuration:

    source ~/.config/fish/config.fish

Or start a new terminal session.
"""

        panel = Panel(
            instructions.strip(), title="[bold cyan]Next Steps[/bold cyan]", border_style="green"
        )
        console.print(panel)


if __name__ == "__main__":
    # Example usage
    manager = CompletionManager()

    # Detect shell
    shell = manager.detect_shell()
    print(f"Detected shell: {shell}")

    # Generate completion script
    if shell:
        script = manager.get_completion_script(shell)
        print(f"\nCompletion script preview (first 500 chars):\n{script[:500]}...")
