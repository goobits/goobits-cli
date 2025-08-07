"""
Performance Monitoring Plugin (Cross-language)
Provides real-time performance monitoring and analysis for CLI applications
"""

import asyncio
import json
import psutil
import time
import threading
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
import subprocess
import platform
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from matplotlib.dates import DateFormatter
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import rich
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress
    from rich.live import Live
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    network_sent_mb: float
    network_recv_mb: float
    process_count: int
    load_average: Optional[List[float]] = None


@dataclass
class ProcessMetrics:
    """Process-specific metrics"""
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    threads: int
    status: str
    create_time: float
    command: str


@dataclass
class CommandMetrics:
    """CLI command execution metrics"""
    command: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    exit_code: Optional[int] = None
    cpu_usage: List[float] = field(default_factory=list)
    memory_usage: List[float] = field(default_factory=list)
    peak_memory: float = 0.0
    avg_cpu: float = 0.0


class PerformanceMonitor:
    """Real-time performance monitoring system"""
    
    def __init__(self, sample_interval: float = 1.0, history_size: int = 1000):
        self.sample_interval = sample_interval
        self.history_size = history_size
        self.system_history: deque = deque(maxlen=history_size)
        self.process_history: Dict[int, deque] = defaultdict(lambda: deque(maxlen=history_size))
        self.command_history: List[CommandMetrics] = []
        
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.callbacks: List[Callable[[SystemMetrics], None]] = []
        
        # Initial network counters
        self.initial_net_io = psutil.net_io_counters()
    
    def add_callback(self, callback: Callable[[SystemMetrics], None]):
        """Add a callback function to be called on each metric update"""
        self.callbacks.append(callback)
    
    def start_monitoring(self):
        """Start continuous monitoring in background thread"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                metrics = self.collect_system_metrics()
                self.system_history.append(metrics)
                
                # Call registered callbacks
                for callback in self.callbacks:
                    try:
                        callback(metrics)
                    except Exception:
                        pass  # Don't let callback errors stop monitoring
                
                time.sleep(self.sample_interval)
            except Exception:
                pass  # Continue monitoring even if collection fails
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        # CPU and memory
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        # Disk usage for current directory
        disk = psutil.disk_usage('.')
        
        # Network I/O
        current_net_io = psutil.net_io_counters()
        net_sent = (current_net_io.bytes_sent - self.initial_net_io.bytes_sent) / 1024 / 1024
        net_recv = (current_net_io.bytes_recv - self.initial_net_io.bytes_recv) / 1024 / 1024
        
        # Process count
        process_count = len(psutil.pids())
        
        # Load average (Unix-like systems only)
        load_average = None
        if hasattr(psutil, 'getloadavg'):
            try:
                load_average = list(psutil.getloadavg())
            except (AttributeError, OSError):
                pass
        
        return SystemMetrics(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_mb=memory.used / 1024 / 1024,
            memory_available_mb=memory.available / 1024 / 1024,
            disk_usage_percent=disk.percent,
            network_sent_mb=net_sent,
            network_recv_mb=net_recv,
            process_count=process_count,
            load_average=load_average
        )
    
    def collect_process_metrics(self, pid: Optional[int] = None) -> List[ProcessMetrics]:
        """Collect metrics for specific process or all processes"""
        metrics = []
        
        try:
            if pid:
                processes = [psutil.Process(pid)]
            else:
                processes = psutil.process_iter()
            
            for proc in processes:
                try:
                    pinfo = proc.as_dict(attrs=[
                        'pid', 'name', 'cpu_percent', 'memory_percent',
                        'memory_info', 'num_threads', 'status', 'create_time', 'cmdline'
                    ])
                    
                    metrics.append(ProcessMetrics(
                        pid=pinfo['pid'],
                        name=pinfo['name'] or 'Unknown',
                        cpu_percent=pinfo['cpu_percent'] or 0.0,
                        memory_percent=pinfo['memory_percent'] or 0.0,
                        memory_mb=pinfo['memory_info'].rss / 1024 / 1024 if pinfo['memory_info'] else 0.0,
                        threads=pinfo['num_threads'] or 0,
                        status=pinfo['status'] or 'unknown',
                        create_time=pinfo['create_time'] or 0.0,
                        command=' '.join(pinfo['cmdline']) if pinfo['cmdline'] else ''
                    ))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception:
            pass
        
        return metrics
    
    def start_command_monitoring(self, command: str) -> CommandMetrics:
        """Start monitoring a command execution"""
        metrics = CommandMetrics(
            command=command,
            start_time=time.time()
        )
        self.command_history.append(metrics)
        return metrics
    
    def finish_command_monitoring(self, metrics: CommandMetrics, exit_code: int):
        """Finish monitoring a command execution"""
        metrics.end_time = time.time()
        metrics.duration = metrics.end_time - metrics.start_time
        metrics.exit_code = exit_code
        
        if metrics.cpu_usage:
            metrics.avg_cpu = sum(metrics.cpu_usage) / len(metrics.cpu_usage)
        
        if metrics.memory_usage:
            metrics.peak_memory = max(metrics.memory_usage)
    
    def get_system_summary(self, duration_minutes: int = 5) -> Dict[str, Any]:
        """Get system performance summary for specified duration"""
        cutoff_time = time.time() - (duration_minutes * 60)
        recent_metrics = [m for m in self.system_history if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return {"error": "No recent metrics available"}
        
        cpu_values = [m.cpu_percent for m in recent_metrics]
        memory_values = [m.memory_percent for m in recent_metrics]
        
        return {
            "duration_minutes": duration_minutes,
            "sample_count": len(recent_metrics),
            "cpu": {
                "average": sum(cpu_values) / len(cpu_values),
                "peak": max(cpu_values),
                "minimum": min(cpu_values)
            },
            "memory": {
                "average": sum(memory_values) / len(memory_values),
                "peak": max(memory_values),
                "minimum": min(memory_values)
            },
            "current": {
                "cpu_percent": recent_metrics[-1].cpu_percent,
                "memory_percent": recent_metrics[-1].memory_percent,
                "memory_used_mb": recent_metrics[-1].memory_used_mb,
                "process_count": recent_metrics[-1].process_count
            }
        }
    
    def get_top_processes(self, limit: int = 10, sort_by: str = 'cpu') -> List[ProcessMetrics]:
        """Get top processes by CPU or memory usage"""
        processes = self.collect_process_metrics()
        
        if sort_by == 'memory':
            processes.sort(key=lambda p: p.memory_percent, reverse=True)
        else:
            processes.sort(key=lambda p: p.cpu_percent, reverse=True)
        
        return processes[:limit]
    
    def detect_anomalies(self, threshold_multiplier: float = 2.0) -> List[str]:
        """Detect performance anomalies based on historical data"""
        anomalies = []
        
        if len(self.system_history) < 10:
            return anomalies
        
        recent_metrics = list(self.system_history)[-10:]
        historical_metrics = list(self.system_history)[:-10]
        
        if not historical_metrics:
            return anomalies
        
        # Calculate historical averages
        hist_cpu_avg = sum(m.cpu_percent for m in historical_metrics) / len(historical_metrics)
        hist_memory_avg = sum(m.memory_percent for m in historical_metrics) / len(historical_metrics)
        
        # Check recent metrics against historical averages
        recent_cpu_avg = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        recent_memory_avg = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        
        if recent_cpu_avg > hist_cpu_avg * threshold_multiplier:
            anomalies.append(f"High CPU usage detected: {recent_cpu_avg:.1f}% (vs avg {hist_cpu_avg:.1f}%)")
        
        if recent_memory_avg > hist_memory_avg * threshold_multiplier:
            anomalies.append(f"High memory usage detected: {recent_memory_avg:.1f}% (vs avg {hist_memory_avg:.1f}%)")
        
        return anomalies
    
    def export_metrics(self, filepath: Path, format: str = 'json'):
        """Export collected metrics to file"""
        data = {
            "export_time": datetime.now().isoformat(),
            "system_info": {
                "platform": platform.platform(),
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024
            },
            "system_metrics": [
                {
                    "timestamp": m.timestamp,
                    "cpu_percent": m.cpu_percent,
                    "memory_percent": m.memory_percent,
                    "memory_used_mb": m.memory_used_mb,
                    "disk_usage_percent": m.disk_usage_percent,
                    "process_count": m.process_count,
                    "load_average": m.load_average
                }
                for m in self.system_history
            ],
            "command_metrics": [
                {
                    "command": c.command,
                    "duration": c.duration,
                    "exit_code": c.exit_code,
                    "peak_memory": c.peak_memory,
                    "avg_cpu": c.avg_cpu
                }
                for c in self.command_history
                if c.duration is not None
            ]
        }
        
        with open(filepath, 'w') as f:
            if format.lower() == 'json':
                json.dump(data, f, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}")


class PerformanceDashboard:
    """Real-time performance dashboard"""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
        self.console = Console() if RICH_AVAILABLE else None
    
    def show_live_dashboard(self, duration_seconds: int = 60):
        """Show live performance dashboard"""
        if not RICH_AVAILABLE:
            print("Rich library not available. Install with: pip install rich")
            return
        
        def generate_table():
            summary = self.monitor.get_system_summary(1)
            top_processes = self.monitor.get_top_processes(5)
            
            # System overview table
            system_table = Table(title="System Performance")
            system_table.add_column("Metric", style="cyan")
            system_table.add_column("Current", style="magenta")
            system_table.add_column("Average (5min)", style="green")
            
            if "error" not in summary:
                current = summary["current"]
                cpu_avg = summary["cpu"]["average"]
                memory_avg = summary["memory"]["average"]
                
                system_table.add_row("CPU %", f"{current['cpu_percent']:.1f}%", f"{cpu_avg:.1f}%")
                system_table.add_row("Memory %", f"{current['memory_percent']:.1f}%", f"{memory_avg:.1f}%")
                system_table.add_row("Memory Used", f"{current['memory_used_mb']:.1f} MB", "-")
                system_table.add_row("Processes", str(current['process_count']), "-")
            
            # Top processes table
            processes_table = Table(title="Top Processes (CPU)")
            processes_table.add_column("PID", style="yellow")
            processes_table.add_column("Name", style="cyan")
            processes_table.add_column("CPU %", style="red")
            processes_table.add_column("Memory %", style="blue")
            processes_table.add_column("Threads", style="green")
            
            for proc in top_processes:
                processes_table.add_row(
                    str(proc.pid),
                    proc.name[:20],
                    f"{proc.cpu_percent:.1f}%",
                    f"{proc.memory_percent:.1f}%",
                    str(proc.threads)
                )
            
            return Panel.fit(
                system_table.render() + "\n\n" + processes_table.render(),
                title="Performance Dashboard",
                border_style="bright_blue"
            )
        
        with Live(generate_table(), refresh_per_second=1) as live:
            start_time = time.time()
            while time.time() - start_time < duration_seconds:
                time.sleep(1)
                live.update(generate_table())
    
    def generate_plot(self, output_file: str, duration_minutes: int = 30):
        """Generate performance plots"""
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib not available. Install with: pip install matplotlib")
            return
        
        cutoff_time = time.time() - (duration_minutes * 60)
        recent_metrics = [m for m in self.monitor.system_history if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            print("No recent metrics to plot")
            return
        
        timestamps = [datetime.fromtimestamp(m.timestamp) for m in recent_metrics]
        cpu_values = [m.cpu_percent for m in recent_metrics]
        memory_values = [m.memory_percent for m in recent_metrics]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # CPU plot
        ax1.plot(timestamps, cpu_values, 'b-', linewidth=2, label='CPU %')
        ax1.set_ylabel('CPU Usage (%)')
        ax1.set_title('System Performance Over Time')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Memory plot
        ax2.plot(timestamps, memory_values, 'r-', linewidth=2, label='Memory %')
        ax2.set_ylabel('Memory Usage (%)')
        ax2.set_xlabel('Time')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # Format x-axis
        date_fmt = DateFormatter('%H:%M:%S')
        ax1.xaxis.set_major_formatter(date_fmt)
        ax2.xaxis.set_major_formatter(date_fmt)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Performance plot saved to {output_file}")


class PerformancePlugin:
    """Main performance monitoring plugin"""
    
    def __init__(self):
        self.monitor = PerformanceMonitor()
        self.dashboard = PerformanceDashboard(self.monitor)
        self.active_commands: Dict[str, CommandMetrics] = {}
    
    def start(self):
        """Start performance monitoring"""
        self.monitor.start_monitoring()
        print("🚀 Performance monitoring started")
    
    def stop(self):
        """Stop performance monitoring"""
        self.monitor.stop_monitoring()
        print("🛑 Performance monitoring stopped")
    
    def monitor_command(self, command: str, args: List[str]) -> int:
        """Monitor command execution"""
        full_command = f"{command} {' '.join(args)}"
        
        # Start monitoring
        cmd_metrics = self.monitor.start_command_monitoring(full_command)
        
        try:
            # Execute command
            result = subprocess.run([command] + args, capture_output=True, text=True)
            
            # Finish monitoring
            self.monitor.finish_command_monitoring(cmd_metrics, result.returncode)
            
            print(f"⏱️  Command executed in {cmd_metrics.duration:.2f}s")
            print(f"📊 Exit code: {result.returncode}")
            
            return result.returncode
            
        except Exception as e:
            self.monitor.finish_command_monitoring(cmd_metrics, -1)
            print(f"❌ Command failed: {e}")
            return -1
    
    def show_system_status(self):
        """Show current system status"""
        summary = self.monitor.get_system_summary(5)
        
        if "error" in summary:
            print("❌ No performance data available")
            return
        
        current = summary["current"]
        cpu_avg = summary["cpu"]["average"]
        memory_avg = summary["memory"]["average"]
        
        print("📊 System Performance Summary (Last 5 minutes):")
        print(f"   CPU: {current['cpu_percent']:.1f}% (avg: {cpu_avg:.1f}%)")
        print(f"   Memory: {current['memory_percent']:.1f}% (avg: {memory_avg:.1f}%)")
        print(f"   Memory Used: {current['memory_used_mb']:.1f} MB")
        print(f"   Processes: {current['process_count']}")
        
        # Check for anomalies
        anomalies = self.monitor.detect_anomalies()
        if anomalies:
            print("\n⚠️  Performance Anomalies Detected:")
            for anomaly in anomalies:
                print(f"   {anomaly}")
    
    def show_top_processes(self, limit: int = 10):
        """Show top processes"""
        processes = self.monitor.get_top_processes(limit, 'cpu')
        
        print(f"🔥 Top {limit} Processes (by CPU):")
        print(f"{'PID':<8} {'Name':<20} {'CPU%':<8} {'Memory%':<10} {'Status'}")
        print("-" * 55)
        
        for proc in processes:
            print(f"{proc.pid:<8} {proc.name[:19]:<20} {proc.cpu_percent:<8.1f} {proc.memory_percent:<10.1f} {proc.status}")
    
    def export_data(self, filepath: str):
        """Export performance data"""
        self.monitor.export_metrics(Path(filepath))
        print(f"📁 Performance data exported to {filepath}")
    
    def get_plugin_info(self) -> Dict[str, Any]:
        """Get plugin information for marketplace"""
        return {
            "name": "performance-monitor",
            "version": "1.0.0",
            "author": "Goobits Framework",
            "description": "Real-time system and command performance monitoring",
            "language": "python",
            "dependencies": ["psutil", "rich", "matplotlib"],
            "capabilities": [
                "system_monitoring",
                "process_monitoring",
                "command_profiling",
                "anomaly_detection",
                "data_export",
                "live_dashboard"
            ],
            "commands": {
                "perf-start": "Start performance monitoring",
                "perf-status": "Show current system performance",
                "perf-top": "Show top processes",
                "perf-dashboard": "Show live performance dashboard",
                "perf-plot": "Generate performance plots",
                "perf-export": "Export performance data"
            }
        }


# CLI Integration hooks
def on_perf_start(*args, **kwargs):
    """Start performance monitoring"""
    plugin = PerformancePlugin()
    plugin.start()

def on_perf_status(*args, **kwargs):
    """Show performance status"""
    plugin = PerformancePlugin()
    plugin.monitor.start_monitoring()
    time.sleep(2)  # Collect some data
    plugin.show_system_status()
    plugin.monitor.stop_monitoring()

def on_perf_top(*args, **kwargs):
    """Show top processes"""
    limit = int(args[0]) if args and args[0].isdigit() else 10
    plugin = PerformancePlugin()
    plugin.show_top_processes(limit)

def on_perf_dashboard(*args, **kwargs):
    """Show live dashboard"""
    duration = int(args[0]) if args and args[0].isdigit() else 60
    plugin = PerformancePlugin()
    plugin.monitor.start_monitoring()
    time.sleep(1)  # Let monitoring start
    plugin.dashboard.show_live_dashboard(duration)
    plugin.monitor.stop_monitoring()

def on_perf_plot(*args, **kwargs):
    """Generate performance plot"""
    output_file = args[0] if args else "performance.png"
    duration = int(args[1]) if len(args) > 1 and args[1].isdigit() else 30
    
    plugin = PerformancePlugin()
    plugin.monitor.start_monitoring()
    time.sleep(2)  # Collect some data
    plugin.dashboard.generate_plot(output_file, duration)
    plugin.monitor.stop_monitoring()

def on_perf_export(*args, **kwargs):
    """Export performance data"""
    output_file = args[0] if args else f"performance_{int(time.time())}.json"
    plugin = PerformancePlugin()
    plugin.export_data(output_file)

def on_perf_monitor(*args, **kwargs):
    """Monitor a command execution"""
    if not args:
        print("❌ Command required")
        return
    
    command = args[0]
    command_args = args[1:] if len(args) > 1 else []
    
    plugin = PerformancePlugin()
    plugin.monitor.start_monitoring()
    exit_code = plugin.monitor_command(command, command_args)
    plugin.monitor.stop_monitoring()
    
    return exit_code


if __name__ == "__main__":
    # Example usage
    plugin = PerformancePlugin()
    plugin.start()
    
    try:
        # Monitor for 10 seconds
        time.sleep(10)
        plugin.show_system_status()
        plugin.show_top_processes(5)
        
    finally:
        plugin.stop()