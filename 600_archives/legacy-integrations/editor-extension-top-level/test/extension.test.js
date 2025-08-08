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
const assert = __importStar(require("assert"));
const vscode = __importStar(require("vscode"));
const yiCoderClient_1 = require("../src/yiCoderClient");
const contextManager_1 = require("../src/contextManager");
suite('Yi-Coder Integration Extension Test Suite', () => {
    test('Extension should be present', () => {
        assert.ok(vscode.extensions.getExtension('yi-coder-integration'));
    });
    test('YiCoderClient should be instantiable', () => {
        const client = new yiCoderClient_1.YiCoderClient();
        assert.ok(client);
        assert.ok(typeof client.generateCode === 'function');
        assert.ok(typeof client.completeCode === 'function');
        assert.ok(typeof client.refactorCode === 'function');
    });
    test('ContextManager should be instantiable', () => {
        const manager = new contextManager_1.ContextManager();
        assert.ok(manager);
        assert.ok(typeof manager.getCurrentContext === 'function');
    });
    test('Language detection should work correctly', () => {
        const manager = new contextManager_1.ContextManager();
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
        };
        const context = manager.getCurrentContext(mockEditor);
        assert.strictEqual(context.language, 'python');
        assert.strictEqual(context.currentFile, '/test/file.py');
    });
    test('Configuration should be accessible', () => {
        const client = new yiCoderClient_1.YiCoderClient();
        // Test that configuration can be accessed (actual values depend on workspace)
        assert.ok(client);
    });
});
//# sourceMappingURL=extension.test.js.map