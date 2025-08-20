# Startup Time Validation Report
Generated: 2025-08-20 12:52:44
Target: <100.0ms startup time
Test iterations: 5 per configuration

## 🎯 Executive Summary
- **Configurations Tested**: 1
- **Passed Target**: 0 / 1 (0.0%)
- **Overall Status**: ❌ FAIL

## 📊 Startup Time Results

| Configuration | Language | Avg Time (ms) | Target (ms) | Status | Score | Success Rate |
|---------------|----------|---------------|-------------|---------|-------|--------------|
| goobits_current | python | 139.55 | 90 | ❌ FAIL | 40/100 | 66.7% |


## 📈 Performance Analysis
- **Overall Average**: 139.55ms
- **Overall Median**: 139.43ms
- **Fastest Startup**: 136.24ms
- **Slowest Startup**: 143.93ms
- **95th Percentile**: 143.93ms

## 🔍 goobits_current Detailed Results
- **Language**: python
- **Average Startup**: 139.55ms
- **Median Startup**: 139.43ms
- **Range**: 136.24ms - 143.93ms
- **Standard Deviation**: 2.74ms
- **95th Percentile**: 143.93ms
- **Success Rate**: 66.7%
- **Optimization Score**: 39.6/100
- **Meets Target**: ❌ No

**Recommendations:**

1. Startup time exceeds target by 49.55ms. Consider optimization strategies.
2. Moderately high startup time. Review initialization code for bottlenecks.
3. Low startup success rate. Check for intermittent errors or dependency issues.
4. Python: Consider using importlib for lazy imports and __pycache__ optimization.
5. Low optimization score. Implement comprehensive performance optimization.

## 💡 Global Optimization Recommendations

1. More than 50% of configurations exceed startup targets. Consider framework-wide optimization.
2. Python shows consistently slow startup times. Implement python-specific optimizations.
3. 1 configurations show reliability issues. Review error handling and dependencies.

