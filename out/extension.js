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
exports.deactivate = exports.activate = void 0;
const vscode = __importStar(require("vscode"));
const yiCoderClient_1 = require("./yiCoderClient");
const contextManager_1 = require("./contextManager");
function activate(context) {
    console.log('Yi-Coder Integration extension is now active!');
    // Initialize components
    const yiCoderClient = new yiCoderClient_1.YiCoderClient();
    const contextManager = new contextManager_1.ContextManager();
    // Register commands
    let generateCodeCommand = vscode.commands.registerCommand('yi-coder.generateCode', async () => {
        try {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active text editor');
                return;
            }
            const context = contextManager.getCurrentContext(editor);
            const response = await yiCoderClient.generateCode(context);
            if (response) {
                // Insert the generated code at cursor position
                await editor.edit(editBuilder => {
                    const position = editor.selection.active;
                    editBuilder.insert(position, response);
                });
                vscode.window.showInformationMessage('Code generated successfully!');
            }
        }
        catch (error) {
            vscode.window.showErrorMessage(`Error generating code: ${error}`);
        }
    });
    let completeCodeCommand = vscode.commands.registerCommand('yi-coder.completeCode', async () => {
        try {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active text editor');
                return;
            }
            const context = contextManager.getCurrentContext(editor);
            const completion = await yiCoderClient.completeCode(context);
            if (completion) {
                // Insert the completion at cursor position
                await editor.edit(editBuilder => {
                    const position = editor.selection.active;
                    editBuilder.insert(position, completion);
                });
                vscode.window.showInformationMessage('Code completed!');
            }
        }
        catch (error) {
            vscode.window.showErrorMessage(`Error completing code: ${error}`);
        }
    });
    let refactorCodeCommand = vscode.commands.registerCommand('yi-coder.refactorCode', async () => {
        try {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active text editor');
                return;
            }
            const selection = editor.selection;
            if (selection.isEmpty) {
                vscode.window.showErrorMessage('Please select code to refactor');
                return;
            }
            const selectedCode = editor.document.getText(selection);
            const context = contextManager.getCurrentContext(editor);
            const refactoredCode = await yiCoderClient.refactorCode(selectedCode, context);
            if (refactoredCode) {
                // Replace the selected code with refactored version
                await editor.edit(editBuilder => {
                    editBuilder.replace(selection, refactoredCode);
                });
                vscode.window.showInformationMessage('Code refactored successfully!');
            }
        }
        catch (error) {
            vscode.window.showErrorMessage(`Error refactoring code: ${error}`);
        }
    });
    context.subscriptions.push(generateCodeCommand, completeCodeCommand, refactorCodeCommand);
}
exports.activate = activate;
function deactivate() {
    console.log('Yi-Coder Integration extension is now deactivated!');
}
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map