# PRD-B-1027: Enhanced Role Voice I/O - Advanced Voice Processing with Noise Suppression, Speaker Adaptation, and Multi-Agent Roundtable

## 📋 **Project Requirements Document**

**Backlog ID**: B-1027
**Title**: Enhanced Role Voice I/O: Advanced Voice Processing with Noise Suppression, Speaker Adaptation, and Multi-Agent Roundtable
**Score**: 9.2
**Priority**: 🔥 High
**Status**: todo
**Estimated Hours**: 20

---

## 🎯 **Executive Summary**

### **Problem Statement**
Verbal collaboration with DSPy roles is not supported; rich discussions are text-only and easily lost, slowing troubleshooting and planning. Need advanced voice processing for real-world environments with noise and multiple speakers.

### **Solution Overview**
Advanced voice interface with noise suppression and speaker adaptation that lets you speak to one or many roles, hear distinct agent voices, interrupt smoothly, and archive transcripts into the lessons/decisions loop to inform backlog prioritization.

### **Key Benefits**
- **Enhanced Voice Quality**: Hybrid noise suppression for real-world environments
- **Personalized Experience**: Speaker adaptation for frequent users
- **Multi-Agent Collaboration**: Voice-enabled roundtable discussions
- **Performance Optimized**: <100ms noise suppression, <200ms speaker adaptation
- **Local-First**: No external API dependencies, VM-safe operation

---

## 🏗️ **Technical Architecture**

### **Core Components**

#### **1. Speech-to-Text (STT)**
- **Engine**: faster-whisper (CTranslate2) with 16kHz mono
- **VAD**: WebRTC VAD with endpointing
- **Wake Word**: openWakeWord integration
- **Performance**: ≤ 800ms p50, ≤ 1500ms p90 (with noise suppression)

#### **2. Text-to-Speech (TTS)**
- **Primary**: Piper (ONNX voices)
- **Alternative**: VibeVoice (newer, high-quality)
- **Fallback**: Coqui TTS
- **Performance**: ≤ 500ms p50, ≤ 900ms p90 for 200-400 chars

#### **3. Noise Suppression (NEW)**
- **Method**: Hybrid neural network + traditional filtering
- **Real-time**: < 100ms processing latency
- **Configurable**: Sensitivity settings, fallback options
- **Libraries**: noisereduce, librosa, scipy

#### **4. Speaker Adaptation (NEW)**
- **Identification**: whisper-speaker-id or pyannote.audio
- **Learning**: Automatic adaptation for frequent users
- **Performance**: < 200ms identification + adaptation
- **Storage**: Speaker profiles and adaptation data

#### **5. Multi-Agent Integration**
- **Moderator**: Hybrid mode (addressable @role OR roundtable)
- **Selection**: Top-N by relevance with 2.2s deadline
- **Response**: ≤ 2 speakers returned, cancel stragglers

---

## 🚀 **Implementation Plan**

### **Phase 0: Enhanced Flags & Config (0.5h)**
**Objective**: Set up configuration system for enhanced features

**Tasks**:
1. **Add Environment Flags**:
   ```bash
   FEATURE_STT=off
   FEATURE_TTS=off
   FEATURE_VOICE_ROLES=off
   FEATURE_VOICE_ROUNDTABLE=off
   FEATURE_NOISE_SUPPRESSION=off
   FEATURE_SPEAKER_ADAPTATION=off
   FEATURE_VIBEVOICE_TTS=off
   ```

2. **Create Configuration Files**:
   - `voiceio.yaml` - Main voice I/O configuration
   - `voices.yaml` - Role-to-voice mapping
   - `speaker_profiles.yaml` - Speaker adaptation settings

**Deliverables**:
- Complete configuration system
- Feature flag infrastructure
- Configuration validation

### **Phase 1: Enhanced Minimal Loop (PTT + STT + TTS + Noise Suppression) (2h)**
**Objective**: Implement core voice loop with noise suppression

**Tasks**:
1. **Push-to-Talk Implementation**:
   - pynput integration for PTT capture
   - WebRTC VAD with endpointing
   - Real-time audio processing

2. **Noise Suppression Pipeline**:
   - Hybrid neural + traditional filtering
   - Real-time processing with <100ms latency
   - Configurable sensitivity settings

3. **STT Integration**:
   - faster-whisper with noise-suppressed audio
   - Performance target: ≤ 800ms turnaround

