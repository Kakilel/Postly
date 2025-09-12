document.addEventListener("DOMContentLoaded", function () {
    const likeButtons = document.querySelectorAll(".like-button");

    likeButtons.forEach(button => {
        button.addEventListener("click", function (e) {
            e.preventDefault();

            const postId = this.dataset.postId;
            const url = this.dataset.url;

            fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const likeCount = document.querySelector(`#like-count-${postId}`);
                    likeCount.textContent = data.likes;

                    // Toggle button text
                    this.textContent = data.liked ? "Unlike" : "Like";
                }
            });
        });
    });

    // Get CSRF token from cookie
    function getCSRFToken() {
        let cookieValue = null;
        let name = "csrftoken";
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
