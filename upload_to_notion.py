#!/usr/bin/env python3
"""
Upload RAG API documentation to Notion database
"""
import json
import subprocess
import os
from pathlib import Path

# Database data source ID
DATA_SOURCE_ID = "31549f1e-23f1-4eec-bcae-3366fbd703b8"

# Files to upload with metadata
FILES = [
    {
        "file": "CHROMEBOOK_TERMINAL_GUIDE.md",
        "name": "Chromebook Terminal Integration Guide",
        "type": "Guide",
        "sphere": "S015 - Engineering",
        "novelty": 0.92,
        "status": "Complete",
        "source": "Manus",
        "github": "https://github.com/atlaslattice/sheldonbrain-rag-api/blob/master/CHROMEBOOK_TERMINAL_GUIDE.md"
    },
    {
        "file": "CLAUDE_CONTINUITY_PACKAGE.md",
        "name": "Claude Continuity Package - Integration Guide",
        "type": "Guide",
        "sphere": "S042 - Meta-cognition",
        "novelty": 0.91,
        "status": "Complete",
        "source": "Manus",
        "github": "https://github.com/atlaslattice/sheldonbrain-rag-api/blob/master/CLAUDE_CONTINUITY_PACKAGE.md"
    },
    {
        "file": "CLOUD_RUN_DEPLOYMENT_GUIDE.md",
        "name": "Cloud Run Deployment Guide",
        "type": "Guide",
        "sphere": "S015 - Engineering",
        "novelty": 0.85,
        "status": "Complete",
        "source": "Manus",
        "github": "https://github.com/atlaslattice/sheldonbrain-rag-api/blob/master/CLOUD_RUN_DEPLOYMENT_GUIDE.md"
    },
    {
        "file": "FINAL_DEPLOYMENT_REPORT.md",
        "name": "Final Deployment Report - 12 Hour Session",
        "type": "Report",
        "sphere": "S042 - Meta-cognition",
        "novelty": 0.89,
        "status": "Complete",
        "source": "Collaborative",
        "github": "https://github.com/atlaslattice/sheldonbrain-rag-api/blob/master/FINAL_DEPLOYMENT_REPORT.md"
    },
    {
        "file": "GEMINI_TERMINAL_MESSAGE.md",
        "name": "Gemini Terminal Message - Ready to Send",
        "type": "Documentation",
        "sphere": "S042 - Meta-cognition",
        "novelty": 0.87,
        "status": "Complete",
        "source": "Manus",
        "github": "https://github.com/atlaslattice/sheldonbrain-rag-api/blob/master/GEMINI_TERMINAL_MESSAGE.md"
    },
    {
        "file": "GEMINI_DEPLOYMENT_COMPLETE.md",
        "name": "Gemini Deployment Complete - Summary",
        "type": "Report",
        "sphere": "S015 - Engineering",
        "novelty": 0.90,
        "status": "Complete",
        "source": "Manus",
        "github": "https://github.com/atlaslattice/sheldonbrain-rag-api/blob/master/GEMINI_DEPLOYMENT_COMPLETE.md"
    },
    {
        "file": "rag_api_gemini.py",
        "name": "RAG API with Gemini Embeddings (Production)",
        "type": "Code",
        "sphere": "S015 - Engineering",
        "novelty": 0.92,
        "status": "Production Ready",
        "source": "Manus",
        "github": "https://github.com/atlaslattice/sheldonbrain-rag-api/blob/master/rag_api_gemini.py"
    },
    {
        "file": "deploy-cloud-run-gemini.sh",
        "name": "Cloud Run Deployment Script (Gemini)",
        "type": "Script",
        "sphere": "S015 - Engineering",
        "novelty": 0.88,
        "status": "Production Ready",
        "source": "Manus",
        "github": "https://github.com/atlaslattice/sheldonbrain-rag-api/blob/master/deploy-cloud-run-gemini.sh"
    },
    {
        "file": "config.py",
        "name": "RAG API Configuration Module",
        "type": "Code",
        "sphere": "S015 - Engineering",
        "novelty": 0.75,
        "status": "Production Ready",
        "source": "Manus",
        "github": "https://github.com/atlaslattice/sheldonbrain-rag-api/blob/master/config.py"
    },
    {
        "file": "embeddings.py",
        "name": "Embedding Generation Utilities",
        "type": "Code",
        "sphere": "S015 - Engineering",
        "novelty": 0.78,
        "status": "Production Ready",
        "source": "Manus",
        "github": "https://github.com/atlaslattice/sheldonbrain-rag-api/blob/master/embeddings.py"
    },
    {
        "file": "pinecone_client.py",
        "name": "Pinecone Vector Database Client",
        "type": "Code",
        "sphere": "S015 - Engineering",
        "novelty": 0.76,
        "status": "Production Ready",
        "source": "Manus",
        "github": "https://github.com/atlaslattice/sheldonbrain-rag-api/blob/master/pinecone_client.py"
    }
]

