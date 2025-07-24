#!/usr/bin/env python3
"""
Local PyPI server for serving Python packages in Docker environments.

This module provides a simple HTTP server that can serve Python packages
(.whl and .tar.gz files) in a PyPI-compatible format for use with pip install.
"""

import logging
import mimetypes
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote
from typing import List, Optional
import threading
import signal
import sys


class PyPIHandler(BaseHTTPRequestHandler):
    """Custom HTTP request handler for serving PyPI packages."""
    
    def __init__(self, *args, package_dir: Path, **kwargs):
        self.package_dir = package_dir
        super().__init__(*args, **kwargs)
    
    def log_message(self, format: str, *args) -> None:
        """Override to use proper logging instead of stderr."""
        logging.info(f"{self.client_address[0]} - - [{self.log_date_time_string()}] {format % args}")
    
    def do_GET(self) -> None:
        """Handle GET requests for package files and index."""
        # Parse the path
        path = unquote(self.path.lstrip('/'))
        
        # Handle root path - return package index
        if path == '' or path == 'index.html':
            self._serve_index()
            return
        
        # Handle PyPI Simple API: /simple/package-name/
        if path.startswith('simple/') and path.endswith('/'):
            package_name = path[7:-1]  # Remove 'simple/' and trailing '/'
            self._serve_package_simple_page(package_name)
            return
        
        # Handle direct package file requests
        file_path = self.package_dir / path
        
        if file_path.exists() and file_path.is_file():
            self._serve_file(file_path)
        else:
            # Try to find file with normalized package name
            normalized_path = self._find_normalized_package_file(path)
            if normalized_path:
                self._serve_file(normalized_path)
            else:
                self._send_404()
    
    def _serve_index(self) -> None:
        """Generate and serve the package index HTML."""
        try:
            index_html = self._generate_index_html()
            self._send_response(200, index_html, 'text/html')
        except Exception as e:
            logging.error(f"Error generating index: {e}")
            self._send_error(500, "Internal server error")
    
    def _serve_file(self, file_path: Path) -> None:
        """Serve a package file with appropriate content type."""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(str(file_path))
            if content_type is None:
                if file_path.suffix == '.whl':
                    content_type = 'application/zip'
                elif file_path.suffix == '.tar.gz':
                    content_type = 'application/gzip'
                else:
                    content_type = 'application/octet-stream'
            
            self._send_response(200, content, content_type)
            
        except Exception as e:
            logging.error(f"Error serving file {file_path}: {e}")
            self._send_error(500, "Internal server error")
    
    def _generate_index_html(self) -> str:
        """Generate HTML index of available packages."""
        packages = self._get_package_files()
        
        # Extract unique package names for Simple API
        package_names = set()
        for package_file in packages:
            base_name = package_file.name.split('-')[0]
            normalized_name = self._normalize_package_name(base_name)
            package_names.add((base_name, normalized_name))
        
        html_lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<title>Local PyPI Server</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 40px; }",
            "h1, h2 { color: #333; }",
            "a { display: block; margin: 5px 0; text-decoration: none; color: #0066cc; }",
            "a:hover { text-decoration: underline; }",
            ".package-list { margin: 20px 0; }",
            ".stats { color: #666; font-size: 0.9em; margin-bottom: 20px; }",
            ".simple-api { background: #f5f5f5; padding: 10px; margin: 20px 0; }",
            "</style>",
            "</head>",
            "<body>",
            "<h1>Local PyPI Server</h1>",
            f'<div class="stats">Serving {len(packages)} packages from: {self.package_dir}</div>',
        ]
        
        # Add Simple API section
        if package_names:
            html_lines.extend([
                '<div class="simple-api">',
                '<h2>PyPI Simple API (for pip install)</h2>',
                '<p>Use these links for package installation:</p>',
            ])
            
            for base_name, normalized_name in sorted(package_names):
                simple_url = f"/simple/{normalized_name}/"
                html_lines.append(f'<a href="{simple_url}">{base_name}</a>')
            
            html_lines.append('</div>')
        
        # Add direct file downloads
        html_lines.extend([
            '<h2>Direct Downloads</h2>',
            '<div class="package-list">',
        ])
        
        if packages:
            for package_file in sorted(packages):
                html_lines.append(f'<a href="{package_file.name}">{package_file.name}</a>')
        else:
            html_lines.append('<p>No packages found in the directory.</p>')
            html_lines.append('<p>Place .whl or .tar.gz files in the package directory to serve them.</p>')
        
        html_lines.extend([
            '</div>',
            '<hr>',
            '<p><em>To install packages from this server:</em></p>',
            '<code>pip install --index-url http://localhost:8080/simple --trusted-host localhost PACKAGE_NAME</code>',
            '</body>',
            '</html>'
        ])
        
        return '\n'.join(html_lines)
    
    def _get_package_files(self) -> List[Path]:
        """Get list of Python package files in the directory."""
        if not self.package_dir.exists():
            return []
        
        package_files = []
        for file_path in self.package_dir.iterdir():
            if file_path.is_file() and file_path.suffix in ['.whl', '.gz']:
                # For .tar.gz files, check the full suffix
                if file_path.suffix == '.gz' and file_path.stem.endswith('.tar'):
                    package_files.append(file_path)
                elif file_path.suffix == '.whl':
                    package_files.append(file_path)
        
        return package_files
    
    def _send_response(self, status_code: int, content: bytes | str, content_type: str) -> None:
        """Send HTTP response with proper headers."""
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(content)
    
    def _send_404(self) -> None:
        """Send 404 Not Found response."""
        content = "404 Not Found"
        self._send_response(404, content, 'text/plain')
    
    def _send_error(self, status_code: int, message: str) -> None:
        """Send error response."""
        self._send_response(status_code, message, 'text/plain')
    
    def _normalize_package_name(self, name: str) -> str:
        """Normalize package name according to PEP 508."""
        import re
        return re.sub(r"[-_.]+", "-", name).lower()
    
    def _find_normalized_package_file(self, requested_path: str) -> Optional[Path]:
        """Find package file using normalized name matching."""
        # Extract package name from path
        if '/' in requested_path:
            return None
        
        requested_base = requested_path.split('-')[0] if '-' in requested_path else requested_path
        requested_normalized = self._normalize_package_name(requested_base)
        
        # Search for matching files
        for file_path in self.package_dir.glob("*.whl"):
            file_base = file_path.name.split('-')[0]
            file_normalized = self._normalize_package_name(file_base)
            
            if requested_normalized == file_normalized:
                return file_path
        
        return None
    
    def _serve_package_simple_page(self, package_name: str) -> None:
        """Serve PyPI Simple API page for a specific package."""
        normalized_name = self._normalize_package_name(package_name)
        
        # Find matching package files
        matching_files = []
        for file_path in self.package_dir.glob("*.whl"):
            file_base = file_path.name.split('-')[0]
            file_normalized = self._normalize_package_name(file_base)
            
            if normalized_name == file_normalized:
                matching_files.append(file_path)
        
        if not matching_files:
            self._send_404()
            return
        
        # Generate simple API HTML
        html_lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            f"<title>Links for {package_name}</title>",
            "</head>",
            "<body>",
            f"<h1>Links for {package_name}</h1>",
        ]
        
        for file_path in matching_files:
            # Create direct download link
            file_url = f"/{file_path.name}"
            html_lines.append(f'<a href="{file_url}">{file_path.name}</a><br/>')
        
        html_lines.extend([
            "</body>",
            "</html>"
        ])
        
        html_content = '\n'.join(html_lines)
        self._send_response(200, html_content, 'text/html')


