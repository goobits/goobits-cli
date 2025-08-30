"""
Progress Manager
================

Progress management system extracted from progress_manager.j2 template.
Provides spinners, progress bars, and status indicators with Rich integration and fallbacks.
"""

import sys
import time
import threading
from typing import Optional, Any, Dict, Union, Callable, Iterator
from contextlib import contextmanager
from enum import Enum
from dataclasses import dataclass, field


class ProgressType(Enum):
    """Types of progress indicators."""
    SPINNER = "spinner"
    PROGRESS_BAR = "progress_bar"
    STATUS = "status"
    PERCENTAGE = "percentage"


class SpinnerStyle(Enum):
    """Available spinner styles."""
    DOTS = "dots"
    LINE = "line"
    STAR = "star"
    ARROW = "arrow"
    BOUNCE = "bounce"
    ARC = "arc"


@dataclass
class ProgressIndicator:
    """Configuration for a progress indicator."""
    type: ProgressType
    description: str = "Processing..."
    total: Optional[int] = None
    show_time: bool = True
    show_percentage: bool = True
    show_count: bool = False
    spinner_style: SpinnerStyle = SpinnerStyle.DOTS
    update_interval: float = 0.1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'type': self.type.value,
            'description': self.description,
            'total': self.total,
            'show_time': self.show_time,
            'show_percentage': self.show_percentage,
            'show_count': self.show_count,
            'spinner_style': self.spinner_style.value,
            'update_interval': self.update_interval
        }


class ProgressTask:
    """Represents a progress tracking task."""
    
    def __init__(self, task_id: str, indicator: ProgressIndicator):
        self.task_id = task_id
        self.indicator = indicator
        self.current = 0
        self.completed = False
        self.start_time = time.time()
        self.end_time = None
        
    def update(self, advance: int = 1) -> None:
        """Update progress by the specified amount."""
        self.current += advance
        
        if self.indicator.total and self.current >= self.indicator.total:
            self.completed = True
            self.end_time = time.time()
    
    def get_percentage(self) -> float:
        """Get completion percentage."""
        if not self.indicator.total:
            return 0.0
        return min(100.0, (self.current / self.indicator.total) * 100)
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        end_time = self.end_time or time.time()
        return end_time - self.start_time
    
    def get_remaining_time(self) -> Optional[float]:
        """Estimate remaining time in seconds."""
        if not self.indicator.total or self.current == 0:
            return None
        
        elapsed = self.get_elapsed_time()
        rate = self.current / elapsed
        remaining_items = self.indicator.total - self.current
        
        return remaining_items / rate if rate > 0 else None


