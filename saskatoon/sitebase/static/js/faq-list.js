$(document).ready(function () {
        setupFAQ();
});

function setupFAQ() {
    var questions = document.querySelectorAll(".faq-question-row");
    questions.forEach(function (question) {
        var answer = question.closest('.faq-item').querySelector('.faq-answer');
        var icon = question.querySelector("i");

        // Set up answer toggle
        question.addEventListener("click", function () {
            question.classList.toggle("active");
            if (icon) {
                icon.classList.toggle("fa-plus");
                icon.classList.toggle("fa-minus");
            }

            if (answer.style.maxHeight) {
                answer.style.maxHeight = null;
            } else {
                answer.style.maxHeight = answer.scrollHeight + "px";
            }
        });

        // Collapse all answers by default
        if (answer) {
            answer.style.maxHeight = null;
            answer.style.overflow = "hidden";
            answer.style.transition = "max-height 0.3s";
        }
    });
}
