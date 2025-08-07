# LM Studio Setup Guide for Yi-Coder Integration

## Prerequisites

- LM Studio installed and running
- Sufficient disk space for Yi-Coder-9B-Chat-Q6_K model (~6GB)
- At least 8GB RAM for model inference
- Stable internet connection for model download

## Step 1: LM Studio Configuration

### 1.1 Start LM Studio Server

1. Open LM Studio application
2. Go to **Local Server** tab
3. Click **Start Server** button
4. Verify server is running on `http://localhost:1234`

### 1.2 Configure Server Settings

- **Port**: 1234 (default)
- **Host**: localhost
- **Context Length**: 4096 (or higher if needed)
- **Threads**: Auto-detect or set to number of CPU cores
- **GPU Layers**: Set based on your GPU memory

## Step 2: Download Yi-Coder Model

### 2.1 Find Yi-Coder Model

1. In LM Studio, go to **Search** tab
2. Search for "Yi-Coder-9B-Chat-Q6_K"
3. Look for the model with these specifications:
   - **Model**: Yi-Coder-9B-Chat-Q6_K
   - **Format**: GGUF
   - **Size**: ~6GB
   - **Quantization**: Q6_K

### 2.2 Download Model

1. Click **Download** on the Yi-Coder model
2. Wait for download to complete (may take 10-30 minutes)
3. Verify model appears in **My Models** tab

## Step 3: Load Model in LM Studio

### 3.1 Load Model

1. Go to **My Models** tab
2. Find Yi-Coder-9B-Chat-Q6_K
3. Click **Load** button
4. Wait for model to load into memory

### 3.2 Configure Model Settings

- **Context Length**: 4096
- **Temperature**: 0.7
- **Top P**: 0.9
- **Top K**: 40
- **Repeat Penalty**: 1.1

## Step 4: Test Model Integration

### 4.1 Test Basic Inference

Use the test script to verify model is working:

```bash
# Test basic model response
curl -X POST http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Yi-Coder-9B-Chat-Q6_K",
    "messages": [
      {"role": "user", "content": "Write a simple Python function to calculate fibonacci numbers"}
    ],
    "temperature": 0.7,
    "max_tokens": 500,
    "stream": false
  }'
```

### 4.2 Expected Response

You should receive a JSON response with generated code:

```json
{
  "choices": [
    {
      "message": {
        "content": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\n# Example usage\nprint(fibonacci(10))"
      }
    }
  ]
}
```

## Step 5: Performance Optimization

### 5.1 Memory Management

- **Minimum RAM**: 8GB
- **Recommended RAM**: 16GB
- **GPU VRAM**: 6GB+ (if using GPU acceleration)

### 5.2 Response Time Optimization

- **Target**: < 2 seconds for code generation
- **Context Length**: Limit to 2048 tokens for faster responses
- **Batch Size**: 1 for real-time generation

### 5.3 Resource Monitoring

Monitor these metrics:
- **Memory Usage**: Should stay under 4GB for extension
- **CPU Usage**: Should stay under 50% during peak load
- **Response Time**: Should be under 2 seconds

## Step 6: Troubleshooting

### 6.1 Common Issues

**Server Not Starting**
- Check if port 1234 is available
- Restart LM Studio
- Check firewall settings

**Model Not Loading**
- Verify sufficient RAM (8GB+)
- Check disk space (6GB+ for model)
- Try loading with lower context length

**Slow Response Times**
- Reduce context length
- Lower temperature setting
- Close other applications
- Use GPU acceleration if available

**Memory Issues**
- Reduce context length
- Close other applications
- Restart LM Studio
- Check system memory usage

### 6.2 Error Messages

**"Connection refused"**
- LM Studio server not running
- Wrong port number
- Firewall blocking connection

**"Model not found"**
- Model not loaded in LM Studio
- Wrong model name in request
- Model file corrupted

**"Out of memory"**
- Insufficient RAM
- Context length too high
- Too many concurrent requests

## Step 7: Integration Testing

### 7.1 Test Extension Connection

Run the extension test script:

```bash
node test_lm_studio_integration.js
```

### 7.2 Verify Configuration

Check that extension can:
- Connect to LM Studio server
- Send code generation requests
- Receive and parse responses
- Handle errors gracefully

## Step 8: Production Readiness

### 8.1 Security Considerations

- **Local Processing**: All data stays on local machine
- **No External Calls**: No data transmitted to external services
- **Input Validation**: Sanitize all user inputs
- **Error Handling**: Graceful degradation on failures

### 8.2 Performance Benchmarks

- **Response Time**: < 2 seconds (95th percentile)
- **Memory Usage**: < 4GB during operation
- **CPU Usage**: < 50% during peak load
- **Concurrent Users**: Support for 1 user (local)

### 8.3 Monitoring

- **Health Checks**: Regular API endpoint checks
- **Performance Metrics**: Response time monitoring
- **Error Tracking**: Failed request logging
- **Resource Usage**: Memory and CPU monitoring

## Next Steps

After completing this setup:

1. **Test Basic Integration**: Verify extension can communicate with LM Studio
2. **Performance Testing**: Ensure response times meet requirements
3. **Error Handling**: Test graceful degradation scenarios
4. **Documentation**: Update setup instructions based on findings

## Support

For issues with LM Studio setup:
- Check LM Studio documentation
- Verify system requirements
- Test with simpler models first
- Contact LM Studio support if needed 