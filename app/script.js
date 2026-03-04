/**
 * AI Auto-Category & Tag Generator — Frontend Logic
 * Handles API communication, dynamic rendering, history, and interactions.
 */

// ===================== DOM Elements =====================
const productName = document.getElementById('productName');
const productDesc = document.getElementById('productDesc');
const charCount = document.getElementById('charCount');
const analyzeBtn = document.getElementById('analyzeBtn');

const emptyState = document.getElementById('emptyState');
const loadingState = document.getElementById('loadingState');
const resultsContent = document.getElementById('resultsContent');
const errorState = document.getElementById('errorState');

const primaryCategory = document.getElementById('primaryCategory');
const subCategory = document.getElementById('subCategory');
const seoTags = document.getElementById('seoTags');
const sustainabilityFilters = document.getElementById('sustainabilityFilters');
const noFilters = document.getElementById('noFilters');
const aiReasoning = document.getElementById('aiReasoning');
const processingTime = document.getElementById('processingTime');
const errorMessage = document.getElementById('errorMessage');

const historyToggle = document.getElementById('historyToggle');
const historyPanel = document.getElementById('historyPanel');
const closeHistory = document.getElementById('closeHistory');
const historyList = document.getElementById('historyList');
const clearHistoryBtn = document.getElementById('clearHistoryBtn');

const copyTagsBtn = document.getElementById('copyTagsBtn');
const exportJsonBtn = document.getElementById('exportJsonBtn');
const analyzeAnotherBtn = document.getElementById('analyzeAnotherBtn');
const retryBtn = document.getElementById('retryBtn');

const toast = document.getElementById('toast');
const toastMessage = document.getElementById('toastMessage');

// ===================== State =====================
let currentResult = null;

// ===================== Sample Data =====================
const SAMPLES = {
    'eco-bottle': {
        name: 'Bamboo Insulated Water Bottle',
        desc: `Eco-friendly bamboo and stainless steel insulated water bottle, 750ml capacity. Features double-wall vacuum insulation that keeps drinks cold for 24 hours and hot for 12 hours. Made from sustainably harvested bamboo exterior with food-grade 18/8 stainless steel interior. BPA-free, plastic-free cap with silicone seal. Comes with a jute carrying sleeve. Perfect for outdoor adventures, gym, or office use. Each bottle sold plants one tree through our reforestation partner. Packaging is 100% recycled cardboard and compostable.`
    },
    'earbuds': {
        name: 'SonicPro X3 Active Noise Cancelling Earbuds',
        desc: `Premium wireless earbuds with hybrid active noise cancellation (ANC) and transparency mode. Powered by custom 11mm dynamic drivers delivering deep bass and crystal-clear treble. Bluetooth 5.3 with multipoint connection for seamless switching between devices. IPX5 water resistance for workouts. 8 hours battery life per charge, 32 hours total with charging case. Touch controls, in-ear detection, and customizable EQ via companion app. Includes 6 sizes of silicone ear tips and 2 sizes of memory foam tips. USB-C fast charging — 10 min charge gives 90 min playback.`
    },
    'dress': {
        name: 'Artisan Linen Wrap Dress',
        desc: `Handcrafted wrap dress made from 100% European flax linen, naturally dyed using plant-based dyes (indigo and turmeric). Features adjustable wrap tie, side pockets, and relaxed midi length. The fabric is OEKO-TEX certified, ensuring zero harmful chemicals. Produced in a fair-trade certified workshop in Portugal. Each piece has slight natural color variations, making every dress unique. Machine washable at 30°C. Available in Natural, Terracotta, and Sage. The linen softens beautifully with every wash. Minimalist, timeless design suitable for casual and semi-formal occasions.`
    },
    'candle': {
        name: 'Nordic Pine Soy Wax Candle',
        desc: `Hand-poured 100% natural soy wax candle with essential oils of Scots pine, cedarwood, and bergamot. Burns clean for 50+ hours with cotton wick — no paraffin, no synthetic fragrances. Housed in a reusable artisan ceramic vessel made by local potters. Vegan, cruelty-free, and plastic-free. The ceramic holder can be repurposed as a planter or drinking cup after the candle is finished. Scent profile: fresh pine needles, warm cedar, and a citrus undertone. Perfect for cozy evenings and mindful living spaces. Gift-ready in a recycled kraft box with dried flower decoration.`
    },
};

