"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.YiCoderClient = void 0;
const vscode = __importStar(require("vscode"));
const axios_1 = __importDefault(require("axios"));
class YiCoderClient {
    constructor() {
        this.config = vscode.workspace.getConfiguration('yi-coder');
        this.baseUrl = this.config.get('lmStudioUrl', 'http://localhost:1234');
    }
    async generateCode(context) {
        try {
            const prompt = this.buildGenerationPrompt(context);
            const response = await this.callLMStudio(prompt);
            return this.extractCodeFromResponse(response);
        }
        catch (error) {
            console.error('Error generating code:', error);
            throw error;
        }
    }
    async completeCode(context) {
        try {
            const prompt = this.buildCompletionPrompt(context);
            const response = await this.callLMStudio(prompt);
            return this.extractCodeFromResponse(response);
        }
        catch (error) {
            console.error('Error completing code:', error);
            throw error;
        }
    }
    async refactorCode(selectedCode, context) {
        try {
            const prompt = this.buildRefactoringPrompt(selectedCode, context);
            const response = await this.callLMStudio(prompt);
            return this.extractCodeFromResponse(response);
        }
        catch (error) {
            console.error('Error refactoring code:', error);
            throw error;
        }
    }
    async callLMStudio(prompt) {
        const request = {
            model: this.config.get('modelName', 'Yi-Coder-9B-Chat-Q6_K'),
            messages: [
                {
                    role: 'system',
                    content: 'You are an expert programmer. Generate high-quality, well-documented code that follows best practices.'
                },
                {
                    role: 'user',
                    content: prompt
                }
            ],
            temperature: this.config.get('temperature', 0.7),
            max_tokens: this.config.get('maxTokens', 2048),
            stream: false
        };
        try {
            const response = await axios_1.default.post(`${this.baseUrl}/v1/chat/completions`, request, {
                headers: {
                    'Content-Type': 'application/json'
                },
                timeout: 30000 // 30 second timeout
            });
            const data = response.data;
            return data.choices[0]?.message?.content || '';
        }
        catch (error) {
            console.error('LM Studio API error:', error);
            throw new Error(`Failed to communicate with LM Studio: ${error}`);
        }
    }
    buildGenerationPrompt(context) {
        return `Generate code for the following context:

File: ${context.currentFile}
Language: ${context.language}
Current Content:
\`\`\`${context.language}
${context.fileContent}
\`\`\`

Cursor Position: ${context.cursorPosition}

Please generate appropriate code that fits the context and follows the existing code style.`;
    }
    buildCompletionPrompt(context) {
        return `Complete the following code:

File: ${context.currentFile}
Language: ${context.language}
Current Content:
\`\`\`${context.language}
${context.fileContent}
\`\`\`

Cursor Position: ${context.cursorPosition}

Please complete the code at the cursor position, maintaining the existing style and logic.`;
    }
    buildRefactoringPrompt(selectedCode, context) {
        return `Refactor the following code to improve its quality, readability, and maintainability:

File: ${context.currentFile}
Language: ${context.language}
Selected Code:
\`\`\`${context.language}
${selectedCode}
\`\`\`

Context:
\`\`\`${context.language}
${context.fileContent}
\`\`\`

Please refactor the selected code to:
1. Improve readability and maintainability
2. Follow best practices for ${context.language}
3. Maintain the same functionality
4. Add appropriate comments and documentation`;
    }
    extractCodeFromResponse(response) {
        // Extract code blocks from the response
        const codeBlockRegex = /```[\w]*\n([\s\S]*?)\n```/g;
        const matches = response.match(codeBlockRegex);
        if (matches && matches.length > 0) {
            // Return the first code block without the markdown formatting
            return matches[0].replace(/```[\w]*\n/, '').replace(/\n```$/, '');
        }
        // If no code blocks found, return the entire response
        return response.trim();
    }
    async testConnection() {
        try {
            await axios_1.default.get(`${this.baseUrl}/v1/models`, {
                timeout: 5000
            });
            return true;
        }
        catch (error) {
            console.error('Connection test failed:', error);
            return false;
        }
    }
}
exports.YiCoderClient = YiCoderClient;
//# sourceMappingURL=yiCoderClient.js.map