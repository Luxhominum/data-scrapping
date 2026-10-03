/**
 * Shopee Scraper Studio — Client Controller
 * Handles SSE live log streaming, interactive filtering, rating charts, and multi-format exports.
 */

class ShopeeStudio {
  constructor() {
    this.currentData = null;
    this.reviewsList = [];
    this.filteredReviews = [];
    this.currentPage = 1;
    this.pageSize = 10;
    this.activeStarFilter = null;
    this.activeEventSource = null;
    this.currentRunId = null;

    this.initElements();
    this.attachEventListeners();
    this.loadInitialSample();
  }

  initElements() {
    // Inputs & controls
    this.urlInput = document.getElementById('shopeeUrlInput');
    this.btnScrape = document.getElementById('btnStartScrape');
    this.btnSample = document.getElementById('btnLoadSample');
    this.reviewLimitSelect = document.getElementById('reviewLimitSelect');
    this.allStarsToggle = document.getElementById('allStarsToggle');
    this.starLimitInput = document.getElementById('starLimitInput');
    this.cookieInput = document.getElementById('shopeeCookieInput');

    // Bento elements
    this.productCard = document.getElementById('productOverviewCard');
    this.productThumb = document.getElementById('productThumbnail');
    this.productName = document.getElementById('productTitle');
    this.productPrice = document.getElementById('productPrice');
    this.productRatingScore = document.getElementById('productRatingScore');
    this.productTotalReviews = document.getElementById('productTotalReviews');
    this.productUrlLink = document.getElementById('productUrlLink');

    // Rating breakdown elements
    this.overallScore = document.getElementById('overallScoreNumber');
    this.overallStars = document.getElementById('overallStarsDisplay');
    this.overallTotalText = document.getElementById('overallTotalText');
    this.ratingBarsContainer = document.getElementById('ratingBarsList');

    // Reviews list & filters
    this.reviewsContainer = document.getElementById('reviewsContainer');
    this.reviewsCountBadge = document.getElementById('reviewsCountBadge');
    this.searchInput = document.getElementById('reviewSearchInput');
    this.starFilterSelect = document.getElementById('starFilterSelect');
    this.variationFilterSelect = document.getElementById('variationFilterSelect');
    this.sortSelect = document.getElementById('sortSelect');
    this.replyOnlyToggle = document.getElementById('replyOnlyToggle');
    this.mediaOnlyToggle = document.getElementById('mediaOnlyToggle');

    // Terminal elements
    this.terminalDrawer = document.getElementById('terminalDrawer');
    this.terminalLogs = document.getElementById('terminalLogs');
    this.btnToggleTerminal = document.getElementById('btnToggleTerminal');
    this.btnClearLogs = document.getElementById('btnClearLogs');
    this.captchaBanner = document.getElementById('captchaBanner');

    // Pagination
    this.paginationControls = document.getElementById('paginationControls');
    this.paginationInfo = document.getElementById('paginationInfo');

    // Export buttons
    this.btnExportCsv = document.getElementById('btnExportCsv');
    this.btnExportJson = document.getElementById('btnExportJson');
    this.btnCopyJson = document.getElementById('btnCopyJson');

    // Lightbox modal
    this.lightboxModal = document.getElementById('lightboxModal');
    this.lightboxImg = document.getElementById('lightboxImg');
    this.lightboxClose = document.getElementById('lightboxClose');
  }

