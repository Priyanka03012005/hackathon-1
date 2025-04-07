import requests
import json
from typing import Dict, List, Any, Optional
import time

class OllamaCodeLlama:
    def __init__(self, model_name="codellama:7b", base_url="http://localhost:11434"):
        """
        Initialize Ollama Code Llama integration.
        
        Args:
            model_name (str): Name of the Ollama model to use
            base_url (str): URL of the Ollama API server
        """
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"

    def analyze_code(self, code_content: str, language: str) -> Dict[str, Any]:
        """
        Use Code Llama to analyze code for bugs, security issues, and optimizations.
        
        Args:
            code_content (str): Code to analyze
            language (str): Programming language of the code
            
        Returns:
            Dict containing analysis results
        """
        print(f"[INFO] Starting Ollama Code Llama analysis for {language} code")
        prompt = self._generate_prompt(code_content, language)
        
        try:
            print(f"[INFO] Sending request to Ollama API at {self.base_url}")
            response = self._call_ollama_api(prompt)
            print(f"[INFO] Received response from Ollama API (length: {len(response)} chars)")
            
            parsed_results = self._parse_results(response, code_content)
            print(f"[INFO] Successfully parsed Ollama results")
            print(f"[INFO] Found {len(parsed_results.get('bugs', []))} bugs, " +
                  f"{len(parsed_results.get('security', []))} security issues, and " +
                  f"{len(parsed_results.get('optimizations', []))} optimization suggestions")
            
            return parsed_results
        except Exception as e:
            error_msg = f"Error calling Ollama API: {str(e)}"
            print(f"[ERROR] {error_msg}")
            # Re-raise the exception to let the caller handle it
            raise Exception(error_msg)

    def _generate_prompt(self, code_content: str, language: str) -> str:
        """Generate a prompt for Code Llama to analyze code."""
        return f"""You are an expert {language} developer with years of experience in code review and static analysis.

Analyze the following code for:
1. Bugs and logical errors
2. Security vulnerabilities
3. Performance optimizations

For each issue you find:
- Include the line number
- Provide a clear explanation of the issue
- Rate the severity (low, medium, high, critical)
- Include a code snippet showing the issue
- Suggest a specific fix

Return ONLY a valid JSON object with the following structure:
{{
  "bugs": [
    {{
      "line": <line_number>,
      "message": "<issue_description>",
      "severity": "<severity_level>",
      "code_snippet": "<relevant_code>",
      "fix": {{
        "before": "<problematic_code>",
        "after": "<fixed_code>",
        "explanation": "<explanation_of_fix>"
      }}
    }}
  ],
  "security": [
    // Similar structure as bugs
  ],
  "optimizations": [
    // Similar structure as bugs
  ],
  "metrics": {{
    "complexity": <0-100>,
    "maintainability": <0-100>,
    "performance": <0-100>
  }}
}}

Here is the code to analyze:

```{language}
{code_content}
```

Respond with ONLY a valid, properly formatted JSON object following the specified structure."""

    def _call_ollama_api(self, prompt: str) -> str:
        """
        Call the Ollama API with the given prompt.
        
        Args:
            prompt (str): The prompt to send to the API
            
        Returns:
            str: The API response
        """
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.1,  # Low temperature for more deterministic results
            "num_predict": 2048,  # Increase token limit for longer responses
            "system": "You are an expert code reviewer specializing in identifying bugs, security issues, and performance optimizations. Focus on providing actionable, clear, and specific feedback."
        }
        
        try:
            print(f"[INFO] Calling Ollama API with model: {self.model_name}")
            print(f"[INFO] API URL: {self.api_url}")
            start_time = time.time()
            
            # Add more robust error handling with a longer timeout
            response = requests.post(self.api_url, json=data, timeout=120)  # 2 minute timeout
            
            elapsed_time = time.time() - start_time
            print(f"[INFO] Ollama API response received in {elapsed_time:.2f} seconds")
            
            if response.status_code != 200:
                error_msg = f"Ollama API error: HTTP {response.status_code} - {response.text}"
                print(f"[ERROR] {error_msg}")
                raise Exception(error_msg)
            
            # Get the response content
            try:
                response_json = response.json()
                if "response" not in response_json:
                    print(f"[WARNING] Unexpected response format. Keys: {list(response_json.keys())}")
                    # Try to extract any text content
                    if "content" in response_json:
                        print(f"[INFO] Using 'content' field instead of 'response'")
                        return response_json.get("content", "")
                    elif "generation" in response_json:
                        print(f"[INFO] Using 'generation' field instead of 'response'")
                        return response_json.get("generation", "")
                    else:
                        # Just return the whole response as a string
                        return json.dumps(response_json)
                
                return response_json.get("response", "")
            except json.JSONDecodeError:
                print(f"[WARNING] Failed to decode JSON from response. Using raw text.")
                return response.text
                
        except requests.exceptions.Timeout:
            raise Exception("Ollama API request timed out after 120 seconds")
        except requests.exceptions.ConnectionError:
            raise Exception(f"Connection error: Could not connect to Ollama API at {self.api_url}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to call Ollama API: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error calling Ollama API: {str(e)}")

    def _parse_results(self, response: str, code_content: str) -> Dict[str, Any]:
        """
        Parse the response from Ollama into a structured format.
        
        Args:
            response (str): Raw response from Ollama
            code_content (str): Original code content
            
        Returns:
            Dict: Structured analysis results
        """
        print(f"[DEBUG] Parsing Ollama response: {response[:100]}...")
        
        # Create a default empty structure to return if parsing fails
        default_results = {
            "bugs": [],
            "security": [],
            "optimizations": [],
            "metrics": {
                "complexity": 50,
                "maintainability": 50,
                "performance": 50
            }
        }
        
        # Check if the response is empty or None
        if not response or response.strip() == "":
            print("[ERROR] Empty response from Ollama API")
            return default_results
        
        # Extract JSON content from the response
        try:
            # First, check if the entire response is a valid JSON
            try:
                results = json.loads(response)
                print(f"[INFO] Parsed full response as valid JSON")
                
                # Check if the response is already in our expected format
                if "bugs" in results and "security" in results and "optimizations" in results:
                    print(f"[INFO] Response is already in the expected format")
                else:
                    print(f"[INFO] Response keys: {list(results.keys())}")
                    
                    # If the JSON doesn't have our expected structure, it might be a direct LLM response
                    # Try to find any JSON object in the response
                    json_start = response.find('{')
                    json_end = response.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        try:
                            json_str = response[json_start:json_end]
                            results = json.loads(json_str)
                            print(f"[INFO] Extracted JSON from response text")
                        except json.JSONDecodeError:
                            print(f"[ERROR] Failed to parse extracted JSON, using default structure")
                            results = default_results
            except json.JSONDecodeError:
                # If it's not valid JSON, try to find JSON object in the text
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    try:
                        json_str = response[json_start:json_end]
                        results = json.loads(json_str)
                        print(f"[INFO] Extracted JSON from response text")
                    except json.JSONDecodeError:
                        print(f"[ERROR] Failed to parse extracted JSON, using default structure")
                        results = default_results
                else:
                    # No JSON found, use default structure
                    print(f"[ERROR] No JSON found in response, using default structure")
                    results = default_results
            
            # Ensure all expected fields exist
            if "bugs" not in results:
                print(f"[WARNING] 'bugs' field not found in response, adding empty array")
                results["bugs"] = []
            if "security" not in results:
                print(f"[WARNING] 'security' field not found in response, adding empty array")
                results["security"] = []
            if "optimizations" not in results:
                print(f"[WARNING] 'optimizations' field not found in response, adding empty array")
                results["optimizations"] = []
            if "metrics" not in results:
                print(f"[WARNING] 'metrics' field not found in response, adding default metrics")
                results["metrics"] = {
                    "complexity": 50,
                    "maintainability": 50,
                    "performance": 50
                }
            
            # For any issues without code snippets, add them
            lines = code_content.split('\n')
            for category in ["bugs", "security", "optimizations"]:
                for issue in results[category]:
                    if "line" in issue and not issue.get("code_snippet"):
                        try:
                            line_num = int(issue["line"])
                            start = max(0, line_num - 4)
                            end = min(len(lines), line_num + 3)
                            issue["code_snippet"] = '\n'.join(lines[start:end])
                        except (ValueError, TypeError):
                            print(f"[WARNING] Invalid line number in issue: {issue.get('line')}")
            
            return results
            
        except Exception as e:
            # Return empty structure if any parsing error occurs
            print(f"[ERROR] Failed to parse Ollama response: {str(e)}")
            return default_results

    def check_availability(self) -> bool:
        """
        Check if Ollama API is available and the model is loaded.
        
        Returns:
            bool: True if available, False otherwise
        """
        try:
            print(f"[INFO] Checking Ollama availability at {self.base_url}")
            
            # Check if Ollama API is running
            try:
                response = requests.get(f"{self.base_url}/api/tags", timeout=5)
                if response.status_code != 200:
                    print(f"[ERROR] Ollama API returned HTTP {response.status_code}")
                    return False
            except requests.exceptions.ConnectionError:
                print(f"[ERROR] Could not connect to Ollama API at {self.base_url}")
                return False
            except requests.exceptions.Timeout:
                print(f"[ERROR] Connection to Ollama API timed out")
                return False
            except Exception as e:
                print(f"[ERROR] Error checking Ollama API: {str(e)}")
                return False
                
            # Check if the model is available
            try:
                # Try to parse the response - the structure is {"models": [{"name": "model_name", ...}]}
                data = response.json()
                
                # Debug the response
                print(f"[DEBUG] Ollama API response: {json.dumps(data)[:200]}...")
                
                if "models" not in data:
                    print(f"[ERROR] Unexpected response format from Ollama API: 'models' key not found")
                    return False
                    
                models = data.get("models", [])
                model_names = [model.get("name", "") for model in models]
                print(f"[INFO] Available models: {', '.join(model_names) if model_names else 'None'}")
                
                # Check if our model is in the list of available models
                if any(self.model_name == model.get("name", "") for model in models):
                    print(f"[INFO] Model {self.model_name} is available")
                    return True
                
                # If model name contains a colon (like "codellama:7b"), also check just the base name
                if ":" in self.model_name:
                    base_model = self.model_name.split(":")[0]
                    if any(base_model in model.get("name", "") for model in models):
                        print(f"[INFO] Base model {base_model} is available")
                        return True
                
                # Model not found, try to pull it
                print(f"[INFO] Model {self.model_name} not found, attempting to pull it")
                try:
                    pull_response = requests.post(
                        f"{self.base_url}/api/pull", 
                        json={"name": self.model_name, "stream": False},
                        timeout=30  # Increase timeout for model pull
                    )
                    success = pull_response.status_code == 200
                    print(f"[{'INFO' if success else 'ERROR'}] Model pull {'succeeded' if success else 'failed'}")
                    return success
                except Exception as pull_error:
                    print(f"[ERROR] Failed to pull model: {str(pull_error)}")
                    return False
            except Exception as e:
                print(f"[ERROR] Error processing models response: {str(e)}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Unexpected error checking Ollama availability: {str(e)}")
            return False

# Create a global instance
ollama_code_llama = OllamaCodeLlama()