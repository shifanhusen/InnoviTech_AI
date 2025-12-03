# API Integration Examples

This document provides integration examples for consuming the AI Assistant API from various platforms and programming languages.

## Base Configuration

- **Base URL**: `http://your-domain/api` (or `https://your-domain/api` with SSL)
- **Content-Type**: `application/json`
- **Session ID**: Generate a unique ID per user/session

## Python Examples

### Basic Chat

```python
import requests
import uuid

class AIAssistantClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session_id = str(uuid.uuid4())
    
    def chat(self, message: str, use_scrape: bool = False, scrape_url: str = None) -> str:
        """Send a chat message and get AI response."""
        url = f"{self.base_url}/llm/chat"
        
        payload = {
            "session_id": self.session_id,
            "message": message,
            "use_scrape": use_scrape
        }
        
        if scrape_url:
            payload["scrape_url"] = scrape_url
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        return data["reply"]
    
    def reset_session(self):
        """Reset the conversation history."""
        url = f"{self.base_url}/llm/reset"
        payload = {"session_id": self.session_id}
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        # Generate new session ID
        self.session_id = str(uuid.uuid4())

# Usage
client = AIAssistantClient("http://your-domain/api")

# Simple conversation
reply = client.chat("What is machine learning?")
print(reply)

# Follow-up question (maintains context)
reply = client.chat("Can you give me an example?")
print(reply)

# Chat with web scraping
reply = client.chat(
    "Summarize this article",
    use_scrape=True,
    scrape_url="https://example.com/article"
)
print(reply)

# Reset conversation
client.reset_session()
```

### Async Python (with aiohttp)

```python
import aiohttp
import asyncio
import uuid

class AsyncAIAssistantClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session_id = str(uuid.uuid4())
    
    async def chat(self, message: str, use_scrape: bool = False, scrape_url: str = None) -> str:
        """Send a chat message asynchronously."""
        url = f"{self.base_url}/llm/chat"
        
        payload = {
            "session_id": self.session_id,
            "message": message,
            "use_scrape": use_scrape
        }
        
        if scrape_url:
            payload["scrape_url"] = scrape_url
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                return data["reply"]

# Usage
async def main():
    client = AsyncAIAssistantClient("http://your-domain/api")
    
    reply = await client.chat("Hello, AI!")
    print(reply)

asyncio.run(main())
```

## JavaScript/Node.js Examples

### Node.js (with axios)

```javascript
const axios = require('axios');
const { v4: uuidv4 } = require('uuid');

class AIAssistantClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.sessionId = uuidv4();
    this.client = axios.create({
      baseURL: this.baseUrl,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  async chat(message, useScrape = false, scrapeUrl = null) {
    const payload = {
      session_id: this.sessionId,
      message: message,
      use_scrape: useScrape
    };

    if (scrapeUrl) {
      payload.scrape_url = scrapeUrl;
    }

    try {
      const response = await this.client.post('/llm/chat', payload);
      return response.data.reply;
    } catch (error) {
      console.error('Chat error:', error.message);
      throw error;
    }
  }

  async resetSession() {
    await this.client.post('/llm/reset', {
      session_id: this.sessionId
    });
    this.sessionId = uuidv4();
  }
}

// Usage
(async () => {
  const client = new AIAssistantClient('http://your-domain/api');
  
  const reply1 = await client.chat('What is AI?');
  console.log(reply1);
  
  const reply2 = await client.chat('Tell me more');
  console.log(reply2);
  
  await client.resetSession();
})();
```

### Browser JavaScript (Vanilla)

```javascript
class AIAssistantClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.sessionId = this.generateSessionId();
  }

  generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  async chat(message, useScrape = false, scrapeUrl = null) {
    const payload = {
      session_id: this.sessionId,
      message: message,
      use_scrape: useScrape
    };

    if (scrapeUrl) {
      payload.scrape_url = scrapeUrl;
    }

    const response = await fetch(`${this.baseUrl}/llm/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data.reply;
  }

  async resetSession() {
    await fetch(`${this.baseUrl}/llm/reset`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ session_id: this.sessionId })
    });
    this.sessionId = this.generateSessionId();
  }
}

// Usage
const client = new AIAssistantClient('http://your-domain/api');

client.chat('Hello!')
  .then(reply => console.log(reply))
  .catch(error => console.error(error));
```

## PHP Examples

### PHP (with cURL)

```php
<?php

class AIAssistantClient {
    private $baseUrl;
    private $sessionId;

    public function __construct($baseUrl) {
        $this->baseUrl = rtrim($baseUrl, '/');
        $this->sessionId = $this->generateSessionId();
    }

