/**
 * VectorStore DBMS Frontend Controller
 * Handles live semantic & keyword search, category filtering, CRUD modals, and Qdrant diagnostics.
 */

// Global Application State
const state = {
  searchMode: 'semantic', // 'semantic' or 'keyword'
  category: 'All',
  query: '',
  categories: [],
  products: [],
  qdrantOnline: false
};

// DOM Elements
const elements = {
  // Tabs
  tabSemantic: document.getElementById('tab-semantic'),
  tabKeyword: document.getElementById('tab-keyword'),

  // Search
  searchForm: document.getElementById('search-form'),
  searchInput: document.getElementById('search-input'),
  btnClearSearch: document.getElementById('btn-clear-search'),
  categoryFilter: document.getElementById('category-filter'),
  sampleQueriesContainer: document.getElementById('sample-queries-container'),

  // Results
  resultsHeading: document.getElementById('results-heading'),
  resultsCount: document.getElementById('results-count'),
  productsGrid: document.getElementById('products-grid'),
  emptyState: document.getElementById('empty-state'),
  btnEmptyReset: document.getElementById('btn-empty-reset'),
  activeFilterTag: document.getElementById('active-filter-tag'),
  activeTagText: document.getElementById('active-tag-text'),
  btnResetFilters: document.getElementById('btn-reset-filters'),

  // Qdrant Status & Drawer
  qdrantStatusBadge: document.getElementById('qdrant-status-badge'),
  qdrantStatusText: document.getElementById('qdrant-status-text'),
  btnToggleStats: document.getElementById('btn-toggle-stats'),
  systemInfoDrawer: document.getElementById('system-info-drawer'),
  btnCloseDrawer: document.getElementById('btn-close-drawer'),
  infoVectorCount: document.getElementById('info-vector-count'),
  btnReseed: document.getElementById('btn-reseed'),
  reseedFeedback: document.getElementById('reseed-feedback'),

  // Modal
  productModal: document.getElementById('product-modal'),
  modalTitle: document.getElementById('modal-title'),
  btnOpenAddModal: document.getElementById('btn-open-add-modal'),
  btnCloseModal: document.getElementById('btn-close-modal'),
  btnCancelModal: document.getElementById('btn-cancel-modal'),
  productForm: document.getElementById('product-form'),
  formProductId: document.getElementById('form-product-id'),
  formName: document.getElementById('form-name'),
  formCategory: document.getElementById('form-category'),
  formPrice: document.getElementById('form-price'),
  formStock: document.getElementById('form-stock'),
  formDescription: document.getElementById('form-description'),

  // Toast
  toast: document.getElementById('toast')
};

// =========================================================
// Initialization
// =========================================================
document.addEventListener('DOMContentLoaded', () => {
  setupEventListeners();
  loadCategories();
  loadProducts();
  checkQdrantStatus();

  // Periodic Qdrant health check every 20 seconds
  setInterval(checkQdrantStatus, 20000);
});

// =========================================================
// Event Listeners
// =========================================================
function setupEventListeners() {
  // Search Mode Switcher
  elements.tabSemantic.addEventListener('click', () => setSearchMode('semantic'));
  elements.tabKeyword.addEventListener('click', () => setSearchMode('keyword'));

  // Search Submission
  elements.searchForm.addEventListener('submit', (e) => {
    e.preventDefault();
    performSearch();
  });

  // Search Input Clear Button Visibility
  elements.searchInput.addEventListener('input', () => {
    if (elements.searchInput.value.trim().length > 0) {
      elements.btnClearSearch.classList.remove('hidden');
    } else {
      elements.btnClearSearch.classList.add('hidden');
    }
  });

  elements.btnClearSearch.addEventListener('click', () => {
    elements.searchInput.value = '';
    elements.btnClearSearch.classList.add('hidden');
    resetSearchAndFilters();
  });

  // Category Filter Dropdown Change
  elements.categoryFilter.addEventListener('change', () => {
    state.category = elements.categoryFilter.value;
    if (elements.searchInput.value.trim().length > 0) {
      performSearch();
    } else {
      loadProducts(state.category);
    }
  });

  // Sample Query Chips Click
  document.querySelectorAll('.chip').forEach((chip) => {
    chip.addEventListener('click', () => {
      const query = chip.getAttribute('data-query');
      setSearchMode('semantic');
      elements.searchInput.value = query;
      elements.btnClearSearch.classList.remove('hidden');
      performSearch();
    });
  });

  // Reset Filters
  elements.btnResetFilters.addEventListener('click', resetSearchAndFilters);
  elements.btnEmptyReset.addEventListener('click', resetSearchAndFilters);

  // Drawer Toggle
  elements.btnToggleStats.addEventListener('click', () => {
    elements.systemInfoDrawer.classList.toggle('hidden');
    checkQdrantStatus();
  });
  elements.btnCloseDrawer.addEventListener('click', () => {
    elements.systemInfoDrawer.classList.add('hidden');
  });

  // Reseed Button
  elements.btnReseed.addEventListener('click', triggerReseed);

  // Modal Open/Close
  elements.btnOpenAddModal.addEventListener('click', openAddModal);
  elements.btnCloseModal.addEventListener('click', closeModal);
  elements.btnCancelModal.addEventListener('click', closeModal);

  // Modal Backdrop Click to close
  elements.productModal.querySelector('.modal-backdrop').addEventListener('click', closeModal);

  // Modal Form Submission
  elements.productForm.addEventListener('submit', handleProductFormSubmit);
}

