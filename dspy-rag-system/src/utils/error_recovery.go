package utils

import (
	"context"
	"fmt"
	"log"
	"runtime"
	"time"
)

// RecoverableError represents an error that can be retried
type RecoverableError struct {
	Err        error
	Retryable  bool
	RetryAfter time.Duration
}

func (e *RecoverableError) Error() string {
	return e.Err.Error()
}

// RetryConfig holds retry configuration
type RetryConfig struct {
	MaxAttempts int
	BaseDelay   time.Duration
	MaxDelay    time.Duration
	Multiplier  float64
}

// DefaultRetryConfig returns sensible default retry settings
func DefaultRetryConfig() *RetryConfig {
	return &RetryConfig{
		MaxAttempts: 3,
		BaseDelay:   100 * time.Millisecond,
		MaxDelay:    5 * time.Second,
		Multiplier:  2.0,
	}
}

// RetryWithBackoff executes a function with exponential backoff retry
func RetryWithBackoff(ctx context.Context, config *RetryConfig, fn func() error) error {
	if config == nil {
		config = DefaultRetryConfig()
	}

	var lastErr error
	delay := config.BaseDelay

	for attempt := 0; attempt < config.MaxAttempts; attempt++ {
		// Check context cancellation
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
		}

		// Execute function with panic recovery
		err := withPanicRecovery(fn)
		if err == nil {
			return nil
		}

		lastErr = err

		// Check if error is retryable
		if recoverableErr, ok := err.(*RecoverableError); ok && !recoverableErr.Retryable {
			return err
		}

		// Don't retry on last attempt
		if attempt == config.MaxAttempts-1 {
			break
		}

		// Wait before retry
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-time.After(delay):
		}

		// Exponential backoff
		delay = time.Duration(float64(delay) * config.Multiplier)
		if delay > config.MaxDelay {
			delay = config.MaxDelay
		}
	}

	return fmt.Errorf("operation failed after %d attempts: %w", config.MaxAttempts, lastErr)
}

// withPanicRecovery executes a function and recovers from panics
func withPanicRecovery(fn func() error) (err error) {
	defer func() {
		if r := recover(); r != nil {
			// Log panic details
			buf := make([]byte, 4096)
			n := runtime.Stack(buf, false)
			log.Printf("Panic recovered: %v\nStack trace:\n%s", r, string(buf[:n]))

			// Convert panic to error
			err = fmt.Errorf("panic recovered: %v", r)
		}
	}()

	return fn()
}

// GracefulShutdown handles graceful shutdown of the Go CLI
func GracefulShutdown(ctx context.Context, cleanup func() error) error {
	// Create a channel to receive shutdown signals
	shutdown := make(chan error, 1)

	// Start cleanup in goroutine
	go func() {
		shutdown <- cleanup()
	}()

	// Wait for context cancellation or cleanup completion
	select {
	case <-ctx.Done():
		log.Printf("Shutdown requested: %v", ctx.Err())
		// Give cleanup a chance to complete
		select {
		case err := <-shutdown:
			if err != nil {
				log.Printf("Cleanup error: %v", err)
			}
		case <-time.After(5 * time.Second):
			log.Printf("Cleanup timeout, forcing shutdown")
		}
		return ctx.Err()
	case err := <-shutdown:
		return err
	}
}

// IsRetryableError checks if an error should be retried
func IsRetryableError(err error) bool {
	if err == nil {
		return false
	}

	// Check for specific retryable error types
	switch {
	case err == context.DeadlineExceeded:
		return true
	case err == context.Canceled:
		return false
	default:
		// Check if it's a recoverable error
		if recoverableErr, ok := err.(*RecoverableError); ok {
			return recoverableErr.Retryable
		}
		return false
	}
}

// WrapRecoverable wraps an error as retryable
func WrapRecoverable(err error, retryable bool, retryAfter time.Duration) *RecoverableError {
	return &RecoverableError{
		Err:        err,
		Retryable:  retryable,
		RetryAfter: retryAfter,
	}
}

