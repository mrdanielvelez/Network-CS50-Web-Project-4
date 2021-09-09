const maxPostLength = 280;

document.addEventListener("DOMContentLoaded", () => {
    
    // Configure like buttons
    document.querySelectorAll(".like").forEach(likeButton => {
        likeButton.onclick = () => toggleLike(likeButton);
    })

    // Configure edit buttons
    document.querySelectorAll(".edit").forEach(editButton => {
        editButton.onclick = () => {
            const postId = editButton.dataset.postId;
            const contentField = document.querySelector(`#content${postId}`);
            const editForm = document.createElement("div");
            const saveButton = document.createElement("a");
            saveButton.innerHTML =
            `<button form="edit-post${postId}" type="submit" class="edit btn btn-sm btn-outline-secondary align-top rounded">Save</button>`
            editForm.innerHTML = 
            `<form id="edit-post${postId}">
            <div class="form-floating">
            <textarea required maxlength="280" id="edit-post" class="form-control" name="content">${contentField.innerHTML}</textarea>
            <label style="padding: .75rem .75rem;" for="edit-post" class="form-label text-white">Edit Post</label>
            </div>
            </form>`
            const editField = editForm.querySelector("#edit-post");
            editButton.replaceWith(saveButton);
            contentField.replaceWith(editForm);
            editField.focus();
            editField.setSelectionRange(editField.value.trim().length, editField.value.trim().length);
            editForm.querySelector("form").onsubmit = () => {
                const newContent = editField.value.trim();
                // Ensure edit length is not greater than maximum post length
                if (0 < newContent.length <= maxPostLength) {
                    editPost(newContent, postId, contentField, editButton, editForm, saveButton);
                } else {
                    console.log("Invalid post length.");
                }
                return false;
            }
        }
    })

    // Configure New Post button in dropdown menu
    document.querySelector("#write-post").onclick = () => window.location.href = "/#write"

    if (window.location.hash === "#write") {
        document.querySelector("#new-post").focus();
    }
})

function toggleLike(likeButton) {
    const postId = likeButton.dataset.postId;
    fetch(`/post/${postId}`, {
        method: "PUT",
        body: JSON.stringify({
            toggle_like: true
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            console.log(result.error);
        } else {
            const oldNumLikes = parseInt(document.querySelector(`#num-likes-${postId}`).innerHTML);
            const newNumLikes = parseInt(result.num_likes);
            const span = likeButton.querySelector("span");
            document.querySelector(`#num-likes-${postId}`).innerHTML = newNumLikes;
            newNumLikes > oldNumLikes ? span.innerHTML = "Unlike" : span.innerHTML = "Like";
        }
    })
    .catch(error => console.log(error))
}

function editPost(newContent, postId, contentField, editButton, editForm, saveButton) {
    fetch(`/post/${postId}`, {
        method: "PUT",
        body: JSON.stringify({
            "content": newContent
        })
    })
    .then(() => {
        contentField.innerHTML = newContent;
        editForm.replaceWith(contentField);
        saveButton.replaceWith(editButton);
    })
    .catch(error => console.log(error))
}
