// Simple LM Studio status checker
const axios = require('axios');

console.log('🔍 Checking Ollama Status...\n');

async function checkStatus() {
    try {
        // Check server connection
        const response = await axios.get('http://localhost:11434/api/tags', {
            timeout: 3000
        });
        
        console.log('✅ Ollama server is running');
        console.log(`📋 Available models: ${response.data.models?.length || 0}`);
        
        // Check for Mistral model
        const models = response.data.models || [];
        const mistralModel = models.find(model => 
            model.name.toLowerCase().includes('mistral')
        );
        
        if (mistralModel) {
            console.log(`✅ Mistral model found: ${mistralModel.name}`);
            console.log('\n🎉 Ollama is ready for integration!');
            console.log('\n📋 Next Steps:');
            console.log('1. Run: node test_lm_studio_integration.js');
            console.log('2. Test the extension with Cursor IDE');
            console.log('3. Configure extension settings');
            return true;
        } else {
            console.log('❌ Mistral model not found');
            console.log('💡 Available models:', models.map(m => m.name).join(', '));
            console.log('\n📋 To complete setup:');
            console.log('1. Load Mistral model: ollama pull mistral');
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