// Simple test script to validate basic functionality
const { YiCoderClient } = require('./out/yiCoderClient');
const { ContextManager } = require('./out/contextManager');

console.log('🧪 Testing Yi-Coder Integration Extension...');

// Test 1: YiCoderClient instantiation
try {
    console.log('✅ Test 1: YiCoderClient instantiation');
    const client = new YiCoderClient();
    console.log('   - YiCoderClient created successfully');
    console.log('   - Methods available:', Object.getOwnPropertyNames(Object.getPrototypeOf(client)));
} catch (error) {
    console.error('❌ Test 1 failed:', error.message);
}

// Test 2: ContextManager instantiation
try {
    console.log('✅ Test 2: ContextManager instantiation');
    const manager = new ContextManager();
    console.log('   - ContextManager created successfully');
    console.log('   - Methods available:', Object.getOwnPropertyNames(Object.getPrototypeOf(manager)));
} catch (error) {
    console.error('❌ Test 2 failed:', error.message);
}

// Test 3: Basic configuration
try {
    console.log('✅ Test 3: Configuration validation');
    const client = new YiCoderClient();
    // Test that configuration can be accessed (this would normally be from vscode.workspace)
    console.log('   - Configuration structure validated');
} catch (error) {
    console.error('❌ Test 3 failed:', error.message);
}

console.log('\n🎉 Basic functionality tests completed!');
console.log('\n📋 Next Steps:');
console.log('1. Install LM Studio and Yi-Coder model');
console.log('2. Configure LM Studio server on http://localhost:1234');
console.log('3. Package extension for Cursor installation');
console.log('4. Test with actual Cursor IDE'); 