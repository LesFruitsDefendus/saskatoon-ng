document.addEventListener('DOMContentLoaded', function () {
    document.addEventListener('click', function (e) {
        const editBtn = e.target.closest('.edit-comment-btn');
        if (editBtn) {
            const commentId = editBtn.getAttribute('data-comment-id');
            const viewContainer = document.getElementById(`comment-view-${commentId}`);
            const editContainer = document.getElementById(`comment-edit-${commentId}`);

            if (viewContainer && editContainer) {
                viewContainer.style.display = 'none';
                editContainer.style.display = 'block';

                const textarea = editContainer.querySelector('textarea');
                if (textarea) {
                    textarea.focus();
                    textarea.setSelectionRange(textarea.value.length, textarea.value.length);
                }
            }
        }

        const cancelBtn = e.target.closest('.cancel-edit-btn');
        if (cancelBtn) {
            const commentId = cancelBtn.getAttribute('data-comment-id');
            const viewContainer = document.getElementById(`comment-view-${commentId}`);
            const editContainer = document.getElementById(`comment-edit-${commentId}`);

            if (viewContainer && editContainer) {
                editContainer.style.display = 'none';
                viewContainer.style.display = '';
            }
        }
    });
});