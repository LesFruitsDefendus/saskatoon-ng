document.addEventListener("DOMContentLoaded", function() {
    // Lighbox Handlers
    const triggers = document.querySelectorAll('.lightbox-trigger');
    const $modal = $('#photoLightboxModal');
    const $lightboxCarousel = $('#lightboxCarousel');
    
    if (triggers.length) {
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
    }

    // Inline Image Description Edit Toggle
    document.querySelectorAll('.edit-image-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const cell = btn.closest('.photo-description-cell');
            const viewDiv = cell.querySelector('.photo-description-container');
            const editDiv = cell.querySelector('.image-edit-form-container');
            
            if (viewDiv && editDiv) {
                viewDiv.style.display = 'none';
                editDiv.style.display = 'block';

                const textarea = editDiv.querySelector('textarea');
                    if (textarea) {
                    textarea.focus();
                    textarea.setSelectionRange(textarea.value.length, textarea.value.length);
                }
            }
        });
    });

    document.querySelectorAll('.cancel-image-edit-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const cell = btn.closest('.photo-description-cell');
            const viewDiv = cell.querySelector('.photo-description-container');
            const editDiv = cell.querySelector('.image-edit-form-container');
            
            if (viewDiv && editDiv) {
                editDiv.style.display = 'none';
                viewDiv.style.display = '';
            }
        });
    });
});