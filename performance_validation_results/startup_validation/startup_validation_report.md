# Startup Time Validation Report
Generated: 2025-08-23 22:46:33
Target: <100.0ms startup time
Test iterations: 5 per configuration

## 🎯 Executive Summary
- **Configurations Tested**: 1
- **Passed Target**: 0 / 1 (0.0%)
- **Overall Status**: ❌ FAIL

## 📊 Startup Time Results

| Configuration | Language | Avg Time (ms) | Target (ms) | Status | Score | Success Rate |
|---------------|----------|---------------|-------------|---------|-------|--------------|
| goobits_current | python | 141.06 | 90 | ❌ FAIL | 40/100 | 66.7% |


## 📈 Performance Analysis
- **Overall Average**: 141.06ms
- **Overall Median**: 140.84ms
- **Fastest Startup**: 137.71ms
- **Slowest Startup**: 144.74ms
- **95th Percentile**: 144.74ms

## 🔍 goobits_current Detailed Results
- **Language**: python
- **Average Startup**: 141.06ms
- **Median Startup**: 140.84ms
- **Range**: 137.71ms - 144.74ms
- **Standard Deviation**: 2.29ms
- **95th Percentile**: 144.74ms
- **Success Rate**: 66.7%
- **Optimization Score**: 39.7/100
- **Meets Target**: ❌ No

**Recommendations:**

