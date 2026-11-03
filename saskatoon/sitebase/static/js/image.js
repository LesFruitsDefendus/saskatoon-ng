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
    document.querySelectorAll('.edit-image-btn').forEach(button => {
        button.addEventListener('click', function() {
            const imageId = this.getAttribute('data-image-id');
            const viewDiv = document.getElementById(`image-view-${imageId}`);
            const editDiv = document.getElementById(`image-edit-${imageId}`);
            
            if (viewDiv && editDiv) {
                viewDiv.style.display = 'none';
                editDiv.style.display = 'block';
            }
        });
    });

    document.querySelectorAll('.cancel-image-edit-btn').forEach(button => {
        button.addEventListener('click', function() {
            const imageId = this.getAttribute('data-image-id');
            const viewDiv = document.getElementById(`image-view-${imageId}`);
            const editDiv = document.getElementById(`image-edit-${imageId}`);
            
            if (viewDiv && editDiv) {
                editDiv.style.display = 'none';
                viewDiv.style.display = 'block';
            }
        });
    });
});