// =========================================================
// Search Mode Logic
// =========================================================
function setSearchMode(mode) {
  state.searchMode = mode;
  if (mode === 'semantic') {
    elements.tabSemantic.classList.add('active');
    elements.tabKeyword.classList.remove('active');
    elements.searchInput.placeholder = "Enter a natural-language query e.g. 'Affordable headphones for travelling'...";
    elements.sampleQueriesContainer.classList.remove('hidden');
  } else {
    elements.tabKeyword.classList.add('active');
    elements.tabSemantic.classList.remove('active');
    elements.searchInput.placeholder = "Search product name or keywords in description (SQLite LIKE)...";
    elements.sampleQueriesContainer.classList.add('hidden');
  }

  // If there's an active query, rerun with the new mode
  if (elements.searchInput.value.trim().length > 0) {
    performSearch();
  }
}

// =========================================================
// API Calls: Load Data
// =========================================================
async function loadCategories() {
  try {
    const res = await fetch('/api/categories');
    const json = await res.json();
    if (json.status === 'success') {
      state.categories = json.data;

      // Populate Category Filter Dropdown
      elements.categoryFilter.innerHTML = '<option value="All">All Categories</option>';
      elements.formCategory.innerHTML = '';

      json.data.forEach((cat) => {
        const optFilter = document.createElement('option');
        optFilter.value = cat;
        optFilter.textContent = cat;
        elements.categoryFilter.appendChild(optFilter);

        const optForm = document.createElement('option');
        optForm.value = cat;
        optForm.textContent = cat;
        elements.formCategory.appendChild(optForm);
      });
    }
  } catch (err) {
    console.error('Failed to load categories:', err);
  }
}

async function loadProducts(category = 'All') {
  showLoading();
  try {
    const url = category && category !== 'All' 
      ? `/api/products?category=${encodeURIComponent(category)}`
      : '/api/products';

    const res = await fetch(url);
    const json = await res.json();

    if (json.status === 'success') {
      state.products = json.data;
      elements.resultsHeading.textContent = category === 'All' ? 'All Products' : `Category: ${category}`;
      elements.resultsCount.textContent = `${json.count} items`;
      elements.activeFilterTag.classList.add('hidden');
      renderProductCards(json.data, false);
    }
  } catch (err) {
    showToast('Failed to load products from database', 'error');
  }
}

async function performSearch() {
  const query = elements.searchInput.value.trim();
  if (!query) {
    loadProducts(state.category);
    return;
  }

  state.query = query;
  showLoading();

  try {
    let url = '';
    const catParam = state.category && state.category !== 'All' ? `&category=${encodeURIComponent(state.category)}` : '';

    if (state.searchMode === 'semantic') {
      url = `/api/search/semantic?q=${encodeURIComponent(query)}${catParam}&limit=12`;
    } else {
      url = `/api/search/keyword?q=${encodeURIComponent(query)}${catParam}`;
    }

    const res = await fetch(url);
    const json = await res.json();

    if (json.status === 'success') {
      const modeLabel = state.searchMode === 'semantic' ? 'Semantic AI' : 'Keyword';
      elements.resultsHeading.textContent = `${modeLabel} Results for "${query}"`;
      elements.resultsCount.textContent = `${json.count} matches`;

      // Update Active Filter Tag
      elements.activeTagText.textContent = `Query: "${query}" | Mode: ${modeLabel}${state.category !== 'All' ? ` | Cat: ${state.category}` : ''}`;
      elements.activeFilterTag.classList.remove('hidden');

      renderProductCards(json.data, state.searchMode === 'semantic');
    } else {
      showToast(json.message || 'Search failed', 'error');
    }
  } catch (err) {
    showToast('Error communicating with search server', 'error');
  }
}

