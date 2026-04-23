"""
LLM Interface Module for Summarizer Tool

This module provides the interface to local LLMs using llama-cpp-python
for GGUF model inference.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    logging.warning("llama-cpp-python not installed. LLM functionality will be limited.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMInterface:
    """
    Interface for local LLM inference using llama-cpp-python.
    
    Attributes:
        model_path: Path to the GGUF model file
        model: Loaded Llama model instance
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
    """
    
    def __init__(
        self,
        model_path: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        n_ctx: int = 4096
    ):
        """
        Initialize the LLM interface.
        
        Args:
            model_path: Path to GGUF model file
            max_tokens: Maximum tokens to generate in response
            temperature: Sampling temperature (0.0-1.0)
            n_ctx: Context window size
        """
        self.model_path = model_path
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.n_ctx = n_ctx
        self.model = None
        
        if not LLAMA_CPP_AVAILABLE:
            raise ImportError(
                "llama-cpp-python is required for LLM functionality. "
                "Install with: pip install llama-cpp-python"
            )
        
        self._load_model()
    
    def _load_model(self):
        """Load the GGUF model into memory."""
        logger.info(f"Loading LLM model from: {self.model_path}")
        try:
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_threads=4,  # Use 4 CPU threads
                n_gpu_layers=0,  # CPU-only for now
                verbose=False
            )
            logger.info("LLM model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load LLM model: {str(e)}")
            raise
    
    def generate_summary(
        self,
        text: str,
        prompt: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate a summary from the given text.
        
        Args:
            text: Text to summarize
            prompt: Custom summarization prompt
            max_tokens: Override max tokens for this request
            
        Returns:
            Dictionary containing summary and metadata
        """
        if max_tokens is None:
            max_tokens = self.max_tokens
        
        if prompt is None:
            prompt = self._get_default_prompt()
        
        start_time = datetime.now()
        
        try:
            # Format the prompt with the text
            full_prompt = f"{prompt}\n\n{text}"
            
            # Generate response
            output = self.model(
                prompt=full_prompt,
                max_tokens=max_tokens,
                temperature=self.temperature,
                stop=["\n\n"],
                echo=False
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Extract the summary
            summary = output['choices'][0]['text'].strip()
            
            # Estimate tokens used (rough approximation)
            tokens_used = len(output['choices'][0]['text'].split())
            
            return {
                'summary': summary,
                'prompt_used': prompt,
                'processing_time': round(processing_time, 2),
                'tokens_used': tokens_used
            }
            
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            raise
    
    def _get_default_prompt(self) -> str:
        """Get the default summarization prompt."""
        return """Summarize the following text concisely while preserving key information.
Provide a clear, informative summary that captures the main points."""
    
    def __del__(self):
        """Clean up resources."""
        if self.model is not None:
            del self.model


def summarize_text(
    text: str,
    model_path: str,
    prompt: Optional[str] = None,
    max_tokens: int = 500,
    temperature: float = 0.7
) -> Dict[str, Any]:
    """
    Convenience function to summarize text using the LLM interface.
    
    Args:
        text: Text to summarize
        model_path: Path to GGUF model file
        prompt: Custom summarization prompt
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        
    Returns:
        Dictionary containing summary and metadata
    """
    interface = LLMInterface(
        model_path=model_path,
        max_tokens=max_tokens,
        temperature=temperature
    )
    
    try:
        return interface.generate_summary(text, prompt, max_tokens)
    finally:
        del interface