// ===================== Event Listeners =====================
productDesc.addEventListener('input', updateCharCount);
analyzeBtn.addEventListener('click', analyzeProduct);
historyToggle.addEventListener('click', toggleHistory);
closeHistory.addEventListener('click', () => historyPanel.classList.add('hidden'));
clearHistoryBtn.addEventListener('click', clearHistory);
copyTagsBtn.addEventListener('click', copyTags);
exportJsonBtn.addEventListener('click', exportJSON);
analyzeAnotherBtn.addEventListener('click', resetToInput);
retryBtn.addEventListener('click', analyzeProduct);

// Sample chip listeners
document.querySelectorAll('.chip[data-sample]').forEach(chip => {
    chip.addEventListener('click', () => loadSample(chip.dataset.sample));
});

// Close history on outside click
document.addEventListener('click', (e) => {
    if (!historyPanel.classList.contains('hidden') &&
        !historyPanel.contains(e.target) &&
        e.target !== historyToggle &&
        !historyToggle.contains(e.target)) {
        historyPanel.classList.add('hidden');
    }
});

// ===================== Core Functions =====================

function updateCharCount() {
    const len = productDesc.value.length;
    charCount.textContent = `${len.toLocaleString()} / 5,000`;
    charCount.style.color = len > 4500 ? '#f43f5e' : len > 3500 ? '#f59e0b' : '';
}

function loadSample(id) {
    const sample = SAMPLES[id];
    if (!sample) return;
    productName.value = sample.name;
    productDesc.value = sample.desc;
    updateCharCount();
    showToast(`Loaded sample: ${sample.name}`);
}

async function analyzeProduct() {
    const desc = productDesc.value.trim();

    if (!desc || desc.length < 10) {
        showToast('Please enter at least 10 characters of product description.');
        productDesc.focus();
        return;
    }

    // Show loading
    setState('loading');
    analyzeBtn.disabled = true;

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                description: desc,
                product_name: productName.value.trim() || null,
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Server error');
        }

        if (!data.success) {
            throw new Error(data.error || 'Analysis failed');
        }

        currentResult = data;
        renderResults(data);
        setState('results');

    } catch (err) {
        console.error('Analysis error:', err);
        errorMessage.textContent = err.message || 'Something went wrong. Please check your API key and try again.';
        setState('error');
    } finally {
        analyzeBtn.disabled = false;
    }
}

// ===================== Rendering =====================

function renderResults(data) {
    const meta = data.metadata;

    // Categories
    primaryCategory.textContent = meta.primary_category;
    subCategory.textContent = meta.sub_category;

    // Processing time
    processingTime.textContent = `${data.processing_time_ms}ms`;

    // SEO Tags
    seoTags.innerHTML = '';
    meta.seo_tags.forEach((tag, i) => {
        const pill = document.createElement('span');
        pill.className = 'tag-pill';
        pill.textContent = tag;
        pill.style.animationDelay = `${i * 0.06}s`;
        seoTags.appendChild(pill);
    });

    // Sustainability Filters
    sustainabilityFilters.innerHTML = '';
    if (meta.sustainability_filters && meta.sustainability_filters.length > 0) {
        noFilters.classList.add('hidden');
        meta.sustainability_filters.forEach((filter, i) => {
            const pill = document.createElement('span');
            pill.className = 'sustainability-pill';
            pill.textContent = filter;
            pill.style.animationDelay = `${i * 0.08}s`;
            sustainabilityFilters.appendChild(pill);
        });
    } else {
        noFilters.classList.remove('hidden');
    }

    // AI Reasoning
    aiReasoning.textContent = meta.ai_reasoning;
}

