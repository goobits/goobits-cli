"""
Display Adapters
================

Display adapters for progress indicators with Rich integration and fallback support.
Handles rendering of progress bars and spinners across different display environments.
"""

import sys
import time
import threading
from typing import Optional, Any, Dict, List, Union
from abc import ABC, abstractmethod
from contextlib import contextmanager

from .progress_manager import ProgressIndicator, SpinnerStyle, ProgressType


class DisplayAdapter(ABC):
    """Abstract base class for progress display adapters."""
    
    @abstractmethod
    def render_spinner(self, indicator: ProgressIndicator) -> Any:
        """Render a spinner indicator."""
        pass
    
    @abstractmethod
    def render_progress_bar(self, indicator: ProgressIndicator) -> Any:
        """Render a progress bar indicator."""
        pass
    
    @abstractmethod
    def update_display(self, context: Any, **kwargs) -> None:
        """Update the display with new information."""
        pass
    
    @abstractmethod
    def cleanup_display(self, context: Any) -> None:
        """Clean up display resources."""
        pass


class RichDisplayAdapter(DisplayAdapter):
    """Rich library display adapter for enhanced progress indicators."""
    
    def __init__(self, console=None):
        """Initialize with optional Rich console."""
        try:
            from rich.console import Console
            from rich.progress import (
                Progress, BarColumn, TextColumn, TimeRemainingColumn,
                SpinnerColumn, MofNCompleteColumn, TimeElapsedColumn
            )
            from rich.status import Status
            
            self.console = console or Console()
            self.has_rich = True
            self._rich_imports = {
                'Progress': Progress,
                'BarColumn': BarColumn,
                'TextColumn': TextColumn,
                'TimeRemainingColumn': TimeRemainingColumn,
                'SpinnerColumn': SpinnerColumn,
                'MofNCompleteColumn': MofNCompleteColumn,
                'TimeElapsedColumn': TimeElapsedColumn,
                'Status': Status
            }
            
        except ImportError:
            raise ImportError("Rich library not available for RichDisplayAdapter")
    
    def render_spinner(self, indicator: ProgressIndicator) -> Any:
        """Render a Rich-based spinner."""
        if not self.has_rich:
            raise RuntimeError("Rich not available")
        
        # Map spinner styles to Rich spinner names
        spinner_mapping = {
            SpinnerStyle.DOTS: "dots",
            SpinnerStyle.LINE: "line",
            SpinnerStyle.STAR: "star",
            SpinnerStyle.ARROW: "arrow",
            SpinnerStyle.BOUNCE: "bounce",
            SpinnerStyle.ARC: "arc"
        }
        
        spinner_name = spinner_mapping.get(indicator.spinner_style, "dots")
        
        return self.console.status(
            f"[bold blue]{indicator.description}",
            spinner=spinner_name
        )
    
    def render_progress_bar(self, indicator: ProgressIndicator) -> Any:
        """Render a Rich-based progress bar."""
        if not self.has_rich:
            raise RuntimeError("Rich not available")
        
        # Build columns based on indicator configuration
        columns = [
            self._rich_imports['TextColumn']("[bold blue]{task.description}"),
            self._rich_imports['SpinnerColumn'](),
            self._rich_imports['BarColumn'](),
        ]
        
        if indicator.show_percentage:
            columns.append(
                self._rich_imports['TextColumn']("[progress.percentage]{task.percentage:>3.0f}%")
            )
        
        if indicator.show_count and indicator.total is not None:
            columns.append(self._rich_imports['MofNCompleteColumn']())
        
        if indicator.show_time:
            columns.extend([
                self._rich_imports['TimeElapsedColumn'](),
                self._rich_imports['TimeRemainingColumn']()
            ])
        
        return self._rich_imports['Progress'](*columns, console=self.console)
    
    def update_display(self, context: Any, **kwargs) -> None:
        """Update Rich display context."""
        if hasattr(context, 'update'):
            context.update(**kwargs)
    
    def cleanup_display(self, context: Any) -> None:
        """Clean up Rich display resources."""
        if hasattr(context, '__exit__'):
            try:
                context.__exit__(None, None, None)
            except Exception:
                pass


