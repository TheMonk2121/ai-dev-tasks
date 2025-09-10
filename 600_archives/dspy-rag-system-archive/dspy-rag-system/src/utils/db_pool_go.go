package utils

import (
	"context"
	"database/sql"
	"fmt"
	"log"
	"sync"
	"time"

	_ "github.com/lib/pq"
)

// ConnectionPool manages database connections with health checks and timeouts
type ConnectionPool struct {
	dsn          string
	pool         chan *sql.DB
	maxConns     int
	minConns     int
	mu           sync.RWMutex
	closed       bool
	healthTicker *time.Ticker
	stopHealth   chan bool
}

// NewConnectionPool creates a new connection pool with health monitoring
func NewConnectionPool(dsn string, minConns, maxConns int) (*ConnectionPool, error) {
	pool := &ConnectionPool{
		dsn:        dsn,
		pool:       make(chan *sql.DB, maxConns),
		maxConns:   maxConns,
		minConns:   minConns,
		stopHealth: make(chan bool),
	}

	// Initialize minimum connections
	for i := 0; i < minConns; i++ {
		conn, err := pool.createConnection()
		if err != nil {
			pool.Close()
			return nil, fmt.Errorf("failed to create initial connection: %w", err)
		}
		pool.pool <- conn
	}

	// Start health monitoring
	pool.startHealthMonitoring()

	return pool, nil
}

// GetConnection returns a healthy database connection
func (p *ConnectionPool) GetConnection(ctx context.Context) (*sql.DB, error) {
	p.mu.RLock()
	if p.closed {
		p.mu.RUnlock()
		return nil, fmt.Errorf("connection pool is closed")
	}
	p.mu.RUnlock()

	select {
	case conn := <-p.pool:
		// Health check the connection
		if err := p.healthCheck(conn); err != nil {
			// Connection is unhealthy, create a new one
			conn.Close()
			return p.createConnection()
		}
		return conn, nil
	case <-ctx.Done():
		return nil, ctx.Err()
	default:
		// Pool is empty, create a new connection if under limit
		return p.createConnection()
	}
}

// ReturnConnection returns a connection to the pool
func (p *ConnectionPool) ReturnConnection(conn *sql.DB) {
	p.mu.RLock()
	if p.closed {
		p.mu.RUnlock()
		conn.Close()
		return
	}
	p.mu.RUnlock()

	select {
	case p.pool <- conn:
		// Connection returned to pool
	default:
		// Pool is full, close the connection
		conn.Close()
	}
}

// createConnection creates a new database connection with timeouts
func (p *ConnectionPool) createConnection() (*sql.DB, error) {
	conn, err := sql.Open("postgres", p.dsn)
	if err != nil {
		return nil, fmt.Errorf("failed to open database connection: %w", err)
	}

	// Set connection timeouts and limits
	conn.SetMaxOpenConns(1)
	conn.SetMaxIdleConns(1)
	conn.SetConnMaxLifetime(30 * time.Minute)
	conn.SetConnMaxIdleTime(5 * time.Minute)

	// Test the connection
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := conn.PingContext(ctx); err != nil {
		conn.Close()
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	return conn, nil
}

// healthCheck verifies a connection is still healthy
func (p *ConnectionPool) healthCheck(conn *sql.DB) error {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	return conn.PingContext(ctx)
}

// startHealthMonitoring periodically checks connection health
func (p *ConnectionPool) startHealthMonitoring() {
	p.healthTicker = time.NewTicker(30 * time.Second)
	go func() {
		for {
			select {
			case <-p.healthTicker.C:
				p.performHealthCheck()
			case <-p.stopHealth:
				return
			}
		}
	}()
}

// performHealthCheck checks all connections in the pool
func (p *ConnectionPool) performHealthCheck() {
	p.mu.RLock()
	if p.closed {
		p.mu.RUnlock()
		return
	}
	p.mu.RUnlock()

	// Check connections in pool
	poolSize := len(p.pool)
	for i := 0; i < poolSize; i++ {
		select {
		case conn := <-p.pool:
			if err := p.healthCheck(conn); err != nil {
				log.Printf("Unhealthy connection detected, closing: %v", err)
				conn.Close()
			} else {
				p.pool <- conn
			}
		default:
			break
		}
	}
}

// Close shuts down the connection pool gracefully
func (p *ConnectionPool) Close() error {
	p.mu.Lock()
	defer p.mu.Unlock()

	if p.closed {
		return nil
	}

	p.closed = true

	// Stop health monitoring
	if p.healthTicker != nil {
		p.healthTicker.Stop()
	}
	close(p.stopHealth)

	// Close all connections
	close(p.pool)
	for conn := range p.pool {
		conn.Close()
	}

	return nil
}

// WithConnection executes a function with a database connection
func (p *ConnectionPool) WithConnection(ctx context.Context, fn func(*sql.DB) error) error {
	conn, err := p.GetConnection(ctx)
	if err != nil {
		return err
	}
	defer p.ReturnConnection(conn)

	return fn(conn)
}