function resetSearchAndFilters() {
  elements.searchInput.value = '';
  elements.btnClearSearch.classList.add('hidden');
  elements.categoryFilter.value = 'All';
  state.category = 'All';
  state.query = '';
  loadProducts('All');
}

// =========================================================
// Render Product Cards
// =========================================================
function renderProductCards(products, isSemantic = false) {
  elements.productsGrid.innerHTML = '';

  if (!products || products.length === 0) {
    elements.emptyState.classList.remove('hidden');
    elements.productsGrid.classList.add('hidden');
    return;
  }

  elements.emptyState.classList.add('hidden');
  elements.productsGrid.classList.remove('hidden');

  products.forEach((p) => {
    const card = document.createElement('article');
    card.className = 'product-card';

    const catClass = getCategoryClass(p.category);
    const stockClass = p.stock_quantity > 10 ? 'in-stock' : 'low-stock';
    const stockText = p.stock_quantity > 10 ? `In Stock (${p.stock_quantity})` : `Low Stock (${p.stock_quantity})`;

    // Similarity Pill (only for semantic search)
    let similarityBadge = '';
    if (isSemantic && p.similarity_score !== undefined) {
      similarityBadge = `
        <div class="similarity-pill" title="Cosine similarity score: ${p.similarity_score}">
          ⚡ ${p.similarity_percentage || (Math.round(p.similarity_score * 100) + '%')} Match
        </div>
      `;
    }

    card.innerHTML = `
      <div>
        <div class="card-top">
          <span class="category-tag ${catClass}">${escapeHtml(p.category)}</span>
          ${similarityBadge}
        </div>
        <h3 class="product-name">${escapeHtml(p.product_name)}</h3>
        <p class="product-desc">${escapeHtml(p.description || 'No description available.')}</p>
      </div>

      <div>
        <div class="card-meta">
          <span class="product-price">$${Number(p.price).toFixed(2)}</span>
          <span class="stock-tag ${stockClass}">${stockText}</span>
        </div>
        <div class="card-actions">
          <button class="btn-card btn-card-edit" data-id="${p.product_id}">Edit</button>
          <button class="btn-card btn-card-delete" data-id="${p.product_id}" data-name="${escapeHtml(p.product_name)}">Delete</button>
        </div>
      </div>
    `;

    // Edit button click
    card.querySelector('.btn-card-edit').addEventListener('click', () => openEditModal(p));

    // Delete button click
    card.querySelector('.btn-card-delete').addEventListener('click', () => deleteProduct(p.product_id, p.product_name));

    elements.productsGrid.appendChild(card);
  });
}

function getCategoryClass(cat) {
  switch (cat) {
    case 'Electronics': return 'cat-electronics';
    case 'Clothing': return 'cat-clothing';
    case 'Books': return 'cat-books';
    case 'Home Appliances': return 'cat-home';
    case 'Sports Equipment': return 'cat-sports';
    default: return 'cat-default';
  }
}

// =========================================================
// CRUD Operations
// =========================================================
function openAddModal() {
  elements.modalTitle.textContent = 'Add New Product';
  elements.formProductId.value = '';
  elements.productForm.reset();
  if (state.categories.length > 0) {
    elements.formCategory.value = state.categories[0];
  }
  elements.productModal.classList.remove('hidden');
}

function openEditModal(product) {
  elements.modalTitle.textContent = 'Edit Product & Vector';
  elements.formProductId.value = product.product_id;
  elements.formName.value = product.product_name;
  elements.formCategory.value = product.category;
  elements.formPrice.value = product.price;
  elements.formStock.value = product.stock_quantity;
  elements.formDescription.value = product.description || '';
  elements.productModal.classList.remove('hidden');
}

