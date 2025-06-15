import os
import json
import logging
from typing import Dict, Any, Optional, List
import aiohttp
from aiohttp import ClientTimeout
from tenacity import retry, stop_after_attempt, wait_exponential
from configuration import OPENAI_API_KEY


logger = logging.getLogger(__name__)

class ChatGPTConnector:
    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize the ChatGPT connector.
        
        Args:
            api_key: OpenAI API key. If not provided, will try to get from environment variable OPENAI_API_KEY
            model: The model to use for completions
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.api_key = OPENAI_API_KEY
        self.model = model
        self.timeout = ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.base_url = "https://api.openai.com/v1/chat/completions"
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def get_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Get a completion from ChatGPT.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Dictionary containing the completion response
            
        Raises:
            aiohttp.ClientError: If there's an error with the HTTP request
            ValueError: If the response is invalid
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }
        
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
            
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            try:
                async with session.post(self.base_url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"OpenAI API error: {error_text}")
                        raise aiohttp.ClientError(f"OpenAI API returned status {response.status}: {error_text}")
                    
                    response_data = await response.json()
                    return response_data
                    
            except aiohttp.ClientError as e:
                logger.error(f"Error making request to OpenAI API: {str(e)}")
                raise
                
    async def get_simple_completion(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Get a simple text completion from ChatGPT.
        
        Args:
            prompt: The prompt to send to ChatGPT
            temperature: Controls randomness (0.0 to 1.0)
            
        Returns:
            The generated text response
        """
        messages = [{"role": "user", "content": prompt}]
        response = await self.get_completion(messages, temperature=temperature)
        
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing OpenAI response: {str(e)}")
            raise ValueError("Invalid response format from OpenAI API")
