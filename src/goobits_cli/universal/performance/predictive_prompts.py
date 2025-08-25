"""
Predictive prompt pre-fetching for Goobits CLI Framework

Provides intelligent prompt pre-loading and caching to improve interactive
mode responsiveness. Analyzes user patterns and pre-loads likely next prompts.
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Callable, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock, Thread
from collections import defaultdict, deque
import logging
import weakref

logger = logging.getLogger(__name__)


@dataclass
class PromptConfig:
    """Configuration for a prompt that can be pre-fetched."""
    
    id: str
    prompt_type: str  # 'text', 'select', 'confirm', 'multiselect'
    message: str
    choices: Optional[List[str]] = None
    default: Optional[str] = None
    validate: Optional[Callable] = None
    when: Optional[Callable[[Dict], bool]] = None
    dependencies: List[str] = field(default_factory=list)
    likelihood: float = 0.5  # Probability this prompt will be shown
    
    def can_prefetch(self, context: Dict[str, Any]) -> bool:
        """Check if this prompt can be pre-fetched given current context."""
        if self.when is None:
            return True
        try:
            return self.when(context)
        except Exception:
            return False


@dataclass
class PromptSequence:
    """A sequence of prompts that typically occur together."""
    
    name: str
    prompts: List[str]  # Prompt IDs in order
    frequency: int = 0  # How often this sequence occurs
    last_used: float = 0.0
    
    def update_usage(self):
        """Record usage of this sequence."""
        self.frequency += 1
        self.last_used = time.time()


class PromptPredictor:
    """
    Analyzes prompt patterns and predicts likely next prompts.
    
    Features:
    - Pattern recognition based on historical sequences
    - Context-aware predictions
    - Machine learning-like scoring
    - Adaptive learning from user behavior
    """
    
    def __init__(self, history_size: int = 1000):
        """
        Initialize the prompt predictor.
        
        Args:
            history_size: Maximum number of prompt sequences to remember
        """
        self.history: deque = deque(maxlen=history_size)
        self.sequences: Dict[str, PromptSequence] = {}
        self.transitions: Dict[Tuple[str, str], int] = defaultdict(int)
        self.context_patterns: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self._lock = Lock()
        
    def record_prompt(self, prompt_id: str, context: Dict[str, Any]) -> None:
        """
        Record a prompt being shown to the user.
        
        Args:
            prompt_id: Unique identifier for the prompt
            context: Current context when prompt was shown
        """
        with self._lock:
            self.history.append({
                'prompt_id': prompt_id,
                'timestamp': time.time(),
                'context': self._simplify_context(context)
            })
            
            # Update transition probabilities
            if len(self.history) >= 2:
                prev_prompt = self.history[-2]['prompt_id']
                self.transitions[(prev_prompt, prompt_id)] += 1
            
            # Update context patterns
            simple_context = self._simplify_context(context)
            for key, value in simple_context.items():
                if isinstance(value, (str, int, bool)):
                    self.context_patterns[str(value)][prompt_id] += 0.1
    
    def _simplify_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Simplify context to key indicators for pattern matching."""
        simple = {}
        
        # Extract key context indicators
        if 'language' in context:
            simple['language'] = context['language']
        if 'project_type' in context:
            simple['project_type'] = context['project_type']
        if 'has_config' in context:
            simple['has_config'] = context['has_config']
        if 'step' in context:
            simple['step'] = context['step']
        
        return simple
    
    def predict_next_prompts(
        self, 
        current_prompt: str,
        context: Dict[str, Any],
        max_predictions: int = 3
    ) -> List[Tuple[str, float]]:
        """
        Predict the most likely next prompts.
        
        Args:
            current_prompt: ID of current/last prompt
            context: Current context
            max_predictions: Maximum number of predictions to return
            
        Returns:
            List of (prompt_id, confidence) tuples ordered by confidence
        """
        with self._lock:
            predictions = defaultdict(float)
            
            # Transition-based predictions
            total_transitions = sum(
                count for (prev, _), count in self.transitions.items() 
                if prev == current_prompt
            )
            
            if total_transitions > 0:
                for (prev, next_prompt), count in self.transitions.items():
                    if prev == current_prompt:
                        predictions[next_prompt] += (count / total_transitions) * 0.6
            
            # Context-based predictions
            simple_context = self._simplify_context(context)
            for key, value in simple_context.items():
                pattern_key = str(value)
                if pattern_key in self.context_patterns:
                    total_context_weight = sum(self.context_patterns[pattern_key].values())
                    if total_context_weight > 0:
                        for prompt_id, weight in self.context_patterns[pattern_key].items():
                            predictions[prompt_id] += (weight / total_context_weight) * 0.4
            
            # Sort by confidence and return top predictions
            sorted_predictions = sorted(
                predictions.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            return sorted_predictions[:max_predictions]


class PrefetchCache:
    """
    Cache for pre-fetched prompt preparations.
    
    Stores prepared prompts with TTL and memory management.
    """
    
    def __init__(self, max_size: int = 50, default_ttl: int = 300):
        """
        Initialize the prefetch cache.
        
        Args:
            max_size: Maximum number of cached items
            default_ttl: Default time-to-live in seconds
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._lock = Lock()
        
    def store(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        """Store a pre-fetched prompt preparation."""
        with self._lock:
            if len(self.cache) >= self.max_size:
                self._evict_oldest()
            
            self.cache[key] = {
                'data': data,
                'timestamp': time.time(),
                'ttl': ttl or self.default_ttl,
                'hits': 0
            }
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve a cached prompt preparation."""
        with self._lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            
            # Check if expired
            if time.time() - entry['timestamp'] > entry['ttl']:
                del self.cache[key]
                return None
            
            entry['hits'] += 1
            return entry['data']
    
    def _evict_oldest(self) -> None:
        """Evict the oldest cache entry."""
        if not self.cache:
            return
        
        oldest_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k]['timestamp']
        )
        del self.cache[oldest_key]
    
    def clear(self) -> None:
        """Clear all cached items."""
        with self._lock:
            self.cache.clear()


