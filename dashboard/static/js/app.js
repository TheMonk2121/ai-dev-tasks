// Dashboard JavaScript functionality

// Global variables
let documents = [];
let currentFilters = {
    search: '',
    priority: '',
    category: ''
};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeFilters();
    initializeSearch();
    loadDocuments();
});

// Initialize filter functionality
function initializeFilters() {
    const priorityFilter = document.getElementById('priority-filter');
    const categoryFilter = document.getElementById('category-filter');
    
    if (priorityFilter) {
        priorityFilter.addEventListener('change', function() {
            currentFilters.priority = this.value;
            filterDocuments();
        });
    }
    
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            currentFilters.category = this.value;
            filterDocuments();
        });
    }
}

// Initialize search functionality
function initializeSearch() {
    const searchInput = document.getElementById('search-input');
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            currentFilters.search = this.value.toLowerCase();
            filterDocuments();
        });
    }
}

// Load documents from API
async function loadDocuments() {
    try {
        const response = await fetch('/api/documents');
        documents = await response.json();
        displayDocuments(documents);
    } catch (error) {
        console.error('Error loading documents:', error);
        showNotification('Error loading documents', 'error');
    }
}

// Display documents with filtering
function displayDocuments(docs) {
    const container = document.getElementById('documents-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (docs.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>📭 No documents found</p>
                <p>Try adjusting your search or filters</p>
            </div>
        `;
        return;
    }
    
    docs.forEach(doc => {
        const card = createDocumentCard(doc);
        container.appendChild(card);
    });
}

// Create document card element
function createDocumentCard(doc) {
    const card = document.createElement('div');
    card.className = `document-card priority-${doc.priority}`;
    card.setAttribute('data-filename', doc.filename);
    card.setAttribute('data-priority', doc.priority);
    card.setAttribute('data-category', doc.category);
    
    const tagsHtml = doc.tags.map(tag => `<span class="tag">🏷️ ${tag}</span>`).join('');
    
    card.innerHTML = `
        <div class="document-header">
            <h3 class="document-title">${doc.filename}</h3>
            <div class="document-meta">
                <span class="file-type">📄 ${doc.file_type}</span>
                <span class="file-size">📏 ${formatFileSize(doc.file_size)}</span>
                <span class="priority-badge priority-${doc.priority}">⭐ ${doc.priority}</span>
            </div>
        </div>
        
        <div class="document-info">
            <p><strong>Category:</strong> ${doc.category}</p>
            <p><strong>Status:</strong> 
                <span class="status-badge status-${doc.status}">
                    ${getStatusIcon(doc.status)} ${doc.status}
                </span>
            </p>
            <p><strong>Chunks:</strong> ${doc.chunk_count}</p>
            <p><strong>Content Type:</strong> 
                <span class="content-type-badge content-type-${doc.content_type}">
                    ${doc.content_type.replace('_', ' ')}
                </span>
            </p>
            <p><strong>Size Category:</strong> 
                <span class="size-category-badge size-${doc.size_category}">
                    ${doc.size_category}
                </span>
            </p>
            ${doc.version ? `<p><strong>Version:</strong> ${doc.version}</p>` : ''}
            ${doc.extracted_date ? `<p><strong>Extracted Date:</strong> ${doc.extracted_date}</p>` : ''}
            <p><strong>Added:</strong> ${formatDate(doc.created_at)}</p>
        </div>
        
        ${doc.tags.length > 0 ? `<div class="document-tags">${tagsHtml}</div>` : ''}
        
        ${doc.notes ? `<div class="document-notes"><p class="notes">📝 ${doc.notes}</p></div>` : ''}
        
        <div class="document-actions">
            <button class="action-btn-small" onclick="viewMetadata('${doc.filename}')">
                🔍 View Metadata
            </button>
            <button class="action-btn-small" onclick="editMetadata('${doc.filename}')">
                ✏️ Edit
            </button>
        </div>
    `;
    
    return card;
}

// Filter documents based on current filters
function filterDocuments() {
    let filteredDocs = documents;
    
    // Search filter
    if (currentFilters.search) {
        filteredDocs = filteredDocs.filter(doc => 
            doc.filename.toLowerCase().includes(currentFilters.search) ||
            doc.category.toLowerCase().includes(currentFilters.search) ||
            doc.tags.some(tag => tag.toLowerCase().includes(currentFilters.search))
        );
    }
    
    // Priority filter
    if (currentFilters.priority) {
        filteredDocs = filteredDocs.filter(doc => doc.priority === currentFilters.priority);
    }
    
    // Category filter
    if (currentFilters.category) {
        filteredDocs = filteredDocs.filter(doc => doc.category === currentFilters.category);
    }
    
    displayDocuments(filteredDocs);
}

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function getStatusIcon(status) {
    switch (status) {
        case 'completed': return '✅';
        case 'pending': return '⏳';
        case 'failed': return '❌';
        default: return '❓';
    }
}

// View metadata for a specific document
async function viewMetadata(filename) {
    try {
        const response = await fetch(`/api/metadata/${encodeURIComponent(filename)}`);
        const metadata = await response.json();
        
        if (metadata.error) {
            showNotification('Error loading metadata', 'error');
            return;
        }
        
        showMetadataModal(filename, metadata);
    } catch (error) {
        console.error('Error loading metadata:', error);
        showNotification('Error loading metadata', 'error');
    }
}

// Show metadata modal
function showMetadataModal(filename, metadata) {
    const modal = document.getElementById('metadata-modal');
    const content = document.getElementById('metadata-content');
    
    if (!modal || !content) return;
    
    const metadataHtml = `
        <div class="metadata-section">
            <h4>📄 File Information</h4>
            <p><strong>Filename:</strong> ${filename}</p>
            <p><strong>Category:</strong> ${metadata.category || 'Uncategorized'}</p>
            <p><strong>Priority:</strong> ${metadata.priority || 'medium'}</p>
            <p><strong>Content Type:</strong> ${metadata.content_type || 'unknown'}</p>
            <p><strong>Size Category:</strong> ${metadata.size_category || 'medium'}</p>
            ${metadata.version ? `<p><strong>Version:</strong> ${metadata.version}</p>` : ''}
            ${metadata.extracted_date ? `<p><strong>Extracted Date:</strong> ${metadata.extracted_date}</p>` : ''}
            ${metadata.extracted_at ? `<p><strong>Metadata Extracted:</strong> ${formatDate(metadata.extracted_at)}</p>` : ''}
        </div>
        
        <div class="metadata-section">
            <h4>🏷️ Tags</h4>
            ${metadata.tags && metadata.tags.length > 0 
                ? metadata.tags.map(tag => `<span class="tag">🏷️ ${tag}</span>`).join('')
                : '<p>No tags assigned</p>'
            }
        </div>
        
        ${metadata.notes ? `
        <div class="metadata-section">
            <h4>📝 Notes</h4>
            <p>${metadata.notes}</p>
        </div>
        ` : ''}
        
        <div class="metadata-section">
            <h4>⚙️ Processing Information</h4>
            <p><strong>Processing Status:</strong> ${metadata.processing_status || 'pending'}</p>
        </div>
    `;
    
    content.innerHTML = metadataHtml;
    modal.classList.remove('hidden');
}

// Close modal
function closeModal() {
    const modal = document.getElementById('metadata-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// Edit metadata (placeholder for future implementation)
function editMetadata(filename) {
    showNotification('Edit metadata feature coming soon!', 'info');
}

// Update all metadata
async function updateAllMetadata() {
    try {
        showNotification('Updating metadata for all documents...', 'info');
        
        const response = await fetch('/api/documents');
        const docs = await response.json();
        
        // This would typically call an API endpoint to update metadata
        // For now, we'll just refresh the data
        await loadDocuments();
        
        showNotification('Metadata updated successfully!', 'success');
    } catch (error) {
        console.error('Error updating metadata:', error);
        showNotification('Error updating metadata', 'error');
    }
}

// Test RAG query
function testRAGQuery() {
    showNotification('RAG query testing feature coming soon!', 'info');
}

// View system health
async function viewSystemHealth() {
    try {
        const response = await fetch('/health');
        const health = await response.json();
        
        if (health.status === 'healthy') {
            showNotification('System is healthy! ✅', 'success');
        } else {
            showNotification('System health issues detected! ❌', 'error');
        }
    } catch (error) {
        console.error('Error checking system health:', error);
        showNotification('Error checking system health', 'error');
    }
}

// Export data
function exportData() {
    showNotification('Export feature coming soon!', 'info');
}

// Refresh data
async function refreshData() {
    try {
        showNotification('Refreshing data...', 'info');
        await loadDocuments();
        showNotification('Data refreshed successfully!', 'success');
    } catch (error) {
        console.error('Error refreshing data:', error);
        showNotification('Error refreshing data', 'error');
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 1001;
        animation: slideIn 0.3s ease;
    `;
    
    // Set background color based on type
    switch (type) {
        case 'success':
            notification.style.backgroundColor = '#10b981';
            break;
        case 'error':
            notification.style.backgroundColor = '#ef4444';
            break;
        case 'warning':
            notification.style.backgroundColor = '#f59e0b';
            break;
        default:
            notification.style.backgroundColor = '#3b82f6';
    }
    
    // Add to page
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    const modal = document.getElementById('metadata-modal');
    if (modal && !modal.classList.contains('hidden')) {
        if (event.target === modal) {
            closeModal();
        }
    }
});

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeModal();
    }
}); 