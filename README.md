# 🚀 AI Development Ecosystem

> **Welcome to the AI Development Ecosystem!** This repository contains a comprehensive AI-powered development system with sophisticated documentation, automated workflows, and intelligent task management.

## 🎯 **Start Here**

**New to this project?** → **[START_HERE.md](START_HERE.md)** - Your guide to navigating this comprehensive documentation system

**Want to understand what this is?** → **[400_project-overview.md](400_project-overview.md)** - 5-minute overview of the entire system

**Want to see what's being built?** → **[000_backlog.md](000_backlog.md)** - Current priorities and roadmap

**Want to understand the current state?** → **[100_cursor-memory-context.md](100_cursor-memory-context.md)** - Instant project state

## 📚 **What This Project Is**

This is a sophisticated AI development ecosystem that transforms ideas into working software using AI agents (Cursor Native AI + Specialized Agents). It provides:

- **Structured Workflows**: From ideation to implementation with built-in checkpoints
- **Automated Task Processing**: AI-driven task execution with intelligent error recovery
- **Comprehensive Documentation**: Cognitive scaffolding system for AI context preservation
- **Metadata Collection**: Sophisticated analytics and data-driven decision making
- **Quality Assurance**: Testing, security, and performance frameworks

## 🚀 **Quick Start**

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r dspy-rag-system/requirements.txt

# Start the system
make run-local
```

## 📖 **Documentation Navigation**

### **Core Documentation**
- **[START_HERE.md](START_HERE.md)** - Navigation guide for humans
- **[400_project-overview.md](400_project-overview.md)** - Main project overview
- **[400_system-overview.md](400_system-overview.md)** - Technical architecture
- **[000_backlog.md](000_backlog.md)** - Current priorities and roadmap

### **Development Workflow**
- **[001_create-prd.md](001_create-prd.md)** - Create Product Requirements Documents
- **[002_generate-tasks.md](002_generate-tasks.md)** - Generate executable tasks
- **[003_process-task-list.md](003_process-task-list.md)** - Execute tasks with AI

### **Setup & Configuration**
- **[202_setup-requirements.md](202_setup-requirements.md)** - Environment setup
- **[201_model-configuration.md](201_model-configuration.md)** - AI model configuration
- **[400_deployment-environment-guide.md](400_deployment-environment-guide.md)** - Production deployment

### **Quality & Standards**
- **[400_contributing-guidelines.md](400_contributing-guidelines.md)** - Development standards
- **[400_testing-strategy-guide.md](400_testing-strategy-guide.md)** - Testing approach
- **[400_security-best-practices-guide.md](400_security-best-practices-guide.md)** - Security guidelines
- **[400_performance-optimization-guide.md](400_performance-optimization-guide.md)** - Performance guidelines

## 🤖 **AI System Components**

### **Core AI System**
- **DSPy RAG System**: Enhanced retrieval-augmented generation
- **Cursor Native AI**: Foundation AI model integration
- **Specialized Agents**: Task-specific AI agents
- **Metadata Collection**: Comprehensive analytics and state management

### **Automation & Workflows**
- **n8n Integration**: Automated backlog management
- **Mission Dashboard**: Real-time task monitoring
- **Error Recovery**: Intelligent error handling and retry logic
- **State Management**: Persistent execution state tracking

### **Quality Assurance**
- **Testing Framework**: Comprehensive test suites
- **Security Scanning**: Automated security validation
- **Performance Monitoring**: Real-time system health tracking
- **Documentation Validation**: Automated documentation coherence checking

## 🔧 **Key Commands**

```bash
# List all tasks
python3 scripts/process_tasks.py list

# Execute a specific task
python3 scripts/process_tasks.py execute B-049

# Check system status
python3 scripts/process_tasks.py status

# Start mission dashboard
./dspy-rag-system/start_mission_dashboard.sh

# Run tests
./dspy-rag-system/run_tests.sh
```

## 📊 **System Status**

- **Current Focus**: B-011 Cursor Native AI + Specialized Agents Integration
- **Infrastructure**: v0.3.1-rc3 Core Hardening ✅ completed
- **Documentation**: Comprehensive cognitive scaffolding system ✅ completed
- **Metadata System**: Advanced analytics and state management ✅ completed

## 🎯 **Getting Help**

1. **Start with [START_HERE.md](START_HERE.md)** for navigation guidance
2. **Check [000_backlog.md](000_backlog.md)** for current priorities
3. **Review [400_system-overview.md](400_system-overview.md)** for technical context
4. **Use [400_metadata-quick-reference.md](400_metadata-quick-reference.md)** for commands

## 📄 **Legacy Components**

This repository also contains legacy components for Mistral integration with Cursor IDE. For those specific components, see the `cursor-yi-coder-integration/` directory.

---

**Last Updated**: 2024-08-07  
**Documentation**: Comprehensive cognitive scaffolding system  
**Status**: Active development with AI-powered workflows

## Features

- **Code Generation**: Generate code based on context and requirements
- **Code Completion**: Intelligent code completion at cursor position
- **Code Refactoring**: AI-powered code refactoring and optimization
- **Multi-language Support**: Support for Python, JavaScript, TypeScript, Java, C++, and more
- **Context Awareness**: Intelligent context extraction and management
- **Local Processing**: All code generation happens locally via LM Studio

## Prerequisites

1. **Cursor IDE**: Latest version of Cursor IDE
2. **Ollama**: Installed and configured with Mistral-7B-Instruct model
3. **Node.js**: Version 16 or higher
4. **TypeScript**: For development and building

## Installation

### 1. Install Ollama and Mistral Model

1. Download and install [Ollama](https://ollama.ai/)
2. Download the Mistral-7B-Instruct model: `ollama pull mistral`
3. Start the Ollama server: `ollama serve`
4. Verify the server is running on `http://localhost:11434`