1. Startup time exceeds target by 51.06ms. Consider optimization strategies.
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
        "command": "/usr/bin/python3 -m goobits_cli.main --version",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 142.48475607018918,
        "success": true,
        "stdout": "goobits-cli 2.0.0\n",
        "stderr": "",
        "return_code": 0,
        "iteration": 0,
        "timestamp": 1756014391.1494687,
        "metadata": {
          "test_command": "--version"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main --version",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 139.15172102861106,
        "success": true,
        "stdout": "goobits-cli 2.0.0\n",
        "stderr": "",
        "return_code": 0,
        "iteration": 1,
        "timestamp": 1756014391.2886448,
        "metadata": {
          "test_command": "--version"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main --version",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 140.59121196623892,
        "success": true,
        "stdout": "goobits-cli 2.0.0\n",
        "stderr": "",
        "return_code": 0,
        "iteration": 2,
        "timestamp": 1756014391.4292617,
        "metadata": {
          "test_command": "--version"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main --version",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 140.8542289864272,
        "success": true,
        "stdout": "goobits-cli 2.0.0\n",
        "stderr": "",
        "return_code": 0,
        "iteration": 3,
        "timestamp": 1756014391.5701349,
        "metadata": {
          "test_command": "--version"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main --version",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 140.8911239122972,
        "success": true,
        "stdout": "goobits-cli 2.0.0\n",
        "stderr": "",
        "return_code": 0,
        "iteration": 4,
        "timestamp": 1756014391.7110448,
        "metadata": {
          "test_command": "--version"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main --help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 138.89911293517798,
        "success": true,
        "stdout": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\n\n\n\nUnified CLI for Goobits projects\n\n\n\n\n\n\u256d\u2500 Options \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\n\u2502 --version                     Show version and exit                          \u2502\n\n\u2502 --install-completion          Install completion for the current shell.      \u2502\n\n\u2502 --show-completion             Show completion for the current shell, to copy \u2502\n\n\u2502                               it or customize the installation.              \u2502\n\n\u2502 --help                        Show this message and exit.                    \u2502\n\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n\n\u256d\u2500 Commands \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\n\u2502 build       Build CLI and setup scripts from goobits.yaml configuration.    \u2502\n\n\u2502 init        Create initial goobits.yaml template.                            \u2502\n\n\u2502 migrate     Migrate YAML configurations to 3.0.0 format.              ",
        "stderr": "",
        "return_code": 0,
        "iteration": 0,
        "timestamp": 1756014391.8499706,
        "metadata": {
          "test_command": "--help"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main --help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 140.8338660839945,
        "success": true,
        "stdout": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\n\n\n\nUnified CLI for Goobits projects\n\n\n\n\n\n\u256d\u2500 Options \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\n\u2502 --version                     Show version and exit                          \u2502\n\n\u2502 --install-completion          Install completion for the current shell.      \u2502\n\n\u2502 --show-completion             Show completion for the current shell, to copy \u2502\n\n\u2502                               it or customize the installation.              \u2502\n\n\u2502 --help                        Show this message and exit.                    \u2502\n\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n\n\u256d\u2500 Commands \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\n\u2502 build       Build CLI and setup scripts from goobits.yaml configuration.    \u2502\n\n\u2502 init        Create initial goobits.yaml template.                            \u2502\n\n\u2502 migrate     Migrate YAML configurations to 3.0.0 format.              ",
        "stderr": "",
        "return_code": 0,
        "iteration": 1,
        "timestamp": 1756014391.990823,
        "metadata": {
          "test_command": "--help"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main --help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 144.47633095551282,
        "success": true,
        "stdout": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\n\n\n\nUnified CLI for Goobits projects\n\n\n\n\n\n\u256d\u2500 Options \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\n\u2502 --version                     Show version and exit                          \u2502\n\n\u2502 --install-completion          Install completion for the current shell.      \u2502\n\n\u2502 --show-completion             Show completion for the current shell, to copy \u2502\n\n\u2502                               it or customize the installation.              \u2502\n\n\u2502 --help                        Show this message and exit.                    \u2502\n\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n\n\u256d\u2500 Commands \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\n\u2502 build       Build CLI and setup scripts from goobits.yaml configuration.    \u2502\n\n\u2502 init        Create initial goobits.yaml template.                            \u2502\n\n\u2502 migrate     Migrate YAML configurations to 3.0.0 format.              ",
        "stderr": "",
        "return_code": 0,
        "iteration": 2,
        "timestamp": 1756014392.1353183,
        "metadata": {
          "test_command": "--help"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main --help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 137.70566903986037,
        "success": true,
        "stdout": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\n\n\n\nUnified CLI for Goobits projects\n\n\n\n\n\n\u256d\u2500 Options \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\n\u2502 --version                     Show version and exit                          \u2502\n\n\u2502 --install-completion          Install completion for the current shell.      \u2502\n\n\u2502 --show-completion             Show completion for the current shell, to copy \u2502\n\n\u2502                               it or customize the installation.              \u2502\n\n\u2502 --help                        Show this message and exit.                    \u2502\n\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n\n\u256d\u2500 Commands \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\n\u2502 build       Build CLI and setup scripts from goobits.yaml configuration.    \u2502\n\n\u2502 init        Create initial goobits.yaml template.                            \u2502\n\n\u2502 migrate     Migrate YAML configurations to 3.0.0 format.              ",
        "stderr": "",
        "return_code": 0,
        "iteration": 3,
        "timestamp": 1756014392.2730453,
        "metadata": {
          "test_command": "--help"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main --help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 144.74447909742594,
        "success": true,
        "stdout": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\n\n\n\nUnified CLI for Goobits projects\n\n\n\n\n\n\u256d\u2500 Options \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\n\u2502 --version                     Show version and exit                          \u2502\n\n\u2502 --install-completion          Install completion for the current shell.      \u2502\n\n\u2502 --show-completion             Show completion for the current shell, to copy \u2502\n\n\u2502                               it or customize the installation.              \u2502\n\n\u2502 --help                        Show this message and exit.                    \u2502\n\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n\n\u256d\u2500 Commands \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\n\u2502 build       Build CLI and setup scripts from goobits.yaml configuration.    \u2502\n\n\u2502 init        Create initial goobits.yaml template.                            \u2502\n\n\u2502 migrate     Migrate YAML configurations to 3.0.0 format.              ",
        "stderr": "",
        "return_code": 0,
        "iteration": 4,
        "timestamp": 1756014392.4178102,
        "metadata": {
          "test_command": "--help"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 145.84001305047423,
        "success": false,
        "stdout": "",
        "stderr": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\nTry 'python -m goobits_cli.main --help' for help.\n\u256d\u2500 Error \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\u2502 No such command 'help'.                                                      \u2502\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n",
        "return_code": 2,
        "iteration": 0,
        "timestamp": 1756014392.5636742,
        "metadata": {
          "test_command": "help"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 145.80053300596774,
        "success": false,
        "stdout": "",
        "stderr": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\nTry 'python -m goobits_cli.main --help' for help.\n\u256d\u2500 Error \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\u2502 No such command 'help'.                                                      \u2502\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n",
        "return_code": 2,
        "iteration": 1,
        "timestamp": 1756014392.7094934,
        "metadata": {
          "test_command": "help"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 142.04091602005064,
        "success": false,
        "stdout": "",
        "stderr": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\nTry 'python -m goobits_cli.main --help' for help.\n\u256d\u2500 Error \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\u2502 No such command 'help'.                                                      \u2502\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n",
        "return_code": 2,
        "iteration": 2,
        "timestamp": 1756014392.8515542,
        "metadata": {
          "test_command": "help"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 141.62731810938567,
        "success": false,
        "stdout": "",
        "stderr": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\nTry 'python -m goobits_cli.main --help' for help.\n\u256d\u2500 Error \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\u2502 No such command 'help'.                                                      \u2502\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n",
        "return_code": 2,
        "iteration": 3,
        "timestamp": 1756014392.9931993,
        "metadata": {
          "test_command": "help"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 149.08061595633626,
        "success": false,
        "stdout": "",
        "stderr": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\nTry 'python -m goobits_cli.main --help' for help.\n\u256d\u2500 Error \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\u2502 No such command 'help'.                                                      \u2502\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n",
        "return_code": 2,
        "iteration": 4,
        "timestamp": 1756014393.1422973,
        "metadata": {
          "test_command": "help"
        }
      }
    ],
    "average_ms": 141.06325000757352,
    "median_ms": 140.84404753521085,
    "min_ms": 137.70566903986037,
    "max_ms": 144.74447909742594,
    "std_dev_ms": 2.289609015441384,
    "percentile_95_ms": 144.74447909742594,
    "percentile_99_ms": 144.74447909742594,
    "success_rate": 0.6666666666666666,
    "meets_target": false,
    "optimization_score": 39.67537838305604,
    "recommendations": [
      "Startup time exceeds target by 51.06ms. Consider optimization strategies.",
      "Moderately high startup time. Review initialization code for bottlenecks.",
      "Low startup success rate. Check for intermittent errors or dependency issues.",
      "Python: Consider using importlib for lazy imports and __pycache__ optimization.",
      "Low optimization score. Implement comprehensive performance optimization."
    ]
  }
}
```
