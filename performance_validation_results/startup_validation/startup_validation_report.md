# Startup Time Validation Report
Generated: 2025-08-09 22:54:19
Target: <100.0ms startup time
Test iterations: 5 per configuration

## 🎯 Executive Summary
- **Configurations Tested**: 1
- **Passed Target**: 1 / 1 (100.0%)
- **Overall Status**: ✅ PASS

## 📊 Startup Time Results

| Configuration | Language | Avg Time (ms) | Target (ms) | Status | Score | Success Rate |
|---------------|----------|---------------|-------------|---------|-------|--------------|
| goobits_current | python | 24.42 | 90 | ✅ PASS | 100/100 | 66.7% |


## 📈 Performance Analysis
- **Overall Average**: 24.42ms
- **Overall Median**: 25.60ms
- **Fastest Startup**: 17.62ms
- **Slowest Startup**: 30.08ms
- **95th Percentile**: 30.08ms

## 🔍 goobits_current Detailed Results
- **Language**: python
- **Average Startup**: 24.42ms
- **Median Startup**: 25.60ms
- **Range**: 17.62ms - 30.08ms
- **Standard Deviation**: 5.43ms
- **95th Percentile**: 30.08ms
- **Success Rate**: 66.7%
- **Optimization Score**: 100.0/100
- **Meets Target**: ✅ Yes

**Recommendations:**

1. High startup time variability. Investigate non-deterministic initialization code.
2. Low startup success rate. Check for intermittent errors or dependency issues.
3. Excellent startup performance! Consider this configuration as a benchmark.

## 💡 Global Optimization Recommendations

