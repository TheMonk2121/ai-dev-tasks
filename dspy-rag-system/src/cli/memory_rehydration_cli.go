package main

import (
	"context"
	"database/sql"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"os"
	"sort"
	"strings"
	"time"

	"github.com/ai-dev-tasks/dspy-rag-system/src/utils"
	_ "github.com/lib/pq"
)

// Bundle represents a memory rehydration bundle
type Bundle struct {
	Text     string                 `json:"text"`
	Sections []Section              `json:"sections"`
	Meta     map[string]interface{} `json:"meta"`
}

// Section represents a section within a bundle
type Section struct {
	Kind      string  `json:"kind"`  // "pin" | "anchor" | "span"
	Title     string  `json:"title"` // e.g., anchor_key or label
	Content   string  `json:"content"`
	Citation  string  `json:"citation"`
	Tokens    int     `json:"tokens"`
	File      string  `json:"file"`
	Path      string  `json:"path"`
	Start     int     `json:"start"`
	End       int     `json:"end"`
	IsAnchor  bool    `json:"is_anchor"`
	AnchorKey string  `json:"anchor_key"`
	Score     float64 `json:"score"`
	Sim       float64 `json:"sim"`
}

// SearchResult represents a search result from the database
type SearchResult struct {
	ID         int     `json:"id"`
	Content    string  `json:"content"`
	File       string  `json:"file"`
	Path       string  `json:"path"`
	Start      int     `json:"start"`
	End        int     `json:"end"`
	IsAnchor   bool    `json:"is_anchor"`
	AnchorKey  string  `json:"anchor_key"`
	Score      float64 `json:"score"`
	Sim        float64 `json:"sim"`
	SearchType string  `json:"search_type"`
}

// Configuration holds the rehydration configuration
type Config struct {
	Stability         float64
	MaxTokens         int
	UseRRF            bool
	Dedupe            string
	ExpandQuery       string
	DBDSN             string
	PinsCapTokens     int
	KVec              int
	KLex              int
	RRFK0             int
	OverlapThresh     float64
	PerFileRoundRobin int
	LowConfSim        float64
}

// CLIArgs represents command line arguments
type CLIArgs struct {
	Query       string
	Stability   float64
	MaxTokens   int
	UseRRF      bool
	Dedupe      string
	ExpandQuery string
	JSON        bool
	Help        bool
}

// DefaultConfig returns the default configuration
func DefaultConfig() *Config {
	return &Config{
		Stability:         getEnvFloat("REHYDRATE_STABILITY", 0.6),
		MaxTokens:         6000,
		UseRRF:            getEnvBool("REHYDRATE_USE_RRF", true),
		Dedupe:            getEnvString("REHYDRATE_DEDUPE", "file+overlap"),
		ExpandQuery:       getEnvString("REHYDRATE_EXPAND_QUERY", "auto"),
		DBDSN:             getEnvString("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency"),
		PinsCapTokens:     200,
		KVec:              32,
		KLex:              32,
		RRFK0:             60,
		OverlapThresh:     0.60,
		PerFileRoundRobin: 2,
		LowConfSim:        0.30,
	}
}

// ParseCLIArgs parses command line arguments
func ParseCLIArgs() *CLIArgs {
	args := &CLIArgs{}

	flag.StringVar(&args.Query, "query", "", "Query for memory rehydration (required)")
	flag.Float64Var(&args.Stability, "stability", 0.6, "Stability slider (0.0-1.0)")
	flag.IntVar(&args.MaxTokens, "max-tokens", 6000, "Maximum tokens for bundle")
	flag.BoolVar(&args.UseRRF, "use-rrf", true, "Use RRF fusion (vector + BM25)")
	flag.StringVar(&args.Dedupe, "dedupe", "file+overlap", "Deduplication mode (file|file+overlap)")
	flag.StringVar(&args.ExpandQuery, "expand-query", "auto", "Query expansion mode (off|auto)")
	flag.BoolVar(&args.JSON, "json", false, "Output in JSON format")
	flag.BoolVar(&args.Help, "help", false, "Show help")

	flag.Parse()

	return args
}

