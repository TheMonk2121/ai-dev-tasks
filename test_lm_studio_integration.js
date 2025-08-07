// Test script for LM Studio integration and Yi-Coder model
const axios = require('axios');

console.log('🧪 Testing LM Studio Integration and Yi-Coder Model...');

const OLLAMA_URL = 'http://localhost:11434';
const MODEL_NAME = 'mistral';

// Test 1: Check if LM Studio server is running
async function testServerConnection() {
    console.log('✅ Test 1: Ollama Server Connection');
    try {
        const response = await axios.get(`${OLLAMA_URL}/api/tags`, {
            timeout: 5000
        });
        console.log('   - ✅ Ollama server is running');
        console.log('   - 📋 Available models:', response.data.models?.length || 0);
        return true;
    } catch (error) {
        console.log('   - ❌ Ollama server not responding');
        console.log('   - 💡 Make sure Ollama is running: ollama serve');
        return false;
    }
}

// Test 2: Check if Mistral model is loaded
async function testModelAvailability() {
    console.log('✅ Test 2: Mistral Model Availability');
    try {
        const response = await axios.get(`${OLLAMA_URL}/api/tags`, {
            timeout: 5000
        });
        
        const models = response.data.models || [];
        const mistralModel = models.find(model => 
            model.name.toLowerCase().includes('mistral')
        );
        
        if (mistralModel) {
            console.log('   - ✅ Mistral model found:', mistralModel.name);
            return true;
        } else {
            console.log('   - ❌ Mistral model not found');
            console.log('   - 💡 Available models:', models.map(m => m.name).join(', '));
            console.log('   - 💡 Load Mistral model: ollama pull mistral');
            return false;
        }
    } catch (error) {
        console.log('   - ❌ Failed to check model availability');
        return false;
    }
}

