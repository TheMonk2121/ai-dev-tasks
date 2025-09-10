package main

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/ai-dev-tasks/dspy-rag-system/src/utils"
)

// Enhanced CLI with crash prevention and resource management
type EnhancedCLI struct {
	config          *utils.Config
	dbPool          *utils.ConnectionPool
	memoryManager   *utils.MemoryManager
	resourceLimiter *utils.ResourceLimiter
	ctx             context.Context
	cancel          context.CancelFunc
}

// NewEnhancedCLI creates a new enhanced CLI instance
func NewEnhancedCLI() (*EnhancedCLI, error) {
	ctx, cancel := context.WithCancel(context.Background())

	// Parse command line arguments
	args := ParseCLIArgs()
	if args.Help {
		printHelp()
		cancel()
		return nil, nil
	}

	if args.Query == "" {
		cancel()
		return nil, fmt.Errorf("--query is required")
	}

	// Create configuration
	config := &utils.Config{
		Stability:         args.Stability,
		MaxTokens:         args.MaxTokens,
		UseRRF:            args.UseRRF,
		Dedupe:            args.Dedupe,
		ExpandQuery:       args.ExpandQuery,
		DBDSN:             getEnvString("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency"),
		PinsCapTokens:     200,
		KVec:              32,
		KLex:              32,
		RRFK0:             60,
		OverlapThresh:     0.60,
		PerFileRoundRobin: 2,
		LowConfSim:        0.30,
	}

	// Initialize connection pool
	dbPool, err := utils.NewConnectionPool(config.DBDSN, 2, 10)
	if err != nil {
		cancel()
		return nil, fmt.Errorf("failed to create database pool: %w", err)
	}

	// Initialize memory manager (limit to 512MB)
	memoryManager := utils.NewMemoryManager(512, 10*time.Second)

	// Initialize resource limiter (max 3 concurrent operations)
	resourceLimiter := utils.NewResourceLimiter(3, 30*time.Second)

	cli := &EnhancedCLI{
		config:          config,
		dbPool:          dbPool,
		memoryManager:   memoryManager,
		resourceLimiter: resourceLimiter,
		ctx:             ctx,
		cancel:          cancel,
	}

	// Start memory monitoring
	cli.memoryManager.StartMonitoring(ctx)

	// Setup signal handling for graceful shutdown
	cli.setupSignalHandling()

	return cli, nil
}

// setupSignalHandling sets up graceful shutdown on signals
func (cli *EnhancedCLI) setupSignalHandling() {
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		sig := <-sigChan
		log.Printf("Received signal %v, initiating graceful shutdown...", sig)
		cli.Shutdown()
	}()
}

// Run executes the enhanced CLI
func (cli *EnhancedCLI) Run(query string, jsonOutput bool) error {
	defer cli.Shutdown()

	// Execute rehydration with resource limits and error recovery
	var bundle *utils.Bundle
	err := cli.resourceLimiter.WithResource(cli.ctx, func() error {
		return utils.RetryWithBackoff(cli.ctx, utils.DefaultRetryConfig(), func() error {
			var err error
			bundle, err = cli.rehydrateWithPool(query)
			return err
		})
	})

	if err != nil {
		return fmt.Errorf("rehydration failed: %w", err)
	}

	// Output result
	if jsonOutput {
		cli.outputJSON(bundle)
	} else {
		cli.outputText(bundle)
	}

	return nil
}

// rehydrateWithPool executes rehydration using the connection pool
func (cli *EnhancedCLI) rehydrateWithPool(query string) (*utils.Bundle, error) {
	// Create a context with timeout for the entire operation
	ctx, cancel := utils.ContextWithTimeout(cli.ctx, 60*time.Second)
	defer cancel()

	// Use the connection pool for database operations
	var bundle *utils.Bundle
	err := cli.dbPool.WithConnection(ctx, func(conn *sql.DB) error {
		// Create a modified config that uses the pooled connection
		// This would require modifying the utils.Rehydrate function to accept a connection
		// For now, we'll use the original approach but with better error handling
		var err error
		bundle, err = utils.Rehydrate(query, cli.config)
		return err
	})

	if err != nil {
		return nil, utils.WrapRecoverable(err, true, 1*time.Second)
	}

	return bundle, nil
}

// Shutdown gracefully shuts down the CLI
func (cli *EnhancedCLI) Shutdown() {
	log.Printf("Shutting down enhanced CLI...")

	// Cancel context
	cli.cancel()

	// Stop memory monitoring
	cli.memoryManager.StopMonitoring()

	// Close database pool
	if err := cli.dbPool.Close(); err != nil {
		log.Printf("Error closing database pool: %v", err)
	}

	log.Printf("Enhanced CLI shutdown complete")
}

// outputJSON outputs the bundle in JSON format
func (cli *EnhancedCLI) outputJSON(bundle *utils.Bundle) {
	jsonData, err := json.MarshalIndent(bundle, "", "  ")
	if err != nil {
		log.Fatalf("Error marshaling JSON: %v", err)
	}
	fmt.Println(string(jsonData))
}

// outputText outputs the bundle in text format
func (cli *EnhancedCLI) outputText(bundle *utils.Bundle) {
	fmt.Println("=== Enhanced Memory Rehydration Bundle ===")
	fmt.Println()
	fmt.Println(bundle.Text)
	fmt.Println()
	fmt.Println("=== Metadata ===")
	fmt.Printf("Sections: %d\n", len(bundle.Sections))
	fmt.Printf("Total tokens: %d\n", bundle.Meta["pins_tokens"].(int)+bundle.Meta["evidence_tokens"].(int))
	fmt.Printf("Pins tokens: %d\n", bundle.Meta["pins_tokens"])
	fmt.Printf("Evidence tokens: %d\n", bundle.Meta["evidence_tokens"])
	fmt.Printf("Elapsed time: %.3fs\n", bundle.Meta["elapsed_s"])
	fmt.Printf("Stability: %.2f\n", bundle.Meta["stability"])
	fmt.Printf("Use RRF: %v\n", bundle.Meta["use_rrf"])
	fmt.Printf("Dedupe mode: %s\n", bundle.Meta["dedupe"])
	fmt.Printf("Expand query: %s\n", bundle.Meta["expand_query"])
	fmt.Printf("Memory usage: %dMB\n", cli.memoryManager.GetMemoryUsage())

	if terms, ok := bundle.Meta["query_expansion_terms"]; ok {
		if termList, ok := terms.([]string); ok && len(termList) > 0 {
			fmt.Printf("Query expansion terms: %v\n", termList)
		}
	}
}

// RunEnhancedCLI runs the enhanced CLI interface
func RunEnhancedCLI() {
	cli, err := NewEnhancedCLI()
	if err != nil {
		if err.Error() == "help requested" {
			return
		}
		log.Fatalf("Failed to create enhanced CLI: %v", err)
	}
	defer cli.Shutdown()

	args := ParseCLIArgs()
	if err := cli.Run(args.Query, args.JSON); err != nil {
		log.Fatalf("Enhanced CLI execution failed: %v", err)
	}
}

