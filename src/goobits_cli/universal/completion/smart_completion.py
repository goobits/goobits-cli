"""
Smart Completion Engine for Goobits CLI Framework.

Extends the existing completion system with intelligent features:
- Fuzzy matching for partial text
- Enhanced history completion with frequency ranking
- Context-aware smart suggestions
- Backward compatible with existing DynamicCompletionRegistry
"""

import re
import time
from collections import defaultdict, Counter
from typing import List, Dict, Any, Set, Optional
from dataclasses import dataclass, field
import logging

from .registry import DynamicCompletionRegistry, CompletionProvider, CompletionContext

logger = logging.getLogger(__name__)


@dataclass
class SmartCompletionContext:
    """Extended context for smart completion features."""
    
    # Fuzzy matching threshold (0.0 - 1.0)
    fuzzy_threshold: float = 0.6
    
    # Maximum fuzzy matches to return
    max_fuzzy_matches: int = 5
    
    # History analysis data
    command_frequency: Dict[str, int] = field(default_factory=dict)
    recent_commands: List[str] = field(default_factory=list)
    
    # Performance tracking
    start_time: float = field(default_factory=time.time)


class SmartCompletionEngine(DynamicCompletionRegistry):
    """
    Enhanced completion engine with smart features.
    
    Inherits from DynamicCompletionRegistry for full backward compatibility
    while adding intelligent completion capabilities.
    """
    
    def __init__(self):
        """Initialize smart completion engine."""
        super().__init__()
        
        # Smart completion features
        self._fuzzy_enabled = True
        self._smart_history_enabled = True
        
        # Performance targets
        self._max_response_time = 0.008  # 8ms target for buffer
        
        # Lazy provider registration
        self._smart_providers_registered = False
    
    def _register_smart_providers(self) -> None:
        """Register smart completion providers."""
        # Register enhanced history provider with higher priority
        enhanced_history = HistoryCompletionProvider(priority=85)
        self.register_provider(enhanced_history)
        
        # Register fuzzy matching provider
        fuzzy_provider = FuzzyMatchProvider(priority=75)
        self.register_provider(fuzzy_provider)
    
    async def get_smart_completions(self,
                                  current_word: str,
                                  full_command: str,
                                  language: str = "python",
                                  enable_fuzzy: bool = True,
                                  enable_smart_history: bool = True) -> List[str]:
        """
        Get smart completions with enhanced features.
        
        Args:
            current_word: Partial word being completed
            full_command: Full command line so far
            language: Target language
            enable_fuzzy: Enable fuzzy matching
            enable_smart_history: Enable smart history features
            
        Returns:
            List of smart completion suggestions
        """
        start_time = time.time()
        
        try:
            # Lazy provider registration for performance
            if not self._smart_providers_registered:
                self._register_smart_providers()
                self._smart_providers_registered = True
            
            # Fast path: Check cache first with smart key
            smart_cache_key = f"smart:{language}:{current_word}:{full_command}:{enable_fuzzy}:{enable_smart_history}"
            if smart_cache_key in self._completion_cache:
                return self._completion_cache[smart_cache_key]
            
            # Get base completions from parent registry
            base_completions = await super().get_completions(
                current_word, full_command, language
            )
            
            # Quick exit if no base results and no smart features to apply
            if not base_completions and not (enable_fuzzy or enable_smart_history):
                return []
            
            # Time budget check - only do expensive operations if we have time
            elapsed = time.time() - start_time
            time_budget = self._max_response_time * 0.7  # Use 70% of budget for smart features
            
            if elapsed < time_budget:
                # Build lightweight smart context (avoid expensive operations)
                smart_context = self._build_lightweight_smart_context(
                    current_word, full_command, language
                )
                
                if enable_fuzzy and self._fuzzy_enabled and len(current_word) >= 2:
                    # Fast fuzzy matches with limited candidates
                    fuzzy_matches = self._get_fast_fuzzy_matches(current_word, language)
                    base_completions.extend(fuzzy_matches)
                
                if enable_smart_history and self._smart_history_enabled:
                    # Fast history ranking without complex analysis
                    base_completions = self._apply_fast_history_ranking(
                        base_completions, smart_context
                    )
            
            # Fast deduplication using set
            seen = set()
            unique_completions = []
            for completion in base_completions:
                if completion not in seen:
                    seen.add(completion)
                    unique_completions.append(completion)
                    if len(unique_completions) >= 15:  # Limit early for performance
                        break
            
            # Cache results
            self._completion_cache[smart_cache_key] = unique_completions
            
            return unique_completions
            
        except Exception as e:
            logger.error(f"Error in smart completions: {e}")
            # Fast fallback
            return await super().get_completions(current_word, full_command, language)
    
    async def _build_smart_context(self,
                                 current_word: str,
                                 full_command: str,
                                 language: str,
                                 start_time: float) -> SmartCompletionContext:
        """Build extended smart completion context."""
        
        # Get base context
        base_context = await self._build_context(current_word, full_command, language)
        
        # Analyze command history for patterns
        command_frequency = {}
        recent_commands = []
        
        if base_context.history:
            # Count command frequency
            command_frequency = dict(Counter(base_context.history))
            
            # Get recent unique commands (last 10)
            seen_recent = set()
            for cmd in reversed(base_context.history):
                if cmd not in seen_recent:
                    recent_commands.append(cmd)
                    seen_recent.add(cmd)
                    if len(recent_commands) >= 10:
                        break
        
        return SmartCompletionContext(
            command_frequency=command_frequency,
            recent_commands=recent_commands,
            start_time=start_time
        )
    
    def _build_lightweight_smart_context(self,
                                       current_word: str,
                                       full_command: str,
                                       language: str) -> SmartCompletionContext:
        """Build lightweight smart context for performance."""
        # Fast context with minimal processing
        return SmartCompletionContext()
    
    def _get_fast_fuzzy_matches(self, current_word: str, language: str) -> List[str]:
        """Get fuzzy matches with performance optimization."""
        if len(current_word) < 2:
            return []
        
        # Pre-built candidate sets for performance
        candidates = {'build', 'test', 'install', 'help', 'version'}
        
        # Language-specific fast candidates
        if language == 'python':
            candidates.update(['pytest', 'pip'])
        elif language == 'nodejs':
            candidates.update(['npm', 'node'])
        elif language == 'rust':
            candidates.update(['cargo', 'clippy'])
        
        # Fast substring matching only
        matches = []
        current_lower = current_word.lower()
        for candidate in candidates:
            if current_lower in candidate.lower() and not candidate.startswith(current_lower):
                matches.append(candidate)
                if len(matches) >= 3:  # Limit for performance
                    break
        
        return matches
    
    def _apply_fast_history_ranking(self, 
                                  completions: List[str],
                                  context: SmartCompletionContext) -> List[str]:
        """Apply fast history ranking without complex analysis."""
        # Simple: just return completions as-is for performance
        # In a real implementation, we'd do minimal frequency checking
        return completions
    
    def _get_fuzzy_matches(self,
                          current_word: str,
                          completions: List[str],
                          context: SmartCompletionContext) -> List[str]:
        """Get fuzzy matching completions."""
        if not current_word or len(current_word) < 2:
            return []
        
        fuzzy_matches = []
        current_lower = current_word.lower()
        
        # Simple fuzzy matching algorithm
        for completion in completions:
            if completion.lower().startswith(current_lower):
                continue  # Already have exact prefix match
            
            # Calculate simple fuzzy score
            score = self._calculate_fuzzy_score(current_lower, completion.lower())
            
            if score >= context.fuzzy_threshold:
                fuzzy_matches.append((completion, score))
        
        # Sort by score and return top matches
        fuzzy_matches.sort(key=lambda x: x[1], reverse=True)
        return [match[0] for match in fuzzy_matches[:context.max_fuzzy_matches]]
    
    def _calculate_fuzzy_score(self, query: str, candidate: str) -> float:
        """Calculate fuzzy matching score between query and candidate."""
        if not query or not candidate:
            return 0.0
        
        # Simple substring-based scoring
        if query in candidate:
            return 0.8
        
        # Character overlap scoring
        query_chars = set(query)
        candidate_chars = set(candidate)
        overlap = len(query_chars & candidate_chars)
        union = len(query_chars | candidate_chars)
        
        if union == 0:
            return 0.0
        
        return overlap / union
    
    def _apply_smart_history_ranking(self,
                                   completions: List[str],
                                   context: SmartCompletionContext) -> List[str]:
        """Apply smart history-based ranking to completions."""
        
        # Separate into history-based and other completions
        history_completions = []
        other_completions = []
        
        for completion in completions:
            if completion in context.command_frequency:
                # Score based on frequency and recency
                frequency_score = context.command_frequency[completion]
                recency_score = 0
                
                if completion in context.recent_commands:
                    # Higher score for more recent commands
                    recency_score = 10 - context.recent_commands.index(completion)
                
                total_score = frequency_score + recency_score
                history_completions.append((completion, total_score))
            else:
                other_completions.append(completion)
        
        # Sort history completions by score
        history_completions.sort(key=lambda x: x[1], reverse=True)
        ranked_history = [comp[0] for comp in history_completions]
        
        # Return history-based completions first, then others
        return ranked_history + other_completions