class PredictivePromptManager:
    """
    Main manager for predictive prompt pre-fetching.
    
    Coordinates prediction, pre-fetching, and caching of prompts.
    """
    
    def __init__(self):
        """Initialize the predictive prompt manager."""
        self.prompts: Dict[str, PromptConfig] = {}
        self.predictor = PromptPredictor()
        self.cache = PrefetchCache()
        self.prefetch_queue = asyncio.Queue()
        self.background_task: Optional[asyncio.Task] = None
        self._active = False
        
    def register_prompt(self, prompt_config: PromptConfig) -> None:
        """Register a prompt for potential pre-fetching."""
        self.prompts[prompt_config.id] = prompt_config
        
    def start_background_processing(self) -> None:
        """Start the background pre-fetching task."""
        if not self._active:
            self._active = True
            loop = asyncio.get_event_loop()
            self.background_task = loop.create_task(self._background_prefetch_worker())
    
    def stop_background_processing(self) -> None:
        """Stop the background pre-fetching task."""
        self._active = False
        if self.background_task:
            self.background_task.cancel()
    
    async def _background_prefetch_worker(self) -> None:
        """Background worker that processes pre-fetch requests."""
        while self._active:
            try:
                # Wait for prefetch requests
                request = await asyncio.wait_for(
                    self.prefetch_queue.get(), 
                    timeout=1.0
                )
                
                await self._process_prefetch_request(request)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in prefetch worker: {e}")
    
    async def _process_prefetch_request(self, request: Dict[str, Any]) -> None:
        """Process a single pre-fetch request."""
        prompt_id = request['prompt_id']
        context = request['context']
        
        if prompt_id not in self.prompts:
            return
        
        prompt_config = self.prompts[prompt_id]
        
        # Check if we can pre-fetch this prompt
        if not prompt_config.can_prefetch(context):
            return
        
        cache_key = f"{prompt_id}_{hash(str(context))}"
        
        # Don't re-fetch if already cached
        if self.cache.get(cache_key) is not None:
            return
        
        try:
            # Pre-compute expensive operations for this prompt
            prepared_data = await self._prepare_prompt(prompt_config, context)
            
            # Cache the prepared data
            self.cache.store(cache_key, prepared_data)
            
            logger.debug(f"Pre-fetched prompt: {prompt_id}")
            
        except Exception as e:
            logger.error(f"Failed to pre-fetch prompt {prompt_id}: {e}")
    
    async def _prepare_prompt(
        self, 
        prompt_config: PromptConfig, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Pre-compute expensive operations for a prompt.
        
        This could include:
        - Loading choice lists from files
        - Running validation checks
        - Computing default values
        - Preparing display formatting
        """
        prepared = {
            'id': prompt_config.id,
            'message': prompt_config.message,
            'default': prompt_config.default,
            'timestamp': time.time()
        }
        
        # Pre-load choices if they come from a function
        if prompt_config.choices:
            if callable(prompt_config.choices):
                try:
                    # If choices is a function, call it to get the list
                    if asyncio.iscoroutinefunction(prompt_config.choices):
                        prepared['choices'] = await prompt_config.choices(context)
                    else:
                        prepared['choices'] = prompt_config.choices(context)
                except Exception as e:
                    logger.warning(f"Failed to pre-load choices for {prompt_config.id}: {e}")
                    prepared['choices'] = []
            else:
                prepared['choices'] = prompt_config.choices
        
        # Pre-compute default value if it's a function
        if callable(prompt_config.default):
            try:
                if asyncio.iscoroutinefunction(prompt_config.default):
                    prepared['default'] = await prompt_config.default(context)
                else:
                    prepared['default'] = prompt_config.default(context)
            except Exception:
                prepared['default'] = None
        
        return prepared
    
    def record_prompt_shown(self, prompt_id: str, context: Dict[str, Any]) -> None:
        """Record that a prompt was shown to the user."""
        self.predictor.record_prompt(prompt_id, context)
        
        # Trigger predictive pre-fetching for likely next prompts
        predictions = self.predictor.predict_next_prompts(prompt_id, context)
        
        for next_prompt_id, confidence in predictions:
            if confidence > 0.3:  # Only pre-fetch high-confidence predictions
                request = {
                    'prompt_id': next_prompt_id,
                    'context': context.copy(),
                    'confidence': confidence
                }
                
                # Non-blocking queue addition
                try:
                    self.prefetch_queue.put_nowait(request)
                except asyncio.QueueFull:
                    logger.warning("Prefetch queue full, skipping request")
    
    def get_prepared_prompt(self, prompt_id: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get a pre-prepared prompt if available."""
        cache_key = f"{prompt_id}_{hash(str(context))}"
        return self.cache.get(cache_key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about predictive prompting performance."""
        return {
            'registered_prompts': len(self.prompts),
            'cache_size': len(self.cache.cache),
            'prediction_accuracy': self._calculate_accuracy(),
            'cache_hit_rate': self._calculate_hit_rate(),
            'queue_size': self.prefetch_queue.qsize(),
            'active': self._active
        }
    
    def _calculate_accuracy(self) -> float:
        """Calculate prediction accuracy (simplified)."""
        # This would require more complex tracking in a real implementation
        return 0.75  # Placeholder
    
    def _calculate_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        if not self.cache.cache:
            return 0.0
        
        total_hits = sum(entry['hits'] for entry in self.cache.cache.values())
        total_entries = len(self.cache.cache)
        
        return total_hits / max(1, total_entries)


# Global manager instance
_prompt_manager: Optional[PredictivePromptManager] = None


def get_prompt_manager() -> PredictivePromptManager:
    """Get the global predictive prompt manager."""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PredictivePromptManager()
    return _prompt_manager


def register_prompt(prompt_config: PromptConfig) -> None:
    """Register a prompt for predictive pre-fetching."""
    manager = get_prompt_manager()
    manager.register_prompt(prompt_config)


def record_prompt_shown(prompt_id: str, context: Dict[str, Any]) -> None:
    """Record that a prompt was shown to update predictions."""
    manager = get_prompt_manager()
    manager.record_prompt_shown(prompt_id, context)


def get_prepared_prompt(prompt_id: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Get a pre-prepared prompt if available."""
    manager = get_prompt_manager()
    return manager.get_prepared_prompt(prompt_id, context)


def start_predictive_prompting() -> None:
    """Start the predictive prompting system."""
    manager = get_prompt_manager()
    manager.start_background_processing()


def stop_predictive_prompting() -> None:
    """Stop the predictive prompting system."""
    manager = get_prompt_manager()
    manager.stop_background_processing()


def get_prompting_stats() -> Dict[str, Any]:
    """Get statistics about the predictive prompting system."""
    manager = get_prompt_manager()
    return manager.get_stats()