    private function generateSessionId() {
        return 'session_' . time() . '_' . bin2hex(random_bytes(8));
    }

    public function chat($message, $useScrape = false, $scrapeUrl = null) {
        $url = $this->baseUrl . '/llm/chat';
        
        $payload = [
            'session_id' => $this->sessionId,
            'message' => $message,
            'use_scrape' => $useScrape
        ];

        if ($scrapeUrl) {
            $payload['scrape_url'] = $scrapeUrl;
        }

        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Content-Type: application/json'
        ]);

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($httpCode !== 200) {
            throw new Exception("HTTP error: $httpCode");
        }

        $data = json_decode($response, true);
        return $data['reply'];
    }

    public function resetSession() {
        $url = $this->baseUrl . '/llm/reset';
        
        $payload = ['session_id' => $this->sessionId];

        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Content-Type: application/json'
        ]);

        curl_exec($ch);
        curl_close($ch);

        $this->sessionId = $this->generateSessionId();
    }
}

// Usage
$client = new AIAssistantClient('http://your-domain/api');

try {
    $reply = $client->chat('What is PHP?');
    echo $reply . PHP_EOL;
    
    $reply = $client->chat('Give me an example');
    echo $reply . PHP_EOL;
    
    $client->resetSession();
} catch (Exception $e) {
    echo 'Error: ' . $e->getMessage() . PHP_EOL;
}
```

## Flutter/Dart Example

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:uuid/uuid.dart';

class AIAssistantClient {
  final String baseUrl;
  late String sessionId;

  AIAssistantClient(this.baseUrl) {
    sessionId = const Uuid().v4();
  }

  Future<String> chat(
    String message, {
    bool useScrape = false,
    String? scrapeUrl,
  }) async {
    final url = Uri.parse('$baseUrl/llm/chat');
    
    final payload = {
      'session_id': sessionId,
      'message': message,
      'use_scrape': useScrape,
    };

    if (scrapeUrl != null) {
      payload['scrape_url'] = scrapeUrl;
    }

    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    );

    if (response.statusCode != 200) {
      throw Exception('HTTP error: ${response.statusCode}');
    }

    final data = jsonDecode(response.body);
    return data['reply'];
  }

  Future<void> resetSession() async {
    final url = Uri.parse('$baseUrl/llm/reset');
    
    await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'session_id': sessionId}),
    );

    sessionId = const Uuid().v4();
  }
}

// Usage
void main() async {
  final client = AIAssistantClient('http://your-domain/api');
  
  try {
    final reply = await client.chat('Hello from Flutter!');
    print(reply);
    
    final reply2 = await client.chat('How are you?');
    print(reply2);
    
    await client.resetSession();
  } catch (e) {
    print('Error: $e');
  }
}
```

## Go Example

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "net/http"
    "github.com/google/uuid"
)

type AIAssistantClient struct {
    BaseURL   string
    SessionID string
    Client    *http.Client
}

type ChatRequest struct {
    SessionID string  `json:"session_id"`
    Message   string  `json:"message"`
    UseScrape bool    `json:"use_scrape"`
    ScrapeURL *string `json:"scrape_url,omitempty"`
}

type ChatResponse struct {
    Reply          string `json:"reply"`
    SessionExpired bool   `json:"session_expired"`
}

func NewAIAssistantClient(baseURL string) *AIAssistantClient {
    return &AIAssistantClient{
        BaseURL:   baseURL,
        SessionID: uuid.New().String(),
        Client:    &http.Client{},
    }
}

func (c *AIAssistantClient) Chat(message string, useScrape bool, scrapeURL *string) (string, error) {
    url := fmt.Sprintf("%s/llm/chat", c.BaseURL)
    
    reqBody := ChatRequest{
        SessionID: c.SessionID,
        Message:   message,
        UseScrape: useScrape,
        ScrapeURL: scrapeURL,
    }
    
    jsonData, err := json.Marshal(reqBody)
    if err != nil {
        return "", err
    }
    
    resp, err := c.Client.Post(url, "application/json", bytes.NewBuffer(jsonData))
    if err != nil {
        return "", err
    }
    defer resp.Body.Close()
    
    if resp.StatusCode != http.StatusOK {
        return "", fmt.Errorf("HTTP error: %d", resp.StatusCode)
    }
    
    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return "", err
    }
    
    var chatResp ChatResponse
    if err := json.Unmarshal(body, &chatResp); err != nil {
        return "", err
    }
    
    return chatResp.Reply, nil
}

