"""
Web search service using DuckDuckGo for searching the internet.
"""
from duckduckgo_search import DDGS
from typing import List, Dict
from app.utils.logger import logger
import traceback


class SearchService:
    """Handles web search functionality using DuckDuckGo."""
    
    def __init__(self):
        self.ddgs = DDGS()
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Search DuckDuckGo and return top results with real-time data.
        
        Args:
            query: Search query
            num_results: Number of results to return (default 5)
        
        Returns:
            List of dicts with 'title', 'url', and 'snippet'
        """
        try:
            logger.info(f"🔍 Searching DuckDuckGo for: {query}")
            
            # Use DuckDuckGo search library for real-time results
            results = []
            
            # Text search for web results
            search_results = self.ddgs.text(query, max_results=num_results)
            
            for result in search_results:
                results.append({
                    "title": result.get('title', 'No title'),
                    "url": result.get('href', result.get('link', '')),
                    "snippet": result.get('body', result.get('snippet', ''))
                })
            
            logger.info(f"✅ Found {len(results)} real-time search results")
            
            # Log first result for debugging
            if results:
                logger.info(f"First result: {results[0]['title'][:50]}...")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
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
