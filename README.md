# 🧠 Jarvis – Local Voice-Controlled AI Assistant with Project Context

**Jarvis** is a voice-activated, conversational AI assistant powered by a local LLM (Qwen via Ollama) with **automatic project context analysis**. It listens for a wake word, processes spoken commands using a local language model with LangChain, and responds out loud via TTS. It supports tool-calling for dynamic functions and automatically provides rich project context to enhance LLM responses.

---

## 🚀 Features

### Core Features
- 🗣 Voice-activated with wake word **"Jarvis"**
- 💬 Text input mode for direct typing
- 🧠 Local language model (Qwen 3 via Ollama)
- 🔧 Tool-calling with LangChain
- 🔊 Text-to-speech responses via `pyttsx3`
- 🌍 Example tool: Get the current time in a given city
- 🔐 Optional support for OpenAI API integration

### 🆕 CLI-Contextualisée-LLM Features
- 📊 **Automatic Project Analysis**: Analyzes project structure, files, and dependencies
- 🔍 **Intelligent Context Generation**: Provides relevant project context to LLM queries
- 📈 **Optional Git Integration**: Tracks recent commits and changes (when Git is available)
- ⚙️ **Configurable Analysis**: Customizable file patterns and analysis settings
- 🎯 **Relevance Scoring**: Finds most relevant files based on user queries
- 📝 **Enhanced Responses**: More accurate and contextual LLM responses

---

## 🎯 How It Works

### 1. **Project Context Analysis**
Jarvis automatically analyzes your project to provide rich context:
- **File Structure**: Scans project directories and identifies file types
- **Language Detection**: Identifies programming languages used
- **Configuration Files**: Detects package.json, requirements.txt, pom.xml, etc.
- **Optional Git Integration**: Tracks recent commits and changes (when Git is available)
- **Content Preview**: Extracts relevant file content for context

### 2. **Enhanced Query Processing**
When you ask a question, Jarvis:
1. Analyzes your project structure
2. Identifies relevant files based on your query
3. Includes recent Git changes and configuration
4. Enhances the LLM prompt with project context
5. Provides more accurate and actionable responses

### 3. **Multiple Input Modes**
- **Voice Mode**: Say "Jarvis" to activate, then speak commands
- **Text Mode**: Type commands directly with special commands
- **Dual Mode**: Use both voice and text simultaneously

---

## 🛠️ Installation & Setup

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Set Up Ollama**
Ensure you have the `qwen3:1.7b` model available in Ollama:
```bash
ollama pull qwen3:1.7b
```

### 3. **Optional: Install Git (for Git Integration)**
If you want Git integration features (commit history, recent changes):
- **Windows**: Download from https://git-scm.com/download/win
- **macOS**: `brew install git`
- **Linux**: `sudo apt-get install git` or `sudo yum install git`

### 4. **Run Jarvis**
```bash
python main.py
```

---

## 📖 Usage Guide

### **Starting Jarvis**
When you run `python main.py`, you'll see:
```
🤖 Jarvis Assistant Started!
Choose your input method:
1. Voice mode (say 'jarvis' to activate)
2. Text mode (type commands directly)
3. Both modes (voice + text simultaneously)
```

### **Voice Mode**
1. Say **"Jarvis"** to activate
2. Speak your command or question
3. Jarvis responds with voice and text
4. Automatically includes project context

### **Text Mode**
Type commands directly with special commands:
- `context` - Show current project analysis
- `config` - Configure project analysis settings
- `no-context` - Disable context for next query
- `quit` - Exit the application

### **Example Queries**
```
You: "How can I fix the error in main.py?"
Jarvis: [Provides context-aware debugging advice with project analysis]

You: "What's the project structure?"
Jarvis: [Shows detailed project analysis with files and languages]

You: "Explain the recent changes"
Jarvis: [Shows Git history and recent modifications (if Git available)]
```

---

## 🎯 How to Use Jarvis