func (c *AIAssistantClient) ResetSession() error {
    url := fmt.Sprintf("%s/llm/reset", c.BaseURL)
    
    reqBody := map[string]string{"session_id": c.SessionID}
    jsonData, _ := json.Marshal(reqBody)
    
    resp, err := c.Client.Post(url, "application/json", bytes.NewBuffer(jsonData))
    if err != nil {
        return err
    }
    defer resp.Body.Close()
    
    c.SessionID = uuid.New().String()
    return nil
}

func main() {
    client := NewAIAssistantClient("http://your-domain/api")
    
    reply, err := client.Chat("Hello from Go!", false, nil)
    if err != nil {
        fmt.Printf("Error: %v\n", err)
        return
    }
    fmt.Println(reply)
    
    client.ResetSession()
}
```

## Ruby Example

```ruby
require 'net/http'
require 'json'
require 'securerandom'

class AIAssistantClient
  attr_accessor :session_id

  def initialize(base_url)
    @base_url = base_url.chomp('/')
    @session_id = SecureRandom.uuid
  end

  def chat(message, use_scrape: false, scrape_url: nil)
    uri = URI("#{@base_url}/llm/chat")
    
    payload = {
      session_id: @session_id,
      message: message,
      use_scrape: use_scrape
    }
    
    payload[:scrape_url] = scrape_url if scrape_url
    
    response = Net::HTTP.post(
      uri,
      payload.to_json,
      'Content-Type' => 'application/json'
    )
    
    raise "HTTP error: #{response.code}" unless response.code == '200'
    
    data = JSON.parse(response.body)
    data['reply']
  end

  def reset_session
    uri = URI("#{@base_url}/llm/reset")
    
    Net::HTTP.post(
      uri,
      { session_id: @session_id }.to_json,
      'Content-Type' => 'application/json'
    )
    
    @session_id = SecureRandom.uuid
  end
end

# Usage
client = AIAssistantClient.new('http://your-domain/api')

reply = client.chat('Hello from Ruby!')
puts reply

client.reset_session
```

## Error Handling Best Practices

### Python Example with Error Handling

```python
import requests
from typing import Optional

class AIAssistantError(Exception):
    """Base exception for AI Assistant errors."""
    pass

class APIError(AIAssistantError):
    """API returned an error response."""
    pass

class NetworkError(AIAssistantError):
    """Network communication failed."""
    pass

class AIAssistantClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.session_id = str(uuid.uuid4())
        self.timeout = timeout
    
    def chat(
        self, 
        message: str, 
        use_scrape: bool = False, 
        scrape_url: Optional[str] = None
    ) -> str:
        """
        Send a chat message with comprehensive error handling.
        
        Raises:
            NetworkError: If network communication fails
            APIError: If API returns an error response
        """
        url = f"{self.base_url}/llm/chat"
        
        payload = {
            "session_id": self.session_id,
            "message": message,
            "use_scrape": use_scrape
        }
        
        if scrape_url:
            payload["scrape_url"] = scrape_url
        
        try:
            response = requests.post(
                url, 
                json=payload, 
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return data["reply"]
            
        except requests.exceptions.Timeout:
            raise NetworkError(f"Request timed out after {self.timeout}s")
        except requests.exceptions.ConnectionError:
            raise NetworkError(f"Failed to connect to {url}")
        except requests.exceptions.HTTPError as e:
            raise APIError(f"API error: {e.response.status_code} - {e.response.text}")
        except KeyError:
            raise APIError("Invalid response format from API")
        except Exception as e:
            raise AIAssistantError(f"Unexpected error: {str(e)}")

# Usage with error handling
client = AIAssistantClient("http://your-domain/api")

try:
    reply = client.chat("Hello!")
    print(reply)
except NetworkError as e:
    print(f"Network error: {e}")
    # Implement retry logic
except APIError as e:
    print(f"API error: {e}")
    # Handle API errors
except AIAssistantError as e:
    print(f"Error: {e}")
```

## Rate Limiting Considerations

The API doesn't have built-in rate limiting, but you should implement client-side throttling:

```python
import time
from functools import wraps

def rate_limit(max_calls: int, period: int):
    """Decorator to rate limit function calls."""
    calls = []
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            calls[:] = [c for c in calls if c > now - period]
            
            if len(calls) >= max_calls:
                sleep_time = period - (now - calls[0])
                time.sleep(sleep_time)
            
            calls.append(time.time())
            return func(*args, **kwargs)
        return wrapper
    return decorator

class RateLimitedClient(AIAssistantClient):
    @rate_limit(max_calls=10, period=60)  # 10 calls per minute
    def chat(self, message: str, **kwargs) -> str:
        return super().chat(message, **kwargs)
```

## Additional Resources

- [Main README](../README.md) - Project overview
- [API Documentation](http://your-domain/docs) - Interactive Swagger docs
- [Deployment Guide](../DEPLOYMENT.md) - Production deployment