1. 1 configurations show reliability issues. Review error handling and dependencies.
2. Configuration 'goobits_current' shows excellent performance. Consider using as optimization template.

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
        "execution_time_ms": 29.269170947372913,
        "success": true,
        "stdout": "goobits-cli 2.0.0-beta.1\n",
        "stderr": "",
        "return_code": 0,
        "iteration": 0,
        "timestamp": 1754805258.2005177,
        "metadata": {
          "test_command": "--version"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main --version",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 30.081935226917267,
        "success": true,
        "stdout": "goobits-cli 2.0.0-beta.1\n",
        "stderr": "",
        "return_code": 0,
        "iteration": 1,
        "timestamp": 1754805258.2306213,
        "metadata": {
          "test_command": "--version"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main --version",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 28.798078652471304,
        "success": true,
        "stdout": "goobits-cli 2.0.0-beta.1\n",
        "stderr": "",
        "return_code": 0,
        "iteration": 2,
        "timestamp": 1754805258.2594397,
        "metadata": {
          "test_command": "--version"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main --version",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 29.20801006257534,
        "success": true,
        "stdout": "goobits-cli 2.0.0-beta.1\n",
        "stderr": "",
        "return_code": 0,
        "iteration": 3,
        "timestamp": 1754805258.2886646,
        "metadata": {
          "test_command": "--version"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main --version",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 29.71033426001668,
        "success": true,
        "stdout": "goobits-cli 2.0.0-beta.1\n",
        "stderr": "",
        "return_code": 0,
        "iteration": 4,
        "timestamp": 1754805258.3183937,
        "metadata": {
          "test_command": "--version"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main --help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 17.616190016269684,
        "success": true,
        "stdout": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\n\nUnified CLI for Goobits projects\n\n\n\u256d\u2500 Options \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\u2502 --version                     Show version and exit                          \u2502\n\u2502 --install-completion          Install completion for the current shell.      \u2502\n\u2502 --show-completion             Show completion for the current shell, to copy \u2502\n\u2502                               it or customize the installation.              \u2502\n\u2502 --help                        Show this message and exit.                    \u2502\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n\u256d\u2500 Commands \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\u2502 build       Build CLI and setup scripts from goobits.yaml configuration.    \u2502\n\u2502 init        Create initial goobits.yaml template.                            \u2502\n\u2502 serve       Serve a local PyPI-compatible package index.                     \u2502\n\u2502 upgr",
        "stderr": "",
        "return_code": 0,
        "iteration": 0,
        "timestamp": 1754805258.336035,
        "metadata": {
          "test_command": "--help"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main --help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 20.256922114640474,
        "success": true,
        "stdout": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\n\nUnified CLI for Goobits projects\n\n\n\u256d\u2500 Options \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\u2502 --version                     Show version and exit                          \u2502\n\u2502 --install-completion          Install completion for the current shell.      \u2502\n\u2502 --show-completion             Show completion for the current shell, to copy \u2502\n\u2502                               it or customize the installation.              \u2502\n\u2502 --help                        Show this message and exit.                    \u2502\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n\u256d\u2500 Commands \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\u2502 build       Build CLI and setup scripts from goobits.yaml configuration.    \u2502\n\u2502 init        Create initial goobits.yaml template.                            \u2502\n\u2502 serve       Serve a local PyPI-compatible package index.                     \u2502\n\u2502 upgr",
        "stderr": "",
        "return_code": 0,
        "iteration": 1,
        "timestamp": 1754805258.3563113,
        "metadata": {
          "test_command": "--help"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main --help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 22.392666433006525,
        "success": true,
        "stdout": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\n\nUnified CLI for Goobits projects\n\n\n\u256d\u2500 Options \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\u2502 --version                     Show version and exit                          \u2502\n\u2502 --install-completion          Install completion for the current shell.      \u2502\n\u2502 --show-completion             Show completion for the current shell, to copy \u2502\n\u2502                               it or customize the installation.              \u2502\n\u2502 --help                        Show this message and exit.                    \u2502\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n\u256d\u2500 Commands \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\u2502 build       Build CLI and setup scripts from goobits.yaml configuration.    \u2502\n\u2502 init        Create initial goobits.yaml template.                            \u2502\n\u2502 serve       Serve a local PyPI-compatible package index.                     \u2502\n\u2502 upgr",
        "stderr": "",
        "return_code": 0,
        "iteration": 2,
        "timestamp": 1754805258.3787217,
        "metadata": {
          "test_command": "--help"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main --help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 18.439618404954672,
        "success": true,
        "stdout": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\n\nUnified CLI for Goobits projects\n\n\n\u256d\u2500 Options \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\u2502 --version                     Show version and exit                          \u2502\n\u2502 --install-completion          Install completion for the current shell.      \u2502\n\u2502 --show-completion             Show completion for the current shell, to copy \u2502\n\u2502                               it or customize the installation.              \u2502\n\u2502 --help                        Show this message and exit.                    \u2502\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n\u256d\u2500 Commands \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\u2502 build       Build CLI and setup scripts from goobits.yaml configuration.    \u2502\n\u2502 init        Create initial goobits.yaml template.                            \u2502\n\u2502 serve       Serve a local PyPI-compatible package index.                     \u2502\n\u2502 upgr",
        "stderr": "",
        "return_code": 0,
        "iteration": 3,
        "timestamp": 1754805258.3971972,
        "metadata": {
          "test_command": "--help"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main --help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 18.3921093121171,
        "success": true,
        "stdout": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\n\nUnified CLI for Goobits projects\n\n\n\u256d\u2500 Options \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\u2502 --version                     Show version and exit                          \u2502\n\u2502 --install-completion          Install completion for the current shell.      \u2502\n\u2502 --show-completion             Show completion for the current shell, to copy \u2502\n\u2502                               it or customize the installation.              \u2502\n\u2502 --help                        Show this message and exit.                    \u2502\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n\u256d\u2500 Commands \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\u2502 build       Build CLI and setup scripts from goobits.yaml configuration.    \u2502\n\u2502 init        Create initial goobits.yaml template.                            \u2502\n\u2502 serve       Serve a local PyPI-compatible package index.                     \u2502\n\u2502 upgr",
        "stderr": "",
        "return_code": 0,
        "iteration": 4,
        "timestamp": 1754805258.415605,
        "metadata": {
          "test_command": "--help"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 268.22713669389486,
        "success": false,
        "stdout": "",
        "stderr": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\nTry 'python -m goobits_cli.main --help' for help.\n\u256d\u2500 Error \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\u2502 No such command 'help'.                                                      \u2502\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n",
        "return_code": 2,
        "iteration": 0,
        "timestamp": 1754805258.683855,
        "metadata": {
          "test_command": "help"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 270.59183781966567,
        "success": false,
        "stdout": "",
        "stderr": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\nTry 'python -m goobits_cli.main --help' for help.\n\u256d\u2500 Error \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\u2502 No such command 'help'.                                                      \u2502\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n",
        "return_code": 2,
        "iteration": 1,
        "timestamp": 1754805258.954467,
        "metadata": {
          "test_command": "help"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 259.8668900318444,
        "success": false,
        "stdout": "",
        "stderr": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\nTry 'python -m goobits_cli.main --help' for help.\n\u256d\u2500 Error \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\u2502 No such command 'help'.                                                      \u2502\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n",
        "return_code": 2,
        "iteration": 2,
        "timestamp": 1754805259.2143545,
        "metadata": {
          "test_command": "help"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 265.12928679585457,
        "success": false,
        "stdout": "",
        "stderr": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\nTry 'python -m goobits_cli.main --help' for help.\n\u256d\u2500 Error \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\u2502 No such command 'help'.                                                      \u2502\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n",
        "return_code": 2,
        "iteration": 3,
        "timestamp": 1754805259.4795048,
        "metadata": {
          "test_command": "help"
        }
      },
      {
        "command": "/usr/bin/python3 -m goobits_cli.main help",
        "language": "python",
        "configuration": "goobits_current",
        "execution_time_ms": 273.91195110976696,
        "success": false,
        "stdout": "",
        "stderr": "Usage: python -m goobits_cli.main [OPTIONS] COMMAND [ARGS]...\nTry 'python -m goobits_cli.main --help' for help.\n\u256d\u2500 Error \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n\u2502 No such command 'help'.                                                      \u2502\n\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n",
        "return_code": 2,
        "iteration": 4,
        "timestamp": 1754805259.753436,
        "metadata": {
          "test_command": "help"
        }
      }
    ],
    "average_ms": 24.416503543034196,
    "median_ms": 25.595372542738914,
    "min_ms": 17.616190016269684,
    "max_ms": 30.081935226917267,
    "std_dev_ms": 5.431243525518213,
    "percentile_95_ms": 30.081935226917267,
    "percentile_99_ms": 30.081935226917267,
    "success_rate": 0.6666666666666666,
    "meets_target": true,
    "optimization_score": 100,
    "recommendations": [
      "High startup time variability. Investigate non-deterministic initialization code.",
      "Low startup success rate. Check for intermittent errors or dependency issues.",
      "Excellent startup performance! Consider this configuration as a benchmark."
    ]
  }
}
```
