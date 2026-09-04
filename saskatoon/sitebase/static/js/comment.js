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

    const $scrollContainer = $('#commentScrollbar');
        const $scrollBtn = $('#scrollOlderBtn');

        if ($scrollContainer.length && $scrollBtn.length) {
            if ($scrollContainer.data('mCustomScrollbar')) {
                $scrollContainer.mCustomScrollbar('destroy');
            }

            $scrollContainer.mCustomScrollbar({
                theme: 'minimal-dark',
                scrollInertia: 200,
                callbacks: {
                    whileScrolling: function () {
                        if (this.mcs && this.mcs.topPct < 90) {
                            $scrollBtn.removeClass('hidden');
                        } else {
                            $scrollBtn.addClass('hidden');
                        }
                    },
                    onOverflowY: function () {
                        $scrollBtn.removeClass('hidden');
                    },
                    onOverflowYNone: function () {
                        $scrollBtn.addClass('hidden');
                    }
                }
            });

            $scrollBtn.off('click').on('click', function (e) {
                e.preventDefault();
                $scrollContainer.mCustomScrollbar('scrollTo', 'bottom');
            });
        }
});