4. **TTS Integration**:
   - Piper TTS with barge-in support
   - VibeVoice alternative implementation
   - Performance target: ≤ 500ms for 200-400 chars

**Deliverables**:
- Working voice loop with noise suppression
- Performance benchmarks me
- Barge-in functionality

### **Phase 2: Speaker Adaptation & Advanced Features (2h)**
**Objective**: Implement speaker identification and adaptation

**Tasks**:
1. **Speaker Identification**:
   - whisper-speaker-id or pyannote.audio integration
   - Automatic speaker detection
   - Speaker profile creation

2. **Speaker Adaptation**:
   - Learning algorithm for frequent users
   - Personalization settings
   - Adaptation data storage

3. **Enhanced Noise Suppression**:
   - Speaker-aware processing
   - Improved accuracy for known speakers
   - Real-time adaptation

**Deliverables**:
- Speaker identification system
- Adaptation learning pipeline
- Enhanced noise suppression

### **Phase 3: Wake-Word + Barge-in Polishing (1h)**
**Objective**: Refine wake-word detection and barge-in functionality

**Tasks**:
1. **Wake-Word Integration**:
   - openWakeWord implementation
   - Smoothing and double-hit detection
   - Configurable threshold settings

2. **Barge-in Enhancement**:
   - Instant TTS cancellation
   - Smooth interruption handling
   - Performance optimization

**Deliverables**:
- Reliable wake-word detection
- Smooth barge-in functionality
- Performance optimization

### **Phase 4: Enhanced Multi-Agent Integration (1.5h)**
**Objective**: Integrate voice system with multi-agent roundtable

**Tasks**:
1. **Hybrid Moderator**:
   - Addressable routing (@role)
   - Roundtable selection by relevance
   - 2.2s deadline managemen

2. **Speaker-Aware Selection**:
   - Voice characteristic analysis
   - Agent selection optimization
   - Multi-speaker coordination

3. **Noise-Suppressed Roundtable**:
   - Enhanced communication quality
   - Better multi-agent interaction
   - Performance monitoring

**Deliverables**:
- Multi-agent voice integration
- Speaker-aware agent selection
- Enhanced roundtable communication

### **Phase 5: Advanced Features & Testing (1h)**
**Objective**: Implement advanced features and comprehensive testing

**Tasks**:
1. **Real-time Features**:
   - Live noise suppression during conversations
   - Continuous speaker adaptation
   - VibeVoice voice cloning for roles

2. **Testing Suite**:
   - Unit tests for noise suppression
   - Speaker adaptation testing
   - Feature flag rollback testing
   - Performance benchmarking

**Deliverables**:
- Advanced real-time features
- Comprehensive test suite
- Performance benchmarks

### **Phase 6: Lessons/Decisions Integration (1h)**
**Objective**: Integrate with B-1026 lessons and decisions system

**Tasks**:
1. **Transcript Storage**:
   - Enhanced metadata (noise suppression, speaker profiles)
   - Role tagging and voice identification
   - Link to runs/steps

2. **Lessons Integration**:
   - Voice session analysis
   - Decision extraction
   - Backlog prioritization input

**Deliverables**:
- Enhanced transcript storage
- Lessons integration
- Decision tracking

### **Phase 7: VM-Safe Profile (0.5h)**
**Objective**: Ensure VM-safe operation and security

**Tasks**:
1. **Security Documentation**:
   - Mode A (VM-only) defaults
   - Mode B (host mirror) optional
   - Mode C (guarded host control) with HITL approvals

2. **Privacy Protection**:
   - Secret redaction from transcripts
   - Opt-out recording flags
   - Data rotation and size caps

**Deliverables**:
- Security documentation
- Privacy protection measures
- VM-safe operation

---

## 📊 **Performance Targets**

### **Core Performance Metrics**
- **STT Latency**: ≤ 800ms p50, ≤ 1500ms p90 (with noise suppression)
- **TTS Latency**: ≤ 500ms p50, ≤ 900ms p90 (Piper/VibeVoice/Coqui)
- **Noise Suppression**: < 100ms real-time processing latency
- **Speaker Adaptation**: < 200ms identification + adaptation
- **VibeVoice TTS**: ≤ 600ms for 200-400 chars (alternative option)
- **Multi-Agent Response**: ≤ 2200ms deadline, ≤ 2 speakers returned

