import * as vscode from 'vscode';
import axios from 'axios';

export interface CodeContext {
    currentFile: string;
    cursorPosition: number;
    fileContent: string;
    language: string;
    projectStructure?: string;
}

export interface LMStudioRequest {
    model: string;
    messages: Array<{
        role: 'system' | 'user' | 'assistant';
        content: string;
    }>;
    temperature: number;
    max_tokens: number;
    stream: boolean;
}

export interface LMStudioResponse {
    choices: Array<{
        message: {
            content: string;
        };
    }>;
}

export class YiCoderClient {
    private config: vscode.WorkspaceConfiguration;
    private baseUrl: string;

    constructor() {
        this.config = vscode.workspace.getConfiguration('yi-coder');
        this.baseUrl = this.config.get('lmStudioUrl', 'http://localhost:1234');
    }

    async generateCode(context: CodeContext): Promise<string | null> {
        try {
            const prompt = this.buildGenerationPrompt(context);
            const response = await this.callLMStudio(prompt);
            return this.extractCodeFromResponse(response);
        } catch (error) {
            console.error('Error generating code:', error);
            throw error;
        }
    }

    async completeCode(context: CodeContext): Promise<string | null> {
        try {
            const prompt = this.buildCompletionPrompt(context);
            const response = await this.callLMStudio(prompt);
            return this.extractCodeFromResponse(response);
        } catch (error) {
            console.error('Error completing code:', error);
            throw error;
        }
    }

    async refactorCode(selectedCode: string, context: CodeContext): Promise<string | null> {
        try {
            const prompt = this.buildRefactoringPrompt(selectedCode, context);
            const response = await this.callLMStudio(prompt);
            return this.extractCodeFromResponse(response);
        } catch (error) {
            console.error('Error refactoring code:', error);
            throw error;
        }
    }

    private async callLMStudio(prompt: string): Promise<string> {
        const request: LMStudioRequest = {
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
            const response = await axios.post(`${this.baseUrl}/v1/chat/completions`, request, {
                headers: {
                    'Content-Type': 'application/json'
                },
                timeout: 30000 // 30 second timeout
            });

            const data = response.data as LMStudioResponse;
            return data.choices[0]?.message?.content || '';
        } catch (error) {
            console.error('LM Studio API error:', error);
            throw new Error(`Failed to communicate with LM Studio: ${error}`);
        }
    }

    private buildGenerationPrompt(context: CodeContext): string {
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

    private buildCompletionPrompt(context: CodeContext): string {
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

    private buildRefactoringPrompt(selectedCode: string, context: CodeContext): string {
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

    private extractCodeFromResponse(response: string): string | null {
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

    async testConnection(): Promise<boolean> {
        try {
            await axios.get(`${this.baseUrl}/v1/models`, {
                timeout: 5000
            });
            return true;
        } catch (error) {
            console.error('Connection test failed:', error);
            return false;
        }
    }
} 