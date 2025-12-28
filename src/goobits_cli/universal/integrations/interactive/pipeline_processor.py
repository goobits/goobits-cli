"""
Pipeline processing system for REPL mode in Goobits CLI Framework.

Provides Unix-style pipeline operations that allow chaining commands with the pipe operator (|).
Features include pipeline templates, data validation, stream processing, and error handling.

This system integrates with the existing VariableREPL and session persistence to provide
a complete advanced interactive mode experience.
"""

import asyncio
import json
import logging
import shlex
import time
from dataclasses import asdict, dataclass
from enum import Enum
from threading import Lock
from typing import Any, AsyncIterator, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class DataFormat(Enum):
    """Supported data formats for pipeline streams."""

    TEXT = "text"
    JSON = "json"
    LINES = "lines"
    STRUCTURED = "structured"


class PipelineStatus(Enum):
    """Pipeline execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class StreamData:
    """Represents data flowing through a pipeline."""

    content: Any
    format: DataFormat
    metadata: Dict[str, Any]
    timestamp: float

    def to_text(self) -> str:
        """Convert data to text format."""
        if self.format == DataFormat.TEXT:
            return str(self.content)
        elif self.format == DataFormat.JSON:
            return (
                json.dumps(self.content, indent=2)
                if isinstance(self.content, (dict, list))
                else str(self.content)
            )
        elif self.format == DataFormat.LINES:
            return (
                "\n".join(str(line) for line in self.content)
                if isinstance(self.content, list)
                else str(self.content)
            )
        else:
            return str(self.content)

    def to_json(self) -> Any:
        """Convert data to JSON-compatible format."""
        if self.format == DataFormat.JSON:
            return self.content
        elif self.format == DataFormat.TEXT:
            try:
                return json.loads(str(self.content))
            except (json.JSONDecodeError, TypeError):
                return {"text": str(self.content)}
        elif self.format == DataFormat.LINES:
            return (
                list(self.content)
                if isinstance(self.content, (list, tuple))
                else [str(self.content)]
            )
        else:
            return self.content


@dataclass
class PipelineCommand:
    """Represents a single command in a pipeline."""

    name: str
    args: List[str]
    original_line: str
    expected_input_format: Optional[DataFormat] = None
    expected_output_format: Optional[DataFormat] = None


@dataclass
class PipelineTemplate:
    """Represents a reusable pipeline template."""

    name: str
    commands: List[str]
    parameters: List[str]
    description: Optional[str] = None
    created_at: float = 0.0
    usage_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PipelineTemplate":
        """Create from dictionary loaded from JSON."""
        return cls(**data)


class StreamProcessor:
    """Handles data transformation and streaming between pipeline commands."""

    def __init__(self, max_buffer_size: int = 10_000):
        """
        Initialize StreamProcessor.

        Args:
            max_buffer_size: Maximum number of items to buffer in stream
        """
        self.max_buffer_size = max_buffer_size
        self._buffer_lock = Lock()

    async def transform_data(
        self, data: StreamData, target_format: DataFormat
    ) -> StreamData:
        """
        Transform data between different formats.

        Args:
            data: Input stream data
            target_format: Desired output format

        Returns:
            Transformed stream data
        """
        if data.format == target_format:
            return data

        try:
            if target_format == DataFormat.TEXT:
                content = data.to_text()
            elif target_format == DataFormat.JSON:
                content = data.to_json()
            elif target_format == DataFormat.LINES:
                text_content = data.to_text()
                content = text_content.split("\n") if text_content else []
            else:
                content = data.content

            return StreamData(
                content=content,
                format=target_format,
                metadata=data.metadata.copy(),
                timestamp=time.time(),
            )

        except Exception as e:
            logger.error(f"Data transformation failed: {e}")
            raise ValueError(
                f"Cannot transform data from {data.format.value} to {target_format.value}: {e}"
            )

    def validate_data_flow(
        self, output_format: DataFormat, input_format: DataFormat
    ) -> bool:
        """
        Validate that data can flow between formats.

        Args:
            output_format: Format of data being output
            input_format: Format expected as input

        Returns:
            True if transformation is possible
        """
        # All formats can be transformed to text
        if input_format == DataFormat.TEXT:
            return True

        # JSON can accept structured data
        if input_format == DataFormat.JSON and output_format in [
            DataFormat.JSON,
            DataFormat.STRUCTURED,
        ]:
            return True

        # Lines format can accept text or lines
        if input_format == DataFormat.LINES and output_format in [
            DataFormat.TEXT,
            DataFormat.LINES,
        ]:
            return True

        # Exact match is always valid
        if output_format == input_format:
            return True

        # Allow transformation with potential data loss
        return True

    async def process_stream(
        self,
        input_stream: AsyncIterator[StreamData],
        transform_func: Optional[callable] = None,
    ) -> AsyncIterator[StreamData]:
        """
        Process a stream of data with optional transformation.

        Args:
            input_stream: Input data stream
            transform_func: Optional transformation function

        Yields:
            Processed stream data
        """
        buffer_count = 0

        async for data in input_stream:
            if buffer_count >= self.max_buffer_size:
                logger.warning(f"Stream buffer limit reached ({self.max_buffer_size})")
                break

            try:
                if transform_func:
                    processed_data = await transform_func(data)
                else:
                    processed_data = data

                yield processed_data
                buffer_count += 1

            except Exception as e:
                logger.error(f"Stream processing error: {e}")
                # Continue processing other items
                continue


class PipelineProcessor:
    """Processes and executes command pipelines with Unix-style pipe syntax."""

    def __init__(
        self, cli_config: Dict[str, Any], variable_store=None, timeout: int = 60
    ):
        """
        Initialize PipelineProcessor.

        Args:
            cli_config: CLI configuration dictionary
            variable_store: Optional variable store for substitution
            timeout: Default timeout for pipeline execution in seconds
        """
        self.cli_config = cli_config
        self.variable_store = variable_store
        self.default_timeout = timeout
        self.stream_processor = StreamProcessor()

        # Pipeline template storage
        self.pipeline_templates: Dict[str, PipelineTemplate] = {}
        self.execution_history: List[Dict[str, Any]] = []

        # Execution state
        self.active_pipelines: Dict[str, Dict[str, Any]] = {}
        self._pipeline_lock = Lock()

        # Command registry from CLI config
        self.available_commands = self._build_command_registry()

    def _build_command_registry(self) -> Dict[str, Dict[str, Any]]:
        """Build a registry of available commands from CLI config."""
        commands = {}

        root_command = self.cli_config.get("root_command", {})
        for cmd in root_command.get("subcommands", []):
            commands[cmd["name"]] = cmd

        # Add built-in pipeline commands
        commands.update(
            {
                "pipeline": {
                    "name": "pipeline",
                    "description": "Define or manage pipeline templates",
                    "builtin": True,
                },
                "run": {
                    "name": "run",
                    "description": "Execute a pipeline template",
                    "builtin": True,
                },
                "pipelines": {
                    "name": "pipelines",
                    "description": "List available pipeline templates",
                    "builtin": True,
                },
            }
        )

        return commands

    def parse_pipeline(self, line: str) -> Tuple[List[PipelineCommand], Optional[str]]:
        """
        Parse a pipeline command line into individual commands.

        Args:
            line: Pipeline command line (e.g., "cmd1 arg | cmd2 | cmd3")

        Returns:
            Tuple of (parsed commands, error message if any)
        """
        try:
            # Handle variable substitution if available
            if self.variable_store and "$" in line:
                line = self.variable_store.substitute_variables(line)

            # Split by pipe operator while respecting quotes
            pipeline_parts = self._split_pipeline(line)

            if not pipeline_parts:
                return [], "Empty pipeline"

            commands = []
            for part in pipeline_parts:
                part = part.strip()
                if not part:
                    continue

                # Parse individual command
                try:
                    tokens = shlex.split(part)
                    if not tokens:
                        continue

                    cmd_name = tokens[0]
                    cmd_args = tokens[1:]

                    # Validate command exists
                    if cmd_name not in self.available_commands:
                        return [], f"Unknown command: {cmd_name}"

                    commands.append(
                        PipelineCommand(
                            name=cmd_name, args=cmd_args, original_line=part
                        )
                    )

                except ValueError as e:
                    return [], f"Command parsing error in '{part}': {e}"

            return commands, None

        except Exception as e:
            return [], f"Pipeline parsing error: {e}"

    def _split_pipeline(self, line: str) -> List[str]:
        """Split pipeline respecting quotes and escapes."""
        parts = []
        current_part = ""
        in_quotes = False
        quote_char = None
        i = 0

        while i < len(line):
            char = line[i]

            if char in ('"', "'") and (i == 0 or line[i - 1] != "\\"):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
                current_part += char
            elif char == "|" and not in_quotes:
                parts.append(current_part)
                current_part = ""
            else:
                current_part += char

            i += 1

        if current_part:
            parts.append(current_part)

        return parts

    def define_pipeline_template(
        self, name: str, definition: str, parameters: Optional[List[str]] = None
    ) -> bool:
        """
        Define a reusable pipeline template.

        Args:
            name: Template name
            definition: Pipeline commands as string
            parameters: Optional parameter names for template

        Returns:
            True if template was created successfully
        """
        try:
            # Parse definition to validate syntax
            commands, error = self.parse_pipeline(definition)
            if error:
                logger.error(f"Template definition error: {error}")
                return False

            # Extract command strings
            command_strings = [cmd.original_line for cmd in commands]

            template = PipelineTemplate(
                name=name,
                commands=command_strings,
                parameters=parameters or [],
                description=f"Pipeline with {len(commands)} commands",
                created_at=time.time(),
            )

            with self._pipeline_lock:
                self.pipeline_templates[name] = template

            logger.info(
                f"Pipeline template '{name}' defined with {len(commands)} commands"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to define pipeline template '{name}': {e}")
            return False

    def list_pipeline_templates(self) -> List[Dict[str, Any]]:
        """
        List all available pipeline templates.

        Returns:
            List of template information dictionaries
        """
        with self._pipeline_lock:
            templates = []
            for name, template in self.pipeline_templates.items():
                templates.append(
                    {
                        "name": name,
                        "description": template.description,
                        "parameters": template.parameters,
                        "command_count": len(template.commands),
                        "usage_count": template.usage_count,
                        "created_at": template.created_at,
                    }
                )

            # Sort by usage count (most used first) then by name
            templates.sort(key=lambda x: (-x["usage_count"], x["name"]))
            return templates

    async def execute_pipeline_template(
        self, name: str, parameter_values: Dict[str, str] = None
    ) -> Tuple[bool, str]:
        """
        Execute a pipeline template with parameter substitution.

        Args:
            name: Template name
            parameter_values: Values for template parameters

        Returns:
            Tuple of (success, result message)
        """
        with self._pipeline_lock:
            if name not in self.pipeline_templates:
                return False, f"Pipeline template '{name}' not found"

            template = self.pipeline_templates[name]
            template.usage_count += 1

        try:
            # Substitute parameters in commands
            command_line = " | ".join(template.commands)

            if template.parameters and parameter_values:
                for param in template.parameters:
                    if param in parameter_values:
                        # Simple parameter substitution
                        command_line = command_line.replace(
                            f"${param}", parameter_values[param]
                        )

            # Execute the pipeline
            success, output = await self.execute_pipeline(command_line)

            if success:
                return True, f"Pipeline '{name}' completed successfully"
            else:
                return False, f"Pipeline '{name}' failed: {output}"

        except Exception as e:
            logger.error(f"Pipeline template execution error: {e}")
            return False, f"Pipeline '{name}' execution error: {e}"

    async def execute_pipeline(
        self, line: str, timeout: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Execute a command pipeline.

        Args:
            line: Pipeline command line
            timeout: Execution timeout in seconds

        Returns:
            Tuple of (success, output/error message)
        """
        execution_id = f"pipeline_{int(time.time() * 1000)}"
        timeout = timeout or self.default_timeout

        try:
            # Parse pipeline
            commands, error = self.parse_pipeline(line)
            if error:
                return False, error

            if not commands:
                return False, "No commands in pipeline"

            # Track execution
            with self._pipeline_lock:
                self.active_pipelines[execution_id] = {
                    "status": PipelineStatus.RUNNING,
                    "commands": [cmd.name for cmd in commands],
                    "started_at": time.time(),
                }

            # Execute pipeline with timeout
            try:
                result = await asyncio.wait_for(
                    self._execute_pipeline_commands(commands, execution_id),
                    timeout=timeout,
                )

                success, output = result

                # Update execution status
                with self._pipeline_lock:
                    if execution_id in self.active_pipelines:
                        self.active_pipelines[execution_id]["status"] = (
                            PipelineStatus.COMPLETED
                            if success
                            else PipelineStatus.FAILED
                        )
                        self.active_pipelines[execution_id]["completed_at"] = (
                            time.time()
                        )

                # Add to execution history
                self.execution_history.append(
                    {
                        "pipeline": line,
                        "commands": [cmd.name for cmd in commands],
                        "success": success,
                        "output_preview": output[:200] if output else None,
                        "timestamp": time.time(),
                    }
                )

                # Keep history limited
                if len(self.execution_history) > 100:
                    self.execution_history = self.execution_history[-50:]

                return success, output

            except asyncio.TimeoutError:
                with self._pipeline_lock:
                    if execution_id in self.active_pipelines:
                        self.active_pipelines[execution_id]["status"] = (
                            PipelineStatus.CANCELLED
                        )

                return False, f"Pipeline timed out after {timeout} seconds"

        except Exception as e:
            logger.error(f"Pipeline execution error: {e}")

            with self._pipeline_lock:
                if execution_id in self.active_pipelines:
                    self.active_pipelines[execution_id]["status"] = (
                        PipelineStatus.FAILED
                    )

            return False, f"Pipeline execution error: {e}"

        finally:
            # Cleanup completed pipeline from active list
            with self._pipeline_lock:
                if execution_id in self.active_pipelines:
                    status = self.active_pipelines[execution_id]["status"]
                    if status in [
                        PipelineStatus.COMPLETED,
                        PipelineStatus.FAILED,
                        PipelineStatus.CANCELLED,
                    ]:
                        del self.active_pipelines[execution_id]

    async def _execute_pipeline_commands(
        self, commands: List[PipelineCommand], execution_id: str
    ) -> Tuple[bool, str]:
        """
        Execute the actual pipeline commands with data streaming.

        Args:
            commands: List of pipeline commands
            execution_id: Unique execution identifier

        Returns:
            Tuple of (success, final output)
        """
        if not commands:
            return False, "No commands to execute"

        try:
            # For now, simulate command execution
            # In a real implementation, this would integrate with the actual command system
            current_data = StreamData(
                content="",
                format=DataFormat.TEXT,
                metadata={"pipeline_id": execution_id},
                timestamp=time.time(),
            )

            output_lines = []

            for i, command in enumerate(commands):
                # Simulate command execution
                await asyncio.sleep(0.01)  # Simulate processing time

                # Build mock output based on command
                if command.name == "list-users":
                    current_data = StreamData(
                        content=["alice", "bob", "charlie"],
                        format=DataFormat.LINES,
                        metadata=current_data.metadata,
                        timestamp=time.time(),
                    )
                    output_lines.append(f"[{command.name}] Generated 3 users")

                elif command.name == "filter":
                    # Filter based on args
                    if "--active" in command.args:
                        if current_data.format == DataFormat.LINES:
                            filtered = [
                                user
                                for user in current_data.content
                                if user != "charlie"
                            ]  # Mock filter
                            current_data = StreamData(
                                content=filtered,
                                format=DataFormat.LINES,
                                metadata=current_data.metadata,
                                timestamp=time.time(),
                            )
                            output_lines.append(
                                f"[{command.name}] Filtered to {len(filtered)} active users"
                            )

                elif command.name == "greet":
                    style = "casual"
                    if "--style" in command.args:
                        style_idx = command.args.index("--style")
                        if style_idx + 1 < len(command.args):
                            style = command.args[style_idx + 1]

                    if current_data.format == DataFormat.LINES:
                        greetings = [
                            f"Hello {user} ({style})" for user in current_data.content
                        ]
                        current_data = StreamData(
                            content=greetings,
                            format=DataFormat.LINES,
                            metadata=current_data.metadata,
                            timestamp=time.time(),
                        )
                        output_lines.append(
                            f"[{command.name}] Generated {len(greetings)} greetings"
                        )

                else:
                    # Generic command processing
                    output_lines.append(
                        f"[{command.name}] Processed data: {command.args}"
                    )

            final_output = "\n".join(output_lines)
            if current_data.format == DataFormat.LINES and current_data.content:
                final_output += "\n\nFinal output:\n" + "\n".join(
                    str(item) for item in current_data.content
                )

            return True, final_output

        except Exception as e:
            logger.error(f"Pipeline command execution error: {e}")
            return False, f"Command execution failed: {e}"

    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get pipeline execution statistics."""
        with self._pipeline_lock:
            total_executions = len(self.execution_history)
            successful_executions = sum(
                1 for exec_info in self.execution_history if exec_info["success"]
            )
            active_count = len(self.active_pipelines)

            # Template usage stats
            total_templates = len(self.pipeline_templates)
            most_used_template = None
            if self.pipeline_templates:
                most_used_template = max(
                    self.pipeline_templates.values(), key=lambda t: t.usage_count
                ).name

            return {
                "total_executions": total_executions,
                "success_rate": (
                    (successful_executions / total_executions)
                    if total_executions > 0
                    else 0.0
                ),
                "active_pipelines": active_count,
                "total_templates": total_templates,
                "most_used_template": most_used_template,
                "recent_executions": (
                    self.execution_history[-5:] if self.execution_history else []
                ),
            }

    def cleanup_execution_history(self, max_age_hours: int = 24):
        """Clean up old execution history entries."""
        cutoff_time = time.time() - (max_age_hours * 3600)

        with self._pipeline_lock:
            self.execution_history = [
                exec_info
                for exec_info in self.execution_history
                if exec_info["timestamp"] > cutoff_time
            ]

            logger.info(
                f"Cleaned up pipeline execution history older than {max_age_hours} hours"
            )


def create_pipeline_processor(
    cli_config: Dict[str, Any], variable_store=None, **kwargs
) -> Optional[PipelineProcessor]:
    """
    Factory function to create a PipelineProcessor if pipeline features are enabled.

    Args:
        cli_config: CLI configuration dictionary
        variable_store: Optional variable store for substitution
        **kwargs: Additional configuration options

    Returns:
        PipelineProcessor instance or None if pipelines not enabled
    """
    # Check if pipelines are enabled in config
    features = cli_config.get("features", {})
    interactive_config = features.get("interactive_mode", {})
    pipelines_enabled = interactive_config.get("pipelines", False)

    if not pipelines_enabled:
        return None

    timeout = interactive_config.get("pipeline_timeout", 60)

    return PipelineProcessor(cli_config, variable_store, timeout)
