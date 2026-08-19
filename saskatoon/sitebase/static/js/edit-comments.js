document.addEventListener('DOMContentLoaded', function () {
    const editBtns = document.querySelectorAll('.edit-comment-btn');

    editBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
            const commentId = btn.getAttribute('data-comment-id');
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
        });
    });

    const cancelBtns = document.querySelectorAll('.cancel-edit-btn');

    cancelBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
            const commentId = btn.getAttribute('data-comment-id');
            const viewContainer = document.getElementById(`comment-view-${commentId}`);
            const editContainer = document.getElementById(`comment-edit-${commentId}`);

            if (viewContainer && editContainer) {
                editContainer.style.display = 'none';
                viewContainer.style.display = '';
            }
        });
    });
});