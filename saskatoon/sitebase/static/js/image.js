document.addEventListener("DOMContentLoaded", function() {
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
});