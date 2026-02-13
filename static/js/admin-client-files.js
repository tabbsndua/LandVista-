(() => {
    const uploadForm = document.getElementById('clientFileUploadForm');
    const uploadBtn = document.getElementById('clientFileUploadBtn');
    const refreshBtn = document.getElementById('clientFileRefreshBtn');
    const feedback = document.getElementById('clientFilesFeedback');
    const body = document.getElementById('clientFilesBody');
    const filter = document.getElementById('clientFilesFilter');

    function showFeedback(message, type = 'success') {
        if (!feedback) return;
        feedback.style.display = 'block';
        feedback.className = `ops-alert ${type}`;
        feedback.textContent = message;
    }

    function escapeHTML(value) {
        return String(value || '').replace(/[&<>"']/g, (char) => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        }[char]));
    }

    function normalizeDate(value) {
        if (!value) return '';
        const d = new Date(value);
        if (Number.isNaN(d.getTime())) return String(value);
        return d.toLocaleString();
    }

    async function loadFiles() {
        if (!body) return;
        body.innerHTML = '<tr><td colspan="6">Loading files...</td></tr>';

        try {
            const query = filter?.value ? `?client_id=${encodeURIComponent(filter.value)}` : '';
            const response = await fetch(`/admin/client-files/list${query}`);
            const data = await response.json();
            if (!response.ok || !Array.isArray(data)) {
                throw new Error('Failed to load files');
            }

            if (!data.length) {
                body.innerHTML = '<tr><td colspan="6">No files found.</td></tr>';
                return;
            }

            body.innerHTML = data.map((item) => `
                <tr>
                    <td>${escapeHTML(item.filename || 'File')}</td>
                    <td>${escapeHTML(item.client_id || 'Unassigned')}</td>
                    <td>${escapeHTML(item.category || 'general')}</td>
                    <td>${escapeHTML(item.uploaded_by || 'admin')}</td>
                    <td>${escapeHTML(normalizeDate(item.created_at))}</td>
                    <td>
                        <div class="ops-row" style="justify-content:flex-start;">
                            <a class="ops-btn secondary" style="text-decoration:none; width:auto;" href="/admin/client-files/download/${encodeURIComponent(item._id)}">Download</a>
                            <button class="ops-btn warn" style="width:auto;" data-delete-file="${escapeHTML(item._id)}">Delete</button>
                        </div>
                    </td>
                </tr>
            `).join('');
        } catch (error) {
            body.innerHTML = '<tr><td colspan="6">Failed to load files.</td></tr>';
            showFeedback(error.message || 'Failed to load files', 'error');
        }
    }

    async function uploadFile(event) {
        event.preventDefault();
        if (!uploadForm) return;

        const formData = new FormData(uploadForm);
        uploadBtn.disabled = true;
        showFeedback('Uploading file...', 'success');

        try {
            const response = await fetch('/admin/client-files/upload', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            if (!response.ok || !data.success) {
                throw new Error(data.error || 'Upload failed');
            }

            uploadForm.reset();
            showFeedback('File uploaded successfully.', 'success');
            await loadFiles();
        } catch (error) {
            showFeedback(error.message || 'Upload failed', 'error');
        } finally {
            uploadBtn.disabled = false;
        }
    }

    async function deleteFile(fileId) {
        if (!confirm('Delete this file? This cannot be undone.')) return;

        try {
            const response = await fetch(`/admin/client-files/delete/${encodeURIComponent(fileId)}`, {
                method: 'POST'
            });
            const data = await response.json();
            if (!response.ok || !data.success) {
                throw new Error(data.error || 'Delete failed');
            }
            showFeedback('File deleted successfully.', 'success');
            await loadFiles();
        } catch (error) {
            showFeedback(error.message || 'Delete failed', 'error');
        }
    }

    uploadForm?.addEventListener('submit', uploadFile);
    refreshBtn?.addEventListener('click', loadFiles);
    filter?.addEventListener('change', loadFiles);

    body?.addEventListener('click', (event) => {
        const target = event.target.closest('[data-delete-file]');
        if (!target) return;
        const fileId = target.getAttribute('data-delete-file');
        if (fileId) deleteFile(fileId);
    });

    loadFiles();
})();
