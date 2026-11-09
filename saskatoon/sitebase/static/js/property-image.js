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
})
