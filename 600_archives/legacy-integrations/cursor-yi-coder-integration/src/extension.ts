import * as vscode from 'vscode';
import { YiCoderClient } from './yiCoderClient';
import { ContextManager } from './contextManager';

export function activate(context: vscode.ExtensionContext) {
    console.log('Yi-Coder Integration extension is now active!');

    // Initialize components
    const yiCoderClient = new YiCoderClient();
    const contextManager = new ContextManager();

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
        } catch (error) {
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
        } catch (error) {
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
        } catch (error) {
            vscode.window.showErrorMessage(`Error refactoring code: ${error}`);
        }
    });

    context.subscriptions.push(generateCodeCommand, completeCodeCommand, refactorCodeCommand);
}

export function deactivate() {
    console.log('Yi-Coder Integration extension is now deactivated!');
} 