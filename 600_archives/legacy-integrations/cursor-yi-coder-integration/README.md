<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 400_contributing-guidelines.md -->

# Yi-Coder Integration for Cursor

AI-powered code generation extension for Cursor IDE using Yi-Coder-9B-Chat-Q6_K model.

## Features

- **Code Generation**: Generate code based on context and requirements
- **Code Completion**: Intelligent code completion at cursor position
- **Code Refactoring**: AI-powered code refactoring and optimization
- **Multi-language Support**: Support for Python, JavaScript, TypeScript, Java, C++, and more
- **Context Awareness**: Intelligent context extraction and management
- **Local Processing**: All code generation happens locally via LM Studio

## Prerequisites

1. **Cursor IDE**: Latest version of Cursor IDE
2. **LM Studio**: Installed and configured with Yi-Coder-9B-Chat-Q6_K model
3. **Node.js**: Version 16 or higher
4. **TypeScript**: For development and building

## Installation

### 1. Install LM Studio and Yi-Coder Model

1. Download and install [LM Studio](https://lmstudio.ai/)
2. Download the Yi-Coder-9B-Chat-Q6_K model
3. Load the model in LM Studio
4. Start the LM Studio server on `<http://localhost:1234`>

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
```sql

### 3. Install in Cursor

1. Open Cursor IDE
2. Go to Extensions (Ctrl+Shift+X)
3. Click "Install from VSIX" and select the packaged extension
4. Or copy the extension folder to Cursor's extensions directory

## Configuration

The extension can be configured through Cursor's settings:

```json
{
  "yi-coder.lmStudioUrl": "<http://localhost:1234",>
  "yi-coder.modelName": "Yi-Coder-9B-Chat-Q6_K",
  "yi-coder.maxTokens": 2048,
  "yi-coder.temperature": 0.7
}
```html

### Configuration Options

- **lmStudioUrl**: URL of the LM Studio server (default: <http://localhost:1234>)
- **modelName**: Name of the model in LM Studio (default: cursor-native-ai)
- **maxTokens**: Maximum tokens for code generation (default: 2048)
- **temperature**: Temperature for code generation (default: 0.7)

## Usage

### Commands

The extension provides three main commands:

1. **Yi-Coder: Generate Code**- Generate code based on current context
2.**Yi-Coder: Complete Code**- Complete code at cursor position
3.**Yi-Coder: Refactor Code**- Refactor selected code

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
```text

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
```text

### Testing

```bash
# Run unit tests
npm test

# Run integration tests
npm run test:integration
```yaml

## Architecture

### Components

1.**Extension Entry Point**(`extension.ts`)
  - Registers commands with Cursor
  - Handles command execution
  - Manages extension lifecycle

2.**Yi-Coder Client**(`yiCoderClient.ts`)
  - Communicates with LM Studio
  - Handles API requests and responses
  - Manages model configuration

3.**Context Manager**(`contextManager.ts`)
  - Extracts code context
  - Manages conversation history
  - Handles project structure analysis

### Communication Flow

1. User triggers command in Cursor
2. Extension extracts current context
3. Context is sent to LM Studio via Yi-Coder Client
4. LM Studio processes request with Yi-Coder model
5. Response is parsed and formatted
6. Generated code is inserted into editor

## Troubleshooting

### Common Issues

1.**LM Studio Connection Failed**- Ensure LM Studio is running
  - Check the server URL in settings
  - Verify the model is loaded

2.**Extension Not Loading**- Check Cursor's extension logs
  - Verify TypeScript compilation
  - Restart Cursor IDE

3.**Code Generation Fails**- Check LM Studio logs
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

1.**Model Configuration**- Use appropriate temperature settings
  - Limit max tokens for faster responses
  - Use quantized models for better performance

2.**Context Management**- Limit context size for large files
  - Use function-level context when possible
  - Clear conversation history periodically

3.**Resource Usage**- Monitor memory usage
  - Use appropriate timeout settings
  - Implement caching for repeated requests

## Security

### Data Privacy

- All code generation happens locally
- No code or context is transmitted externally
- API keys are stored securely
- Input validation prevents malicious code

### Best Practices

1.**Input Validation**- All user inputs are validated
  - Malicious code is filtered
  - Context size is limited

2.**Error Handling**
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

