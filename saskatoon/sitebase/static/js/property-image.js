document.addEventListener("DOMContentLoaded", function() {
    // Lighbox Handlers
    const triggers = document.querySelectorAll('.lightbox-trigger');
    if (!triggers.length) return;
    
    const $modal = $('#photoLightboxModal');
    const $lightboxCarousel = $('#lightboxCarousel');
    
    triggers.forEach(img => {
        img.addEventListener('click', function() {
            const slideIndex = parseInt(this.getAttribute('data-slide-index'), 10);
                
            $modal.modal('show');
                
            if (!isNaN(slideIndex)) {
                $lightboxCarousel.carousel(slideIndex);
            }
        });
    });
        
    $modal.on('shown.bs.modal', function () {
        $lightboxCarousel.focus();
    });

    // Reopen the lightbox on a photo (fragment set by the upload and update views)
    const hashMatch = window.location.hash.match(/^#photo-(\d+)$/);
    if (hashMatch) {
        const trigger = document.querySelector(
            `#photoCarousel .lightbox-trigger[data-photo-id="${hashMatch[1]}"]`
        );
        if (trigger) trigger.click();
        // Drop the fragment so a refresh doesn't reopen the lightbox
        history.replaceState(null, '', window.location.pathname + window.location.search);
    }

    // Description editor handlers
    function editorParts(cell) {
        return {
            view: cell.querySelector('.image-description-view'),
            form: cell.querySelector('.image-edit-form'),
            textarea: cell.querySelector('.image-edit-textarea'),
            toggle: cell.querySelector('.image-edit-toggle')
        };
    }

    function openEditor(cell) {
        const p = editorParts(cell);
        p.view.hidden = true;
        p.form.hidden = false;
        p.textarea.focus();
        const end = p.textarea.value.length;
        p.textarea.setSelectionRange(end, end);
    }

    function closeEditor(cell, restoreFocus) {
        const p = editorParts(cell);
        if (!p.form || p.form.hidden) return;
        p.textarea.value = p.textarea.defaultValue; // discard unsaved edits
        p.form.hidden = true;
        p.view.hidden = false;
        if (restoreFocus) p.toggle.focus();
    }

    function closeAllEditors() {
        document.querySelectorAll('.photo-description-cell').forEach(cell => closeEditor(cell, false));
    }

    document.querySelectorAll('.image-edit-toggle').forEach(btn => {
        btn.addEventListener('click', () => openEditor(btn.closest('.photo-description-cell')));
    });

    document.querySelectorAll('.image-edit-cancel').forEach(btn => {
        btn.addEventListener('click', () => closeEditor(btn.closest('.photo-description-cell'), true));
    });

    // Capture phase so Escape cancels the edit instead of closing the modal
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && e.target.classList.contains('image-edit-textarea')) {
            e.preventDefault();
            e.stopPropagation();
            closeEditor(e.target.closest('.photo-description-cell'), true);
        }
    }, true);

    $lightboxCarousel.on('slide.bs.carousel', closeAllEditors);
    $modal.on('hidden.bs.modal', closeAllEditors);

});