## 📄 Raw Measurement Data
```json
{
  "goobits_current": {
    "test_name": "goobits_current",
    "language": "python",
    "configuration": "goobits_current",
    "target_ms": 90.0,
    "measurements": [
      {
        "command": "/workspace/venv/bin/python -m goobits_cli.main --version",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 140.16464701853693,
        "success": true,
        "stdout": "goobits-cli 2.0.0-rc2\n",
        "stderr": "",
        "return_code": 0,
        "iteration": 0,
        "timestamp": 1755719562.2870028,
        "metadata": {
          "test_command": "--version"
        }
      },
      {
        "command": "/workspace/venv/bin/python -m goobits_cli.main --version",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 142.4220220069401,
        "success": true,
        "stdout": "goobits-cli 2.0.0-rc2\n",
        "stderr": "",
        "return_code": 0,
        "iteration": 1,
        "timestamp": 1755719562.4294477,
        "metadata": {
          "test_command": "--version"
        }
      },
      {
        "command": "/workspace/venv/bin/python -m goobits_cli.main --version",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 143.92809598939493,
        "success": true,
        "stdout": "goobits-cli 2.0.0-rc2\n",
        "stderr": "",
        "return_code": 0,
        "iteration": 2,
        "timestamp": 1755719562.573399,
        "metadata": {
          "test_command": "--version"
        }
      },
      {
        "command": "/workspace/venv/bin/python -m goobits_cli.main --version",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 138.84879602119327,
        "success": true,
        "stdout": "goobits-cli 2.0.0-rc2\n",
        "stderr": "",
        "return_code": 0,
        "iteration": 3,
        "timestamp": 1755719562.71227,
        "metadata": {
          "test_command": "--version"
        }
      },
      {
        "command": "/workspace/venv/bin/python -m goobits_cli.main --version",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 137.19573902199045,
        "success": true,
        "stdout": "goobits-cli 2.0.0-rc2\n",
        "stderr": "",
        "return_code": 0,
        "iteration": 4,
        "timestamp": 1755719562.849484,
        "metadata": {
          "test_command": "--version"
        }
      },
      {
        "command": "/workspace/venv/bin/python -m goobits_cli.main --help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 136.24454697128385,
        "success": true,
        "stdout": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\n\n\n\nUnified CLI for Goobits projects\n\n\n\n\n\n\u256d\u2500 Options \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\n\u2502 --version                     Show version and exit                          \u2502\n\n\u2502 --install-completion          Install completion for the current shell.      \u2502\n\n\u2502 --show-completion             Show completion for the current shell, to copy \u2502\n\n\u2502                               it or customize the installation.              \u2502\n\n\u2502 --help                        Show this message and exit.                    \u2502\n\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n\n\u256d\u2500 Commands \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\n\u2502 build       Build CLI and setup scripts from goobits.yaml configuration.    \u2502\n\n\u2502 init        Create initial goobits.yaml template.                            \u2502\n\n\u2502 serve       Serve a local PyPI-compatible package index.              ",
        "stderr": "",
        "return_code": 0,
        "iteration": 0,
        "timestamp": 1755719562.9857514,
        "metadata": {
          "test_command": "--help"
        }
      },
      {
        "command": "/workspace/venv/bin/python -m goobits_cli.main --help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 142.6269409712404,
        "success": true,
        "stdout": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\n\n\n\nUnified CLI for Goobits projects\n\n\n\n\n\n\u256d\u2500 Options \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\n\u2502 --version                     Show version and exit                          \u2502\n\n\u2502 --install-completion          Install completion for the current shell.      \u2502\n\n\u2502 --show-completion             Show completion for the current shell, to copy \u2502\n\n\u2502                               it or customize the installation.              \u2502\n\n\u2502 --help                        Show this message and exit.                    \u2502\n\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n\n\u256d\u2500 Commands \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\n\u2502 build       Build CLI and setup scripts from goobits.yaml configuration.    \u2502\n\n\u2502 init        Create initial goobits.yaml template.                            \u2502\n\n\u2502 serve       Serve a local PyPI-compatible package index.              ",
        "stderr": "",
        "return_code": 0,
        "iteration": 1,
        "timestamp": 1755719563.1283984,
        "metadata": {
          "test_command": "--help"
        }
      },
      {
        "command": "/workspace/venv/bin/python -m goobits_cli.main --help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 136.38973800698295,
        "success": true,
        "stdout": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\n\n\n\nUnified CLI for Goobits projects\n\n\n\n\n\n\u256d\u2500 Options \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\n\u2502 --version                     Show version and exit                          \u2502\n\n\u2502 --install-completion          Install completion for the current shell.      \u2502\n\n\u2502 --show-completion             Show completion for the current shell, to copy \u2502\n\n\u2502                               it or customize the installation.              \u2502\n\n\u2502 --help                        Show this message and exit.                    \u2502\n\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n\n\u256d\u2500 Commands \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\n\u2502 build       Build CLI and setup scripts from goobits.yaml configuration.    \u2502\n\n\u2502 init        Create initial goobits.yaml template.                            \u2502\n\n\u2502 serve       Serve a local PyPI-compatible package index.              ",
        "stderr": "",
        "return_code": 0,
        "iteration": 2,
        "timestamp": 1755719563.2648103,
        "metadata": {
          "test_command": "--help"
        }
      },
      {
        "command": "/workspace/venv/bin/python -m goobits_cli.main --help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 140.01540001481771,
        "success": true,
        "stdout": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\n\n\n\nUnified CLI for Goobits projects\n\n\n\n\n\n\u256d\u2500 Options \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\n\u2502 --version                     Show version and exit                          \u2502\n\n\u2502 --install-completion          Install completion for the current shell.      \u2502\n\n\u2502 --show-completion             Show completion for the current shell, to copy \u2502\n\n\u2502                               it or customize the installation.              \u2502\n\n\u2502 --help                        Show this message and exit.                    \u2502\n\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n\n\u256d\u2500 Commands \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\n\u2502 build       Build CLI and setup scripts from goobits.yaml configuration.    \u2502\n\n\u2502 init        Create initial goobits.yaml template.                            \u2502\n\n\u2502 serve       Serve a local PyPI-compatible package index.              ",
        "stderr": "",
        "return_code": 0,
        "iteration": 3,
        "timestamp": 1755719563.4048448,
        "metadata": {
          "test_command": "--help"
        }
      },
      {
        "command": "/workspace/venv/bin/python -m goobits_cli.main --help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 137.7135260263458,
        "success": true,
        "stdout": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\n\n\n\nUnified CLI for Goobits projects\n\n\n\n\n\n\u256d\u2500 Options \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\n\u2502 --version                     Show version and exit                          \u2502\n\n\u2502 --install-completion          Install completion for the current shell.      \u2502\n\n\u2502 --show-completion             Show completion for the current shell, to copy \u2502\n\n\u2502                               it or customize the installation.              \u2502\n\n\u2502 --help                        Show this message and exit.                    \u2502\n\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n\n\u256d\u2500 Commands \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\n\u2502 build       Build CLI and setup scripts from goobits.yaml configuration.    \u2502\n\n\u2502 init        Create initial goobits.yaml template.                            \u2502\n\n\u2502 serve       Serve a local PyPI-compatible package index.              ",
        "stderr": "",
        "return_code": 0,
        "iteration": 4,
        "timestamp": 1755719563.542578,
        "metadata": {
          "test_command": "--help"
        }
      },
      {
        "command": "/workspace/venv/bin/python -m goobits_cli.main help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 279.34093202929944,
        "success": false,
        "stdout": "",
        "stderr": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\nTry 'python -m goobits_cli.main --help' for help.\n\u256d\u2500 Error \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\u2502 No such command 'help'.                                                      \u2502\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n",
        "return_code": 2,
        "iteration": 0,
        "timestamp": 1755719563.8219395,
        "metadata": {
          "test_command": "help"
        }
      },
      {
        "command": "/workspace/venv/bin/python -m goobits_cli.main help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 290.38336500525475,
        "success": false,
        "stdout": "",
        "stderr": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\nTry 'python -m goobits_cli.main --help' for help.\n\u256d\u2500 Error \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\u2502 No such command 'help'.                                                      \u2502\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n",
        "return_code": 2,
        "iteration": 1,
        "timestamp": 1755719564.1123447,
        "metadata": {
          "test_command": "help"
        }
      },
      {
        "command": "/workspace/venv/bin/python -m goobits_cli.main help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 280.42514802655205,
        "success": false,
        "stdout": "",
        "stderr": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\nTry 'python -m goobits_cli.main --help' for help.\n\u256d\u2500 Error \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\u2502 No such command 'help'.                                                      \u2502\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n",
        "return_code": 2,
        "iteration": 2,
        "timestamp": 1755719564.3927937,
        "metadata": {
          "test_command": "help"
        }
      },
      {
        "command": "/workspace/venv/bin/python -m goobits_cli.main help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 285.13979201670736,
        "success": false,
        "stdout": "",
        "stderr": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\nTry 'python -m goobits_cli.main --help' for help.\n\u256d\u2500 Error \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\u2502 No such command 'help'.                                                      \u2502\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n",
        "return_code": 2,
        "iteration": 3,
        "timestamp": 1755719564.6779525,
        "metadata": {
          "test_command": "help"
        }
      },
      {
        "command": "/workspace/venv/bin/python -m goobits_cli.main help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 288.57402299763635,
        "success": false,
        "stdout": "",
        "stderr": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\nTry 'python -m goobits_cli.main --help' for help.\n\u256d\u2500 Error \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\u2502 No such command 'help'.                                                      \u2502\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n",
        "return_code": 2,
        "iteration": 4,
        "timestamp": 1755719564.9665458,
        "metadata": {
          "test_command": "help"
        }
      }
    ],
    "average_ms": 139.55494520487264,
    "median_ms": 139.4320980180055,
    "min_ms": 136.24454697128385,
    "max_ms": 143.92809598939493,
    "std_dev_ms": 2.7446531503152207,
    "percentile_95_ms": 143.92809598939493,
    "percentile_99_ms": 143.92809598939493,
    "success_rate": 0.6666666666666666,
    "meets_target": false,
    "optimization_score": 39.60665626771076,
    "recommendations": [
      "Startup time exceeds target by 49.55ms. Consider optimization strategies.",
      "Moderately high startup time. Review initialization code for bottlenecks.",
      "Low startup success rate. Check for intermittent errors or dependency issues.",
      "Python: Consider using importlib for lazy imports and __pycache__ optimization.",
      "Low optimization score. Implement comprehensive performance optimization."
    ]
  }
}
```
