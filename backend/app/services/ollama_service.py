"""
Ollama API integration for LLaMA model inference.
"""
import requests
from app.core.config import settings
from app.utils.logger import logger


class OllamaService:
    """Handles communication with Ollama API."""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT
    
    def call_ollama(self, prompt: str) -> str:
        """
        Send a prompt to Ollama and return the generated response.
        
        Args:
            prompt: The complete prompt to send to the model
        
        Returns:
            Generated text response from the model
        
        Raises:
            Exception: If the API call fails
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40
            }
        }
        
        try:
            logger.info(f"Calling Ollama at {url} with model {self.model}")
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            
            # Check for HTTP errors
            if response.status_code != 200:
                error_msg = f"Ollama API returned status {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Parse response
            data = response.json()
            generated_text = data.get("response", "")
            
            if not generated_text:
                logger.warning("Ollama returned empty response")
                return "I apologize, but I couldn't generate a response. Please try again."
            
            logger.info(f"Ollama generated {len(generated_text)} characters")
            return generated_text.strip()
            
        except requests.exceptions.Timeout:
            error_msg = f"Ollama request timed out after {self.timeout} seconds"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Failed to connect to Ollama at {self.base_url}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        except requests.exceptions.RequestException as e:
            error_msg = f"Ollama request failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        except (KeyError, ValueError) as e:
            error_msg = f"Failed to parse Ollama response: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
