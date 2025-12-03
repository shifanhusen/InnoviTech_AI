"""
Web search service using DuckDuckGo for searching the internet.
"""
import requests
from typing import List, Dict
from app.utils.logger import logger


class SearchService:
    """Handles web search functionality using DuckDuckGo."""
    
    def __init__(self):
        self.base_url = "https://html.duckduckgo.com/html/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Search DuckDuckGo and return top results.
        
        Args:
            query: Search query
            num_results: Number of results to return (default 5)
        
        Returns:
            List of dicts with 'title', 'url', and 'snippet'
        """
        try:
            logger.info(f"Searching DuckDuckGo for: {query}")
            
            # DuckDuckGo lite search
            params = {"q": query}
            response = requests.post(
                self.base_url,
                data=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Search failed with status {response.status_code}")
                return []
            
            # Parse results using simple text parsing
            results = []
            html = response.text
            
            # Extract result blocks (simple parsing)
            result_blocks = html.split('class="result__a"')
            
            for block in result_blocks[1:num_results+1]:  # Skip first split
                try:
                    # Extract URL
                    url_start = block.find('href="') + 6
                    url_end = block.find('"', url_start)
                    url = block[url_start:url_end]
                    
                    # Extract title
                    title_start = block.find('>') + 1
                    title_end = block.find('</a>')
                    title = block[title_start:title_end].strip()
                    
                    # Extract snippet (next section)
                    snippet_start = block.find('class="result__snippet"')
                    if snippet_start > 0:
                        snippet_start = block.find('>', snippet_start) + 1
                        snippet_end = block.find('</a>', snippet_start)
                        snippet = block[snippet_start:snippet_end].strip()
                        # Clean HTML tags
                        snippet = snippet.replace('<b>', '').replace('</b>', '')
                    else:
                        snippet = ""
                    
                    if url and title:
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet
                        })
                except Exception as e:
                    logger.warning(f"Failed to parse result block: {e}")
                    continue
            
            logger.info(f"Found {len(results)} search results")
            return results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Search request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def format_results_for_prompt(self, results: List[Dict[str, str]]) -> str:
        """
        Format search results into a text block for the LLM prompt.
        
        Args:
            results: List of search results
        
        Returns:
            Formatted string with search results
        """
        if not results:
            return "No search results found."
        
        formatted = "Here are the top search results:\n\n"
        
        for i, result in enumerate(results, 1):
            formatted += f"{i}. **{result['title']}**\n"
            formatted += f"   URL: {result['url']}\n"
            if result['snippet']:
                formatted += f"   {result['snippet']}\n"
            formatted += "\n"
        
        return formatted
