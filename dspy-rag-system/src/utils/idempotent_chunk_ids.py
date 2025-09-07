
def generate_idempotent_chunk_id(doc_id: str, byte_span: tuple, chunk_version: str, config_hash: str) -> str:
    """Generate idempotent chunk ID using SHA1 hash."""
    import hashlib
    
    # Create deterministic input
    input_string = f"{doc_id}|{byte_span[0]}:{byte_span[1]}|{chunk_version}|{config_hash}"
    
    # Generate SHA1 hash
    chunk_id = hashlib.sha1(input_string.encode()).hexdigest()
    
    return chunk_id
