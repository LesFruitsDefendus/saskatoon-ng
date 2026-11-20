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
})
