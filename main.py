import queue
import glob
import json
from typing import Optional, List, Dict
from pathlib import Path

# Optional Git import - handle case where Git is not available
try:
    import git
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    logging.warning("GitPython not available - Git integration disabled")
except Exception as e:
    GIT_AVAILABLE = False
    logging.warning(f"Git not available: {e}")

load_dotenv()

MIC_INDEX = 0
TRIGGER_WORD = "jarvis"
CONVERSATION_TIMEOUT = 30  # seconds of inactivity before exiting conversation mode
CONFIG_FILE = ".jarvis_config.json"

logging.basicConfig(level=logging.DEBUG) # logging

# api_key = os.getenv("OPENAI_API_KEY") removed because it's not needed for ollama
# org_id = os.getenv("OPENAI_ORG_ID") removed because it's not needed for ollama

recognizer = sr.Recognizer()
mic = sr.Microphone(device_index=MIC_INDEX)

# Initialize LLM
llm = ChatOllama(model="qwen3:1.7b", reasoning=False)

# llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, organization=org_id) for openai

# Tool list
tools = [get_time]

# Enhanced prompt with project context awareness
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are Jarvis, an intelligent, conversational AI assistant specialized in software development. 
Your goal is to be helpful, friendly, and informative, especially when working with code and project contexts.

When provided with project context, use it to give more accurate and relevant answers about:
- Code structure and architecture
- File organization and dependencies
- Recent changes and modifications
- Configuration files and settings
- Error analysis and debugging suggestions

Always explain your reasoning simply when appropriate, and keep your responses conversational and concise.
If you're analyzing code, provide specific, actionable advice."""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# Agent + executor
agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

