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
                    if (this.mcs && this.mcs.topPct < 40) {
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

    const commentWrappers = document.querySelectorAll('.comment-wrapper');

    commentWrappers.forEach((wrapper) => {
        const commentP = wrapper.querySelector('.comment-text');
        const toggleBtn = wrapper.querySelector('.toggle-comment-btn');

        if (commentP && toggleBtn) {
            setTimeout(() => {
                if (commentP.scrollHeight > commentP.clientHeight || commentP.textContent.trim().length > 100) {
                    toggleBtn.style.display = 'inline-block';
                }
            }, 50);

            toggleBtn.addEventListener('click', () => {
                const moreText = toggleBtn.getAttribute('data-more-text') || 'Read more';
                const lessText = toggleBtn.getAttribute('data-less-text') || 'Read less';

                if (commentP.classList.contains('collapsed-comment')) {
                    commentP.classList.remove('collapsed-comment');
                    commentP.classList.add('expanded-comment');
                    toggleBtn.textContent = lessText;
                } else {
                    commentP.classList.remove('expanded-comment');
                    commentP.classList.add('collapsed-comment');
                    toggleBtn.textContent = moreText;
                }
            });
        }
    });
});