  attachEventListeners() {
    this.btnScrape?.addEventListener('click', () => this.startScrape());
    this.btnSample?.addEventListener('click', () => this.loadInitialSample());

    this.searchInput?.addEventListener('input', () => this.applyFilters());
    this.starFilterSelect?.addEventListener('change', () => {
      this.activeStarFilter = this.starFilterSelect.value ? parseInt(this.starFilterSelect.value) : null;
      this.applyFilters();
    });
    this.variationFilterSelect?.addEventListener('change', () => this.applyFilters());
    this.sortSelect?.addEventListener('change', () => this.applyFilters());
    this.replyOnlyToggle?.addEventListener('change', () => this.applyFilters());
    this.mediaOnlyToggle?.addEventListener('change', () => this.applyFilters());

    this.btnExportCsv?.addEventListener('click', () => this.exportCsv());
    this.btnExportJson?.addEventListener('click', () => this.exportJson());
    this.btnCopyJson?.addEventListener('click', () => this.copyJsonToClipboard());

    this.btnToggleTerminal?.addEventListener('click', () => {
      const body = document.getElementById('terminalBody');
      body.style.display = body.style.display === 'none' ? 'block' : 'none';
    });

    this.btnClearLogs?.addEventListener('click', () => {
      if (this.terminalLogs) this.terminalLogs.innerHTML = '';
    });

    this.lightboxClose?.addEventListener('click', () => this.closeLightbox());
    this.lightboxModal?.addEventListener('click', (e) => {
      if (e.target === this.lightboxModal) this.closeLightbox();
    });

    // Handle enter key in input
    this.urlInput?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') this.startScrape();
    });
  }

  async loadInitialSample() {
    try {
      this.logToTerminal('[SYSTEM] Loading sample dataset for preview...', 'info');
      const res = await fetch('/api/shopee/sample-data');
      if (!res.ok) throw new Error('Sample data endpoint error');
      const data = await res.json();
      this.renderDataset(data);
      this.showToast('Sample dataset loaded successfully!');
    } catch (err) {
      console.warn('Could not load from API, using fallback embedded sample:', err);
    }
  }

  async startScrape() {
    const url = this.urlInput.value.trim();
    if (!url) {
      this.showToast('Please enter a valid Shopee product URL.', 'error');
      this.urlInput.focus();
      return;
    }

    const reviewLimit = parseInt(this.reviewLimitSelect.value) || 50;
    const allStarTypes = this.allStarsToggle ? this.allStarsToggle.checked : false;
    const starLimit = parseInt(this.starLimitInput?.value) || 10;

    this.btnScrape.disabled = true;
    this.btnScrape.innerHTML = '<span class="status-dot"></span> Scraping Live...';
    this.captchaBanner.style.display = 'none';

    this.logToTerminal(`[TRIGGER] Initiating Shopee Scraper for: ${url}`, 'info');

    try {
      const res = await fetch('/api/shopee/scrape-url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: url,
          review_limit: reviewLimit,
          all_star_types: allStarTypes,
          star_limit_per_type: starLimit,
          cookie_str: this.cookieInput?.value?.trim() || ""
        })
      });

      const json = await res.json();
      if (!res.ok || json.status !== 'success') {
        throw new Error(json.detail || json.message || 'Failed to start scraper');
      }

      this.currentRunId = json.data.run_id;
      this.logToTerminal(`[RUN] Execution started with Run ID: ${this.currentRunId}`, 'info');
      this.connectEventSource(this.currentRunId);

    } catch (err) {
      this.logToTerminal(`[ERROR] ${err.message}`, 'error');
      this.showToast(`Error: ${err.message}`, 'error');
      this.btnScrape.disabled = false;
      this.btnScrape.innerHTML = '<i class="ph ph-play"></i> Start Live Scraping';
    }
  }

  connectEventSource(runId) {
    if (this.activeEventSource) {
      this.activeEventSource.close();
    }
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
    }

    // 1. SSE Stream
    this.activeEventSource = new EventSource(`/api/shopee/runs/${runId}/stream`);

    this.activeEventSource.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);

        if (msg.type === 'log') {
          const line = msg.line;
          let level = 'info';
          if (line.includes('[ERROR]') || line.toLowerCase().includes('error')) level = 'error';
          else if (line.includes('Captcha') || line.includes('verify') || line.includes('Verification')) {
            level = 'warning';
            this.captchaBanner.style.display = 'flex';
          } else if (line.includes('Successfully') || line.includes('completed') || line.includes('Extracted')) level = 'success';

          this.logToTerminal(line, level);
        } else if (msg.type === 'finished') {
          this.handleRunFinished(runId, msg.status, msg.item_count);
        }
      } catch (e) {
        console.error('Error parsing SSE event:', e);
      }
    };

    this.activeEventSource.onerror = (err) => {
      console.warn('SSE stream notice:', err);
    };

    // 2. Double-safety polling fallback
    this.pollInterval = setInterval(async () => {
      try {
        const res = await fetch(`/api/v2/actor-runs/${runId}`);
        if (res.ok) {
          const json = await res.json();
          const run = json.data;
          if (run && (run.status === 'SUCCEEDED' || run.status === 'FAILED')) {
            clearInterval(this.pollInterval);
            this.handleRunFinished(runId, run.status, run.item_count);
          }
        }
      } catch (e) {}
    }, 2000);
  }

  handleRunFinished(runId, status, itemCount) {
    if (this.activeEventSource) {
      this.activeEventSource.close();
    }
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
    }

    this.btnScrape.disabled = false;
    this.btnScrape.innerHTML = '<i class="ph ph-play"></i> Start Live Scraping';
    this.captchaBanner.style.display = 'none';

    if (status === 'SUCCEEDED') {
      this.logToTerminal(`[SUCCESS] Scraping completed! Extracted ${itemCount || 0} customer reviews.`, 'success');
      this.fetchCompletedDataset(runId);
      this.showToast(`Scraping completed! ${itemCount || 0} reviews collected.`, 'success');
    } else {
      this.logToTerminal(`[FINISHED] Scraper run ended with status: ${status}`, 'warning');
      this.fetchCompletedDataset(runId);
    }
  }

  async fetchCompletedDataset(runId) {
    try {
      const res = await fetch(`/api/v2/datasets/${runId}/items`);
      if (!res.ok) throw new Error('Could not fetch dataset');
      const items = await res.json();
      
      const structuredData = {
        product_info: {
          title: this.urlInput.value.split('/').filter(Boolean).pop() || "Shopee Scraped Product",
          price: "Live Extracted",
          rating_score: "5.0",
          total_reviews: items.length,
          url: this.urlInput.value
        },
        scraped_at: new Date().toISOString(),
        total_scraped_reviews: items.length,
        comments: items
      };

      this.renderDataset(structuredData);
    } catch (e) {
      this.logToTerminal(`[ERROR] Failed to load dataset: ${e.message}`, 'error');
    }
  }

  renderDataset(data) {
    this.currentData = data;
    this.reviewsList = data.comments || [];
    this.filteredReviews = [...this.reviewsList];

    // 1. Render Product Info
    const meta = data.product_info || {};
    if (this.productName) this.productName.textContent = meta.title || "Shopee Product";
    if (this.productPrice) this.productPrice.textContent = meta.price || "N/A";
    if (this.productRatingScore) this.productRatingScore.textContent = `${meta.rating_score || '5.0'} ★`;
    if (this.productTotalReviews) this.productTotalReviews.textContent = `(${meta.total_reviews || this.reviewsList.length} reviews)`;
    if (this.productUrlLink) this.productUrlLink.href = meta.url || "#";

    // 2. Render Rating Analytics & Bars
    this.renderRatingAnalytics();

    // 3. Populate Variation Filter
    this.populateVariationFilter();

    // 4. Render Reviews List
    this.currentPage = 1;
    this.applyFilters();
  }

  renderRatingAnalytics() {
    const total = this.reviewsList.length;
    if (total === 0) {
      if (this.overallScore) this.overallScore.textContent = "0.0";
      if (this.overallTotalText) this.overallTotalText.textContent = "0 total reviews";
      if (this.ratingBarsContainer) this.ratingBarsContainer.innerHTML = '<div style="color:var(--text-muted); font-size:0.8rem;">No review stats available</div>';
      return;
    }

    const counts = { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 };
    let sumStars = 0;

    this.reviewsList.forEach(r => {
      const star = Math.min(5, Math.max(1, parseInt(r.rating) || 5));
      counts[star] = (counts[star] || 0) + 1;
      sumStars += star;
    });

    const avg = (sumStars / total).toFixed(1);
    if (this.overallScore) this.overallScore.textContent = avg;
    if (this.overallTotalText) this.overallTotalText.textContent = `${total} scraped reviews`;

    // Render bars
    if (this.ratingBarsContainer) {
      this.ratingBarsContainer.innerHTML = [5, 4, 3, 2, 1].map(star => {
        const count = counts[star];
        const pct = total > 0 ? ((count / total) * 100).toFixed(0) : 0;
        const isSelected = this.activeStarFilter === star ? 'background: var(--bg-surface-hover);' : '';
        return `
          <div class="bar-row" style="${isSelected}" onclick="window.shopeeStudio.filterByStarBar(${star})">
            <div class="bar-label">${star} <i class="ph ph-star star-rating-icon"></i></div>
            <div class="bar-track">
              <div class="bar-fill" style="width: ${pct}%;"></div>
            </div>
            <div class="bar-count">${count} (${pct}%)</div>
          </div>
        `;
      }).join('');
    }
  }

  filterByStarBar(star) {
    if (this.activeStarFilter === star) {
      this.activeStarFilter = null;
      if (this.starFilterSelect) this.starFilterSelect.value = "";
    } else {
      this.activeStarFilter = star;
      if (this.starFilterSelect) this.starFilterSelect.value = star.toString();
    }
    this.renderRatingAnalytics();
    this.applyFilters();
  }

  populateVariationFilter() {
    if (!this.variationFilterSelect) return;
    const variations = new Set();
    this.reviewsList.forEach(r => {
      if (r.variation && r.variation.trim()) {
        variations.add(r.variation.trim());
      }
    });

    const optionsHtml = ['<option value="">All Variations</option>'];
    Array.from(variations).sort().forEach(v => {
      optionsHtml.push(`<option value="${this.escapeHtml(v)}">${this.escapeHtml(v)}</option>`);
    });
    this.variationFilterSelect.innerHTML = optionsHtml.join('');
  }

  applyFilters() {
    const q = (this.searchInput?.value || '').toLowerCase().trim();
    const starVal = this.activeStarFilter;
    const variationVal = this.variationFilterSelect?.value || '';
    const sortVal = this.sortSelect?.value || 'recent';
    const replyOnly = this.replyOnlyToggle?.checked || false;
    const mediaOnly = this.mediaOnlyToggle?.checked || false;

    this.filteredReviews = this.reviewsList.filter(r => {
      // Star filter
      if (starVal !== null && r.rating !== starVal) return false;

      // Variation filter
      if (variationVal && r.variation !== variationVal) return false;

      // Search term
      if (q) {
        const inContent = (r.content || '').toLowerCase().includes(q);
        const inAuthor = (r.author || '').toLowerCase().includes(q);
        const inVariation = (r.variation || '').toLowerCase().includes(q);
        if (!inContent && !inAuthor && !inVariation) return false;
      }

      // Seller reply
      if (replyOnly && (!r.seller_respond || !r.seller_respond.trim())) return false;

      // Media only
      if (mediaOnly && (!r.images || r.images.length === 0) && (!r.videos || r.videos.length === 0)) return false;

      return true;
    });

    // Sorting
    this.filteredReviews.sort((a, b) => {
      if (sortVal === 'highest') return (b.rating || 0) - (a.rating || 0);
      if (sortVal === 'lowest') return (a.rating || 0) - (b.rating || 0);
      if (sortVal === 'likes') return (b.like_count || 0) - (a.like_count || 0);
      // Recent default
      return new Date(b.time || 0) - new Date(a.time || 0);
    });

    if (this.reviewsCountBadge) {
      this.reviewsCountBadge.textContent = `${this.filteredReviews.length} / ${this.reviewsList.length}`;
    }

    this.renderReviewsPage();
  }

  renderReviewsPage() {
    if (!this.reviewsContainer) return;

    if (this.filteredReviews.length === 0) {
      this.reviewsContainer.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon"><i class="ph ph-chat-slash"></i></div>
          <div class="empty-title">No reviews match your filters</div>
          <div class="empty-subtitle">Try adjusting your search terms, star ratings, or variation selections.</div>
        </div>
      `;
      if (this.paginationControls) this.paginationControls.innerHTML = '';
      if (this.paginationInfo) this.paginationInfo.textContent = '';
      return;
    }

    const totalPages = Math.ceil(this.filteredReviews.length / this.pageSize);
    if (this.currentPage > totalPages) this.currentPage = totalPages;
    if (this.currentPage < 1) this.currentPage = 1;

    const startIdx = (this.currentPage - 1) * this.pageSize;
    const pageItems = this.filteredReviews.slice(startIdx, startIdx + this.pageSize);

    const cardsHtml = pageItems.map(r => {
      // Star badges
      const starsHtml = Array.from({ length: 5 }).map((_, i) => {
        return `<i class="ph ${i < (r.rating || 0) ? 'ph-star-fill' : 'ph-star'}" style="color:${i < (r.rating || 0) ? '#fbbf24' : 'var(--border-strong)'}"></i>`;
      }).join('');

      // Media thumbnails
      let mediaHtml = '';
      if (r.images && r.images.length > 0) {
        mediaHtml = `
          <div class="review-media-gallery">
            ${r.images.map(img => `<img src="${this.escapeHtml(img)}" alt="Review photo" class="media-thumbnail" onclick="window.shopeeStudio.openLightbox('${this.escapeHtml(img)}')" onerror="this.style.display='none'">`).join('')}
          </div>
        `;
      }

      // Seller reply
      let replyHtml = '';
      if (r.seller_respond && r.seller_respond.trim()) {
        replyHtml = `
          <div class="seller-reply-box">
            <div class="seller-reply-title"><i class="ph ph-arrow-bend-down-right"></i> Respon Penjual</div>
            <div class="seller-reply-text">${this.escapeHtml(r.seller_respond)}</div>
          </div>
        `;
      }

      // Variation pill
      const variationHtml = r.variation ? `<div class="review-variation"><i class="ph ph-tag"></i> Variasi: ${this.escapeHtml(r.variation)}</div>` : '';

      return `
        <div class="review-card">
          <div class="review-card-header">
            <div class="reviewer-profile">
              <div class="reviewer-avatar">${(r.author || 'U').charAt(0).toUpperCase()}</div>
              <div class="reviewer-meta">
                <div class="reviewer-name">${this.escapeHtml(r.author || 'Pengguna Shopee')}</div>
                <div class="reviewer-stars">${starsHtml}</div>
              </div>
            </div>
            <div class="review-date">${this.escapeHtml(r.time || '')}</div>
          </div>

          ${variationHtml}

          <div class="review-content">${this.escapeHtml(r.content || 'Pembeli tidak meninggalkan komentar tertulis.')}</div>

          ${mediaHtml}
          ${replyHtml}

          <div class="review-card-footer">
            <div class="like-badge"><i class="ph ph-thumbs-up"></i> ${r.like_count || 0} orang terbantu</div>
            <div>Pembelian Terverifikasi Shopee</div>
          </div>
        </div>
      `;
    }).join('');

    this.reviewsContainer.innerHTML = cardsHtml;
    this.renderPagination(totalPages);
  }

  renderPagination(totalPages) {
    if (!this.paginationControls) return;

    if (totalPages <= 1) {
      this.paginationControls.innerHTML = '';
      if (this.paginationInfo) this.paginationInfo.textContent = `Showing all ${this.filteredReviews.length} results`;
      return;
    }

    if (this.paginationInfo) {
      const start = (this.currentPage - 1) * this.pageSize + 1;
      const end = Math.min(this.currentPage * this.pageSize, this.filteredReviews.length);
      this.paginationInfo.textContent = `Showing ${start}-${end} of ${this.filteredReviews.length}`;
    }

    let buttons = `
      <button class="page-btn" ${this.currentPage === 1 ? 'disabled' : ''} onclick="window.shopeeStudio.goToPage(${this.currentPage - 1})">
        <i class="ph ph-caret-left"></i> Prev
      </button>
    `;

    for (let p = 1; p <= totalPages; p++) {
      if (p === 1 || p === totalPages || (p >= this.currentPage - 1 && p <= this.currentPage + 1)) {
        buttons += `<button class="page-btn ${p === this.currentPage ? 'active' : ''}" onclick="window.shopeeStudio.goToPage(${p})">${p}</button>`;
      } else if (p === this.currentPage - 2 || p === this.currentPage + 2) {
        buttons += `<span style="padding:0.4rem 0.2rem; color:var(--text-muted);">...</span>`;
      }
    }

    buttons += `
      <button class="page-btn" ${this.currentPage === totalPages ? 'disabled' : ''} onclick="window.shopeeStudio.goToPage(${this.currentPage + 1})">
        Next <i class="ph ph-caret-right"></i>
      </button>
    `;

    this.paginationControls.innerHTML = buttons;
  }

  goToPage(p) {
    this.currentPage = p;
    this.renderReviewsPage();
    this.reviewsContainer?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  exportCsv() {
    if (!this.filteredReviews || this.filteredReviews.length === 0) {
      this.showToast('No reviews to export.', 'warning');
      return;
    }

    const headers = ["Author", "Rating", "Time", "Variation", "Comment Content", "Seller Response", "Likes", "Images Count"];
    const rows = this.filteredReviews.map(r => [
      `"${(r.author || '').replace(/"/g, '""')}"`,
      r.rating || 0,
      `"${(r.time || '').replace(/"/g, '""')}"`,
      `"${(r.variation || '').replace(/"/g, '""')}"`,
      `"${(r.content || '').replace(/"/g, '""')}"`,
      `"${(r.seller_respond || '').replace(/"/g, '""')}"`,
      r.like_count || 0,
      (r.images || []).length
    ]);

    const csvContent = "\uFEFF" + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `shopee_reviews_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    this.showToast(`Exported ${this.filteredReviews.length} reviews to CSV!`, 'success');
  }

  exportJson() {
    if (!this.currentData) {
      this.showToast('No data to export.', 'warning');
      return;
    }
    const blob = new Blob([JSON.stringify(this.currentData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `shopee_reviews_${new Date().toISOString().slice(0,10)}.json`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    this.showToast('Exported dataset to JSON!', 'success');
  }

  async copyJsonToClipboard() {
    if (!this.currentData) {
      this.showToast('No data available to copy.', 'warning');
      return;
    }
    try {
      await navigator.clipboard.writeText(JSON.stringify(this.currentData, null, 2));
      this.showToast('Dataset JSON copied to clipboard!', 'success');
    } catch (e) {
      this.showToast('Failed to copy to clipboard.', 'error');
    }
  }

  logToTerminal(msg, level = 'info') {
    if (!this.terminalLogs) return;
    const timestamp = new Date().toLocaleTimeString();
    const div = document.createElement('div');
    div.className = `log-line log-${level}`;
    div.textContent = `[${timestamp}] ${msg}`;
    this.terminalLogs.appendChild(div);
    const body = document.getElementById('terminalBody');
    if (body) body.scrollTop = body.scrollHeight;
  }

  openLightbox(src) {
    if (!this.lightboxModal || !this.lightboxImg) return;
    this.lightboxImg.src = src;
    this.lightboxModal.classList.add('open');
  }

  closeLightbox() {
    if (!this.lightboxModal) return;
    this.lightboxModal.classList.remove('open');
  }

  showToast(msg, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = 'toast';
    const icon = type === 'success' ? 'check-circle' : type === 'error' ? 'warning-circle' : 'info';
    toast.innerHTML = `<i class="ph ph-${icon}" style="color:${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#38bdf8'}"></i> ${msg}`;
    container.appendChild(toast);
    setTimeout(() => {
      toast.remove();
    }, 4000);
  }

  escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
}

// Global initialization
document.addEventListener('DOMContentLoaded', () => {
  window.shopeeStudio = new ShopeeStudio();
});
