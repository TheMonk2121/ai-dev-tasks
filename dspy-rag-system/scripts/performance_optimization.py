#!/usr/bin/env python3
"""
Performance Optimization Script
Optimize vector database performance and analyze optimization opportunities.
"""
import json
import sys

import psycopg2

DB_DSN = "postgresql://danieljacobs@localhost:5432/ai_agency"


def analyze_database_performance():
    """Analyze database performance and optimization opportunities."""
    print("🚀 Database Performance Analysis")
    print("=" * 50)

    try:
        conn = psycopg2.connect(DB_DSN)
        cursor = conn.cursor()

        # Database statistics
        cursor.execute(
            """
            SELECT
                COUNT(*) as total_documents,
                SUM(chunk_count) as total_chunks,
                AVG(file_size) as avg_file_size,
                AVG(chunk_count) as avg_chunks_per_doc
            FROM documents
        """
        )
        stats = cursor.fetchone()

        print("📊 Database Statistics:")
        print(f"  Total Documents: {stats[0]}")
        print(f"  Total Chunks: {stats[1]}")
        print(f"  Average File Size: {stats[2]:.0f} bytes")
        print(f"  Average Chunks per Document: {stats[3]:.1f}")

        # Chunk size analysis
        cursor.execute(
            """
            SELECT
                filename,
                file_size,
                chunk_count,
                ROUND(file_size::numeric / chunk_count, 1) as avg_chunk_size
            FROM documents
            WHERE filename LIKE '400_%'
            ORDER BY avg_chunk_size DESC
        """
        )
        chunk_sizes = cursor.fetchall()

        print("\n📏 Chunk Size Analysis:")
        total_chunk_size = 0
        for filename, file_size, chunk_count, avg_chunk_size in chunk_sizes:
            total_chunk_size += avg_chunk_size
            print(f"  {filename}: {avg_chunk_size} chars/chunk")

        avg_chunk_size = total_chunk_size / len(chunk_sizes) if chunk_sizes else 0
        print(f"  Average Chunk Size: {avg_chunk_size:.1f} characters")

        # Index analysis
        cursor.execute(
            """
            SELECT
                schemaname,
                tablename,
                indexname,
                indexdef
            FROM pg_indexes
            WHERE tablename IN ('documents', 'document_chunks')
            ORDER BY tablename, indexname
        """
        )
        indexes = cursor.fetchall()

        print("\n🔍 Index Analysis:")
        for schema, table, index, definition in indexes:
            index_type = (
                "GIN"
                if "gin" in definition.lower()
                else (
                    "BTREE"
                    if "btree" in definition.lower()
                    else (
                        "HNSW"
                        if "hnsw" in definition.lower()
                        else "IVFFLAT" if "ivfflat" in definition.lower() else "OTHER"
                    )
                )
            )
            print(f"  {table}.{index}: {index_type}")

        # Cross-reference efficiency
        cursor.execute(
            """
            SELECT
                d.filename,
                COUNT(dc.id) as chunks_with_refs,
                d.chunk_count,
                ROUND(COUNT(dc.id)::numeric / d.chunk_count * 100, 1) as coverage_pct
            FROM documents d
            LEFT JOIN document_chunks dc ON d.id::text = dc.document_id AND dc.content LIKE '%400_%'
            WHERE d.filename LIKE '400_%'
            GROUP BY d.filename, d.chunk_count
            ORDER BY coverage_pct DESC
        """
        )
        cross_refs = cursor.fetchall()

        print("\n🔗 Cross-Reference Efficiency:")
        total_coverage = 0
        for filename, chunks_with_refs, total_chunks, coverage_pct in cross_refs:
            total_coverage += coverage_pct
            print(f"  {filename}: {coverage_pct}% coverage ({chunks_with_refs}/{total_chunks} chunks)")

        avg_coverage = total_coverage / len(cross_refs) if cross_refs else 0
        print(f"  Average Coverage: {avg_coverage:.1f}%")

        # Performance recommendations
        print("\n💡 Performance Recommendations:")

        if avg_chunk_size < 400:
            print(f"  ⚠️  Chunk size ({avg_chunk_size:.1f} chars) is below optimal (500 chars)")
            print("     Consider increasing chunk size for better retrieval")
        elif avg_chunk_size > 600:
            print(f"  ⚠️  Chunk size ({avg_chunk_size:.1f} chars) is above optimal (500 chars)")
            print("     Consider decreasing chunk size for more granular retrieval")
        else:
            print(f"  ✅ Chunk size ({avg_chunk_size:.1f} chars) is optimal")

        if avg_coverage < 30:
            print(f"  ⚠️  Cross-reference coverage ({avg_coverage:.1f}%) is low")
            print("     Consider adding more cross-references for better navigation")
        else:
            print(f"  ✅ Cross-reference coverage ({avg_coverage:.1f}%) is good")

        # Check for potential optimizations
        cursor.execute(
            """
            SELECT COUNT(*) as duplicate_chunks
            FROM document_chunks dc1
            JOIN document_chunks dc2 ON dc1.content = dc2.content AND dc1.id != dc2.id
        """
        )
        duplicates = cursor.fetchone()[0]

        if duplicates > 0:
            print(f"  ⚠️  Found {duplicates} potential duplicate chunks")
            print("     Consider deduplication for storage optimization")
        else:
            print("  ✅ No duplicate chunks detected")

        # Memory usage estimation
        cursor.execute(
            """
            SELECT
                pg_size_pretty(pg_total_relation_size('documents')) as docs_size,
                pg_size_pretty(pg_total_relation_size('document_chunks')) as chunks_size
        """
        )
        sizes = cursor.fetchone()

        print("\n💾 Storage Analysis:")
        print(f"  Documents Table: {sizes[0]}")
        print(f"  Document Chunks Table: {sizes[1]}")

        cursor.close()
        conn.close()

        return {
            "stats": stats,
            "chunk_sizes": chunk_sizes,
            "indexes": indexes,
            "cross_refs": cross_refs,
            "avg_chunk_size": avg_chunk_size,
            "avg_coverage": avg_coverage,
            "duplicates": duplicates,
            "sizes": sizes,
        }

    except Exception as e:
        print(f"❌ Error analyzing performance: {e}")
        return None