class ProgressManager:
    """
    Advanced progress manager extracted from progress_manager.j2.
    
    Provides context managers for spinners and progress bars with Rich integration
    and fallback support for environments without Rich library.
    """
    
    def __init__(self, use_rich: Optional[bool] = None, console=None):
        """
        Initialize progress manager.
        
        Args:
            use_rich: Force Rich usage (True) or fallback (False). None for auto-detect.
            console: Rich console instance. Only used if use_rich is True.
        """
        # Try to detect Rich availability
        self.has_rich = False
        self.console = None
        
        if use_rich is not False:  # Allow auto-detection or forced True
            try:
                from rich.progress import Progress
                from rich.console import Console
                from rich.status import Status
                
                self.has_rich = True
                self.console = console or Console()
                
            except ImportError:
                if use_rich is True:
                    raise ImportError("Rich library not available but use_rich=True was specified")
                self.has_rich = False
        
        self._active_tasks: Dict[str, ProgressTask] = {}
        self._task_counter = 0
        self._lock = threading.Lock()
    
    def _generate_task_id(self) -> str:
        """Generate a unique task ID."""
        with self._lock:
            self._task_counter += 1
            return f"task_{self._task_counter}"
    
    @contextmanager
    def spinner(
        self,
        text: str = "Processing...",
        spinner_style: SpinnerStyle = SpinnerStyle.DOTS,
        success_text: Optional[str] = None,
        error_text: Optional[str] = None
    ):
        """
        Context manager for showing a spinner.
        
        Args:
            text: Status text to display
            spinner_style: Style of spinner animation
            success_text: Text to show on success (None = "✓")
            error_text: Text to show on error (None = "✗")
            
        Yields:
            SpinnerContext object for updating status
        """
        if self.has_rich and self.console:
            yield from self._rich_spinner(text, spinner_style, success_text, error_text)
        else:
            yield from self._fallback_spinner(text, success_text, error_text)
    
    def _rich_spinner(self, text: str, spinner_style: SpinnerStyle, success_text: Optional[str], error_text: Optional[str]):
        """Rich-based spinner implementation."""
        try:
            # Map our spinner styles to Rich spinner names
            rich_spinners = {
                SpinnerStyle.DOTS: "dots",
                SpinnerStyle.LINE: "line",
                SpinnerStyle.STAR: "star",
                SpinnerStyle.ARROW: "arrow",
                SpinnerStyle.BOUNCE: "bounce",
                SpinnerStyle.ARC: "arc"
            }
            
            spinner_name = rich_spinners.get(spinner_style, "dots")
            
            with self.console.status(f"[bold blue]{text}", spinner=spinner_name) as status:
                
                class SpinnerContext:
                    def __init__(self, status_obj):
                        self.status = status_obj
                    
                    def update_text(self, new_text: str):
                        self.status.update(f"[bold blue]{new_text}")
                
                try:
                    yield SpinnerContext(status)
                    # Success
                    if success_text is not None:
                        self.console.print(f"[green]{success_text}[/green]")
                    else:
                        self.console.print(f"[green]{text} ✓[/green]")
                        
                except Exception as e:
                    # Error
                    if error_text is not None:
                        self.console.print(f"[red]{error_text}[/red]")
                    else:
                        self.console.print(f"[red]{text} ✗[/red]")
                    raise e
                    
        except Exception:
            # Fallback if Rich fails
            yield from self._fallback_spinner(text, success_text, error_text)
    
    def _fallback_spinner(self, text: str, success_text: Optional[str], error_text: Optional[str]):
        """Fallback spinner implementation without Rich."""
        print(f"{text}", end="", flush=True)
        
        class SpinnerContext:
            def update_text(self, new_text: str):
                # In fallback mode, we can't dynamically update text
                pass
        
        try:
            yield SpinnerContext()
            # Success
            if success_text is not None:
                print(f" {success_text}")
            else:
                print(" ✓")
                
        except Exception as e:
            # Error
            if error_text is not None:
                print(f" {error_text}")
            else:
                print(" ✗")
            raise e
    
    @contextmanager
    def progress_bar(
        self,
        description: str = "Processing...",
        total: Optional[int] = None,
        show_time: bool = True,
        show_percentage: bool = True,
        show_count: bool = False
    ):
        """
        Context manager for showing a progress bar.
        
        Args:
            description: Description of the operation
            total: Total number of items (None for indeterminate progress)
            show_time: Show elapsed/remaining time
            show_percentage: Show completion percentage
            show_count: Show current/total count
            
        Yields:
            (progress_manager, task_id) tuple for updating progress
        """
        indicator = ProgressIndicator(
            type=ProgressType.PROGRESS_BAR,
            description=description,
            total=total,
            show_time=show_time,
            show_percentage=show_percentage,
            show_count=show_count
        )
        
        if self.has_rich and self.console:
            yield from self._rich_progress_bar(indicator)
        else:
            yield from self._fallback_progress_bar(indicator)
    
    def _rich_progress_bar(self, indicator: ProgressIndicator):
        """Rich-based progress bar implementation."""
        try:
            from rich.progress import (
                Progress, TaskID, BarColumn, TextColumn, 
                TimeRemainingColumn, SpinnerColumn, 
                MofNCompleteColumn, TimeElapsedColumn
            )
            
            # Build columns based on configuration
            columns = [
                TextColumn("[bold blue]{task.description}"),
                SpinnerColumn(),
                BarColumn(),
            ]
            
            if indicator.show_percentage:
                columns.append(TextColumn("[progress.percentage]{task.percentage:>3.0f}%"))
            
            if indicator.show_count and indicator.total is not None:
                columns.append(MofNCompleteColumn())
            
            if indicator.show_time:
                columns.extend([TimeElapsedColumn(), TimeRemainingColumn()])
            
            with Progress(*columns, console=self.console) as progress:
                task_id = progress.add_task(indicator.description, total=indicator.total)
                
                class ProgressContext:
                    def __init__(self, progress_obj, task_id):
                        self.progress = progress_obj
                        self.task_id = task_id
                    
                    def update(self, advance: int = 1):
                        self.progress.update(self.task_id, advance=advance)
                    
                    def set_total(self, total: int):
                        self.progress.update(self.task_id, total=total)
                    
                    def set_description(self, description: str):
                        self.progress.update(self.task_id, description=description)
                
                yield ProgressContext(progress, task_id)
                
        except Exception:
            # Fallback if Rich fails
            yield from self._fallback_progress_bar(indicator)
    
    def _fallback_progress_bar(self, indicator: ProgressIndicator):
        """Fallback progress bar implementation without Rich."""
        print(f"{indicator.description}")
        
        class FallbackProgressContext:
            def __init__(self, indicator):
                self.indicator = indicator
                self.current = 0
                self.last_percentage = -1
                self.start_time = time.time()
            
            def update(self, advance: int = 1):
                self.current += advance
                
                if self.indicator.total and self.indicator.total > 0:
                    percentage = min(100, (self.current / self.indicator.total) * 100)
                    
                    if int(percentage) != self.last_percentage:
                        elapsed = time.time() - self.start_time
                        
                        if self.indicator.show_time and elapsed > 1:
                            time_str = f" ({elapsed:.1f}s)"
                        else:
                            time_str = ""
                        
                        if self.indicator.show_count:
                            count_str = f" ({self.current}/{self.indicator.total})"
                        else:
                            count_str = ""
                            
                        print(f"\\rProgress: {percentage:.1f}%{count_str}{time_str}", end="", flush=True)
                        self.last_percentage = int(percentage)
            
            def set_total(self, total: int):
                self.indicator.total = total
            
            def set_description(self, description: str):
                self.indicator.description = description
                print(f"\\n{description}")
        
        context = FallbackProgressContext(indicator)
        try:
            yield context
        finally:
            print()  # New line after completion
    
    def create_progress_task(self, indicator: ProgressIndicator) -> str:
        """
        Create a new progress task.
        
        Args:
            indicator: Progress indicator configuration
            
        Returns:
            Task ID for tracking progress
        """
        task_id = self._generate_task_id()
        task = ProgressTask(task_id, indicator)
        
        with self._lock:
            self._active_tasks[task_id] = task
        
        return task_id
    
    def update_task(self, task_id: str, advance: int = 1) -> bool:
        """
        Update a progress task.
        
        Args:
            task_id: Task identifier
            advance: Amount to advance progress
            
        Returns:
            True if task was found and updated
        """
        with self._lock:
            if task_id in self._active_tasks:
                self._active_tasks[task_id].update(advance)
                return True
        return False
    
    def complete_task(self, task_id: str) -> bool:
        """
        Mark a task as completed.
        
        Args:
            task_id: Task identifier
            
        Returns:
            True if task was found and completed
        """
        with self._lock:
            if task_id in self._active_tasks:
                task = self._active_tasks[task_id]
                task.completed = True
                task.end_time = time.time()
                return True
        return False
    
    def remove_task(self, task_id: str) -> bool:
        """
        Remove a completed task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            True if task was found and removed
        """
        with self._lock:
            return self._active_tasks.pop(task_id, None) is not None
    
    def get_task(self, task_id: str) -> Optional[ProgressTask]:
        """
        Get a progress task by ID.
        
        Args:
            task_id: Task identifier
            
        Returns:
            ProgressTask instance or None if not found
        """
        with self._lock:
            return self._active_tasks.get(task_id)
    
    def get_active_tasks(self) -> Dict[str, ProgressTask]:
        """Get all active tasks."""
        with self._lock:
            return self._active_tasks.copy()
    
    def clear_completed_tasks(self) -> int:
        """
        Remove all completed tasks.
        
        Returns:
            Number of tasks removed
        """
        with self._lock:
            completed_tasks = [
                task_id for task_id, task in self._active_tasks.items()
                if task.completed
            ]
            
            for task_id in completed_tasks:
                del self._active_tasks[task_id]
            
            return len(completed_tasks)
    
    def get_manager_stats(self) -> Dict[str, Any]:
        """Get progress manager statistics."""
        with self._lock:
            active_count = len(self._active_tasks)
            completed_count = sum(1 for task in self._active_tasks.values() if task.completed)
            
            return {
                'has_rich': self.has_rich,
                'total_tasks': self._task_counter,
                'active_tasks': active_count,
                'completed_tasks': completed_count,
                'pending_tasks': active_count - completed_count
            }