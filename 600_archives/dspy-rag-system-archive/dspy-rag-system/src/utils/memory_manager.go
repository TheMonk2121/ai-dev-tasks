package utils

import (
	"context"
	"fmt"
	"log"
	"runtime"
	"sync"
	"time"
)

// MemoryManager handles memory monitoring and limits
type MemoryManager struct {
	maxMemoryMB    int64
	checkInterval  time.Duration
	mu             sync.RWMutex
	stopMonitoring chan bool
	monitoring     bool
}

// NewMemoryManager creates a new memory manager
func NewMemoryManager(maxMemoryMB int64, checkInterval time.Duration) *MemoryManager {
	return &MemoryManager{
		maxMemoryMB:    maxMemoryMB,
		checkInterval:  checkInterval,
		stopMonitoring: make(chan bool),
	}
}

// StartMonitoring begins memory monitoring
func (m *MemoryManager) StartMonitoring(ctx context.Context) {
	m.mu.Lock()
	if m.monitoring {
		m.mu.Unlock()
		return
	}
	m.monitoring = true
	m.mu.Unlock()

	go func() {
		ticker := time.NewTicker(m.checkInterval)
		defer ticker.Stop()

		for {
			select {
			case <-ticker.C:
				m.checkMemoryUsage()
			case <-m.stopMonitoring:
				return
			case <-ctx.Done():
				return
			}
		}
	}()
}

// StopMonitoring stops memory monitoring
func (m *MemoryManager) StopMonitoring() {
	m.mu.Lock()
	defer m.mu.Unlock()

	if !m.monitoring {
		return
	}

	m.monitoring = false
	close(m.stopMonitoring)
}

// checkMemoryUsage checks current memory usage and triggers GC if needed
func (m *MemoryManager) checkMemoryUsage() {
	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)

	// Convert bytes to MB
	memoryMB := int64(memStats.Alloc / 1024 / 1024)

	if memoryMB > m.maxMemoryMB {
		log.Printf("Memory usage high: %dMB (limit: %dMB), triggering GC", memoryMB, m.maxMemoryMB)
		runtime.GC()

		// Check again after GC
		runtime.ReadMemStats(&memStats)
		memoryMB = int64(memStats.Alloc / 1024 / 1024)
		log.Printf("Memory after GC: %dMB", memoryMB)
	}
}

// GetMemoryUsage returns current memory usage in MB
func (m *MemoryManager) GetMemoryUsage() int64 {
	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)
	return int64(memStats.Alloc / 1024 / 1024)
}

// ForceGC triggers garbage collection
func (m *MemoryManager) ForceGC() {
	runtime.GC()
}

// ResourceLimiter limits resource usage for operations
type ResourceLimiter struct {
	maxConcurrent int
	semaphore     chan struct{}
	timeout       time.Duration
}

// NewResourceLimiter creates a new resource limiter
func NewResourceLimiter(maxConcurrent int, timeout time.Duration) *ResourceLimiter {
	return &ResourceLimiter{
		maxConcurrent: maxConcurrent,
		semaphore:     make(chan struct{}, maxConcurrent),
		timeout:       timeout,
	}
}

// Acquire acquires a resource slot
func (rl *ResourceLimiter) Acquire(ctx context.Context) error {
	select {
	case rl.semaphore <- struct{}{}:
		return nil
	case <-ctx.Done():
		return ctx.Err()
	case <-time.After(rl.timeout):
		return fmt.Errorf("resource acquisition timeout")
	}
}

// Release releases a resource slot
func (rl *ResourceLimiter) Release() {
	select {
	case <-rl.semaphore:
	default:
		// This shouldn't happen in normal operation
		log.Printf("Warning: releasing resource that wasn't acquired")
	}
}

// WithResource executes a function with resource limits
func (rl *ResourceLimiter) WithResource(ctx context.Context, fn func() error) error {
	if err := rl.Acquire(ctx); err != nil {
		return err
	}
	defer rl.Release()

	return fn()
}

// ContextWithTimeout creates a context with timeout
func ContextWithTimeout(parent context.Context, timeout time.Duration) (context.Context, context.CancelFunc) {
	return context.WithTimeout(parent, timeout)
}

// ContextWithDeadline creates a context with deadline
func ContextWithDeadline(parent context.Context, deadline time.Time) (context.Context, context.CancelFunc) {
	return context.WithDeadline(parent, deadline)
}