def optimize_chunk_sizes():
    """Optimize chunk sizes for better performance."""
    print("\n🔧 Chunk Size Optimization")
    print("=" * 30)

    try:
        conn = psycopg2.connect(DB_DSN)
        cursor = conn.cursor()

        # Find files with suboptimal chunk sizes
        cursor.execute(
            """
            SELECT
                filename,
                file_size,
                chunk_count,
                ROUND(file_size::numeric / chunk_count, 1) as avg_chunk_size
            FROM documents
            WHERE ABS(file_size::numeric / chunk_count - 500) > 100
            ORDER BY ABS(file_size::numeric / chunk_count - 500) DESC
        """
        )
        suboptimal = cursor.fetchall()

        if not suboptimal:
            print("✅ All files have optimal chunk sizes")
            return True

        print(f"Found {len(suboptimal)} files with suboptimal chunk sizes:")
        for filename, file_size, chunk_count, avg_chunk_size in suboptimal:
            optimal_chunks = max(1, round(file_size / 500))
            print(f"  {filename}: {avg_chunk_size:.1f} chars/chunk (optimal: ~500)")
            print(f"    Current: {chunk_count} chunks, Optimal: {optimal_chunks} chunks")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"❌ Error optimizing chunk sizes: {e}")
        return False


def create_performance_report():
    """Create a comprehensive performance report."""
    print("\n📋 Performance Report Generation")
    print("=" * 40)

    data = analyze_database_performance()
    if not data:
        return False

    report = {
        "timestamp": datetime.now().isoformat(),
        "database_stats": {
            "total_documents": int(data["stats"][0]),
            "total_chunks": int(data["stats"][1]),
            "avg_file_size": float(data["stats"][2]),
            "avg_chunks_per_doc": float(data["stats"][3]),
        },
        "performance_metrics": {
            "avg_chunk_size": float(data["avg_chunk_size"]),
            "avg_cross_ref_coverage": float(data["avg_coverage"]),
            "duplicate_chunks": int(data["duplicates"]),
        },
        "storage_analysis": {"documents_size": str(data["sizes"][0]), "chunks_size": str(data["sizes"][1])},
        "recommendations": [],
    }

    # Add recommendations based on analysis
    if data["avg_chunk_size"] < 400:
        report["recommendations"].append("Increase chunk size for better retrieval performance")
    elif data["avg_chunk_size"] > 600:
        report["recommendations"].append("Decrease chunk size for more granular retrieval")

    if data["avg_coverage"] < 30:
        report["recommendations"].append("Add more cross-references for better navigation")

    if data["duplicates"] > 0:
        report["recommendations"].append("Consider deduplication for storage optimization")

    # Save report
    report_path = "performance_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"✅ Performance report saved to {report_path}")
    return True


def main():
    """Main performance optimization function."""
    print("🚀 Vector Database Performance Optimization")
    print("=" * 50)

    # Analyze performance
    data = analyze_database_performance()
    if not data:
        return False

    # Optimize chunk sizes
    optimize_chunk_sizes()

    # Generate performance report
    create_performance_report()

    print("\n✅ Performance optimization analysis complete!")
    print("📊 Key Metrics:")
    print(f"  - Average Chunk Size: {data['avg_chunk_size']:.1f} characters")
    print(f"  - Cross-Reference Coverage: {data['avg_coverage']:.1f}%")
    print(f"  - Storage: {data['sizes'][1]} for chunks")

    return True


if __name__ == "__main__":
    from datetime import datetime

    success = main()
    sys.exit(0 if success else 1)
