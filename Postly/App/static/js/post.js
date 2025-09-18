document.addEventListener("DOMContentLoaded", () => {
  const likeButtons = document.querySelectorAll(".like-button");

  likeButtons.forEach((button) => {
    button.addEventListener("click", function (e) {
      e.preventDefault();

      const postId = this.dataset.postId;
      const url = this.dataset.url;

      fetch(url, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCSRFToken(),
          "X-Requested-With": "XMLHttpRequest",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            const likeCount = document.querySelector(`#like-count-${postId}`);
            if (likeCount) likeCount.textContent = data.likes;

            const icon = this.querySelector("i");
            if (icon) icon.classList.toggle("liked", data.liked);
          }
        })
        .catch((err) => console.error("Like error:", err));
    });
  });

const categorySelect = document.querySelector("#category");
if (categorySelect) {
  categorySelect.addEventListener("change", function () {
    const url = `/filter_posts?category=${this.value}`;
    fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } })
      .then(res => res.json())
      .then(data => {
        const postsContainer = document.querySelector("#posts-container");
        if (postsContainer) postsContainer.innerHTML = data.html;
      })
      .catch(err => console.error("Filter error:", err));
  });
}



const postViews = document.querySelectorAll(".post-views");

postViews.forEach((element) => {
  const postId = element.dataset.postId;
  const url = `/ajax/increment-view/${postId}/`;

  fetch(url, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCSRFToken(),
      "X-Requested-With": "XMLHttpRequest",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      element.textContent = data.views + " views";
    })
    .catch((err) => console.error("View error:", err));
});



  const commentForms = document.querySelectorAll(".comment-form");

  commentForms.forEach((form) => {
    form.addEventListener("submit", function (e) {
      e.preventDefault();

      const url = this.action;
      const formData = new FormData(this);

      fetch(url, {
        method: "POST",
        body: formData,
        headers: { "X-Requested-With": "XMLHttpRequest" },
      })
        .then((response) => response.text())
        .then((html) => {
          const postId = this.dataset.postId;
          const commentList = document.querySelector(
            `#comment-list-${postId}`
          );

          if (commentList) {
            commentList.innerHTML = html;
            this.reset(); // clear input after success
          }
        })
        .catch((err) => console.error("Comment error:", err));
    });
  });

  function getCSRFToken() {
    let cookieValue = null;
    const name = "csrftoken";
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