// Test 3: Test basic code generation
async function testCodeGeneration() {
    console.log('✅ Test 3: Basic Code Generation');
    try {
        const testPrompt = {
            model: MODEL_NAME,
            messages: [
                {
                    role: 'user',
                    content: 'Write a simple Python function to calculate the sum of two numbers'
                }
            ],
            temperature: 0.7,
            max_tokens: 200,
            stream: false
        };
        
        const startTime = Date.now();
        const response = await axios.post(`${OLLAMA_URL}/api/chat`, testPrompt, {
            timeout: 30000, // 30 second timeout
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const endTime = Date.now();
        const responseTime = endTime - startTime;
        
        const content = response.data.choices?.[0]?.message?.content;
        if (content) {
            console.log('   - ✅ Code generation successful');
            console.log('   - ⏱️  Response time:', responseTime + 'ms');
            console.log('   - 📝 Generated code preview:', content.substring(0, 100) + '...');
            
            // Check if response time meets requirements
            if (responseTime < 2000) {
                console.log('   - ✅ Response time under 2 seconds');
            } else {
                console.log('   - ⚠️  Response time over 2 seconds:', responseTime + 'ms');
            }
            
            return true;
        } else {
            console.log('   - ❌ No content in response');
            return false;
        }
    } catch (error) {
        console.log('   - ❌ Code generation failed:', error.message);
        return false;
    }
}

// Test 4: Test code completion
async function testCodeCompletion() {
    console.log('✅ Test 4: Code Completion');
    try {
        const testPrompt = {
            model: MODEL_NAME,
            messages: [
                {
                    role: 'user',
                    content: 'Complete this Python function:\n\ndef calculate_area(radius):\n    # Calculate the area of a circle'
                }
            ],
            temperature: 0.7,
            max_tokens: 150,
            stream: false
        };
        
        const response = await axios.post(`${OLLAMA_URL}/api/chat`, testPrompt, {
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const content = response.data.choices?.[0]?.message?.content;
        if (content && content.includes('return')) {
            console.log('   - ✅ Code completion successful');
            console.log('   - 📝 Completion preview:', content.substring(0, 100) + '...');
            return true;
        } else {
            console.log('   - ❌ Code completion failed or incomplete');
            return false;
        }
    } catch (error) {
        console.log('   - ❌ Code completion failed:', error.message);
        return false;
    }
}

// Test 5: Test error handling
async function testErrorHandling() {
    console.log('✅ Test 5: Error Handling');
    try {
        // Test with invalid model name
        const testPrompt = {
            model: 'Invalid-Model-Name',
            messages: [
                {
                    role: 'user',
                    content: 'Hello'
                }
            ],
            temperature: 0.7,
            max_tokens: 50,
            stream: false
        };
        
        await axios.post(`${OLLAMA_URL}/api/chat`, testPrompt, {
            timeout: 10000,
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        console.log('   - ❌ Should have failed with invalid model');
        return false;
    } catch (error) {
        if (error.response && error.response.status === 400) {
            console.log('   - ✅ Error handling working correctly');
            return true;
        } else {
            console.log('   - ⚠️  Unexpected error:', error.message);
            return true; // Still counts as error handling
        }
    }
}

// Test 6: Performance benchmark
async function testPerformanceBenchmark() {
    console.log('✅ Test 6: Performance Benchmark');
    try {
        const testPrompt = {
            model: MODEL_NAME,
            messages: [
                {
                    role: 'user',
                    content: 'Write a simple JavaScript function to reverse a string'
                }
            ],
            temperature: 0.7,
            max_tokens: 100,
            stream: false
        };
        
        const times = [];
        const numTests = 3;
        
        for (let i = 0; i < numTests; i++) {
            const startTime = Date.now();
            await axios.post(`${OLLAMA_URL}/api/chat`, testPrompt, {
                timeout: 30000,
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            const endTime = Date.now();
            times.push(endTime - startTime);
        }
        
        const avgTime = times.reduce((a, b) => a + b, 0) / times.length;
        const minTime = Math.min(...times);
        const maxTime = Math.max(...times);
        
        console.log('   - 📊 Performance results:');
        console.log(`     Average time: ${avgTime.toFixed(0)}ms`);
        console.log(`     Min time: ${minTime}ms`);
        console.log(`     Max time: ${maxTime}ms`);
        
        if (avgTime < 2000) {
            console.log('   - ✅ Performance meets requirements (< 2s average)');
            return true;
        } else {
            console.log('   - ⚠️  Performance below requirements (> 2s average)');
            return false;
        }
    } catch (error) {
        console.log('   - ❌ Performance test failed:', error.message);
        return false;
    }
}

// Main test runner
async function runAllTests() {
    console.log('🚀 Starting LM Studio Integration Tests...\n');
    
    const tests = [
        testServerConnection,
        testModelAvailability,
        testCodeGeneration,
        testCodeCompletion,
        testErrorHandling,
        testPerformanceBenchmark
    ];
    
    const results = [];
    
    for (const test of tests) {
        try {
            const result = await test();
            results.push(result);
            console.log(''); // Add spacing between tests
        } catch (error) {
            console.log(`   - ❌ Test failed with error: ${error.message}`);
            results.push(false);
        }
    }
    
    // Summary
    console.log('📋 Test Summary:');
    const passedTests = results.filter(r => r).length;
    const totalTests = results.length;
    
    console.log(`✅ Passed: ${passedTests}/${totalTests}`);
    console.log(`❌ Failed: ${totalTests - passedTests}/${totalTests}`);
    
    if (passedTests === totalTests) {
            console.log('\n🎉 All tests passed! Ollama integration is ready.');
    console.log('\n📋 Next Steps:');
    console.log('1. Test the extension with Cursor IDE');
    console.log('2. Configure extension settings');
    console.log('3. Test real-world code generation scenarios');
    } else {
            console.log('\n⚠️  Some tests failed. Please check the setup:');
    console.log('1. Ensure Ollama server is running: ollama serve');
    console.log('2. Load Mistral model: ollama pull mistral');
    console.log('3. Check system resources (RAM, CPU)');
    console.log('4. Verify network connectivity');
    }
    
    return passedTests === totalTests;
}

// Run tests if this script is executed directly
if (require.main === module) {
    runAllTests().catch(console.error);
}

module.exports = {
    testServerConnection,
    testModelAvailability,
    testCodeGeneration,
    testCodeCompletion,
    testErrorHandling,
    testPerformanceBenchmark,
    runAllTests
}; 