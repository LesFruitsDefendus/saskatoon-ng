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

    // Upload Preview & Size Validation Handler
    const triggerInput = document.getElementById('trigger_file_input');
    
    if (triggerInput) {
        triggerInput.addEventListener('change', function(e) {
            if (this.files && this.files[0]) {
                const file = this.files[0];
                const MAX_SIZE_BYTES = 5 * 1024 * 1024; // 5MB

                const reader = new FileReader();
                reader.onload = function(event) {
                    const img = new Image();
                    img.onload = function() {
                        let w0 = img.width;
                        let h0 = img.height;
                        const maxPx = 1080;
                        let w1 = w0;
                        let h1 = h0;

                        if (Math.max(w0, h0) > maxPx) {
                            if (h0 > w0) {  // portrait
                                h1 = maxPx;
                                w1 = Math.round(w0 * h1 / h0);
                            } else {  // landscape
                                w1 = maxPx;
                                h1 = Math.round(h0 * w1 / h0);
                            }
                        }

                        const canvas = document.createElement('canvas');
                        canvas.width = w1;
                        canvas.height = h1;
                        const ctx = canvas.getContext('2d');
                        
                        ctx.imageSmoothingEnabled = true;
                        ctx.imageSmoothingQuality = 'high';
                        ctx.drawImage(img, 0, 0, w1, h1);

                        // Convert canvas to a JPEG blob and check its processed size
                        canvas.toBlob(function(blob) {
                            if (blob.size > MAX_SIZE_BYTES) {
                                const sizeMB = (blob.size / (1024 * 1024)).toFixed(1);
                                alert("Processed file size too large (" + sizeMB + "MB). Maximum allowed size is 5MB.");
                                
                                triggerInput.value = '';
                                return;
                            }

                            // 1. Set the preview image using the compressed blob URL
                            const previewImg = document.getElementById('imagePreview');
                            if (previewImg) {
                                previewImg.src = URL.createObjectURL(blob);
                                previewImg.style.display = 'inline-block';
                            }

                            // 2. Transfer the original file to the modal's form input
                            const modalFileInput = document.getElementById('modal_file_input');
                            if (modalFileInput) {
                                modalFileInput.files = e.target.files;
                            }

                            // 3. Open the modal
                            $('#imageUploadModal').modal('show');
                        }, 'image/jpeg', 0.9);
                    };
                    img.src = event.target.result;
                };
                reader.readAsDataURL(file);
            }
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