### **Resource Requirements**
- **CPU**: Steady within local M-series budge
- **Memory**: Optimized for 128GB RAM system
- **GPU**: No hard requirement (CPU-optimized)
- **Storage**: Minimal local storage for profiles and models

---

## 🔧 **Configuration Files**

### **voiceio.yaml**
```yaml
# Enhanced voice I/O configuration
stt:
  engine: "faster-whisper"
  model: "base.en"
  device: "auto"  # M4 Mac optimization

tts:
  primary: "piper"
  alternative: "vibevoice"
  fallback: "coqui"

noise_suppression:
  enabled: true
  method: "hybrid"  # neural + traditional
  sensitivity: 0.7
  real_time: true

speaker_adaptation:
  enabled: true
  library: "whisper-speaker-id"  # or "pyannote.audio"
  learning_rate: 0.1
  min_samples: 10

wake_word:
  engine: "openWakeWord"
  threshold: 0.5

vad:
  engine: "WebRTC"
  aggressiveness: 2
```

### **voices.yaml**
```yaml
# Enhanced voice mapping with multiple TTS options
roles:
  planner:
    piper: "en_US-lessac-medium"
    vibevoice: "planner_voice"
    coqui: "en_US-lessac-medium"
  implementer:
    piper: "en_US-lessac-medium"
    vibevoice: "implementer_voice"
    coqui: "en_US-lessac-medium"
  researcher:
    piper: "en_US-lessac-medium"
    vibevoice: "researcher_voice"
    coqui: "en_US-lessac-medium"
  coder:
    piper: "en_US-lessac-medium"
    vibevoice: "coder_voice"
    coqui: "en_US-lessac-medium"
```

### **speaker_profiles.yaml**
```yaml
# Speaker adaptation profiles
speakers:
  default:
    adaptation_enabled: false
    learning_rate: 0.1
    min_samples: 10
  user_1:
    adaptation_enabled: true
    learning_rate: 0.15
    min_samples: 5
    voice_characteristics:
      pitch: 0.8
      speed: 1.0
      clarity: 0.9
```

---

## 🛡️ **Security & Privacy**

### **Security Measures**
- **VM-Safe Default**: Mode A (VM-only control) as default
- **Host Actions**: Disabled by default, documented approval gates
- **Secret Redaction**: Basic mask list for spoken tex
- **Opt-out Recording**: Flag to disable recording entirely

### **Privacy Protection**
- **Data Rotation**: Automatic rotation and size caps
- **Local Storage**: All data stored locally, no external transmission
- **User Control**: Full control over recording and adaptation data
- **Transparency**: Clear logging of all voice processing activities

---

## 📈 **Observability & Monitoring**

### **Enhanced Metrics**
- **Per-Utterance Logging**: stt_ms, tts_ms, barge_in_count, selected_agents, replies_ms, wake_word score, noise_suppression_ms, speaker_adaptation_ms, vibevoice_ms
- **Transcript Storage**: run_id/step_idx, noise suppression settings, speaker profiles, adaptation data
- **Performance Monitoring**: noise suppression effectiveness, speaker adaptation accuracy, VibeVoice performance vs Piper

### **Integration Points**
- **B-1024**: Dual-Mode Troubleshooting (View-Only vs VM Privileged modes)
- **B-1025**: Context accuracy and retrieval
- **B-1026**: Closed-loop capture and lessons integration

---

## 🔄 **Rollback Strategy**

### **Feature Flags**
All enhanced features can be disabled via environment flags:
```bash
# Disable all enhanced features
export FEATURE_NOISE_SUPPRESSION=off
export FEATURE_SPEAKER_ADAPTATION=off
export FEATURE_VIBEVOICE_TTS=off

# Fall back to basic voice I/O
export FEATURE_STT=off
export FEATURE_TTS=off
export FEATURE_VOICE_ROLES=off
export FEATURE_VOICE_ROUNDTABLE=off
```

### **Rollback Commands**
- **Complete Rollback**: All voice features disabled, text workflows unchanged
- **Partial Rollback**: Individual features can be disabled independently
- **Performance Rollback**: Fallback to smaller models if performance issues

---

## ⚠️ **Risks & Mitigations**

### **Technical Risks**
1. **False Wake-Word Triggers**
   - **Mitigation**: Increase threshold, require double-hit, prefer PTT mode by default