class ProjectAnalyzer:
    """Analyzes project structure and provides context for LLM queries"""
    
    def __init__(self, project_path: str = None):
        self.project_path = project_path or os.getcwd()
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from file"""
        config_path = os.path.join(self.project_path, CONFIG_FILE)
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Error loading config: {e}")
        return {
            "include_patterns": ["*.py", "*.js", "*.java", "*.cpp", "*.html", "*.css", "*.json", "*.yml", "*.yaml", "*.md"],
            "exclude_patterns": ["__pycache__", "node_modules", ".git", "venv", ".env", "*.log"],
            "max_files": 50,
            "max_file_size": 10000  # bytes
        }
    
    def _save_config(self):
        """Save configuration to file"""
        config_path = os.path.join(self.project_path, CONFIG_FILE)
        try:
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving config: {e}")
    
    def analyze_project_structure(self) -> Dict:
        """Analyze project structure and return context"""
        context = {
            "project_path": self.project_path,
            "files": [],
            "recent_changes": [],
            "config_files": [],
            "languages": set(),
            "file_count": 0
        }
        
        try:
            # Get all files matching include patterns
            all_files = []
            for pattern in self.config["include_patterns"]:
                files = glob.glob(os.path.join(self.project_path, "**", pattern), recursive=True)
                all_files.extend(files)
            
            # Filter out excluded patterns
            filtered_files = []
            for file_path in all_files:
                relative_path = os.path.relpath(file_path, self.project_path)
                if not any(exclude in relative_path for exclude in self.config["exclude_patterns"]):
                    filtered_files.append(file_path)
            
            # Analyze files
            for file_path in filtered_files[:self.config["max_files"]]:
                relative_path = os.path.relpath(file_path, self.project_path)
                
                # Get file info
                stat = os.stat(file_path)
                file_size = stat.st_size
                
                if file_size > self.config["max_file_size"]:
                    continue
                
                # Determine language
                ext = os.path.splitext(file_path)[1].lower()
                language_map = {
                    '.py': 'Python', '.js': 'JavaScript', '.java': 'Java',
                    '.cpp': 'C++', '.html': 'HTML', '.css': 'CSS',
                    '.json': 'JSON', '.yml': 'YAML', '.yaml': 'YAML',
                    '.md': 'Markdown', '.txt': 'Text'
                }
                language = language_map.get(ext, 'Unknown')
                context["languages"].add(language)
                
                # Check if it's a config file
                config_files = ['package.json', 'requirements.txt', 'pom.xml', '.env', 'dockerfile', 'docker-compose.yml']
                if any(config in relative_path.lower() for config in config_files):
                    context["config_files"].append(relative_path)
                
                # Get file content preview
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        preview = content[:500] + "..." if len(content) > 500 else content
                        
                        file_info = {
                            "path": relative_path,
                            "language": language,
                            "size": file_size,
                            "preview": preview
                        }
                        context["files"].append(file_info)
                except Exception as e:
                    logging.warning(f"Could not read file {file_path}: {e}")
            
            # Get recent changes from Git (if available)
            if GIT_AVAILABLE:
                try:
                    repo = git.Repo(self.project_path)
                    recent_commits = list(repo.iter_commits('HEAD', max_count=5))
                    for commit in recent_commits:
                        context["recent_changes"].append({
                            "hash": commit.hexsha[:8],
                            "message": commit.message.strip(),
                            "author": commit.author.name,
                            "date": commit.committed_datetime.isoformat()
                        })
                except git.InvalidGitRepositoryError:
                    context["recent_changes"] = []
                except Exception as e:
                    logging.warning(f"Error getting Git info: {e}")
                    context["recent_changes"] = []
            else:
                context["recent_changes"] = []
                logging.info("Git integration disabled - skipping Git analysis")
            
            context["file_count"] = len(context["files"])
            context["languages"] = list(context["languages"])
            
        except Exception as e:
            logging.error(f"Error analyzing project: {e}")
        
        return context
    
    def generate_context_summary(self, context: Dict) -> str:
        """Generate a human-readable summary of project context"""
        summary_parts = []
        
        summary_parts.append(f"📁 Project: {os.path.basename(context['project_path'])}")
        summary_parts.append(f"📍 Path: {context['project_path']}")
        summary_parts.append(f"📊 Files: {context['file_count']} files analyzed")
        
        if context["languages"]:
            summary_parts.append(f"🔧 Languages: {', '.join(context['languages'])}")
        
        if context["config_files"]:
            summary_parts.append(f"⚙️ Config files: {', '.join(context['config_files'][:3])}")
            if len(context["config_files"]) > 3:
                summary_parts.append(f"   ... and {len(context['config_files']) - 3} more")
        
        if context["recent_changes"]:
            summary_parts.append("🔄 Recent changes:")
            for change in context["recent_changes"][:3]:
                summary_parts.append(f"   • {change['hash']}: {change['message']}")
        elif not GIT_AVAILABLE:
            summary_parts.append("🔄 Git integration: Disabled (Git not available)")
        
        if context["files"]:
            summary_parts.append("📄 Key files:")
            for file_info in context["files"][:5]:
                summary_parts.append(f"   • {file_info['path']} ({file_info['language']})")
            if len(context["files"]) > 5:
                summary_parts.append(f"   ... and {len(context['files']) - 5} more files")
        
        return "\n".join(summary_parts)
    
    def get_relevant_files_content(self, query: str, context: Dict) -> str:
        """Get content of files that might be relevant to the query"""
        relevant_content = []
        
        # Simple keyword matching to find relevant files
        query_lower = query.lower()
        keywords = query_lower.split()
        
        for file_info in context["files"]:
            file_path = file_info["path"].lower()
            content = file_info["preview"].lower()
            
            # Check if file path or content contains keywords
            relevance_score = 0
            for keyword in keywords:
                if keyword in file_path or keyword in content:
                    relevance_score += 1
            
            if relevance_score > 0:
                relevant_content.append(f"📄 {file_info['path']}:\n{file_info['preview']}\n")
        
        return "\n".join(relevant_content[:3])  # Limit to 3 most relevant files

# Initialize project analyzer
project_analyzer = ProjectAnalyzer()

def process_command_with_context(command: str, speak_response: bool = True, include_context: bool = True):
    """Process a command with optional project context"""
    try:
        if include_context:
            # Analyze project context
            context = project_analyzer.analyze_project_structure()
            context_summary = project_analyzer.generate_context_summary(context)
            relevant_files = project_analyzer.get_relevant_files_content(command, context)
            
            # Create enhanced prompt with context
            enhanced_prompt = f"""Project Context:
{context_summary}

Relevant Files:
{relevant_files}

User Query: {command}

