from app.ollama_integration import ollama_code_llama
import json

print("Step 1: Checking if Ollama is available...")
available = ollama_code_llama.check_availability()
print(f"Ollama available: {available}")

if available:
    print("\nStep 2: Testing simple message API call...")
    try:
        simple_prompt = "Hello, how are you?"
        print(f"Sending prompt: {simple_prompt}")
        result = ollama_code_llama._call_ollama_api(simple_prompt)
        print(f"Response received (first 100 chars): {result[:100]}...")
    except Exception as e:
        print(f"Error with simple prompt: {str(e)}")

    print("\nStep 3: Testing code analysis with a small Python sample...")
    try:
        code_sample = """
def factorial(n):
    if n < 0:
        return None
    if n == 0:
        return 1
    return n * factorial(n-1)

# Test function
print(factorial(5))
"""
        print(f"Analyzing Python code sample...")
        analysis = ollama_code_llama.analyze_code(code_sample, "python")
        print(f"Analysis keys: {list(analysis.keys())}")
        print(f"Found {len(analysis.get('bugs', []))} bugs")
        print(f"Found {len(analysis.get('security', []))} security issues")
        print(f"Found {len(analysis.get('optimizations', []))} optimizations")
    except Exception as e:
        print(f"Error with code analysis: {str(e)}")
else:
    print("Ollama is not available - please check the Ollama server") 