### 2. Build and Install Extension

```bash
# Clone the repository
git clone <repository-url>
cd cursor-yi-coder-integration

# Install dependencies
npm install

# Build the extension
npm run compile

# Package the extension (the execution engine)
npm run package
```

### 3. Install in Cursor

1. Open Cursor IDE
2. Go to Extensions (Ctrl+Shift+X)
3. Click "Install from VSIX" and select the packaged extension
4. Or copy the extension folder to Cursor's extensions directory

## Configuration

The extension can be configured through Cursor's settings:

```json
{
  "yi-coder.ollamaUrl": "http://localhost:11434",
  "yi-coder.modelName": "mistral",
  "yi-coder.maxTokens": 2048,
  "yi-coder.temperature": 0.7
}
```

### Configuration Options

- **ollamaUrl**: URL of the Ollama server (default: http://localhost:11434)
- **modelName**: Name of the model in Ollama (default: cursor-native-ai)
- **maxTokens**: Maximum tokens for code generation (default: 2048)
- **temperature**: Temperature for code generation (default: 0.7)

## Usage

### Commands

The extension provides three main commands:

1. **Yi-Coder: Generate Code** - Generate code based on current context
2. **Yi-Coder: Complete Code** - Complete code at cursor position
3. **Yi-Coder: Refactor Code** - Refactor selected code

### Keyboard Shortcuts

- `Ctrl+Shift+G` - Generate Code
- `Ctrl+Shift+C` - Complete Code
- `Ctrl+Shift+R` - Refactor Code

### Usage Examples

#### Code Generation
1. Place cursor where you want to generate code
2. Press `Ctrl+Shift+G` or use Command Palette
3. The AI will generate appropriate code based on context

#### Code Completion
1. Start typing code
2. Press `Ctrl+Shift+C` when you need completion
3. The AI will complete the code at cursor position

#### Code Refactoring
1. Select the code you want to refactor
2. Press `Ctrl+Shift+R` or use Command Palette
3. The AI will suggest refactored code

## Development

### Project Structure

```
cursor-yi-coder-integration/
├── src/
│   ├── extension.ts          # Main extension entry point
│   ├── yiCoderClient.ts      # LM Studio client
│   └── contextManager.ts     # Context management
├── test/
│   ├── extension.test.ts     # Extension tests
│   └── suite/
│       └── index.ts          # Test runner
├── package.json              # Extension manifest
├── tsconfig.json             # TypeScript configuration
└── README.md                 # This file
```

### Building

```bash
# Compile TypeScript
npm run compile

# Watch for changes
npm run watch

# Run tests
npm test

# Lint code
npm run lint
```

### Testing

```bash
# Run unit tests
npm test

# Run integration tests
npm run test:integration
```

## Architecture

### Components

1. **Extension Entry Point** (`extension.ts`)
   - Registers commands with Cursor
   - Handles command execution
   - Manages extension lifecycle

2. **Mistral Client** (`yiCoderClient.ts`)
   - Communicates with Ollama
   - Handles API requests and responses
   - Manages model configuration

3. **Context Manager** (`contextManager.ts`)
   - Extracts code context
   - Manages conversation history
   - Handles project structure analysis

### Communication Flow

1. User triggers command in Cursor
2. Extension extracts current context
3. Context is sent to Ollama via Mistral Client
4. Ollama processes request with Mistral model
5. Response is parsed and formatted
6. Generated code is inserted into editor

## Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   - Ensure Ollama is running: `ollama serve`
   - Check the server URL in settings
   - Verify the model is loaded: `ollama list`

2. **Extension Not Loading**
   - Check Cursor's extension logs
   - Verify TypeScript compilation
   - Restart Cursor IDE

3. **Code Generation Fails**
   - Check Ollama logs
   - Verify model configuration
   - Check network connectivity

### Debug Mode

Enable debug mode by setting:

```json
{
  "yi-coder.debug": true
}
```

This will show detailed logs in Cursor's Developer Console.

## Performance

### Optimization Tips

1. **Model Configuration**
   - Use appropriate temperature settings
   - Limit max tokens for faster responses
   - Use quantized models for better performance

2. **Context Management**
   - Limit context size for large files
   - Use function-level context when possible
   - Clear conversation history periodically

3. **Resource Usage**
   - Monitor memory usage
   - Use appropriate timeout settings
   - Implement caching for repeated requests

## Security

### Data Privacy

- All code generation happens locally
- No code or context is transmitted externally
- API keys are stored securely
- Input validation prevents malicious code

### Best Practices

1. **Input Validation**
   - All user inputs are validated
   - Malicious code is filtered
   - Context size is limited

2. **Error Handling**
   - Graceful degradation on failures
   - Secure error messages
   - Automatic retry mechanisms

## Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

### Code Style

- Follow TypeScript best practices
- Use ESLint for code quality
- Add comprehensive tests
- Document new features

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review the documentation
3. Open an issue on GitHub
4. Contact the development team

## Changelog

### v0.1.0
- Initial release
- Basic code generation functionality
- Code completion support
- Code refactoring capabilities
- Multi-language support
- Context management system