// RunCLI runs the CLI interface
func RunCLI() {
	args := ParseCLIArgs()

	if args.Help {
		printHelp()
		return
	}

	if args.Query == "" {
		log.Fatal("Error: --query is required")
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

	// Run rehydration
	bundle, err := utils.Rehydrate(args.Query, config)
	if err != nil {
		log.Fatalf("Error: %v", err)
	}

	// Output result
	if args.JSON {
		outputJSON(bundle)
	} else {
		outputText(bundle)
	}
}

// Rehydrate is the main function for memory rehydration using Lean Hybrid with Kill-Switches
func Rehydrate(query string, config *Config) (*Bundle, error) {
	if config == nil {
		config = DefaultConfig()
	}

	startTime := time.Now()

	// 0) Load guardrail pins (always tiny, pre-compressed)
	pins, err := loadGuardrailPins(config.PinsCapTokens)
	if err != nil {
		return nil, fmt.Errorf("failed to load guardrail pins: %w", err)
	}

	// 1) Initial vector probe for confidence
	vecProbe, err := vectorSearch(query, config.KVec, config.DBDSN)
	if err != nil {
		return nil, fmt.Errorf("failed to perform vector probe: %w", err)
	}

	simTop := 0.0
	if len(vecProbe) > 0 {
		simTop = vecProbe[0].Sim
	}

	// 2) Optional auto query expansion on low confidence
	var anchorTerms []string
	expandedQ := query
	if config.ExpandQuery == "auto" && simTop < config.LowConfSim {
		anchorTerms, err = mineAnchorTerms(query, 6, config.DBDSN)
		if err != nil {
			log.Printf("Warning: failed to mine anchor terms: %v", err)
		} else {
			expandedQ = augmentQuery(query, anchorTerms)
		}
	}

	// 3) Full searches with canonicalization
	vec, err := vectorSearch(expandedQ, config.KVec, config.DBDSN)
	if err != nil {
		return nil, fmt.Errorf("failed to perform vector search: %w", err)
	}

	var lex []SearchResult
	if config.UseRRF {
		lex, err = bm25Search(expandedQ, config.KLex, config.DBDSN)
		if err != nil {
			log.Printf("Warning: failed to perform BM25 search: %v", err)
		}
	}

	// Canonicalize results to consistent format
	vecCanon := normalizeToCanonical(vec, "vector")
	lexCanon := normalizeToCanonical(lex, "bm25")

	// 4) Fusion (RRF or pure vector)
	var fused []SearchResult
	if config.UseRRF && len(lexCanon) > 0 {
		fused = rrfFuse(vecCanon, lexCanon, config.RRFK0)
	} else {
		// Pure vector path with canonical 'score' field
		fused = vecCanon
		for i := range fused {
			fused[i].Score = fused[i].Sim
		}
		// Sort by score descending, then by file, then by path
		sort.Slice(fused, func(i, j int) bool {
			if fused[i].Score != fused[j].Score {
				return fused[i].Score > fused[j].Score
			}
			if fused[i].File != fused[j].File {
				return fused[i].File < fused[j].File
			}
			return fused[i].Path < fused[j].Path
		})
	}

	// 5) Low-confidence anchor uplift (tiny, deterministic epsilon)
	if simTop < config.LowConfSim && config.ExpandQuery != "off" {
		eps := 0.02 + 0.05*clamp(config.Stability, 0.0, 1.0)
		for i := range fused {
			if fused[i].IsAnchor && overlapsScope(fused[i], query) {
				fused[i].Score += eps
			}
		}
		// Re-sort after score adjustments
		sort.Slice(fused, func(i, j int) bool {
			if fused[i].Score != fused[j].Score {
				return fused[i].Score > fused[j].Score
			}
			if fused[i].File != fused[j].File {
				return fused[i].File < fused[j].File
			}
			return fused[i].Path < fused[j].Path
		})
	}

	// 6) Cheap diversity / dedupe
	ranked := fused
	if strings.HasPrefix(config.Dedupe, "file") {
		ranked = roundRobinByFile(ranked, config.PerFileRoundRobin)
	}
	if strings.HasSuffix(config.Dedupe, "overlap") {
		ranked = dropNearDuplicates(ranked, config.OverlapThresh)
	}

	// 7) Compression & budgeting
	budgetForEvidence := max(0, config.MaxTokens-tokenLen(pins))
	evidence := []Section{}
	used := 0

	for _, d := range ranked {
		comp := compressChunk(d)
		cTokens := comp.Tokens
		if cTokens == 0 {
			cTokens = tokenLen(comp.Content)
		}
		if used+cTokens > budgetForEvidence {
			break
		}
		evidence = append(evidence, comp)
		used += cTokens
	}

	// 8) Package bundle
	bundle := packageBundle(pins, anchorTerms, evidence, map[string]interface{}{
		"stability":       config.Stability,
		"sim_top":         simTop,
		"use_rrf":         config.UseRRF,
		"dedupe":          config.Dedupe,
		"expand_query":    config.ExpandQuery,
		"k_vec":           config.KVec,
		"k_lex":           config.KLex,
		"rrf_k0":          config.RRFK0,
		"overlap_thresh":  config.OverlapThresh,
		"per_file":        config.PerFileRoundRobin,
		"pins_tokens":     tokenLen(pins),
		"evidence_tokens": used,
		"elapsed_s":       time.Since(startTime).Seconds(),
	})

	return bundle, nil
}

// Helper functions
func getEnvString(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvFloat(key string, defaultValue float64) float64 {
	if value := os.Getenv(key); value != "" {
		if parsed, err := parseFloat(value); err == nil {
			return parsed
		}
	}
	return defaultValue
}

func getEnvBool(key string, defaultValue bool) bool {
	if value := os.Getenv(key); value != "" {
		return value != "0" && value != "false"
	}
	return defaultValue
}

func parseFloat(s string) (float64, error) {
	var f float64
	_, err := fmt.Sscanf(s, "%f", &f)
	return f, err
}

func clamp(value, min, max float64) float64 {
	if value < min {
		return min
	}
	if value > max {
		return max
	}
	return value
}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func tokenLen(text string) int {
	// Approximate ~4 chars/token; safe budgeter for mix of prose/code
	return max(1, len(text)/4)
}

func loadGuardrailPins(maxTokens int) (string, error) {
	// Load stable anchors from memory scaffold
	// This would load from the same source as the Python version
	// For now, return a placeholder that respects the token limit
	content := "## 🔎 TL;DR\n\n| what this file is | read when | do next |\n|---|---|---|\n| Primary memory scaffold for AI rehydration and context management | Starting new session or need current project state | Check backlog and system overview for next priorities |"

	// Ensure content doesn't exceed maxTokens
	if tokenLen(content) > maxTokens {
		// Truncate content to fit within token limit
		// Approximate: 4 chars per token, so maxChars = maxTokens * 4
		maxChars := maxTokens * 4
		if len(content) > maxChars {
			content = content[:maxChars]
			// Try to truncate at a word boundary
			if lastSpace := strings.LastIndex(content, " "); lastSpace > maxChars*3/4 {
				content = content[:lastSpace]
			}
		}
	}

	return content, nil
}

func vectorSearch(query string, k int, dbDSN string) ([]SearchResult, error) {
	// Check for mock mode
	if strings.HasPrefix(dbDSN, "mock://") {
		// Return mock data that matches Python system output
		return []SearchResult{
			{
				ID:         1,
				Content:    "Memory Context Bundle - Project Overview - Current project status and backlog priorities - Unified Memory System with LTST, Cursor, Go CLI, and Prime systems",
				File:       "100_memory/100_cursor-memory-context.md",
				Path:       "100_memory",
				Start:      0,
				End:        100,
				IsAnchor:   true,
				AnchorKey:  "memory-context",
				Score:      0.95,
				Sim:        0.95,
				SearchType: "vector",
			},
			{
				ID:         2,
				Content:    "Backlog - Current development priorities and roadmap - P0 Lane, P1 Lane, P2 Lane - Mathematical Framework Foundation, DSPy 3.0 Migration, Advanced RAG Optimization",
				File:       "000_core/000_backlog.md",
				Path:       "000_core",
				Start:      0,
				End:        80,
				IsAnchor:   true,
				AnchorKey:  "backlog",
				Score:      0.92,
				Sim:        0.92,
				SearchType: "vector",
			},
			{
				ID:         3,
				Content:    "System Overview - Architecture and core components - Memory systems, DSPy integration - Unified Memory Orchestrator, LTST Memory System, Go CLI Memory, Prime Cursor",
				File:       "400_guides/400_03_system-overview-and-architecture.md",
				Path:       "400_guides",
				Start:      0,
				End:        120,
				IsAnchor:   true,
				AnchorKey:  "architecture",
				Score:      0.88,
				Sim:        0.88,
				SearchType: "vector",
			},
			{
				ID:         4,
				Content:    "DSPy RAG System - Complete DSPy implementation with RAG capabilities - Modules, optimization, signatures - Production-ready with PostgreSQL, pgvector, LTST Memory System integration",
				File:       "dspy-rag-system/README.md",
				Path:       "dspy-rag-system",
				Start:      0,
				End:        150,
				IsAnchor:   true,
				AnchorKey:  "dspy-rag",
				Score:      0.85,
				Sim:        0.85,
				SearchType: "vector",
			},
			{
				ID:         5,
				Content:    "Development Workflow - Complete end-to-end development process - Backlog to PRD to Tasks to Execution - Solo developer optimizations",
				File:       "400_guides/400_04_development-workflow-and-standards.md",
				Path:       "400_guides",
				Start:      0,
				End:        100,
				IsAnchor:   true,
				AnchorKey:  "workflow",
				Score:      0.82,
				Sim:        0.82,
				SearchType: "vector",
			},
			{
				ID:         6,
				Content:    "DSPy Framework Guide - Complete DSPy framework reference and implementation patterns - Signatures, modules, optimization, model switching",
				File:       "400_guides/400_07_ai-frameworks-dspy.md",
				Path:       "400_guides",
				Start:      0,
				End:        120,
				IsAnchor:   true,
				AnchorKey:  "dspy-framework",
				Score:      0.87,
				Sim:        0.87,
				SearchType: "vector",
			},
		}, nil
	}

	// Implement vector search using PostgreSQL + pgvector
	// This would use the same database schema as the Python version
	db, err := sql.Open("postgres", dbDSN)
	if err != nil {
		return nil, err
	}
	defer db.Close()

	// Placeholder implementation
	// In practice, this would use pgvector's similarity search
	rows, err := db.QueryContext(context.Background(), `
		SELECT id, content, file_path, line_start, line_end, is_anchor, anchor_key
		FROM document_chunks_compat
		WHERE embedding IS NOT NULL
		ORDER BY embedding <-> $1
		LIMIT $2
	`, query, k)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var results []SearchResult
	for rows.Next() {
		var result SearchResult
		err := rows.Scan(&result.ID, &result.Content, &result.File, &result.Start, &result.End, &result.IsAnchor, &result.AnchorKey)
		if err != nil {
			return nil, err
		}
		result.SearchType = "vector"
		results = append(results, result)
	}

	return results, nil
}

func bm25Search(query string, k int, dbDSN string) ([]SearchResult, error) {
	// Check for mock mode
	if strings.HasPrefix(dbDSN, "mock://") {
		// Return mock data that matches Python system output
		return []SearchResult{
			{
				ID:         4,
				Content:    "Development Workflow - Complete development workflow and standards - Backlog → PRD → Tasks → Execution",
				File:       "400_guides/400_04_development-workflow-and-standards.md",
				Path:       "400_guides",
				Start:      0,
				End:        90,
				IsAnchor:   true,
				AnchorKey:  "workflow",
				Score:      0.75,
				Sim:        0.75,
				SearchType: "bm25",
			},
			{
				ID:         5,
				Content:    "DSPy Framework - AI frameworks and DSPy integration - DSPy modules, optimization, signatures",
				File:       "400_guides/400_07_ai-frameworks-dspy.md",
				Path:       "400_guides",
				Start:      0,
				End:        110,
				IsAnchor:   true,
				AnchorKey:  "dspy",
				Score:      0.7,
				Sim:        0.7,
				SearchType: "bm25",
			},
		}, nil
	}

	// Implement BM25 search using PostgreSQL full-text search
	db, err := sql.Open("postgres", dbDSN)
	if err != nil {
		return nil, err
	}
	defer db.Close()

	// Placeholder implementation
	// In practice, this would use PostgreSQL's ts_rank_cd with content_tsv
	rows, err := db.QueryContext(context.Background(), `
		SELECT id, content, file_path, line_start, line_end, is_anchor, anchor_key,
		       0.5 as score
		FROM document_chunks_compat
		WHERE content ILIKE '%' || $1 || '%'
		ORDER BY score DESC
		LIMIT $2
	`, query, k)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var results []SearchResult
	for rows.Next() {
		var result SearchResult
		err := rows.Scan(&result.ID, &result.Content, &result.File, &result.Start, &result.End, &result.IsAnchor, &result.AnchorKey, &result.Score)
		if err != nil {
			return nil, err
		}
		result.SearchType = "bm25"
		results = append(results, result)
	}

	return results, nil
}

func mineAnchorTerms(query string, topN int, dbDSN string) ([]string, error) {
	// Mine anchor terms for query expansion
	// This would extract relevant anchor keys from the database
	// Placeholder implementation - use parameters to satisfy linter
	_ = query // TODO: implement query-based anchor mining
	_ = topN  // TODO: implement topN limit
	_ = dbDSN // TODO: implement database connection
	return []string{"memory", "context", "system"}, nil
}

func augmentQuery(query string, anchorTerms []string) string {
	// Augment query with anchor terms
	augmented := query
	for _, term := range anchorTerms {
		if !strings.Contains(strings.ToLower(query), strings.ToLower(term)) {
			augmented += " " + term
		}
	}
	return augmented
}

func normalizeToCanonical(results []SearchResult, searchType string) []SearchResult {
	// Normalize search results to canonical format
	for i := range results {
		results[i].SearchType = searchType
		if results[i].Score == 0 {
			results[i].Score = results[i].Sim
		}
	}
	return results
}

func rrfFuse(vec, lex []SearchResult, k0 int) []SearchResult {
	// Reciprocal Rank Fusion
	rankMap := make(map[int]float64)

	// Calculate RRF scores for vector results
	for i, result := range vec {
		rank := float64(i + 1)
		rrfScore := float64(k0) / (rank + float64(k0))
		rankMap[result.ID] += rrfScore
	}

	// Calculate RRF scores for BM25 results
	for i, result := range lex {
		rank := float64(i + 1)
		rrfScore := float64(k0) / (rank + float64(k0))
		rankMap[result.ID] += rrfScore
	}

	// Combine and sort by RRF score
	combined := make(map[int]SearchResult)
	for _, result := range vec {
		combined[result.ID] = result
	}
	for _, result := range lex {
		if existing, exists := combined[result.ID]; exists {
			// Merge scores
			existing.Score = rankMap[result.ID]
			combined[result.ID] = existing
		} else {
			result.Score = rankMap[result.ID]
			combined[result.ID] = result
		}
	}

	// Convert to slice and sort
	var fused []SearchResult
	for _, result := range combined {
		fused = append(fused, result)
	}

	sort.Slice(fused, func(i, j int) bool {
		return fused[i].Score > fused[j].Score
	})

	return fused
}

func overlapsScope(result SearchResult, query string) bool {
	// Check if result overlaps with query scope
	// Simple implementation - could be enhanced with semantic similarity
	queryLower := strings.ToLower(query)
	contentLower := strings.ToLower(result.Content)

	// Check for keyword overlap
	queryWords := strings.Fields(queryLower)
	for _, word := range queryWords {
		if len(word) > 3 && strings.Contains(contentLower, word) {
			return true
		}
	}

	return false
}

func roundRobinByFile(results []SearchResult, perFile int) []SearchResult {
	// File round-robin deduplication
	fileGroups := make(map[string][]SearchResult)
	for _, result := range results {
		fileGroups[result.File] = append(fileGroups[result.File], result)
	}

	var ranked []SearchResult
	for len(ranked) < len(results) {
		for file, group := range fileGroups {
			if len(group) > 0 {
				ranked = append(ranked, group[0])
				fileGroups[file] = group[1:]
			}
		}
		// Break if no more results
		hasMore := false
		for _, group := range fileGroups {
			if len(group) > 0 {
				hasMore = true
				break
			}
		}
		if !hasMore {
			break
		}
	}

	// TODO: implement perFile limit - currently using simple round-robin
	_ = perFile
	return ranked
}

func dropNearDuplicates(results []SearchResult, threshold float64) []SearchResult {
	// Drop near-duplicate chunks using Jaccard similarity
	var filtered []SearchResult
	for _, result := range results {
		isDuplicate := false
		for _, existing := range filtered {
			if jaccardSimilarity(result.Content, existing.Content) > threshold {
				isDuplicate = true
				break
			}
		}
		if !isDuplicate {
			filtered = append(filtered, result)
		}
	}
	return filtered
}

func jaccardSimilarity(text1, text2 string) float64 {
	// Calculate Jaccard similarity between two texts
	// Simple implementation using word sets
	words1 := make(map[string]bool)
	words2 := make(map[string]bool)

	for _, word := range strings.Fields(strings.ToLower(text1)) {
		if len(word) > 2 {
			words1[word] = true
		}
	}

	for _, word := range strings.Fields(strings.ToLower(text2)) {
		if len(word) > 2 {
			words2[word] = true
		}
	}

	intersection := 0
	for word := range words1 {
		if words2[word] {
			intersection++
		}
	}

	union := len(words1) + len(words2) - intersection
	if union == 0 {
		return 0
	}

	return float64(intersection) / float64(union)
}

func compressChunk(result SearchResult) Section {
	// Compress chunk to section format
	return Section{
		Kind:      "span",
		Title:     result.AnchorKey,
		Content:   result.Content,
		Citation:  fmt.Sprintf("Doc %d, chars %d-%d", result.ID, result.Start, result.End),
		Tokens:    tokenLen(result.Content),
		File:      result.File,
		Path:      result.Path,
		Start:     result.Start,
		End:       result.End,
		IsAnchor:  result.IsAnchor,
		AnchorKey: result.AnchorKey,
		Score:     result.Score,
		Sim:       result.Sim,
	}
}

func packageBundle(pins string, queryExpansionTerms []string, evidence []Section, debug map[string]interface{}) *Bundle {
	// Package the final bundle
	var sections []Section

	// Add pins section
	if pins != "" {
		sections = append(sections, Section{
			Kind:    "pin",
			Title:   "guardrails",
			Content: pins,
			Tokens:  tokenLen(pins),
		})
	}

	// Add evidence sections
	sections = append(sections, evidence...)

	// Build bundle text
	var bundleText strings.Builder
	for i, section := range sections {
		if i > 0 {
			bundleText.WriteString("\n\n")
		}
		bundleText.WriteString(fmt.Sprintf("## %s\n\n%s", section.Title, section.Content))
	}

	// Add query expansion info to debug
	if len(queryExpansionTerms) > 0 {
		debug["query_expansion_terms"] = queryExpansionTerms
	}

	return &Bundle{
		Text:     bundleText.String(),
		Sections: sections,
		Meta:     debug,
	}
}

func printHelp() {
	fmt.Print(`Memory Rehydration CLI - Lean Hybrid with Kill-Switches

Usage: memory_rehydration_cli [options] --query "your query"

Options:
  --query string        Query for memory rehydration (required)
  --stability float     Stability slider (0.0-1.0, default 0.6)
  --max-tokens int      Maximum tokens for bundle (default 6000)
  --use-rrf bool        Use RRF fusion (vector + BM25) (default true)
  --dedupe string       Deduplication mode: file|file+overlap (default file+overlap)
  --expand-query string Query expansion mode: off|auto (default auto)
  --json bool           Output in JSON format (default false)
  --help                Show this help message

Environment Variables:
  POSTGRES_DSN          Database connection string
  REHYDRATE_STABILITY   Default stability value
  REHYDRATE_USE_RRF     Default RRF setting
  REHYDRATE_DEDUPE      Default deduplication mode
  REHYDRATE_EXPAND_QUERY Default query expansion mode

Examples:
  # Basic usage
  memory_rehydration_cli --query "memory context system"

  # With custom stability
  memory_rehydration_cli --query "DSPy integration" --stability 0.8

  # Kill-switches for debugging
  memory_rehydration_cli --query "test query" --use-rrf=false --dedupe=file --expand-query=off

  # JSON output
  memory_rehydration_cli --query "test query" --json

Configuration:
  The system uses Lean Hybrid with Kill-Switches approach:
  - Semantic-first: Vector search does the heavy lifting
  - Tiny pins: Only 200 tokens for guardrails
  - Kill-switches: Simple flags to disable features when needed
  - Four-slot model: Pinned invariants + Anchor priors + Semantic evidence + Recency
`)
}

func outputJSON(bundle *utils.Bundle) {
	jsonData, err := json.MarshalIndent(bundle, "", "  ")
	if err != nil {
		log.Fatalf("Error marshaling JSON: %v", err)
	}
	fmt.Println(string(jsonData))
}

func outputText(bundle *utils.Bundle) {
	fmt.Println("=== Memory Rehydration Bundle ===")
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

	if terms, ok := bundle.Meta["query_expansion_terms"]; ok {
		if termList, ok := terms.([]string); ok && len(termList) > 0 {
			fmt.Printf("Query expansion terms: %v\n", termList)
		}
	}
}

// Main function for standalone CLI
func main() {
	RunCLI()
}
