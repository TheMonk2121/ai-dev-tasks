module github.com/ai-dev-tasks/dspy-rag-system

go 1.21

require (
	github.com/ai-dev-tasks/dspy-rag-system/src/utils v0.0.0
	github.com/lib/pq v1.10.9
)

replace github.com/ai-dev-tasks/dspy-rag-system/src/utils => ./src/utils
