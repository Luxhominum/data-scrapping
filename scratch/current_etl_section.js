// RAW DATA IMPORT (SHOPEE & TIKTOK) & FACTORY MASTER RESTORE ENGINE
        // =========================================================================
        let parsedPendingTransactions = [];
        const MASTER_BACKUP_URL = 'https://orhjrktaujhmvxtlrybi.supabase.co/storage/v1/object/public/pge-data/master_factory_backup.json';
        const SERVICE_ROLE_KEY = 'SUPABASE_SERVICE_ROLE_KEY_PLACEHOLDER';

        function openPgeImportModal() {
            const modal = document.getElementById('pgeImportDataModal');
            if (!modal) return;
            resetImportModalState();
            modal.style.display = 'flex';
        }

        function closePgeImportModal() {
            const modal = document.getElementById('pgeImportDataModal');
            if (modal) modal.style.display = 'none';
            resetImportModalState();
        }

        function openMasterRestoreModal() {
            const modal = document.getElementById('pgeRestoreMasterModal');
            if (modal) modal.style.display = 'flex';
        }

        function closeMasterRestoreModal() {
            const modal = document.getElementById('pgeRestoreMasterModal');
            if (modal) modal.style.display = 'none';
        }

        function resetImportModalState() {
            parsedPendingTransactions = [];
            const fileInput = document.getElementById('pgeFileInput');
            if (fileInput) fileInput.value = '';
            const previewCard = document.getElementById('pgeImportPreviewCard');
            if (previewCard) previewCard.style.display = 'none';
            const errCard = document.getElementById('pgeImportErrorCard');
            if (errCard) errCard.style.display = 'none';
            const indicator = document.getElementById('pgeImportParsingIndicator');
            if (indicator) indicator.style.display = 'none';
            const btn = document.getElementById('btnConfirmImportSave');
            if (btn) {
                btn.disabled = true;
                btn.style.background = '#cbd5e1';
                btn.style.cursor = 'not-allowed';
            }
        }

        function handlePgeFileDrop(e) {
            e.preventDefault();
            const dt = e.dataTransfer;
            if (dt && dt.files && dt.files.length > 0) {
                processPgeUploadedFile(dt.files[0]);
            }
        }

        function handlePgeFileSelect(e) {
            if (e.target && e.target.files && e.target.files.length > 0) {
                processPgeUploadedFile(e.target.files[0]);
            }
        }

        async function processPgeUploadedFile(file) {
            if (!file) return;
            const indicator = document.getElementById('pgeImportParsingIndicator');
            const previewCard = document.getElementById('pgeImportPreviewCard');
            const errCard = document.getElementById('pgeImportErrorCard');
            const btn = document.getElementById('btnConfirmImportSave');

            if (errCard) errCard.style.display = 'none';
            if (previewCard) previewCard.style.display = 'none';
            if (indicator) {
                indicator.style.display = 'block';
                document.getElementById('pgeImportParsingText').textContent = `Membaca ${file.name} (${(file.size / (1024*1024)).toFixed(2)} MB)...`;
            }

            try {
                if (typeof XLSX === 'undefined') {
                    throw new Error('Library SheetJS belum siap di browser.');
                }

                const data = await file.arrayBuffer();
                const workbook = XLSX.read(data, { type: 'array' });
                const firstSheetName = workbook.SheetNames[0];
                const worksheet = workbook.Sheets[firstSheetName];
                const rawJson = XLSX.utils.sheet_to_json(worksheet, { defval: '' });

                if (!rawJson || rawJson.length === 0) {
                    throw new Error('File tidak memuat baris data atau worksheet kosong.');
                }

                // Identify Platform from headers
                const firstRowKeys = Object.keys(rawJson[0]).map(k => k.toLowerCase().trim());
                let platform = 'Shopee';
                if (firstRowKeys.some(k => k.includes('order id') || k.includes('tiktok') || k.includes('seller sku'))) {
                    platform = 'TikTok';
                }

                // Existing transaction fingerprint set for deduplication
                const existingFingerprints = new Set(
                    rawData.map(d => `${d.Year}_${d.Month}_${(d.Product_Name||'').trim().toLowerCase()}_${(d.Variation||'').trim().toLowerCase()}_${Number(d.Revenue||0)}`)
                );

                const newRows = [];
                let skippedCount = 0;
                let totalAddedRev = 0;
                let totalAddedQty = 0;

                rawJson.forEach(row => {
                    // Extract fields based on platform
                    let orderDate = '';
                    let prodName = '';
                    let variation = '';
                    let revenue = 0;
                    let quantity = 1;

                    if (platform === 'Shopee') {
                        // Shopee standard export headers
                        orderDate = row['Waktu Pesanan Dibuat'] || row['Waktu Pembayaran Dilakukan'] || row['Order Creation Date'] || '';
                        prodName = row['Nama Produk'] || row['Product Name'] || '';
                        variation = row['Nama Variasi'] || row['Variation Name'] || '';
                        const rawPrice = String(row['Harga Diskon'] || row['Harga Awal'] || row['Total Pembayaran'] || 0).replace(/[^0-9.-]+/g, '');
                        revenue = parseFloat(rawPrice) || 0;
                        quantity = parseInt(row['Jumlah'] || row['Quantity'] || 1, 10) || 1;
                    } else {
                        // TikTok standard export headers
                        orderDate = row['Created Time'] || row['Waktu Dibuat'] || '';
                        prodName = row['Product Name'] || row['Nama Produk'] || '';
                        variation = row['Variation'] || row['Variasi'] || row['Seller SKU'] || '';
                        const rawPrice = String(row['Order Amount'] || row['Total Amount'] || row['SKU Subtotal'] || 0).replace(/[^0-9.-]+/g, '');
                        revenue = parseFloat(rawPrice) || 0;
                        quantity = parseInt(row['Quantity'] || row['Jumlah'] || 1, 10) || 1;
                    }

                    if (!prodName) return; // Skip non-product row

                    // Parse year and month
                    let year = 2026;
                    let month = '2026-08';
                    if (orderDate) {
                        const d = new Date(orderDate);
                        if (!isNaN(d.getTime())) {
                            year = d.getFullYear();
                            const mStr = String(d.getMonth() + 1).padStart(2, '0');
                            month = `${year}-${mStr}`;
                        } else {
                            // Try regex YYYY-MM
                            const mMatch = String(orderDate).match(/(\d{4})[-/](\d{2})/);
                            if (mMatch) {
                                year = parseInt(mMatch[1], 10);
                                month = `${year}-${mMatch[2]}`;
                            }
                        }
                    }

                    const normalizedProdName = String(prodName).trim();
                    const normalizedVar = String(variation).trim();
                    const fingerprint = `${year}_${month}_${normalizedProdName.toLowerCase()}_${normalizedVar.toLowerCase()}_${revenue}`;

                    if (existingFingerprints.has(fingerprint)) {
                        skippedCount++;
                        return;
                    }

                    existingFingerprints.add(fingerprint);
                    const tx = {
                        Year: year,
                        Month: month,
                        Platform: platform,
                        Product_Name: normalizedProdName,
                        Variation: normalizedVar,
                        Revenue: Math.round(revenue),
                        Quantity: quantity,
                        Orders: 1
                    };

                    newRows.push(tx);
                    totalAddedRev += tx.Revenue;
                    totalAddedQty += tx.Quantity;
                });

                if (indicator) indicator.style.display = 'none';

                if (newRows.length === 0 && skippedCount === 0) {
                    throw new Error('Tidak ditemukan baris transaksi produk yang valid pada berkas ini.');
                }

                parsedPendingTransactions = newRows;

                // Update Preview UI
                if (previewCard) previewCard.style.display = 'block';
                const fNameEl = document.getElementById('pgePreviewFileName');
                const platBadge = document.getElementById('pgePreviewPlatformBadge');
                const valCountEl = document.getElementById('pgePreviewValidCount');
                const newRevEl = document.getElementById('pgePreviewNewRevenue');
                const newQtyEl = document.getElementById('pgePreviewNewQty');
                const skipEl = document.getElementById('pgePreviewSkippedCount');

                if (fNameEl) fNameEl.textContent = file.name;
                if (platBadge) {
                    platBadge.textContent = platform;
                    platBadge.style.background = platform === 'Shopee' ? 'rgba(238, 77, 45, 0.12)' : 'rgba(15, 23, 42, 0.12)';
                    platBadge.style.color = platform === 'Shopee' ? '#ee4d2d' : '#0f172a';
                }
                if (valCountEl) valCountEl.textContent = newRows.length.toLocaleString('id-ID');
                if (newRevEl) newRevEl.textContent = formatIDR(totalAddedRev);
                if (newQtyEl) newQtyEl.textContent = `${totalAddedQty.toLocaleString('id-ID')} Pcs`;
                if (skipEl) skipEl.textContent = `${skippedCount.toLocaleString('id-ID')} duplikat`;

                if (btn) {
                    btn.disabled = false;
                    btn.style.background = '#3b82f6';
                    btn.style.cursor = 'pointer';
                }

            } catch (err) {
                if (indicator) indicator.style.display = 'none';
                if (errCard) {
                    errCard.style.display = 'block';
                    document.getElementById('pgeImportErrorMsg').textContent = err.message || 'Format tidak dapat dibaca.';
                }
            }
        }

        async function commitPgeImportToCloud() {
            if (!parsedPendingTransactions || parsedPendingTransactions.length === 0) {
                alert('Tidak ada transaksi baru yang perlu disimpan.');
                return;
            }

            const btn = document.getElementById('btnConfirmImportSave');
            if (btn) {
                btn.disabled = true;
                btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Menyimpan ke Cloud...';
            }

            try {
                // 1. Combine new transactions with rawData
                const updatedRawData = [...rawData, ...parsedPendingTransactions];
                const jsonString = JSON.stringify(updatedRawData);

                // 2. Upload to Supabase Storage
                const uploadUrl = 'https://orhjrktaujhmvxtlrybi.supabase.co/storage/v1/object/pge-data/pge_data.json';
                const res = await fetch(uploadUrl, {
                    method: 'POST',
                    headers: {
                        'apikey': SERVICE_ROLE_KEY,
                        'Authorization': `Bearer ${SERVICE_ROLE_KEY}`,
                        'Content-Type': 'application/json',
                        'x-upsert': 'true'
                    },
                    body: jsonString
                });

                if (!res.ok) {
                    const errText = await res.text();
                    throw new Error(`Gagal mengunggah ke Supabase (${res.status}): ${errText}`);
                }

                // 3. Save to local IndexedDB
                await saveCachedDataToIndexedDB(updatedRawData);

                // 4. Update in-memory state
                window.rawData = updatedRawData;
                rawData = updatedRawData;
                const updatedTableData = rawData.map(d => ({
                    ...d,
                    Category: classifyProduct(d.Product_Name, d.Variation)
                }));
                window.tableData = updatedTableData;
                tableData = updatedTableData;

                // 5. Reinitialize all dashboard views
                initMonthOptions();
                initCharts();
                if (dataTableInstance) {
                    dataTableInstance.clear();
                    dataTableInstance.rows.add(tableData);
                    dataTableInstance.draw();
                }

                const initialData = getFilteredData();
                updateKPIs(initialData);
                updateCharts(initialData);
                initForecastingEngine();

                const counterEl = document.getElementById('liveTxTotalBadge');
                if (counterEl) {
                    counterEl.textContent = `${rawData.length.toLocaleString('id-ID')} Transaksi`;
                }

                closePgeImportModal();
                alert(`Sukses! ${parsedPendingTransactions.length.toLocaleString('id-ID')} transaksi baru berhasil diintegrasikan ke basis data cloud PGE.`);

            } catch (e) {
                console.error('Commit import error:', e);
                alert('Terjadi kesalahan saat menyimpan ke cloud: ' + e.message);
                if (btn) {
                    btn.disabled = false;
                    btn.innerHTML = '<i class="bi bi-cloud-check"></i><span>Simpan & Sinkronkan ke Cloud</span>';
                }
            }
        }

        async function executeMasterFactoryRestore() {
            const btn = document.getElementById('btnExecuteMasterRestore');
            if (btn) {
                btn.disabled = true;
                btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Memulihkan...';
            }

            try {
                // 1. Fetch master factory backup
                const res = await fetch(MASTER_BACKUP_URL);
                if (!res.ok) throw new Error(`HTTP ${res.status} gagal mengambil backup master.`);
                const masterData = await res.json();

                if (!Array.isArray(masterData) || masterData.length === 0) {
                    throw new Error('Data master backup tidak valid.');
                }

                // 2. Overwrite pge_data.json on Supabase Storage
                const jsonString = JSON.stringify(masterData);
                const uploadUrl = 'https://orhjrktaujhmvxtlrybi.supabase.co/storage/v1/object/pge-data/pge_data.json';
                const uploadRes = await fetch(uploadUrl, {
                    method: 'POST',
                    headers: {
                        'apikey': SERVICE_ROLE_KEY,
                        'Authorization': `Bearer ${SERVICE_ROLE_KEY}`,
                        'Content-Type': 'application/json',
                        'x-upsert': 'true'
                    },
                    body: jsonString
                });

                if (!uploadRes.ok) {
                    throw new Error('Gagal menimpa pge_data.json di Supabase.');
                }

                // 3. Save to IndexedDB
                await saveCachedDataToIndexedDB(masterData);

                // 4. Update in-memory arrays
                window.rawData = masterData;
                rawData = masterData;
                const restoredTableData = rawData.map(d => ({
                    ...d,
                    Category: classifyProduct(d.Product_Name, d.Variation)
                }));
                window.tableData = restoredTableData;
                tableData = restoredTableData;

                // 5. Re-render dashboard
                initMonthOptions();
                initCharts();
                if (dataTableInstance) {
                    dataTableInstance.clear();
                    dataTableInstance.rows.add(tableData);
                    dataTableInstance.draw();
                }

                const initialData = getFilteredData();
                updateKPIs(initialData);
                updateCharts(initialData);
                initForecastingEngine();

                const counterEl = document.getElementById('liveTxTotalBadge');
                if (counterEl) {
                    counterEl.textContent = `${rawData.length.toLocaleString('id-ID')} Transaksi`;
                }

                closeMasterRestoreModal();
                alert(`Berhasil! Dasbor telah dipulihkan secara sempurna ke ${masterData.length.toLocaleString('id-ID')} transaksi master pabrikan.`);

            } catch (e) {
                console.error('Factory restore error:', e);
                alert('Gagal memulihkan data master: ' + e.message);
                if (btn) {
                    btn.disabled = false;
                    btn.textContent = 'Ya, Pulihkan Data';
                }
            }
        }

        // =========================================================================
        