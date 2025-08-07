// Simple LM Studio status checker
const axios = require('axios');

console.log('🔍 Checking Ollama Status...\n');

async function checkStatus() {
    try {
        // Check server connection
        const response = await axios.get('http://localhost:1234/v1/models', {
            timeout: 3000
        });
        
        console.log('✅ LM Studio server is running');
        console.log(`📋 Available models: ${response.data.data?.length || 0}`);
        
        // Check for Yi-Coder model
        const models = response.data.data || [];
        const yiCoderModel = models.find(model => 
            model.id.toLowerCase().includes('yi-coder') || 
            model.id.toLowerCase().includes('yi_coder')
        );
        
        if (yiCoderModel) {
            console.log(`✅ Yi-Coder model found: ${yiCoderModel.id}`);
            console.log('\n🎉 LM Studio is ready for integration!');
            console.log('\n📋 Next Steps:');
            console.log('1. Run: node test_lm_studio_integration.js');
            console.log('2. Test the extension with Cursor IDE');
            console.log('3. Configure extension settings');
            return true;
        } else {
            console.log('❌ Yi-Coder model not found');
            console.log('💡 Available models:', models.map(m => m.id).join(', '));
            console.log('\n📋 To complete setup:');
            console.log('1. Load Yi-Coder-9B-Chat-Q6_K model in LM Studio');
            console.log('2. Run this check again');
            return false;
        }
        
    } catch (error) {
        console.log('❌ Ollama server not responding');
        console.log('\n📋 To start Ollama server:');
        console.log('1. Open terminal');
        console.log('2. Run: ollama serve');
        console.log('3. Run this check again');
        return false;
    }
}

// Run the check
checkStatus().catch(console.error); 