import * as vscode from 'vscode';
import { CodeContext } from './yiCoderClient';
import * as path from 'path';

export class ContextManager {
    private conversationHistory: Map<string, string[]> = new Map();

    getCurrentContext(editor: vscode.TextEditor): CodeContext {
        const document = editor.document;
        const position = editor.selection.active;
        const filePath = document.fileName;
        const language = this.getLanguageFromFile(filePath);
        
        // Get file content
        const fileContent = document.getText();
        
        // Get cursor position as character offset
        const cursorPosition = document.offsetAt(position);
        
        // Get project structure if available
        const projectStructure = this.getProjectStructure(filePath);
        
        return {
            currentFile: filePath,
            cursorPosition: cursorPosition,
            fileContent: fileContent,
            language: language,
            projectStructure: projectStructure
        };
    }

    private getLanguageFromFile(filePath: string): string {
        const extension = path.extname(filePath).toLowerCase();
        
        const languageMap: { [key: string]: string } = {
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.py': 'python',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
            '.json': 'json',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.sql': 'sql',
            '.sh': 'bash',
            '.ps1': 'powershell'
        };
        
        return languageMap[extension] || 'text';
    }

    private getProjectStructure(filePath: string): string | undefined {
        try {
            const workspaceFolder = vscode.workspace.getWorkspaceFolder(vscode.Uri.file(filePath));
            if (!workspaceFolder) {
                return undefined;
            }

            const workspacePath = workspaceFolder.uri.fsPath;
            const relativePath = path.relative(workspacePath, filePath);
            
            // Get a simplified project structure
            return this.getSimplifiedProjectStructure(workspacePath, relativePath);
        } catch (error) {
            console.error('Error getting project structure:', error);
            return undefined;
        }
    }

    private getSimplifiedProjectStructure(workspacePath: string, relativePath: string): string {
        try {
            const fs = require('fs');
            const path = require('path');
            
            const structure: string[] = [];
            const maxDepth = 3; // Limit depth to avoid too much context
            
            const addToStructure = (dirPath: string, depth: number) => {
                if (depth > maxDepth) return;
                
                try {
                    const items = fs.readdirSync(dirPath);
                    for (const item of items) {
                        const fullPath = path.join(dirPath, item);
                        const stat = fs.statSync(fullPath);
                        
                        if (stat.isDirectory()) {
                            structure.push(`${'  '.repeat(depth)}📁 ${item}/`);
                            addToStructure(fullPath, depth + 1);
                        } else if (stat.isFile() && this.isRelevantFile(item)) {
                            structure.push(`${'  '.repeat(depth)}📄 ${item}`);
                        }
                    }
                } catch (error) {
                    // Ignore permission errors or other issues
                }
            };
            
            addToStructure(workspacePath, 0);
            
            return `Project Structure:\n${structure.join('\n')}\nCurrent File: ${relativePath}`;
        } catch (error) {
            return `Current File: ${relativePath}`;
        }
    }

    private isRelevantFile(filename: string): boolean {
        const relevantExtensions = [
            '.js', '.ts', '.jsx', '.tsx', '.py', '.java', '.cpp', '.c', '.cs',
            '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.html',
            '.css', '.scss', '.sass', '.json', '.xml', '.yaml', '.yml', '.md',
            '.sql', '.sh', '.ps1', '.vue', '.svelte', '.r', '.m', '.pl', '.lua'
        ];
        
        const extension = path.extname(filename).toLowerCase();
        return relevantExtensions.includes(extension);
    }

    addToConversationHistory(filePath: string, message: string): void {
        if (!this.conversationHistory.has(filePath)) {
            this.conversationHistory.set(filePath, []);
        }
        
        const history = this.conversationHistory.get(filePath)!;
        history.push(message);
        
        // Keep only the last 10 messages to avoid context overflow
        if (history.length > 10) {
            history.shift();
        }
    }

    getConversationHistory(filePath: string): string[] {
        return this.conversationHistory.get(filePath) || [];
    }

    clearConversationHistory(filePath?: string): void {
        if (filePath) {
            this.conversationHistory.delete(filePath);
        } else {
            this.conversationHistory.clear();
        }
    }

    getRelevantContext(editor: vscode.TextEditor, maxLines: number = 50): string {
        const document = editor.document;
        const position = editor.selection.active;
        const line = position.line;
        
        // Get lines around the cursor position
        const startLine = Math.max(0, line - Math.floor(maxLines / 2));
        const endLine = Math.min(document.lineCount - 1, line + Math.floor(maxLines / 2));
        
        const relevantLines: string[] = [];
        for (let i = startLine; i <= endLine; i++) {
            const lineText = document.lineAt(i).text;
            relevantLines.push(lineText);
        }
        
        return relevantLines.join('\n');
    }

    getFunctionContext(editor: vscode.TextEditor): string | null {
        const document = editor.document;
        const position = editor.selection.active;
        const language = this.getLanguageFromFile(document.fileName);
        
        // Simple function detection for common languages
        const functionRegex = this.getFunctionRegex(language);
        if (!functionRegex) return null;
        
        const text = document.getText();
        const lines = text.split('\n');
        const currentLine = position.line;
        
        // Find the function containing the current position
        for (let i = currentLine; i >= 0; i--) {
            const line = lines[i];
            if (functionRegex.test(line)) {
                // Found function start, collect function body
                const functionStart = i;
                let functionEnd = currentLine;
                
                // Find function end (simplified)
                for (let j = currentLine; j < lines.length; j++) {
                    if (this.isFunctionEnd(lines[j], language)) {
                        functionEnd = j;
                        break;
                    }
                }
                
                return lines.slice(functionStart, functionEnd + 1).join('\n');
            }
        }
        
        return null;
    }

    private getFunctionRegex(language: string): RegExp | null {
        const regexMap: { [key: string]: RegExp } = {
            'javascript': /^(export\s+)?(async\s+)?function\s+\w+\s*\(/,
            'typescript': /^(export\s+)?(async\s+)?function\s+\w+\s*\(/,
            'python': /^def\s+\w+\s*\(/,
            'java': /^(public|private|protected)?\s*(static\s+)?\w+\s+\w+\s*\(/,
            'cpp': /^(void|int|string|bool|auto)\s+\w+\s*\(/,
            'c': /^(void|int|char|float|double)\s+\w+\s*\(/,
            'csharp': /^(public|private|protected)?\s*(static\s+)?\w+\s+\w+\s*\(/,
            'php': /^function\s+\w+\s*\(/,
            'ruby': /^def\s+\w+/,
            'go': /^func\s+\w+\s*\(/,
            'rust': /^fn\s+\w+\s*\(/
        };
        
        return regexMap[language] || null;
    }

    private isFunctionEnd(line: string, language: string): boolean {
        const trimmed = line.trim();
        
        if (language === 'python') {
            return trimmed === '' || (trimmed[0] !== ' ' && trimmed[0] !== '\t');
        }
        
        return trimmed === '}' || trimmed === '};';
    }
} 