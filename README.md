# Cortex Guard Demo

This demo showcases how to use Cortex Guard to protect your LLM applications from security threats like prompt injection, jailbreaks, and malicious inputs.

## Features Demonstrated

1. **Prompt Injection Detection** - Identifies attempts to manipulate the AI's behavior
2. **Jailbreak Prevention** - Blocks attempts to bypass safety guidelines
3. **PII Detection** - Identifies and flags personally identifiable information
4. **Toxic Content Filtering** - Detects harmful or inappropriate content
5. **Custom Policy Enforcement** - Apply your own security rules

## Setup

### Installation

```bash
pip install -r requirements.txt
```

### Running the Demo

#### Web Interface
```bash
python app.py
```
Then open your browser to `http://localhost:5000`

#### CLI Demo
```bash
python cli_demo.py
```

#### API Demo
```bash
# Start the API server
python api_server.py

# In another terminal, test the API
python test_api.py
```

## Demo Scenarios

The demo includes several pre-configured test cases:

- ✅ **Safe prompts** - Normal, benign user inputs
- ⚠️ **Prompt injection attempts** - Malicious instructions embedded in prompts
- 🚫 **Jailbreak attempts** - Attempts to bypass safety measures
- 🔒 **PII leakage** - Inputs containing sensitive personal information
- ☠️ **Toxic content** - Harmful or inappropriate language

## Architecture

```
User Input → Cortex Guard → Analysis → Decision → Protected LLM
                ↓
         [Multiple Checks]
         - Prompt Injection
         - Jailbreak Detection
         - PII Scanner
         - Toxicity Filter
         - Custom Rules
```

## Configuration

Edit `config.yaml` to customize:
- Sensitivity thresholds
- Enabled/disabled checks
- Custom rules and patterns
- Logging preferences

## API Usage

```python
from cortex_guard import CortexGuard

guard = CortexGuard()

# Check a user input
result = guard.check(user_input)

if result.is_safe:
    # Proceed with LLM call
    response = llm.generate(user_input)
else:
    # Handle the threat
    print(f"Blocked: {result.threat_type}")
```

## License

MIT

