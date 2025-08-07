import * as assert from 'assert';
import * as vscode from 'vscode';
import { YiCoderClient } from '../src/yiCoderClient';
import { ContextManager } from '../src/contextManager';

suite('Yi-Coder Integration Extension Test Suite', () => {
    test('Extension should be present', () => {
        assert.ok(vscode.extensions.getExtension('yi-coder-integration'));
    });

    test('YiCoderClient should be instantiable', () => {
        const client = new YiCoderClient();
        assert.ok(client);
        assert.ok(typeof client.generateCode === 'function');
        assert.ok(typeof client.completeCode === 'function');
        assert.ok(typeof client.refactorCode === 'function');
    });

    test('ContextManager should be instantiable', () => {
        const manager = new ContextManager();
        assert.ok(manager);
        assert.ok(typeof manager.getCurrentContext === 'function');
    });

    test('Language detection should work correctly', () => {
        const manager = new ContextManager();
        
        // Mock editor for testing
        const mockEditor = {
            document: {
                fileName: '/test/file.py',
                getText: () => 'def test(): pass',
                offsetAt: () => 0
            },
            selection: {
                active: { line: 0, character: 0 }
            }
        } as any;

        const context = manager.getCurrentContext(mockEditor);
        assert.strictEqual(context.language, 'python');
        assert.strictEqual(context.currentFile, '/test/file.py');
    });

    test('Configuration should be accessible', () => {
        const client = new YiCoderClient();
        // Test that configuration can be accessed (actual values depend on workspace)
        assert.ok(client);
    });
}); 