class FallbackDisplayAdapter(DisplayAdapter):
    """Fallback display adapter for environments without Rich."""
    
    def __init__(self):
        """Initialize fallback adapter."""
        self._active_spinners: Dict[str, Dict[str, Any]] = {}
        self._spinner_frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self._lock = threading.Lock()
    
    def render_spinner(self, indicator: ProgressIndicator) -> Any:
        """Render a text-based spinner."""
        spinner_id = f"spinner_{id(indicator)}"
        
        context = {
            'id': spinner_id,
            'indicator': indicator,
            'frame_index': 0,
            'active': True,
            'thread': None
        }
        
        return context
    
    def render_progress_bar(self, indicator: ProgressIndicator) -> Any:
        """Render a text-based progress bar."""
        context = {
            'indicator': indicator,
            'current': 0,
            'last_percentage': -1,
            'start_time': time.time()
        }
        
        print(f"{indicator.description}")
        return context
    
    def update_display(self, context: Any, **kwargs) -> None:
        """Update fallback display."""
        if isinstance(context, dict):
            if 'indicator' in context:
                # Progress bar update
                advance = kwargs.get('advance', 1)
                context['current'] += advance
                
                indicator = context['indicator']
                if indicator.total and indicator.total > 0:
                    percentage = min(100, (context['current'] / indicator.total) * 100)
                    
                    if int(percentage) != context['last_percentage']:
                        elapsed = time.time() - context['start_time']
                        
                        # Build status string
                        status_parts = [f"Progress: {percentage:.1f}%"]
                        
                        if indicator.show_count:
                            status_parts.append(f"({context['current']}/{indicator.total})")
                        
                        if indicator.show_time and elapsed > 1:
                            status_parts.append(f"({elapsed:.1f}s)")
                        
                        status = " ".join(status_parts)
                        print(f"\r{status}", end="", flush=True)
                        context['last_percentage'] = int(percentage)
            
            elif 'frame_index' in context:
                # Spinner update (handled by thread)
                pass
    
    def cleanup_display(self, context: Any) -> None:
        """Clean up fallback display resources."""
        if isinstance(context, dict):
            if 'active' in context:
                context['active'] = False
                
                if context.get('thread'):
                    try:
                        context['thread'].join(timeout=0.5)
                    except Exception:
                        pass
            
            # Ensure we end with a newline
            print()
    
    def _start_spinner_animation(self, context: Dict[str, Any]) -> None:
        """Start spinner animation in a separate thread."""
        def animate():
            while context.get('active', False):
                frame = self._spinner_frames[context['frame_index']]
                text = context['indicator'].description
                
                print(f"\r{frame} {text}", end="", flush=True)
                
                context['frame_index'] = (context['frame_index'] + 1) % len(self._spinner_frames)
                time.sleep(context['indicator'].update_interval)
        
        thread = threading.Thread(target=animate, daemon=True)
        context['thread'] = thread
        thread.start()


class SmartDisplayAdapter(DisplayAdapter):
    """Smart adapter that automatically chooses between Rich and fallback."""
    
    def __init__(self, prefer_rich: bool = True, console=None):
        """
        Initialize smart adapter.
        
        Args:
            prefer_rich: Prefer Rich if available
            console: Optional Rich console instance
        """
        self.prefer_rich = prefer_rich
        
        try:
            self._rich_adapter = RichDisplayAdapter(console)
            self._has_rich = True
        except ImportError:
            self._rich_adapter = None
            self._has_rich = False
        
        self._fallback_adapter = FallbackDisplayAdapter()
    
    def _get_adapter(self) -> DisplayAdapter:
        """Get the appropriate adapter."""
        if self._has_rich and self.prefer_rich:
            return self._rich_adapter
        return self._fallback_adapter
    
    def render_spinner(self, indicator: ProgressIndicator) -> Any:
        """Render spinner using appropriate adapter."""
        return self._get_adapter().render_spinner(indicator)
    
    def render_progress_bar(self, indicator: ProgressIndicator) -> Any:
        """Render progress bar using appropriate adapter."""
        return self._get_adapter().render_progress_bar(indicator)
    
    def update_display(self, context: Any, **kwargs) -> None:
        """Update display using appropriate adapter."""
        self._get_adapter().update_display(context, **kwargs)
    
    def cleanup_display(self, context: Any) -> None:
        """Clean up display using appropriate adapter."""
        self._get_adapter().cleanup_display(context)
    
    def is_rich_available(self) -> bool:
        """Check if Rich is available."""
        return self._has_rich
    
    def force_fallback(self) -> None:
        """Force use of fallback adapter."""
        self.prefer_rich = False
    
    def force_rich(self) -> None:
        """Force use of Rich adapter (will raise if not available)."""
        if not self._has_rich:
            raise RuntimeError("Rich adapter not available")
        self.prefer_rich = True