function closeModal() {
  elements.productModal.classList.add('hidden');
}

async function handleProductFormSubmit(e) {
  e.preventDefault();

  const id = elements.formProductId.value;
  const isEdit = Boolean(id);

  const payload = {
    product_name: elements.formName.value.trim(),
    category: elements.formCategory.value.trim(),
    price: parseFloat(elements.formPrice.value),
    stock_quantity: parseInt(elements.formStock.value, 10),
    description: elements.formDescription.value.trim()
  };

  try {
    const url = isEdit ? `/api/products/${id}` : '/api/products';
    const method = isEdit ? 'PUT' : 'POST';

    const res = await fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const json = await res.json();

    if (json.status === 'success') {
      closeModal();
      showToast(isEdit ? 'Product updated and vector re-indexed!' : 'Product added and vector indexed!', 'success');
      loadProducts(state.category);
      checkQdrantStatus();
    } else {
      showToast(json.message || 'Operation failed', 'error');
    }
  } catch (err) {
    showToast('Error saving product to server', 'error');
  }
}

async function deleteProduct(productId, productName) {
  const confirmed = confirm(`Are you sure you want to delete "${productName}"?\n\nThis will remove the record from SQLite and delete its dense vector from Qdrant.`);
  if (!confirmed) return;

  try {
    const res = await fetch(`/api/products/${productId}`, { method: 'DELETE' });
    const json = await res.json();

    if (json.status === 'success') {
      showToast(`Deleted "${productName}" from SQLite & Qdrant`, 'success');
      loadProducts(state.category);
      checkQdrantStatus();
    } else {
      showToast(json.message || 'Failed to delete product', 'error');
    }
  } catch (err) {
    showToast('Error communicating with server', 'error');
  }
}

// =========================================================
// Diagnostics & Health Checks
// =========================================================
async function checkQdrantStatus() {
  try {
    const res = await fetch('/api/qdrant/stats');
    const json = await res.json();

    if (json.status === 'success' && json.data.status === 'online') {
      state.qdrantOnline = true;
      elements.qdrantStatusBadge.className = 'status-badge status-online';
      elements.qdrantStatusText.textContent = `Qdrant Online (${json.data.vector_count} vectors)`;
      elements.infoVectorCount.textContent = `${json.data.vector_count} vectors`;
    } else {
      state.qdrantOnline = false;
      elements.qdrantStatusBadge.className = 'status-badge status-offline';
      elements.qdrantStatusText.textContent = 'Qdrant Offline';
      elements.infoVectorCount.textContent = '0 (Disconnected)';
    }
  } catch (err) {
    state.qdrantOnline = false;
    elements.qdrantStatusBadge.className = 'status-badge status-offline';
    elements.qdrantStatusText.textContent = 'Qdrant Offline';
    elements.infoVectorCount.textContent = 'Error';
  }
}

async function triggerReseed() {
  elements.btnReseed.disabled = true;
  elements.reseedFeedback.textContent = 'Re-seeding database and computing embeddings (may take ~5s)...';

  try {
    const res = await fetch('/api/seed', { method: 'POST' });
    const json = await res.json();

    if (json.status === 'success') {
      elements.reseedFeedback.textContent = '✓ Successfully re-seeded SQLite & Qdrant!';
      showToast('Database & Vectors Re-Seeded Successfully!', 'success');
      loadCategories();
      loadProducts('All');
      checkQdrantStatus();
    } else {
      elements.reseedFeedback.textContent = '✗ Re-seed failed.';
      showToast(json.message || 'Re-seed failed', 'error');
    }
  } catch (err) {
    elements.reseedFeedback.textContent = '✗ Connection error during re-seed.';
    showToast('Failed to trigger re-seed', 'error');
  } finally {
    elements.btnReseed.disabled = false;
  }
}

// =========================================================
// Helpers
// =========================================================
function showLoading() {
  elements.resultsCount.textContent = 'Searching...';
}

function showToast(message, type = 'info') {
  elements.toast.textContent = message;
  elements.toast.className = `toast toast-${type}`;
  elements.toast.classList.remove('hidden');

  setTimeout(() => {
    elements.toast.classList.add('hidden');
  }, 3500);
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