2. **Latency Spikes**
   - **Mitigation**: Use smaller STT models (base.en/small.en), int8 compute, pre-render short TTS

3. **Audio Device Issues**
   - **Mitigation**: Document macOS permissions and VM audio routing

4. **Noise Suppression Quality**
   - **Mitigation**: Fallback to traditional filtering, configurable sensitivity, real-time monitoring

5. **Speaker Adaptation Accuracy**
   - **Mitigation**: Fallback to default profiles, learning rate adjustment, minimum sample requirements

6. **VibeVoice Performance**
   - **Mitigation**: Fallback to Piper, performance monitoring, alternative TTS options

### **Operational Risks**
1. **Resource Usage**
   - **Mitigation**: CPU/memory monitoring, automatic fallback to lighter models

2. **User Experience**
   - **Mitigation**: Comprehensive testing, gradual rollout, user feedback integration

---

## 🎯 **Success Criteria**

### **Functional Requirements**
- ✅ Live loop: push-to-talk and wake-word both work; barge-in interrupts TTS reliably
- ✅ STT: faster-whisper streaming with noise-suppressed audio; latency per 5-8s utterance ≤ 800ms post-endpoint on M-series
- ✅ TTS: Piper default, VibeVoice alternative, Coqui optional with per-role voices; p50 synthesis+playback < 500ms for 200-400 chars
- ✅ Noise Suppression: Hybrid neural + traditional filtering; real-time processing with <100ms latency; configurable sensitivity
- ✅ Speaker Adaptation: Automatic speaker identification and personalization; adaptation learning over time; <200ms identification + adaptation
- ✅ Roundtable: hybrid moderator routes @addressed agents or selects top-N by relevance; collects ≤2 responses within 2.2s
- ✅ Enhanced Traceability: transcripts stored with noise suppression settings, speaker profiles, and adaptation data; each reply tagged with agent role and voice used
- ✅ Flags: All feature flags default off; one-flip rollback; no impact when off
- ✅ Security: VM-safe mode available (no host control required); approval gate documented for any guarded host actions

### **Performance Requirements**
- ✅ All performance targets met or exceeded
- ✅ Resource usage within M-series budge
- ✅ No GPU hard requiremen
- ✅ Real-time processing capabilities

### **Quality Requirements**
- ✅ Comprehensive test coverage
- ✅ Feature flag rollback functionality
- ✅ Security and privacy compliance
- ✅ Documentation completeness

---

## 📚 **Dependencies**

### **Required Dependencies**
- **B-1024**: AI Assistant Computer Control System
- **B-1025**: Context accuracy and retrieval system
- **B-1026**: Lessons and decisions integration

### **Technical Dependencies**
- **faster-whisper**: STT engine with CTranslate2 optimization
- **Piper**: Primary TTS engine with ONNX voices
- **VibeVoice**: Alternative TTS engine
- **openWakeWord**: Wake-word detection
- **WebRTC VAD**: Voice activity detection
- **noisereduce**: Noise suppression library
- **librosa**: Audio processing
- **scipy**: Signal processing
- **whisper-speaker-id**: Speaker identification
- **pyannote.audio**: Alternative speaker identification

---

## 🚀 **Next Steps**

1. **RAGChecker Baseline Check**: Verify current metrics before implementation
2. **Environment Setup**: Install required dependencies and configure system
3. **Phase 0 Implementation**: Set up configuration system and feature flags
4. **Incremental Development**: Implement phases sequentially with testing
5. **Performance Validation**: Ensure all targets are me
6. **Integration Testing**: Test with existing B-1024, B-1025, B-1026 systems
7. **Documentation**: Complete implementation documentation
8. **Deployment**: Gradual rollout with monitoring

---

## 📝 **Notes**

- **Local-First Approach**: No external API dependencies, fully local operation
- **M4 Mac Optimization**: Optimized for Apple Silicon performance
- **VM-Safe Operation**: Default VM-only mode for security
- **Feature Flag Architecture**: All features can be disabled independently
- **Performance Monitoring**: Comprehensive metrics and observability
- **Rollback Capability**: Complete rollback to text-only workflows

This PRD provides complete execution guidance for implementing the enhanced B-1027 voice processing system with noise suppression, speaker adaptation, and multi-agent integration.