class PyPIServer:
    """Local PyPI server for serving Python packages."""
    
    def __init__(self, package_dir: Path, host: str = "localhost", port: int = 8080):
        self.package_dir = Path(package_dir).resolve()
        self.host = host
        self.port = port
        self.server: Optional[HTTPServer] = None
        self.server_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def start(self) -> None:
        """Start the PyPI server."""
        # Validate package directory
        if not self.package_dir.exists():
            logging.warning(f"Package directory does not exist: {self.package_dir}")
            logging.info("Creating package directory...")
            self.package_dir.mkdir(parents=True, exist_ok=True)
        
        # Create handler factory with package directory
        def handler_factory(*args, **kwargs):
            return PyPIHandler(*args, package_dir=self.package_dir, **kwargs)
        
        try:
            # Create and start server
            self.server = HTTPServer((self.host, self.port), handler_factory)
            
            logging.info(f"Starting PyPI server on http://{self.host}:{self.port}")
            logging.info(f"Serving packages from: {self.package_dir}")
            
            # List available packages
            packages = self._get_available_packages()
            if packages:
                logging.info(f"Available packages: {', '.join(packages)}")
            else:
                logging.info("No packages found - place .whl or .tar.gz files in the directory")
            
            # Set up signal handlers for graceful shutdown (only in main thread)
            try:
                signal.signal(signal.SIGINT, self._signal_handler)
                signal.signal(signal.SIGTERM, self._signal_handler)
            except ValueError:
                # Signal handling only works in main thread, skip if not available
                pass
            
            # Start server in a separate thread
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            
            logging.info("✅ PyPI server started successfully!")
            logging.info("Usage example:")
            logging.info(f"  pip install --index-url http://{self.host}:{self.port} --trusted-host {self.host} PACKAGE_NAME")
            
        except OSError as e:
            if e.errno == 48:  # Address already in use
                logging.error(f"Port {self.port} is already in use. Try a different port.")
            else:
                logging.error(f"Failed to start server: {e}")
            raise
        except Exception as e:
            logging.error(f"Failed to start PyPI server: {e}")
            raise
    
    def _run_server(self) -> None:
        """Run the server in a loop until shutdown."""
        try:
            while not self._shutdown_event.is_set():
                self.server.handle_request()
        except Exception as e:
            if not self._shutdown_event.is_set():
                logging.error(f"Server error: {e}")
    
    def stop(self) -> None:
        """Stop the PyPI server."""
        if self.server:
            logging.info("Shutting down PyPI server...")
            self._shutdown_event.set()
            self.server.server_close()
            
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=5)
            
            logging.info("✅ PyPI server stopped")
    
    def wait_for_shutdown(self) -> None:
        """Wait for the server to be shut down (blocking call)."""
        try:
            if self.server_thread:
                self.server_thread.join()
        except KeyboardInterrupt:
            logging.info("Received interrupt signal")
            self.stop()
    
    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals."""
        logging.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def _get_available_packages(self) -> List[str]:
        """Get list of available package names."""
        if not self.package_dir.exists():
            return []
        
        packages = []
        for file_path in self.package_dir.iterdir():
            if file_path.is_file():
                if file_path.suffix == '.whl' or (file_path.suffix == '.gz' and file_path.stem.endswith('.tar')):
                    packages.append(file_path.name)
        
        return sorted(packages)


def serve_packages(package_dir: Path, host: str = "localhost", port: int = 8080) -> None:
    """
    Start a local PyPI server to serve Python packages.
    
    Args:
        package_dir: Directory containing .whl and .tar.gz package files
        host: Host to bind the server to (default: localhost)
        port: Port to run the server on (default: 8080)
    """
    server = PyPIServer(package_dir, host, port)
    
    try:
        server.start()
        server.wait_for_shutdown()
    except KeyboardInterrupt:
        logging.info("Interrupted by user")
    except Exception as e:
        logging.error(f"Server error: {e}")
        raise
    finally:
        server.stop()


if __name__ == "__main__":
    # Simple command-line interface for testing
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python pypi_server.py <package_directory>")
        sys.exit(1)
    
    package_dir = Path(sys.argv[1])
    serve_packages(package_dir)