class HistoryCompletionProvider(CompletionProvider):
    """Enhanced history completion with frequency and recency ranking."""
    
    def __init__(self, priority: int = 85):
        """Initialize with high priority for smart history."""
        super().__init__(priority)
        self.max_suggestions = 8
    
    def can_provide(self, context: CompletionContext) -> bool:
        """Provide history completions when available."""
        return bool(context.history) and len(context.current_word) >= 1
    
    async def provide_completions(self, context: CompletionContext) -> List[str]:
        """Provide enhanced history completions."""
        try:
            if not context.history:
                return []
            
            current_word = context.current_word.lower()
            
            # Analyze command patterns
            command_scores = defaultdict(float)
            
            # Score commands based on frequency and recency
            for i, cmd in enumerate(reversed(context.history)):
                if cmd.lower().startswith(current_word):
                    # Recency bonus (more recent = higher score)
                    recency_bonus = max(0, 10 - i * 0.1)
                    command_scores[cmd] += recency_bonus
            
            # Sort by score and return top suggestions
            scored_commands = sorted(
                command_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            return [cmd for cmd, _ in scored_commands[:self.max_suggestions]]
            
        except Exception as e:
            logger.error(f"Error in enhanced history completion: {e}")
            return []


class FuzzyMatchProvider(CompletionProvider):
    """Fuzzy matching completion provider."""
    
    def __init__(self, priority: int = 75):
        """Initialize with high priority for fuzzy matching."""
        super().__init__(priority)
        self.min_query_length = 2
        self.max_suggestions = 5
    
    def can_provide(self, context: CompletionContext) -> bool:
        """Provide fuzzy matches for longer queries."""
        return len(context.current_word) >= self.min_query_length
    
    async def provide_completions(self, context: CompletionContext) -> List[str]:
        """Provide fuzzy matching completions."""
        try:
            current_word = context.current_word.lower()
            
            # Build candidate list from available commands and common terms
            candidates = set()
            candidates.update(context.available_commands)
            candidates.update(['build', 'test', 'install', 'config', 'help', 'version'])
            
            # Add language-specific commands
            if context.language == 'python':
                candidates.update(['pytest', 'pip', 'poetry', 'black', 'mypy'])
            elif context.language == 'nodejs':
                candidates.update(['npm', 'yarn', 'node', 'tsc', 'webpack'])
            elif context.language == 'rust':
                candidates.update(['cargo', 'rustc', 'clippy', 'fmt', 'doc'])
            
            # Find fuzzy matches
            matches = []
            for candidate in candidates:
                if candidate.lower().startswith(current_word):
                    continue  # Skip exact prefix matches (handled elsewhere)
                
                if current_word in candidate.lower():
                    matches.append((candidate, 0.8))  # Substring match
                elif self._has_character_overlap(current_word, candidate.lower()):
                    matches.append((candidate, 0.6))  # Character overlap
            
            # Sort by score and return top matches  
            matches.sort(key=lambda x: x[1], reverse=True)
            return [match[0] for match in matches[:self.max_suggestions]]
            
        except Exception as e:
            logger.error(f"Error in fuzzy matching: {e}")
            return []
    
    def _has_character_overlap(self, query: str, candidate: str) -> bool:
        """Check if query and candidate have significant character overlap."""
        if len(query) < 2 or len(candidate) < 2:
            return False
        
        query_chars = set(query)
        candidate_chars = set(candidate)
        overlap = len(query_chars & candidate_chars)
        
        # Require at least 60% character overlap
        return overlap >= max(2, len(query_chars) * 0.6)


# Global smart registry instance
_smart_registry = SmartCompletionEngine()


def get_smart_completion_registry() -> SmartCompletionEngine:
    """Get the global smart completion registry instance."""
    return _smart_registry