Please provide a detailed response based on the project context above."""
            
            logging.info("🤖 Sending command with context to agent...")
            response = executor.invoke({"input": enhanced_prompt})
        else:
            logging.info("🤖 Sending command to agent...")
            response = executor.invoke({"input": command})
        
        content = response["output"]
        logging.info(f"✅ Agent responded: {content}")
        
        print("Jarvis:", content)
        if speak_response:
            speak_text(content)
        
        return content
    except Exception as e:
        error_msg = f"❌ Error processing command: {e}"
        logging.error(error_msg)
        print("Jarvis:", error_msg)
        if speak_response:
            speak_text("Sorry, I encountered an error processing your request.")
        return error_msg

# TTS setup
def speak_text(text: str):
    try:
        engine = pyttsx3.init()
        for voice in engine.getProperty('voices'):
            if "jamie" in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        engine.setProperty('rate', 180)
        engine.setProperty('volume', 1.0)
        engine.say(text)
        engine.runAndWait()
        time.sleep(0.3)
    except Exception as e:
        logging.error(f"❌ TTS failed: {e}")

def configure_project_settings():
    """Configure project analysis settings"""
    print("⚙️ Project Analysis Configuration")
    print("Current settings:")
    for key, value in project_analyzer.config.items():
        print(f"  {key}: {value}")
    
    print("\nConfigure settings (press Enter to keep current value):")
    
    # Include patterns
    include_input = input(f"Include patterns (comma-separated) [{', '.join(project_analyzer.config['include_patterns'])}]: ").strip()
    if include_input:
        project_analyzer.config['include_patterns'] = [p.strip() for p in include_input.split(',')]
    
    # Exclude patterns
    exclude_input = input(f"Exclude patterns (comma-separated) [{', '.join(project_analyzer.config['exclude_patterns'])}]: ").strip()
    if exclude_input:
        project_analyzer.config['exclude_patterns'] = [p.strip() for p in exclude_input.split(',')]
    
    # Max files
    max_files_input = input(f"Max files to analyze [{project_analyzer.config['max_files']}]: ").strip()
    if max_files_input:
        try:
            project_analyzer.config['max_files'] = int(max_files_input)
        except ValueError:
            print("Invalid number, keeping current value")
    
    # Max file size
    max_size_input = input(f"Max file size in bytes [{project_analyzer.config['max_file_size']}]: ").strip()
    if max_size_input:
        try:
            project_analyzer.config['max_file_size'] = int(max_size_input)
        except ValueError:
            print("Invalid number, keeping current value")
    
    project_analyzer._save_config()
    print("✅ Configuration saved!")

def show_project_context():
    """Show current project context"""
    print("📊 Analyzing project context...")
    context = project_analyzer.analyze_project_structure()
    summary = project_analyzer.generate_context_summary(context)
    print("\n" + summary)

def text_input_loop():
    """Handle text input in a separate thread"""
    print("💬 Text mode active. Type your commands (or 'quit' to exit):")
    print("Special commands:")
    print("  'context' - Show project context")
    print("  'config' - Configure project analysis")
    print("  'no-context' - Disable context for next query")
    
    context_enabled = True
    
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'context':
                show_project_context()
            elif user_input.lower() == 'config':
                configure_project_settings()
            elif user_input.lower() == 'no-context':
                context_enabled = False
                print("⚠️ Context disabled for next query")
            elif user_input:
                process_command_with_context(user_input, speak_response=False, include_context=context_enabled)
                context_enabled = True  # Re-enable context after query
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            logging.error(f"❌ Error in text input: {e}")

def voice_input_loop():
    """Handle voice input"""
    conversation_mode = False
    last_interaction_time = None

    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            while True:
                try:
                    if not conversation_mode:
                        logging.info("🎤 Listening for wake word...")
                        audio = recognizer.listen(source, timeout=10)
                        transcript = recognizer.recognize_google(audio)
                        logging.info(f"🗣 Heard: {transcript}")

                        if TRIGGER_WORD.lower() in transcript.lower():
                            logging.info(f"🗣 Triggered by: {transcript}")
                            speak_text("Yes sir?")
                            conversation_mode = True
                            last_interaction_time = time.time()
                        else:
                            logging.debug("Wake word not detected, continuing...")
                    else:
                        logging.info("🎤 Listening for next command...")
                        audio = recognizer.listen(source, timeout=10)
                        command = recognizer.recognize_google(audio)
                        logging.info(f"📥 Command: {command}")

                        process_command_with_context(command)
                        last_interaction_time = time.time()

                        if time.time() - last_interaction_time > CONVERSATION_TIMEOUT:
                            logging.info("⌛ Timeout: Returning to wake word mode.")
                            conversation_mode = False

                except sr.WaitTimeoutError:
                    logging.warning("⚠️ Timeout waiting for audio.")
                    if conversation_mode and time.time() - last_interaction_time > CONVERSATION_TIMEOUT:
                        logging.info("⌛ No input in conversation mode. Returning to wake word mode.")
                        conversation_mode = False
                except sr.UnknownValueError:
                    logging.warning("⚠️ Could not understand audio.")
                except Exception as e:
                    logging.error(f"❌ Error during recognition or tool call: {e}")
                    time.sleep(1)

    except Exception as e:
        logging.critical(f"❌ Critical error in voice loop: {e}")

def main():
    """Main function to handle both voice and text input"""
    print("🤖 Jarvis Assistant Started!")
    print("Choose your input method:")
    print("1. Voice mode (say 'jarvis' to activate)")
    print("2. Text mode (type commands directly)")
    print("3. Both modes (voice + text simultaneously)")
    
    while True:
        try:
            choice = input("Enter your choice (1/2/3): ").strip()
            
            if choice == "1":
                print("🎤 Starting voice mode...")
                voice_input_loop()
                break
            elif choice == "2":
                print("💬 Starting text mode...")
                text_input_loop()
                break
            elif choice == "3":
                print("🎤💬 Starting both voice and text modes...")
                # Start voice input in a separate thread
                voice_thread = threading.Thread(target=voice_input_loop, daemon=True)
                voice_thread.start()
                
                # Run text input in main thread
                text_input_loop()
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            logging.error(f"❌ Error in main: {e}")

# Main interaction loop
def write():
    main()

if __name__ == "__main__":
    main()
