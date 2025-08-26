#!/usr/bin/env python3
"""
Comprehensive Performance Validation Suite for Goobits CLI Framework
Integrates all performance analysis tools and generates unified validation report
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Import our performance analysis modules
try:
    # Try relative imports first (when run as module)
    from .benchmark_suite import PerformanceValidator
    from .startup_validator import StartupValidator
    from .memory_profiler import CLIMemoryBenchmark
    from .template_benchmark import TemplateBenchmark
    from .cross_language_analyzer import CrossLanguageAnalyzer
    MODULES_AVAILABLE = True
except ImportError:
    try:
        # Fallback to direct imports (when run directly)
        from benchmark_suite import PerformanceValidator
        from startup_validator import StartupValidator
        from memory_profiler import CLIMemoryBenchmark
        from template_benchmark import TemplateBenchmark
        from cross_language_analyzer import CrossLanguageAnalyzer
        MODULES_AVAILABLE = True
    except ImportError:
        MODULES_AVAILABLE = False


@dataclass
class ValidationResults:
    """Complete validation results across all performance tests"""
    startup_validation: Dict[str, Any]
    memory_analysis: Dict[str, Any]
    template_benchmarks: Dict[str, Any]
    cross_language_comparison: Dict[str, Any]
    overall_score: float
    meets_production_requirements: bool
    critical_issues: List[str]
    recommendations: List[str]
    timestamp: float


class PerformanceValidationSuite:
    """Master performance validation suite"""
    
    def __init__(self, 
                 target_startup_ms: float = 100.0,
                 target_memory_mb: float = 50.0,
                 iterations: int = 5,
                 output_dir: Path = Path("performance_validation_results")):
        
        self.target_startup_ms = target_startup_ms
        self.target_memory_mb = target_memory_mb
        self.iterations = iterations
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
        
        # Performance thresholds for production readiness
        self.production_thresholds = {
            "startup_time_ms": {"python": 90, "nodejs": 70, "typescript": 80},
            "memory_usage_mb": {"python": 35, "nodejs": 45, "typescript": 50},
            "template_render_ms": {"python": 60, "nodejs": 50, "typescript": 70},
            "success_rate": 0.95,  # 95% success rate required
            "optimization_score": 75.0  # Minimum optimization score
        }
        
        # Test configurations
        self.test_languages = ["python", "nodejs", "typescript"]
        self.test_configurations = ["minimal", "standard", "universal"]
        
    def run_comprehensive_validation(self) -> ValidationResults:
        """Run comprehensive performance validation across all components"""
        
        if self.console:
            self.console.print(Panel.fit(
                "[bold blue]🎯 Goobits CLI Framework - Comprehensive Performance Validation[/bold blue]\n"
                f"Target: <{self.target_startup_ms}ms startup, <{self.target_memory_mb}MB memory\n"
                f"Languages: {', '.join(self.test_languages)}\n"
                f"Configurations: {', '.join(self.test_configurations)}\n"
                f"Iterations: {self.iterations}",
                title="Performance Validation Suite"
            ))
        
        validation_start = time.time()
        
        try:
            # Phase 1: Startup Time Validation
            if self.console:
                self.console.print("\n[blue]🚀 Phase 1: Startup Time Validation[/blue]")
            startup_results = self._run_startup_validation()
            
            # Phase 2: Memory Usage Analysis
            if self.console:
                self.console.print("\n[blue]💾 Phase 2: Memory Usage Analysis[/blue]")
            memory_results = self._run_memory_analysis()
            
            # Phase 3: Template Performance Benchmarks
            if self.console:
                self.console.print("\n[blue]🏗️ Phase 3: Template Performance Benchmarks[/blue]")
            template_results = self._run_template_benchmarks()
            
            # Phase 4: Cross-Language Comparison
            if self.console:
                self.console.print("\n[blue]🔄 Phase 4: Cross-Language Performance Comparison[/blue]")
            cross_lang_results = self._run_cross_language_analysis()
            
            # Analyze overall results
            overall_score = self._calculate_overall_score(
                startup_results, memory_results, template_results, cross_lang_results
            )
            
            # Check production readiness
            meets_requirements = self._check_production_requirements(
                startup_results, memory_results, template_results, overall_score
            )
            
            # Identify critical issues
            critical_issues = self._identify_critical_issues(
                startup_results, memory_results, template_results, meets_requirements
            )
            
            # Generate recommendations
            recommendations = self._generate_comprehensive_recommendations(
                startup_results, memory_results, template_results, critical_issues
            )
            
            validation_time = time.time() - validation_start
            
            if self.console:
                self.console.print(f"\n[green]🏁 Validation completed in {validation_time:.2f}s[/green]")
                self.console.print(f"[blue]📊 Overall Score: {overall_score:.1f}/100[/blue]")
                status = "✅ READY" if meets_requirements else "❌ NOT READY"
                self.console.print(f"[blue]🎯 Production Ready: {status}[/blue]")
            
            results = ValidationResults(
                startup_validation=startup_results,
                memory_analysis=memory_results,
                template_benchmarks=template_results,
                cross_language_comparison=cross_lang_results,
                overall_score=overall_score,
                meets_production_requirements=meets_requirements,
                critical_issues=critical_issues,
                recommendations=recommendations,
                timestamp=time.time()
            )
            
            return results
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]❌ Validation failed: {e}[/red]")
            
            # Return minimal results on failure
            return ValidationResults(
                startup_validation={"error": str(e)},
                memory_analysis={"error": str(e)},
                template_benchmarks={"error": str(e)},
                cross_language_comparison={"error": str(e)},
                overall_score=0.0,
                meets_production_requirements=False,
                critical_issues=[f"Validation suite failed: {e}"],
                recommendations=["Fix validation suite errors before proceeding"],
                timestamp=time.time()
            )
    
    def _run_startup_validation(self) -> Dict[str, Any]:
        """Run startup time validation across all configurations"""
        try:
            if MODULES_AVAILABLE:
                validator = StartupValidator(
                    target_ms=self.target_startup_ms,
                    iterations=self.iterations,
                    output_dir=self.output_dir / "startup_validation"
                )
                
                # Create test configurations for startup validation
                test_configs = self._create_startup_test_configs()
                results = validator.validate_multiple_configurations(test_configs)
                
                # Save startup results
                validator.save_results(results)
                
                # Summarize results
                summary = {
                    "total_configurations": len(results),
                    "passed_configurations": len([p for p in results.values() if p.meets_target]),
                    "average_startup_ms": sum(p.average_ms for p in results.values()) / len(results),
                    "success_rate": sum(p.success_rate for p in results.values()) / len(results),
                    "detailed_results": {k: asdict(v) for k, v in results.items()}
                }
                
                return summary
            else:
                return {"error": "Startup validation module not available"}
                
        except Exception as e:
            return {"error": f"Startup validation failed: {e}"}
    
    def _run_memory_analysis(self) -> Dict[str, Any]:
        """Run memory usage analysis across configurations"""
        try:
            if MODULES_AVAILABLE:
                benchmark = CLIMemoryBenchmark(
                    output_dir=self.output_dir / "memory_analysis"
                )
                
                # Create test configurations for memory analysis
                test_configs = self._create_memory_test_configs()
                results = benchmark.benchmark_multiple_configs(test_configs)
                
                # Generate comparison report
                if results:
                    comparison_report = benchmark.generate_comparison_report(results)
                    
                    # Save memory analysis report
                    report_file = self.output_dir / "memory_analysis" / "memory_comparison.md"
                    with open(report_file, 'w') as f:
                        f.write(comparison_report)
                
                # Summarize results
                if results:
                    summary = {
                        "total_configurations": len(results),
                        "average_memory_mb": sum(p.peak_memory_mb for p in results.values()) / len(results),
                        "memory_efficiency_score": sum(p.optimization_score for p in results.values()) / len(results),
                        "memory_leaks_detected": sum(1 for p in results.values() if p.leak_detected),
                        "detailed_results": {k: asdict(v) for k, v in results.items()}
                    }
                else:
                    summary = {"error": "No memory analysis results"}
                
                return summary
            else:
                return {"error": "Memory analysis module not available"}
                
        except Exception as e:
            return {"error": f"Memory analysis failed: {e}"}
    
    def _run_template_benchmarks(self) -> Dict[str, Any]:
        """Run template rendering performance benchmarks"""
        try:
            if MODULES_AVAILABLE:
                benchmark = TemplateBenchmark(
                    iterations=max(3, self.iterations // 2),  # Fewer iterations for template tests
                    output_dir=self.output_dir / "template_benchmarks"
                )
                
                # Run comprehensive template benchmarks
                analysis = benchmark.run_comprehensive_benchmark()
                
                # Save template results
                benchmark.save_results(analysis)
                
                return analysis
            else:
                return {"error": "Template benchmark module not available"}
                
        except Exception as e:
            return {"error": f"Template benchmarks failed: {e}"}
    
    def _run_cross_language_analysis(self) -> Dict[str, Any]:
        """Run cross-language performance comparison"""
        try:
            if MODULES_AVAILABLE:
                analyzer = CrossLanguageAnalyzer(
                    output_dir=self.output_dir / "cross_language_analysis"
                )
                
                # Run cross-language comparison
                comparison = analyzer.compare_languages()
                
                # Save cross-language results
                analyzer.save_results()
                
                return asdict(comparison)
            else:
                return {"error": "Cross-language analyzer module not available"}
                
        except Exception as e:
            return {"error": f"Cross-language analysis failed: {e}"}
    
    def _create_startup_test_configs(self) -> List[Dict[str, Any]]:
        """Create test configurations for startup validation"""
        configs = []
        
        # Test current goobits CLI
        configs.append({
            "name": "goobits_current",
            "command": [sys.executable, "-m", "goobits_cli.main"],
            "language": "python",
            "cwd": Path.cwd()
        })
        
        return configs
    
    def _create_memory_test_configs(self) -> List[Dict[str, Any]]:
        """Create test configurations for memory analysis"""
        configs = []
        
        # Test current goobits CLI memory usage
        configs.append({
            "name": "goobits_memory_test",
            "command": [sys.executable, "-m", "goobits_cli.main", "--version"],
            "language": "python",
            "iterations": 3
        })
        
        return configs
    
    def _calculate_overall_score(self, 
                                startup_results: Dict[str, Any],
                                memory_results: Dict[str, Any],
                                template_results: Dict[str, Any],
                                cross_lang_results: Dict[str, Any]) -> float:
        """Calculate overall performance score (0-100)"""
        
        scores = []
        weights = []
        
        # Startup performance score (40% weight)
        if "error" not in startup_results:
            startup_score = 0
            if "passed_configurations" in startup_results and "total_configurations" in startup_results:
                pass_rate = startup_results["passed_configurations"] / startup_results["total_configurations"]
                startup_score = pass_rate * 100
                
                # Bonus for fast startup times
                avg_startup = startup_results.get("average_startup_ms", self.target_startup_ms)
                if avg_startup < self.target_startup_ms * 0.7:
                    startup_score = min(100, startup_score + 20)
            
            scores.append(startup_score)
            weights.append(0.4)
        
        # Memory performance score (25% weight)
        if "error" not in memory_results:
            memory_score = 0
            if "memory_efficiency_score" in memory_results:
                memory_score = memory_results["memory_efficiency_score"]
                
                # Penalty for memory leaks
                if memory_results.get("memory_leaks_detected", 0) > 0:
                    memory_score = max(0, memory_score - 20)
            
            scores.append(memory_score)
            weights.append(0.25)
        
        # Template performance score (20% weight)
        if "error" not in template_results:
            template_score = 75  # Base score
            
            # Analyze universal template performance
            universal_performance = template_results.get("universal_performance", {})
            if universal_performance:
                # Analyze universal template performance characteristics
                avg_overhead = []
                for lang_comparison in universal_performance.values():
                    overhead = lang_comparison.get("performance_difference_pct", 0)
                    avg_overhead.append(overhead)
                
                if avg_overhead:
                    avg_overhead_pct = sum(avg_overhead) / len(avg_overhead)
                    if avg_overhead_pct < 10:
                        template_score = 95  # Excellent
                    elif avg_overhead_pct < 25:
                        template_score = 85  # Good
                    elif avg_overhead_pct < 50:
                        template_score = 75  # Acceptable
                    else:
                        template_score = 60  # Poor
            
            scores.append(template_score)
            weights.append(0.2)
        
        # Cross-language parity score (15% weight)
        if "error" not in cross_lang_results:
            cross_lang_score = 0
            if "feature_parity_score" in cross_lang_results:
                cross_lang_score = cross_lang_results["feature_parity_score"]
                
                # Bonus for having a clear performance leader
                if cross_lang_results.get("performance_leader") != "none":
                    cross_lang_score = min(100, cross_lang_score + 10)
            
            scores.append(cross_lang_score)
            weights.append(0.15)
        
        # Calculate weighted average
        if scores and weights:
            total_weight = sum(weights)
            weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
            overall_score = weighted_sum / total_weight
        else:
            overall_score = 0.0
        
        return min(100.0, max(0.0, overall_score))
    
    def _check_production_requirements(self, 
                                     startup_results: Dict[str, Any],
                                     memory_results: Dict[str, Any],
                                     template_results: Dict[str, Any],
                                     overall_score: float) -> bool:
        """Check if performance meets production requirements"""
        
        requirements_met = []
        
        # Startup time requirement
        if "error" not in startup_results:
            avg_startup = startup_results.get("average_startup_ms", float('inf'))
            success_rate = startup_results.get("success_rate", 0.0)
            
            startup_ok = (avg_startup <= self.target_startup_ms and 
                         success_rate >= self.production_thresholds["success_rate"])
            requirements_met.append(startup_ok)
        
        # Memory usage requirement
        if "error" not in memory_results:
            avg_memory = memory_results.get("average_memory_mb", float('inf'))
            leaks_detected = memory_results.get("memory_leaks_detected", 0)
            
            memory_ok = (avg_memory <= self.target_memory_mb and leaks_detected == 0)
            requirements_met.append(memory_ok)
        
        # Template performance requirement
        if "error" not in template_results:
            template_ok = True  # Assume OK if no critical template issues
            
            # Check for excessive universal template overhead
            universal_performance = template_results.get("universal_performance", {})
            for lang_comparison in universal_performance.values():
                overhead = lang_comparison.get("performance_difference_pct", 0)
                if overhead > 100:  # More than 100% slower
                    template_ok = False
                    break
            
            requirements_met.append(template_ok)
        
        # Overall score requirement
        score_ok = overall_score >= self.production_thresholds["optimization_score"]
        requirements_met.append(score_ok)
        
        # All requirements must be met
        return all(requirements_met) and len(requirements_met) > 0
    
    def _identify_critical_issues(self, 
                                startup_results: Dict[str, Any],
                                memory_results: Dict[str, Any],
                                template_results: Dict[str, Any],
                                meets_requirements: bool) -> List[str]:
        """Identify critical performance issues"""
        issues = []
        
        # Startup issues
        if "error" in startup_results:
            issues.append(f"Startup validation failed: {startup_results['error']}")
        else:
            avg_startup = startup_results.get("average_startup_ms", 0)
            if avg_startup > self.target_startup_ms * 1.5:
                issues.append(f"Startup time ({avg_startup:.1f}ms) significantly exceeds target ({self.target_startup_ms}ms)")
            
            success_rate = startup_results.get("success_rate", 1.0)
            if success_rate < 0.9:
                issues.append(f"Low startup success rate ({success_rate:.1%}) indicates reliability issues")
        
        # Memory issues
        if "error" in memory_results:
            issues.append(f"Memory analysis failed: {memory_results['error']}")
        else:
            leaks = memory_results.get("memory_leaks_detected", 0)
            if leaks > 0:
                issues.append(f"Memory leaks detected in {leaks} configuration(s)")
            
            avg_memory = memory_results.get("average_memory_mb", 0)
            if avg_memory > self.target_memory_mb * 1.5:
                issues.append(f"Memory usage ({avg_memory:.1f}MB) significantly exceeds target ({self.target_memory_mb}MB)")
        
        # Template issues
        if "error" in template_results:
            issues.append(f"Template benchmarks failed: {template_results['error']}")
        else:
            # Check for severe universal template performance issues
            universal_performance = template_results.get("universal_performance", {})
            for language, comparison in universal_performance.items():
                overhead = comparison.get("performance_difference_pct", 0)
                if overhead > 200:  # More than 200% slower
                    issues.append(f"Universal templates need optimization in {language}")
        
        # Overall production readiness
        if not meets_requirements:
            issues.append("Framework does not meet production performance requirements")
        
        return issues
    
    def _generate_comprehensive_recommendations(self, 
                                              startup_results: Dict[str, Any],
                                              memory_results: Dict[str, Any],
                                              template_results: Dict[str, Any],
                                              critical_issues: List[str]) -> List[str]:
        """Generate comprehensive optimization recommendations"""
        recommendations = []
        
        # High priority recommendations for critical issues
        if critical_issues:
            recommendations.append("🚨 CRITICAL ISSUES DETECTED - Address immediately:")
            for issue in critical_issues:
                recommendations.append(f"   • {issue}")
            recommendations.append("")
        
        # Startup optimization recommendations
        if "error" not in startup_results:
            avg_startup = startup_results.get("average_startup_ms", 0)
            if avg_startup > self.target_startup_ms:
                recommendations.extend([
                    "🚀 Startup Time Optimization:",
                    "   • Implement lazy loading for CLI modules",
                    "   • Optimize import statements and reduce dependency loading",
                    "   • Enable startup optimization flags in CLI configuration",
                    "   • Consider caching compiled templates and components"
                ])
        
        # Memory optimization recommendations
        if "error" not in memory_results:
            avg_memory = memory_results.get("average_memory_mb", 0)
            if avg_memory > self.target_memory_mb:
                recommendations.extend([
                    "💾 Memory Usage Optimization:",
                    "   • Implement memory pooling for frequently used objects",
                    "   • Review template caching strategies to reduce memory footprint", 
                    "   • Consider using streaming for large configuration processing",
                    "   • Implement garbage collection optimization"
                ])
            
            if memory_results.get("memory_leaks_detected", 0) > 0:
                recommendations.extend([
                    "🔍 Memory Leak Resolution:",
                    "   • Review object lifecycle management in generated CLIs",
                    "   • Ensure proper cleanup of event listeners and timers",
                    "   • Implement weak references for cached objects"
                ])
        
        # Template performance recommendations
        if "error" not in template_results:
            universal_performance = template_results.get("universal_performance", {})
            high_overhead_langs = []
            
            for language, comparison in universal_performance.items():
                overhead = comparison.get("performance_difference_pct", 0)
                if overhead > 50:
                    high_overhead_langs.append(f"{language} ({overhead:.1f}%)")
            
            if high_overhead_langs:
                recommendations.extend([
                    "🏗️ Template Rendering Optimization:",
                    f"   • Universal templates show high overhead in: {', '.join(high_overhead_langs)}",
                    "   • Implement template compilation caching",
                    "   • Optimize Jinja2/template engine configuration",
                    "   • Consider template pre-compilation for production builds"
                ])
        
        # General performance recommendations
        recommendations.extend([
            "⚡ General Performance Optimization:",
            "   • Enable production mode optimizations in generated CLIs",
            "   • Implement comprehensive performance monitoring",
            "   • Use performance profiling tools to identify bottlenecks",
            "   • Consider using performance optimization libraries specific to each language"
        ])
        
        # Success case
        if not critical_issues and not recommendations:
            recommendations.extend([
                "✅ EXCELLENT PERFORMANCE!",
                "   • All performance targets met across all configurations",
                "   • Framework is ready for production deployment",
                "   • Consider documenting current configuration as performance baseline"
            ])
        
        return recommendations
    
    def generate_validation_report(self, results: ValidationResults) -> str:
        """Generate comprehensive validation report"""
        report_lines = [
            "# Goobits CLI Framework - Performance Validation Report",
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Validation Target: <{self.target_startup_ms}ms startup, <{self.target_memory_mb}MB memory",
            ""
        ]
        
        # Executive Summary
        status = "✅ PRODUCTION READY" if results.meets_production_requirements else "❌ NOT PRODUCTION READY"
        report_lines.extend([
            "## 🎯 Executive Summary",
            f"- **Overall Performance Score**: {results.overall_score:.1f}/100",
            f"- **Production Readiness**: {status}",
            f"- **Critical Issues**: {len(results.critical_issues)}",
            f"- **Languages Tested**: {', '.join(self.test_languages)}",
            f"- **Test Configurations**: {', '.join(self.test_configurations)}",
            ""
        ])
        
        # Critical Issues
        if results.critical_issues:
            report_lines.extend(["## 🚨 Critical Issues", ""])
            for i, issue in enumerate(results.critical_issues, 1):
                report_lines.append(f"{i}. {issue}")
            report_lines.append("")
        
        # Performance Summary
        report_lines.extend(["## 📊 Performance Summary", ""])
        
        # Startup Performance
        startup_data = results.startup_validation
        if "error" not in startup_data:
            passed_configs = startup_data.get("passed_configurations", 0)
            total_configs = startup_data.get("total_configurations", 0)
            avg_startup = startup_data.get("average_startup_ms", 0)
            success_rate = startup_data.get("success_rate", 0)
            
            report_lines.extend([
                "### 🚀 Startup Performance",
                f"- **Average Startup Time**: {avg_startup:.2f}ms",
                f"- **Target Compliance**: {passed_configs}/{total_configs} configurations",
                f"- **Success Rate**: {success_rate:.1%}",
                ""
            ])
        
        # Memory Performance
        memory_data = results.memory_analysis
        if "error" not in memory_data:
            avg_memory = memory_data.get("average_memory_mb", 0)
            efficiency_score = memory_data.get("memory_efficiency_score", 0)
            leaks = memory_data.get("memory_leaks_detected", 0)
            
            report_lines.extend([
                "### 💾 Memory Performance",
                f"- **Average Memory Usage**: {avg_memory:.2f}MB",
                f"- **Memory Efficiency Score**: {efficiency_score:.1f}/100",
                f"- **Memory Leaks Detected**: {leaks}",
                ""
            ])
        
        # Template Performance
        template_data = results.template_benchmarks
        if "error" not in template_data:
            report_lines.extend([
                "### 🏗️ Template Rendering Performance",
                "- **Universal vs Legacy Comparison**: See detailed analysis below",
                "- **Cross-Complexity Scaling**: Analyzed across multiple CLI sizes",
                ""
            ])
        
        # Cross-Language Analysis
        cross_lang_data = results.cross_language_comparison
        if "error" not in cross_lang_data:
            leader = cross_lang_data.get("performance_leader", "none")
            parity_score = cross_lang_data.get("feature_parity_score", 0)
            assessment = cross_lang_data.get("overall_assessment", "unknown")
            
            report_lines.extend([
                "### 🔄 Cross-Language Performance",
                f"- **Performance Leader**: {leader.title()}",
                f"- **Feature Parity Score**: {parity_score:.1f}/100",
                f"- **Overall Assessment**: {assessment}",
                ""
            ])
        
        # Recommendations
        if results.recommendations:
            report_lines.extend(["## 💡 Performance Optimization Recommendations", ""])
            for recommendation in results.recommendations:
                report_lines.append(recommendation)
            report_lines.append("")
        
        # Production Readiness Checklist
        report_lines.extend([
            "## ✅ Production Readiness Checklist",
            ""
        ])
        
        checklist_items = [
            ("Startup time meets targets", results.startup_validation.get("average_startup_ms", float('inf')) <= self.target_startup_ms),
            ("Memory usage within limits", results.memory_analysis.get("average_memory_mb", float('inf')) <= self.target_memory_mb),
            ("No memory leaks detected", results.memory_analysis.get("memory_leaks_detected", 1) == 0),
            ("Template performance acceptable", "error" not in results.template_benchmarks),
            ("Cross-language parity achieved", results.cross_language_comparison.get("feature_parity_score", 0) >= 80),
            ("Overall score meets threshold", results.overall_score >= self.production_thresholds["optimization_score"]),
            ("No critical issues identified", len(results.critical_issues) == 0)
        ]
        
        for item, status in checklist_items:
            status_icon = "✅" if status else "❌"
            report_lines.append(f"- {status_icon} {item}")
        
        report_lines.append("")
        
        # Raw Data
        report_lines.extend([
            "## 📄 Raw Validation Data",
            "```json"
        ])
        
        report_lines.append(json.dumps(asdict(results), indent=2))
        report_lines.extend(["```", ""])
        
        # Footer
        report_lines.extend([
            "---",
            f"*Performance validation completed at {time.strftime('%Y-%m-%d %H:%M:%S')}*",
            f"*Framework Status: {'Production Ready' if results.meets_production_requirements else 'Optimization Required'}*"
        ])
        
        return "\n".join(report_lines)
    
    def save_results(self, results: ValidationResults):
        """Save comprehensive validation results"""
        
        # Save comprehensive validation report
        report = self.generate_validation_report(results)
        report_file = self.output_dir / "performance_validation_report.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        # Save raw results as JSON
        results_file = self.output_dir / "validation_results.json"
        with open(results_file, 'w') as f:
            json.dump(asdict(results), f, indent=2)
        
        # Save production readiness summary
        summary_file = self.output_dir / "production_readiness.json"
        summary = {
            "production_ready": results.meets_production_requirements,
            "overall_score": results.overall_score,
            "critical_issues_count": len(results.critical_issues),
            "validation_timestamp": results.timestamp,
            "next_steps": results.recommendations[:5] if results.recommendations else []
        }
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        if self.console:
            self.console.print(f"\n[green]📁 Validation results saved to {self.output_dir}[/green]")
            self.console.print(f"   📄 Main Report: {report_file}")
            self.console.print(f"   📊 Raw Data: {results_file}")
            self.console.print(f"   🎯 Production Summary: {summary_file}")


def main():
    """Main entry point for comprehensive performance validation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Goobits CLI Framework - Performance Validation Suite")
    parser.add_argument("--target-startup", type=float, default=100.0,
                       help="Target startup time in milliseconds")
    parser.add_argument("--target-memory", type=float, default=50.0,
                       help="Target memory usage in megabytes")
    parser.add_argument("--iterations", type=int, default=5,
                       help="Number of test iterations")
    parser.add_argument("--output-dir", type=Path, default=Path("performance_validation_results"),
                       help="Output directory for results")
    parser.add_argument("--quick", action="store_true",
                       help="Run quick validation with fewer iterations")
    
    args = parser.parse_args()
    
    if args.quick:
        iterations = 3
    else:
        iterations = args.iterations
    
    # Create validation suite
    suite = PerformanceValidationSuite(
        target_startup_ms=args.target_startup,
        target_memory_mb=args.target_memory,
        iterations=iterations,
        output_dir=args.output_dir
    )
    
    try:
        # Run comprehensive validation
        results = suite.run_comprehensive_validation()
        
        # Save results
        suite.save_results(results)
        
        # Display summary
        print(f"\n🎯 Performance Validation Summary:")
        print(f"   Overall Score: {results.overall_score:.1f}/100")
        print(f"   Production Ready: {'✅ YES' if results.meets_production_requirements else '❌ NO'}")
        print(f"   Critical Issues: {len(results.critical_issues)}")
        
        if results.critical_issues:
            print(f"\n🚨 Critical Issues:")
            for i, issue in enumerate(results.critical_issues[:3], 1):
                print(f"   {i}. {issue}")
            if len(results.critical_issues) > 3:
                print(f"   ... and {len(results.critical_issues) - 3} more")
        
        # Return appropriate exit code
        return 0 if results.meets_production_requirements else 1
        
    except Exception as e:
        print(f"\n❌ Performance validation failed: {e}")
        return 2


if __name__ == "__main__":
    exit(main())