def count_words_or_lines(filepath):
    """Count words for markdown files, lines for code files"""
    if filepath.endswith('.md'):
        result = subprocess.run(['wc', '-w', filepath], capture_output=True, text=True)
        return int(result.stdout.split()[0])
    else:
        result = subprocess.run(['wc', '-l', filepath], capture_output=True, text=True)
        return int(result.stdout.split()[0])

def read_file_content(filepath, max_chars=25000):
    """Read file content, truncate if too long"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if len(content) > max_chars:
        content = content[:max_chars] + "\n\n... (content truncated, see GitHub for full version)"
    
    return content

def upload_file(file_info):
    """Upload a single file to Notion"""
    filepath = file_info['file']
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    print(f"📤 Uploading: {file_info['name']}")
    
    # Count words/lines
    count = count_words_or_lines(filepath)
    
    # Read content
    content = read_file_content(filepath)
    
    # Build JSON input
    input_data = {
        "parent": {"data_source_id": DATA_SOURCE_ID},
        "pages": [{
            "properties": {
                "Name": file_info['name'],
                "Type": file_info['type'],
                "Sphere": file_info['sphere'],
                "Novelty": file_info['novelty'],
                "Status": file_info['status'],
                "Source": file_info['source'],
                "date:Date Created:start": "2026-01-01",
                "date:Date Created:is_datetime": 0,
                "GitHub URL": file_info['github'],
                "Word Count": count
            },
            "content": content
        }]
    }
    
    # Write to temp file to avoid shell escaping issues
    temp_file = f"/tmp/notion_input_{filepath.replace('/', '_').replace('.', '_')}.json"
    with open(temp_file, 'w') as f:
        json.dump(input_data, f)
    
    # Call MCP CLI
    try:
        result = subprocess.run(
            ['manus-mcp-cli', 'tool', 'call', 'notion-create-pages', 
             '--server', 'notion', '--input', json.dumps(input_data)],
            capture_output=True,
            text=True,
            timeout=90
        )
        
        if result.returncode == 0:
            print(f"✅ Uploaded: {file_info['name']}")
            return True
        else:
            print(f"❌ Failed: {file_info['name']}")
            print(f"   Error: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱️ Timeout: {file_info['name']}")
        return False
    except Exception as e:
        print(f"❌ Error: {file_info['name']} - {str(e)}")
        return False
    finally:
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)

def main():
    print("🚀 Starting Notion upload...")
    print(f"📁 Total files: {len(FILES)}")
    print()
    
    success_count = 0
    fail_count = 0
    
    for file_info in FILES:
        if upload_file(file_info):
            success_count += 1
        else:
            fail_count += 1
        print()
    
    print("=" * 60)
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"📊 Total: {len(FILES)}")
    print("=" * 60)

if __name__ == "__main__":
    main()
