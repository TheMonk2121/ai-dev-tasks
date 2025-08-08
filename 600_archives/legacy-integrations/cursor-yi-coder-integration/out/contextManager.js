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
Object.defineProperty(exports, "__esModule", { value: true });
exports.ContextManager = void 0;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
class ContextManager {
    constructor() {
        this.conversationHistory = new Map();
    }
    getCurrentContext(editor) {
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
    getLanguageFromFile(filePath) {
        const extension = path.extname(filePath).toLowerCase();
        const languageMap = {
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
    getProjectStructure(filePath) {
        try {
            const workspaceFolder = vscode.workspace.getWorkspaceFolder(vscode.Uri.file(filePath));
            if (!workspaceFolder) {
                return undefined;
            }
            const workspacePath = workspaceFolder.uri.fsPath;
            const relativePath = path.relative(workspacePath, filePath);
            // Get a simplified project structure
            return this.getSimplifiedProjectStructure(workspacePath, relativePath);
        }
        catch (error) {
            console.error('Error getting project structure:', error);
            return undefined;
        }
    }
    getSimplifiedProjectStructure(workspacePath, relativePath) {
        try {
            const fs = require('fs');
            const path = require('path');
            const structure = [];
            const maxDepth = 3; // Limit depth to avoid too much context
            const addToStructure = (dirPath, depth) => {
                if (depth > maxDepth)
                    return;
                try {
                    const items = fs.readdirSync(dirPath);
                    for (const item of items) {
                        const fullPath = path.join(dirPath, item);
                        const stat = fs.statSync(fullPath);
                        if (stat.isDirectory()) {
                            structure.push(`${'  '.repeat(depth)}📁 ${item}/`);
                            addToStructure(fullPath, depth + 1);
                        }
                        else if (stat.isFile() && this.isRelevantFile(item)) {
                            structure.push(`${'  '.repeat(depth)}📄 ${item}`);
                        }
                    }
                }
                catch (error) {
                    // Ignore permission errors or other issues
                }
            };
            addToStructure(workspacePath, 0);
            return `Project Structure:\n${structure.join('\n')}\nCurrent File: ${relativePath}`;
        }
        catch (error) {
            return `Current File: ${relativePath}`;
        }
    }
    isRelevantFile(filename) {
        const relevantExtensions = [
            '.js', '.ts', '.jsx', '.tsx', '.py', '.java', '.cpp', '.c', '.cs',
            '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.html',
            '.css', '.scss', '.sass', '.json', '.xml', '.yaml', '.yml', '.md',
            '.sql', '.sh', '.ps1', '.vue', '.svelte', '.r', '.m', '.pl', '.lua'
        ];
        const extension = path.extname(filename).toLowerCase();
        return relevantExtensions.includes(extension);
    }
    addToConversationHistory(filePath, message) {
        if (!this.conversationHistory.has(filePath)) {
            this.conversationHistory.set(filePath, []);
        }
        const history = this.conversationHistory.get(filePath);
        history.push(message);
        // Keep only the last 10 messages to avoid context overflow
        if (history.length > 10) {
            history.shift();
        }
    }
    getConversationHistory(filePath) {
        return this.conversationHistory.get(filePath) || [];
    }
    clearConversationHistory(filePath) {
        if (filePath) {
            this.conversationHistory.delete(filePath);
        }
        else {
            this.conversationHistory.clear();
        }
    }
    getRelevantContext(editor, maxLines = 50) {
        const document = editor.document;
        const position = editor.selection.active;
        const line = position.line;
        // Get lines around the cursor position
        const startLine = Math.max(0, line - Math.floor(maxLines / 2));
        const endLine = Math.min(document.lineCount - 1, line + Math.floor(maxLines / 2));
        const relevantLines = [];
        for (let i = startLine; i <= endLine; i++) {
            const lineText = document.lineAt(i).text;
            relevantLines.push(lineText);
        }
        return relevantLines.join('\n');
    }
    getFunctionContext(editor) {
        const document = editor.document;
        const position = editor.selection.active;
        const language = this.getLanguageFromFile(document.fileName);
        // Simple function detection for common languages
        const functionRegex = this.getFunctionRegex(language);
        if (!functionRegex)
            return null;
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
    getFunctionRegex(language) {
        const regexMap = {
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
    isFunctionEnd(line, language) {
        const trimmed = line.trim();
        if (language === 'python') {
            return trimmed === '' || (trimmed[0] !== ' ' && trimmed[0] !== '\t');
        }
        return trimmed === '}' || trimmed === '};';
    }
}
exports.ContextManager = ContextManager;
//# sourceMappingURL=contextManager.js.map