# Performance Validation Suite

Comprehensive performance validation and benchmarking tools for the Goobits CLI Framework.

## 🎯 Overview

This performance validation suite ensures the Goobits CLI Framework meets production performance requirements:
- **Startup Time**: <100ms across all languages
- **Memory Usage**: <50MB for typical operations  
- **Template Rendering**: <500ms for complex CLI generation
- **Cross-Language Parity**: Consistent performance across Python, Node.js, and TypeScript

## 🚀 Quick Start

### Run Complete Performance Validation
```bash
python performance/performance_suite.py --quick
```

### Individual Performance Tools

**Startup Time Validation**
```bash
python performance/startup_validator.py \
  --command "python cli.py" \
  --target 90 \
  --iterations 10
```

**Memory Usage Profiling**
```bash
python performance/memory_profiler.py \
  --command "python cli.py --help" \
  --iterations 5
```

**Template Rendering Benchmarks**
```bash
python performance/template_benchmark.py \
  --iterations 3 \
  --complexity all
```

**Cross-Language Performance Analysis**
```bash
python performance/cross_language_analyzer.py \
  --language all
```

## 📊 Tools Overview

### 1. Performance Suite (`performance_suite.py`)
**Master controller** that orchestrates all performance validation tools.

**Features:**
- Comprehensive validation across all performance metrics
- Production readiness assessment
- Unified reporting with pass/fail criteria
- CI/CD pipeline integration support

### 2. Startup Validator (`startup_validator.py`) 
**Validates CLI startup times** against <100ms targets.

**Features:**
- Language-specific startup targets (Python: 90ms, Node.js: 70ms, TypeScript: 80ms)
- Statistical analysis with multiple iterations
- Warmup iterations for accurate measurements
- Success rate and reliability tracking

### 3. Memory Profiler (`memory_profiler.py`)
**Real-time memory monitoring** with leak detection.

**Features:**
- Background memory sampling during CLI execution
- Memory leak detection using weak references  
- Allocation tracking with tracemalloc
- Memory optimization scoring (0-100)
- Phase-based memory analysis

### 4. Template Benchmark (`template_benchmark.py`)
**Compares Universal vs Legacy** template rendering performance.

**Features:**
- Template rendering across complexity levels (5-150 commands)
- Universal vs Legacy performance comparison
- Cross-language template performance analysis
- Scaling analysis for large CLI configurations

### 5. Cross-Language Analyzer (`cross_language_analyzer.py`)
**Performance parity analysis** across all supported languages.

**Features:**
- Performance consistency validation
- Feature completeness comparison
- Language-specific optimization recommendations
- Performance leader identification

### 6. Benchmark Suite (`benchmark_suite.py`)
**Comprehensive benchmarking** framework with rich metrics.

**Features:**
- Multi-configuration testing (minimal, standard, full-feature)
- Statistical analysis with confidence intervals
- Performance regression detection
- Detailed performance reporting

## 📈 Performance Targets

| Metric | Python | Node.js | TypeScript |
|--------|--------|---------|------------|
| Startup Time | <90ms | <70ms | <80ms |
| Memory Usage | <35MB | <45MB | <50MB |
| Template Render | <60ms | <50ms | <70ms |

## 🔧 Configuration

### Environment Variables
```bash
export PERF_ITERATIONS=10        # Test iterations
export PERF_TIMEOUT_MS=5000      # Command timeout
export PERF_OUTPUT_DIR=results   # Results directory
```

### Command Line Options
```bash
--iterations N          # Number of test iterations
--target-startup MS     # Startup time target in milliseconds  
--target-memory MB      # Memory usage target in megabytes
--output-dir PATH       # Output directory for results
--quick                 # Quick validation with fewer iterations
--verbose               # Detailed output during testing
```

## 📊 Output Formats

### Reports Generated
- **Markdown Reports**: Human-readable analysis with recommendations
- **JSON Data**: Machine-readable results for integration
- **CSV Files**: Statistical data for spreadsheet analysis
- **Production Summary**: Binary pass/fail for deployment decisions

### Key Metrics
- **Startup Time**: Average, median, 95th percentile, standard deviation
- **Memory Usage**: Peak, baseline, increase, leak detection
- **Template Performance**: Rendering time, scaling factor, universal vs legacy
- **Success Rate**: Command execution reliability
- **Optimization Score**: Overall performance rating (0-100)

## 🚨 CI/CD Integration

### Exit Codes
- `0`: All performance targets met
- `1`: Performance issues detected but not critical
- `2`: Critical performance failures

### Pipeline Integration
```bash
# Add to your CI/CD pipeline
if ! python performance/performance_suite.py; then
    echo "❌ Performance validation failed - blocking deployment"
    exit 1
fi
echo "✅ Performance validation passed - ready for deployment"
```

## 🔍 Troubleshooting

### Common Issues

**Import Errors**
- Ensure all dependencies are installed: `pip install rich psutil pyyaml`
- Check Python path includes the performance directory

**Timeout Issues**
- Increase timeout with `--timeout` option
- Check system resources and competing processes

**Memory Profiling Failures**
- Install psutil: `pip install psutil`
- Ensure sufficient system memory

### Debug Mode
```bash
python performance/performance_suite.py --verbose --debug
```

## 📋 Requirements

### Python Dependencies
```bash
pip install rich psutil pyyaml jinja2 click
```

### System Requirements
- Python 3.8+
- 2GB+ available RAM for memory profiling
- Node.js 16+ (for Node.js/TypeScript testing)

### Optional Dependencies
- `matplotlib`: For performance visualization
- `pandas`: For advanced statistical analysis

## 🤝 Contributing

When adding new performance tests:
1. Follow the existing pattern of statistical analysis with multiple iterations
2. Include both success and failure scenarios
3. Provide clear optimization recommendations
4. Update this README with new tool documentation

## 📄 License

Part of the Goobits CLI Framework - see main project license.