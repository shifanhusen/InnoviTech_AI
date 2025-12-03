"""
Web scraping service using BeautifulSoup for extracting content from URLs.
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from app.core.config import settings
from app.utils.logger import logger


class ScrapeService:
    """Handles web scraping functionality."""
    
    def __init__(self):
        self.timeout = settings.SCRAPE_TIMEOUT
        self.max_chars = settings.SCRAPE_MAX_CHARS
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    
    def _validate_url(self, url: str) -> bool:
        """
        Validate URL format.
        
        Args:
            url: URL to validate
        
        Returns:
            True if valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme in ['http', 'https'], result.netloc])
        except Exception:
            return False
    
    def _clean_text(self, soup: BeautifulSoup) -> str:
        """
        Extract and clean visible text from BeautifulSoup object.
        
        Args:
            soup: BeautifulSoup parsed HTML
        
        Returns:
            Cleaned text content
        """
        # Remove unwanted tags
        for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form", "button"]):
            tag.decompose()
        
        # Get text
        text = soup.get_text(separator=" ", strip=True)
        
        # Normalize whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = " ".join(chunk for chunk in chunks if chunk)
        
        # Limit length
        if len(text) > self.max_chars:
            text = text[:self.max_chars] + "..."
            logger.debug(f"Truncated scraped text to {self.max_chars} characters")
        
        return text
    
    def scrape_website(self, url: str) -> str:
        """
        Fetch a URL and return cleaned text content.
        
        Args:
            url: URL to scrape
        
        Returns:
            Cleaned text content or error message
        """
        # Validate URL
        if not self._validate_url(url):
            error_msg = f"Invalid URL format: {url}"
            logger.warning(error_msg)
            return f"[Scraping Error: {error_msg}]"
        
        try:
            logger.info(f"Scraping URL: {url}")
            
            # Fetch URL
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            # Check status code
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code} error for {url}"
                logger.warning(error_msg)
                return f"[Scraping Error: {error_msg}]"
            
            # Parse HTML
            soup = BeautifulSoup(response.content, "lxml")
            
            # Extract and clean text
            cleaned_text = self._clean_text(soup)
            
            if not cleaned_text:
                logger.warning(f"No text content extracted from {url}")
                return "[Scraping Error: No text content found on the page]"
            
            logger.info(f"Successfully scraped {len(cleaned_text)} characters from {url}")
            return cleaned_text
            
        except requests.exceptions.Timeout:
            error_msg = f"Request timed out after {self.timeout} seconds for {url}"
            logger.error(error_msg)
            return f"[Scraping Error: {error_msg}]"
        
        except requests.exceptions.ConnectionError:
            error_msg = f"Failed to connect to {url}"
            logger.error(error_msg)
            return f"[Scraping Error: {error_msg}]"
        
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed for {url}: {str(e)}"
            logger.error(error_msg)
            return f"[Scraping Error: {error_msg}]"
        
        except Exception as e:
            error_msg = f"Unexpected error scraping {url}: {str(e)}"
            logger.error(error_msg)
            return f"[Scraping Error: {error_msg}]"