### **Getting Started**

#### **1. Basic Setup**
```bash
# Navigate to your project directory
cd your-project-folder

# Install dependencies
pip install -r requirements.txt

# Set up Ollama (if not already done)
ollama pull qwen3:1.7b

# Start Jarvis
python main.py
```

#### **2. Choose Your Input Method**
- **Option 1**: Voice mode - Say "Jarvis" to activate
- **Option 2**: Text mode - Type commands directly
- **Option 3**: Both modes - Use voice and text simultaneously

### **Voice Mode Usage**

#### **Activation**
```
You: "Jarvis"
Jarvis: "Yes sir?"
You: "What's the current time?"
Jarvis: "The current time is 2:30 PM"
```

#### **Project Analysis with Voice**
```
You: "Jarvis"
Jarvis: "Yes sir?"
You: "How can I improve the code in main.py?"
Jarvis: [Analyzes your project and provides specific recommendations]
```

### **Text Mode Usage**

#### **Basic Commands**
```bash
# Show project context
You: context

# Configure analysis settings
You: config

# Ask questions with context
You: "What programming languages are used in this project?"

# Disable context for next query
You: no-context
You: "What's the weather like?"  # No project context included

# Exit the application
You: quit
```

#### **Project-Specific Queries**
```bash
# Debug code issues
You: "There's an error in the login function, can you help?"

# Understand project structure
You: "What files are most important in this project?"

# Analyze recent changes
You: "What has changed recently in the codebase?"

# Get coding advice
You: "How can I optimize the database queries?"

# Review configuration
You: "Are there any issues with the package.json file?"
```

### **Configuration Commands**

#### **Project Analysis Settings**
When you run `config`, you can customize:
```
Include patterns: *.py, *.js, *.java, *.cpp, *.html, *.css, *.json, *.yml, *.yaml, *.md
Exclude patterns: __pycache__, node_modules, .git, venv, .env, *.log
Max files: 50
Max file size: 10000
```

#### **Example Configuration Session**
```
⚙️ Project Analysis Configuration
Current settings:
  include_patterns: ['*.py', '*.js', '*.java', '*.cpp', '*.html', '*.css', '*.json', '*.yml', '*.yaml', '*.md']
  exclude_patterns: ['__pycache__', 'node_modules', '.git', 'venv', '.env', '*.log']
  max_files: 50
  max_file_size: 10000

Configure settings (press Enter to keep current value):
Include patterns (comma-separated) [*.py, *.js, *.java, *.cpp, *.html, *.css, *.json, *.yml, *.yaml, *.md]: *.ts, *.tsx
Exclude patterns (comma-separated) [__pycache__, node_modules, .git, venv, .env, *.log]: 
Max files to analyze [50]: 100
Max file size in bytes [10000]: 
✅ Configuration saved!
```

### **Advanced Usage Examples**

#### **Debugging with Context**
```bash
You: "I'm getting a TypeError in the authentication module"
Jarvis: [Analyzes your project, finds auth-related files, and provides specific debugging advice]
```

#### **Code Review**
```bash
You: "Review the main.py file for potential improvements"
Jarvis: [Shows file content and provides detailed code review with suggestions]
```

#### **Architecture Analysis**
```bash
You: "How is this project structured?"
Jarvis: [Provides detailed project structure analysis with file relationships]
```

#### **Dependency Analysis**
```bash
You: "What dependencies does this project have?"
Jarvis: [Analyzes package.json, requirements.txt, and other config files]
```

### **Context-Aware Responses**

Jarvis automatically provides context-aware responses by:

1. **Analyzing Project Structure**
   - Scans all relevant files
   - Identifies programming languages
   - Detects configuration files

2. **Finding Relevant Files**
   - Matches your query keywords
   - Identifies most relevant files
   - Includes file content previews

3. **Enhancing Responses**
   - Includes project context in LLM prompts
   - Provides specific, actionable advice
   - References actual files in your project

