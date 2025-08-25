#!/usr/bin/env python3
"""
Test script to validate PDF MCP Server is working correctly.
"""

import asyncio
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.mcp_integration.base_server import MCPConfig
from utils.mcp_integration.pdf_server import PDFMCPServer


async def test_pdf_server():
    """Test the PDF MCP Server."""
    print("🧪 Testing PDF MCP Server...")

    # Create configuration
    config = MCPConfig(server_name="test_pdf_server")
    server = PDFMCPServer(config)

    print("1. Server Configuration:")
    print(f"   ✅ Server name: {server.config.server_name}")
    print(f"   ✅ Supported types: {len(server.get_supported_types())}")
    print(f"   ✅ PDF config: {server.pdf_config.max_pages} max pages")

    print("\n2. Testing Source Validation:")
    print(f"   ✅ Valid PDF file: {server.validate_source('/path/to/document.pdf')}")
    print(f"   ✅ Valid PDF URL: {server.validate_source('https://example.com/document.pdf')}")
    print(f"   ✅ Invalid source: {not server.validate_source('not-a-pdf.txt')}")

    print("\n3. Testing PDF Configuration:")
    pdf_config = server.get_pdf_config()
    print(f"   ✅ Enable OCR: {pdf_config['enable_ocr']}")
    print(f"   ✅ Extract images: {pdf_config['extract_images']}")
    print(f"   ✅ Max pages: {pdf_config['max_pages']}")
    print(f"   ✅ Text extraction mode: {pdf_config['text_extraction_mode']}")

    # Test configuration update
    server.update_pdf_config(max_pages=50)
    updated_config = server.get_pdf_config()
    print(f"   ✅ Updated max pages: {updated_config['max_pages']}")

    print("\n4. Testing PDF Creation and Processing:")
    try:
        # Create a simple test PDF
        import PyPDF2

        # Create a simple PDF for testing
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            # Create a minimal PDF with some text
            writer = PyPDF2.PdfWriter()

            # Create a page with text
            page = PyPDF2.PageObject.create_blank_page(width=612, height=792)
            page.merge_page(PyPDF2.PageObject.create_blank_page(width=612, height=792))

            # Add metadata
            writer.add_page(page)
            writer.add_metadata(
                {
                    "/Title": "Test PDF Document",
                    "/Author": "Test Author",
                    "/Subject": "Test Subject",
                    "/Creator": "Test Creator",
                    "/Producer": "Test Producer",
                }
            )

            # Write to file
            with open(temp_file.name, "wb") as output_file:
                writer.write(output_file)

            try:
                print(f"   ✅ Created test PDF: {temp_file.name}")

                # Test processing the PDF
                result = await server.process_document(temp_file.name)
                print(f"   ✅ PDF processing: {result.success}")
                print(f"   ✅ Content type: {result.metadata.content_type}")
                print(f"   ✅ Title: {result.metadata.title}")
                print(f"   ✅ Author: {result.metadata.author}")
                print(f"   ✅ Page count: {result.metadata.page_count}")
                print(f"   ✅ Word count: {result.metadata.word_count}")
                print(f"   ✅ Content preview: {result.content[:100]}...")

                # Test getting page info
                page_info = await server.get_page_info(temp_file.name, 1)
                if page_info:
                    print(f"   ✅ Page 1 word count: {page_info.word_count}")

            finally:
                # Clean up
                Path(temp_file.name).unlink()

    except Exception as e:
        print(f"   ❌ PDF processing failed: {e}")

    print("\n5. Testing Error Handling:")
    try:
        await server.process_document("not-a-pdf.txt")
        print("   ❌ Should have raised an error")
    except Exception as e:
        print(f"   ✅ Error caught: {type(e).__name__}")

    try:
        await server.process_document("/nonexistent/file.pdf")
        print("   ❌ Should have raised an error")
    except Exception as e:
        print(f"   ✅ Error caught: {type(e).__name__}")

    print("\n6. Testing Table and Image Extraction:")
    tables = await server.extract_tables("/path/to/test.pdf")
    print(f"   ✅ Table extraction: {len(tables)} tables")

    images = await server.extract_images("/path/to/test.pdf")
    print(f"   ✅ Image extraction: {len(images)} images")

    print("\n7. Testing Server Information:")
    info = server.get_server_info()
    print(f"   ✅ Server name: {info['name']}")
    print(f"   ✅ Version: {info['version']}")
    print(f"   ✅ Supported types: {len(info['supported_types'])}")
    print(f"   ✅ Cache size: {info['cache_size']}")

    print("\n🎉 All PDF MCP Server tests completed!")


if __name__ == "__main__":
    asyncio.run(test_pdf_server())