// ===================== State Management =====================

function setState(state) {
    emptyState.classList.add('hidden');
    loadingState.classList.add('hidden');
    resultsContent.classList.add('hidden');
    errorState.classList.add('hidden');

    switch (state) {
        case 'empty': emptyState.classList.remove('hidden'); break;
        case 'loading': loadingState.classList.remove('hidden'); break;
        case 'results': resultsContent.classList.remove('hidden'); break;
        case 'error': errorState.classList.remove('hidden'); break;
    }
}

function resetToInput() {
    productName.value = '';
    productDesc.value = '';
    updateCharCount();
    setState('empty');
    currentResult = null;
    productDesc.focus();
}

// ===================== History =====================

function toggleHistory() {
    const isHidden = historyPanel.classList.contains('hidden');
    if (isHidden) {
        loadHistory();
    }
    historyPanel.classList.toggle('hidden');
}

async function loadHistory() {
    try {
        const res = await fetch('/api/history?limit=20');
        const data = await res.json();
        renderHistory(data.history || []);
    } catch (err) {
        historyList.innerHTML = '<p class="history-empty">Failed to load history.</p>';
    }
}

function renderHistory(items) {
    if (!items.length) {
        historyList.innerHTML = '<p class="history-empty">No analysis history yet.</p>';
        return;
    }

    historyList.innerHTML = items.map(item => {
        const meta = item.metadata;
        const time = new Date(item.timestamp).toLocaleString('en-IN', {
            month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
        });
        const name = item.product_name || 'Untitled Product';
        const desc = item.description || '';

        return `
            <div class="history-item" onclick="loadHistoryItem(${JSON.stringify(item).replace(/"/g, '&quot;')})">
                <div class="history-item-header">
                    <span class="history-item-name">${escapeHTML(name)}</span>
                    <span class="history-item-time">${time}</span>
                </div>
                <span class="history-item-category">${escapeHTML(meta.primary_category)} → ${escapeHTML(meta.sub_category)}</span>
                <p class="history-item-desc">${escapeHTML(desc)}</p>
            </div>
        `;
    }).join('');
}

window.loadHistoryItem = function(item) {
    currentResult = {
        success: true,
        product_name: item.product_name,
        metadata: item.metadata,
        processing_time_ms: 0,
    };
    productName.value = item.product_name || '';
    productDesc.value = item.description || '';
    updateCharCount();
    renderResults(currentResult);
    setState('results');
    historyPanel.classList.add('hidden');
    showToast('Loaded from history');
};

async function clearHistory() {
    if (!confirm('Clear all analysis history?')) return;
    try {
        await fetch('/api/history', { method: 'DELETE' });
        historyList.innerHTML = '<p class="history-empty">No analysis history yet.</p>';
        showToast('History cleared');
    } catch (err) {
        showToast('Failed to clear history');
    }
}

// ===================== Actions =====================

function copyTags() {
    if (!currentResult?.metadata?.seo_tags) return;
    const text = currentResult.metadata.seo_tags.join(', ');
    navigator.clipboard.writeText(text).then(() => {
        showToast('Tags copied to clipboard!');
    }).catch(() => {
        // Fallback
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        showToast('Tags copied to clipboard!');
    });
}

function exportJSON() {
    if (!currentResult) return;
    const json = JSON.stringify(currentResult.metadata, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `product-analysis-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('JSON exported!');
}

// ===================== Toast =====================

let toastTimeout;
function showToast(message) {
    clearTimeout(toastTimeout);
    toastMessage.textContent = message;
    toast.classList.remove('hidden', 'hiding');

    toastTimeout = setTimeout(() => {
        toast.classList.add('hiding');
        setTimeout(() => toast.classList.add('hidden'), 300);
    }, 2500);
}

// ===================== Helpers =====================

function escapeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// ===================== Init =====================
updateCharCount();