### **Best Practices**

#### **For Better Results**
- **Be Specific**: "Fix the error in login.py" vs "Fix this error"
- **Use File Names**: "Analyze main.py" vs "Analyze this file"
- **Mention Context**: "How does this project handle authentication?"
- **Ask for Improvements**: "How can I optimize this code?"

#### **Common Use Cases**
- **Debugging**: "What's wrong with this function?"
- **Code Review**: "Review this file for best practices"
- **Architecture**: "How is this project organized?"
- **Dependencies**: "What libraries are being used?"
- **Configuration**: "Check the project settings"

### **Troubleshooting**

#### **If Jarvis Doesn't Respond**
1. Check microphone settings
2. Ensure Ollama is running
3. Verify model is downloaded: `ollama list`

#### **If Context is Missing**
1. Run `context` command to check project analysis
2. Use `config` to adjust file patterns
3. Ensure you're in the correct project directory

#### **If Git Features Don't Work**
1. Install Git: https://git-scm.com/download/win
2. Add Git to system PATH
3. Restart Jarvis

---

## ⚙️ Configuration

### **Project Analysis Settings**
Jarvis creates a `.jarvis_config.json` file in your project with:
```json
{
  "include_patterns": ["*.py", "*.js", "*.java", "*.cpp", "*.html", "*.css", "*.json", "*.yml", "*.yaml", "*.md"],
  "exclude_patterns": ["__pycache__", "node_modules", ".git", "venv", ".env", "*.log"],
  "max_files": 50,
  "max_file_size": 10000
}
```

### **Customizing Analysis**
Use the `config` command in text mode to customize:
- **Include Patterns**: File types to analyze
- **Exclude Patterns**: Directories/files to ignore
- **Max Files**: Maximum number of files to analyze
- **Max File Size**: Maximum file size in bytes

---

## 🔧 Technical Architecture

### **Core Components**
1. **ProjectAnalyzer**: Handles project structure analysis
2. **LangChain Integration**: Manages LLM interactions
3. **Voice Recognition**: Speech-to-text processing
4. **Text-to-Speech**: Voice response generation
5. **Optional Git Integration**: Repository analysis (when Git is available)

### **Context Enhancement Process**
1. **Query Reception**: User asks question
2. **Project Analysis**: Scans project structure
3. **Relevance Scoring**: Finds relevant files
4. **Context Generation**: Creates enhanced prompt
5. **LLM Processing**: Sends enriched query to model
6. **Response Delivery**: Provides contextual answer

---

## 🎯 Use Cases

### **Development Assistance**
- Debug code with project context
- Understand project architecture
- Analyze recent changes (with Git integration)
- Get coding recommendations

### **Project Understanding**
- Explore project structure
- Identify dependencies
- Review configuration files
- Track development history (with Git integration)

### **Learning & Documentation**
- Understand codebase organization
- Learn from recent commits (with Git integration)
- Explore different file types
- Get contextual explanations

---

## 🚀 Benefits

✅ **Productivity Boost**: No more manual copy-pasting of code context  
✅ **Precise Responses**: LLM gets full project context automatically  
✅ **Developer-Friendly**: Specialized for software development tasks  
✅ **Extensible**: Easy to add new analysis strategies  
✅ **Configurable**: Adapts to different project types  
✅ **Local Privacy**: All processing happens locally  

---

## 🔮 Future Enhancements
Here's the updated LinkedIn project description with focus on project context:

- **Dependency Mapping**: Automatic dependency analysis
- **Error Pattern Recognition**: Intelligent error detection
- **Project Templates**: Pre-configured analysis profiles
- **Multi-Project Support**: Context switching between projects
- **Enhanced Git Integration**: Better Git status and diff analysis

---


## 🤝 Contributing

Feel free to contribute to this project by:
- Adding new analysis strategies
- Improving context generation
- Enhancing voice recognition
- Adding new tools and capabilities

---

 
