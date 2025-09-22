## Intelligent Mobile Agent

> AI-powered mobile automation using computer vision (CV)  and natural language processing (NLP)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Qwen](https://img.shields.io/badge/AI-Qwen%20Vision-orange.svg)](https://huggingface.co/Qwen)

## 🎯 Problem Statement

Mobile application testing and automation faces several critical challenges:

### Current Pain Points
- **Manual Testing Bottleneck**: Mobile app testing requires extensive manual effort for UI interactions
- **Fragmented Automation Tools**: Existing solutions require complex setup and don't understand UI context
- **Limited Natural Language Interface**: Most tools require technical scripting rather than intuitive instructions
- **Poor Adaptability**: Traditional automation fails when UI layouts change or unexpected states occur
- **Time-Intensive Workflows**: Setting up automation for simple tasks takes longer than manual execution

### Real-World Impact
- QA teams spend **60-80%** of their time on repetitive manual testing
- Mobile app releases are delayed due to testing bottlenecks
- User experience issues go undetected due to limited test coverage
- Small teams cannot afford comprehensive mobile testing

## 🚀 Solution Design

The Intelligent Mobile Agent addresses these challenges through an AI approach that combines computer vision, natural language processing, and intelligent automation.

### Core Innovation
```
Natural Language → AI Vision Understanding → Contextual Actions → Task Completion
```

### Architecture Overview

```mermaid
graph TD
    A[Natural Language Input] --> B[Task Parser]
    B --> C[App Launcher]
    C --> D[Screen Capture]
    D --> E[Qwen Vision Analysis]
    E --> F{Action Decision}
    F -->|Primary| G[AI-Suggested Action]
    F -->|Fallback| H[UI Hierarchy Analysis]
    G --> J[Action Execution]
    H --> J
    I --> J
    J --> K[State Update]
    K --> L{Task Complete?}
    L -->|No| D
    L -->|Yes| M[Result Report]
```

### Key Advantages

1. **Natural Language Interface**: "Search for headphones under ₹1000 on Amazon"
2. **AI-Powered Vision**: Understands UI context like a human tester
3. **Adaptive Execution**: Handles unexpected UI states and recovers from failures  
4. **Zero Configuration**: Works out-of-the-box with any Android app
5. **Intelligent Fallbacks**: Multiple strategies ensure task completion

## 🏗️ Technical Architecture

### Modular Design
```
intelligent_mobile_agent/
├── core/
│   ├── android_controller.py      # ADB communication & device control
│   ├── qwen_vision_agent.py       # AI vision processing
│   ├── ui_element_parser.py       # UI hierarchy analysis
│   ├── action_coordinator.py      # Action execution & loop prevention
│   ├── task_execution_state.py    # State management
│   └── app_utilities.py           # Helper functions
├── intelligent_mobile_agent.py    # Main orchestrator
├── agent_config.py               # Configuration management
└── run_agent.py                  # Entry point
```

### Component Responsibilities

#### 🤖 **QwenVisionAgent**
- Processes screenshots using Qwen/Qwen2.5-VL-32B-Instruct model
- Generates context-aware prompts based on task progress
- Extracts and scales action coordinates from AI responses

#### 📱 **AndroidController**  
- Manages ADB communication with Android devices
- Captures screenshots and UI hierarchy dumps
- Executes touch, type, and scroll actions

#### 🔍 **UIElementParser**
- Parses XML UI hierarchy for interactive elements
- Identifies search bars, buttons, and input fields with scoring
- Provides fallback actions when AI vision fails

#### ⚡ **ActionCoordinator**
- Coordinates action parsing and execution
- Detects and prevents infinite loops
- Tracks action history for intelligent recovery

#### 📊 **TaskExecutionState**
- Manages task progress and step counting
- Tracks search initiation and query entry states
- Detects screen loops for navigation recovery

## 🚀 Getting Started

### Prerequisites
- **Python 3.8+** 
- **Android Device** with USB debugging enabled
- **ADB (Android Debug Bridge)** installed
- **Hugging Face API Key** ([Get one here](https://huggingface.co/settings/tokens))

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/MogilipalemHemanthKumar/Intelligent_Mobile_Agent.git
   cd Intelligent_Mobile_Agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp environment_template .env
   # Edit .env with your Hugging Face API token
   ```

4. **Connect your Android device**
   ```bash
   # Enable Developer Options and USB Debugging
   adb devices  # Verify device connection
   ```

5. **Run your first automation**
   ```bash
   python run_agent.py
   ```

## 📖 Usage Examples

### Basic Task Execution
```python
from intelligent_mobile_agent import IntelligentMobileAgent

# Initialize agent
agent = IntelligentMobileAgent()

# Execute tasks with natural language
result = agent.execute_task_instruction("Search for wireless earbuds under ₹2000 on Amazon")
print(result)
```

### Supported Task Types

| Category | Example Instructions |
|----------|---------------------|
| **E-commerce** | `"Search for iPhone 15 on Flipkart and check price"` |
| **Food Delivery** | `"Order biryani from Zomato for Koramangala delivery"` |
| **Transportation** | `"Check Ola cab availability to Indiranagar"` |


## 🔧 Advanced Features

### AI Vision Processing
- **Context-Aware Prompts**: Adapts prompts based on task progress
- **Coordinate Scaling**: Handles different screen resolutions automatically
- **Multi-Strategy Parsing**: Robust action extraction from AI responses

### Loop Prevention
- **Action History Tracking**: Detects repetitive actions
- **Screen Hash Comparison**: Identifies UI state loops  
- **Smart Recovery**: Automatic navigation alternatives

### Fallback Mechanisms
- **UI Hierarchy Analysis**: XML-based element detection when vision fails
- **Search Element Scoring**: Intelligent identification of search interfaces
- **Predefined Actions**: Last-resort actions for edge cases

## 📱 Supported Applications

| App | Package Name | Features |
|-----|--------------|----------|
| **Flipkart** | `com.flipkart.android` | Search, Products, Orders |
| **Zomato** | `com.application.zomata` | Search, Restaurants, Delivery |
| **Ola** | `com.olacabs.customer` | Booking, Location, Pricing |
| **Blinkit** | `com.grofers.customerapp` | Grocery, Quick Commerce |






