/* jshint esversion: 8, module: true */

(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {
        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.forEach(function (tooltipTriggerEl) {
            new bootstrap.Tooltip(tooltipTriggerEl);
        });

        // Handle post creation
        const postForm = document.getElementById('postForm');
        if (postForm) {
            postForm.addEventListener('submit', function(e) {
                e.preventDefault();
                const content = this.querySelector('textarea[name="content"]').value;
                if (!content.trim()) {
                    alert('Please enter some content');
                    return;
                }
                const formData = new FormData(this);

                fetch(this.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            location.reload();
                        } else {
                            alert('Error creating post: ' + data.error);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('An error occurred while creating the post.');
                    });
            });
        }

        // Handle post likes
        document.querySelectorAll('.like-post').forEach(button => {
            button.addEventListener('click', function() {
                const postId = this.dataset.postId;
                fetch(`/community/posts/${postId}/like/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            const likeCount = this.querySelector('.like-count');
                            if (likeCount) {
                                likeCount.textContent = data.likes_count ? data.likes_count.toString() : '0';
                            }
                            this.classList.toggle('text-danger');
                        } else {
                            alert('Error liking post: ' + data.error);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Error liking post: ' + error.message);
                    });
            });
        });

        // Handle comment creation
        document.querySelectorAll('.comment-form').forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                const content = this.querySelector('textarea[name="content"]').value;
                if (!content.trim()) {
                    alert('Please enter some content');
                    return;
                }
                const formData = new FormData(this);
                const postId = this.dataset.postId;

                fetch(`/community/posts/${postId}/comment/`, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            location.reload();
                        } else {
                            alert('Error adding comment: ' + data.error);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('An error occurred while adding the comment.');
                    });
            });
        });

        // Handle comment likes
        document.querySelectorAll('.like-comment').forEach(button => {
            button.addEventListener('click', function() {
                const commentId = this.dataset.commentId;
                fetch(`/community/comments/${commentId}/like/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            const likeCount = this.querySelector('.like-count');
                            if (likeCount) {
                                likeCount.textContent = data.likes_count ? data.likes_count.toString() : '0';
                            }
                            this.classList.toggle('text-danger');
                        } else {
                            alert('Error liking comment: ' + data.error);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Error liking comment: ' + error.message);
                    });
            });
        });

        // Handle post deletion
        document.querySelectorAll('.delete-post').forEach(button => {
            button.addEventListener('click', function() {
                if (confirm('Are you sure you want to delete this post?')) {
                    const postId = this.dataset.postId;
                    fetch(`/community/posts/${postId}/delete/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                        }
                    })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                location.reload();
                            } else {
                                alert('Error deleting post: ' + data.error);
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            alert('An error occurred while deleting the post.');
                        });
                }
            });
        });

        // Handle comment deletion
        document.querySelectorAll('.delete-comment').forEach(button => {
            button.addEventListener('click', function() {
                if (confirm('Are you sure you want to delete this comment?')) {
                    const commentId = this.dataset.commentId;
                    fetch(`/community/comments/${commentId}/delete/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                        }
                    })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                location.reload();
                            } else {
                                alert('Error deleting comment: ' + data.error);
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            alert('An error occurred while deleting the comment.');
                        });
                }
            });
        });

        // Handle challenge participation
        document.querySelectorAll('.join-challenge').forEach(button => {
            button.addEventListener('click', function() {
                const challengeId = this.dataset.challengeId;
                fetch(`/community/challenges/${challengeId}/join/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            location.reload();
                        } else {
                            alert('Error joining challenge: ' + data.error);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('An error occurred while joining the challenge.');
                    });
            });
        });

        // Handle group workout participation
        document.querySelectorAll('.join-workout').forEach(button => {
            button.addEventListener('click', function() {
                const workoutId = this.dataset.workoutId;
                fetch(`/community/workouts/${workoutId}/join/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            location.reload();
                        } else {
                            alert('Error joining workout: ' + data.error);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('An error occurred while joining the workout.');
                    });
            });
        });
    });
})();
