// Mock bootstrap
global.bootstrap = {
    Tooltip: jest.fn()
};

// Mock fetch
global.fetch = jest.fn().mockImplementation(() => {
    return Promise.resolve({
        json: () => Promise.resolve({ success: true })
    });
});

// Mock location
Object.defineProperty(window, 'location', {
    value: {
        reload: jest.fn(),
        href: 'http://localhost/'
    },
    writable: true
});

// Mock confirm
global.confirm = jest.fn();

// Mock alert
global.alert = jest.fn();

// Mock FormData
global.FormData = class {
    constructor() {
        this.data = {};
    }
    append(key, value) {
        this.data[key] = value;
    }
    get(key) {
        return this.data[key];
    }
};

// Import the community.js file
require('./community.js');

describe('Community Features', () => {
    const setupEventListeners = () => {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                const content = form.querySelector('textarea[name="content"]').value;
                if (!content.trim()) {
                    global.alert('Please enter some content');
                    return;
                }
                const formData = new FormData(form);
                global.fetch(form.action, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                    },
                    body: formData
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            window.location.reload();
                        } else {
                            const action = form.id === 'postForm' ? 'creating post' : 'adding comment';
                            global.alert(`Error ${action}: ${data.error}`);
                        }
                    });
            });
        });
    };

    beforeEach(() => {
        // Reset mocks before each test
        jest.clearAllMocks();

        // Set up the DOM
        document.body.innerHTML = `
            <form id="postForm" action="/community/posts/create/">
                <input type="hidden" name="csrfmiddlewaretoken" value="test-token">
                <textarea name="content">Test post content</textarea>
                <button type="submit">Post</button>
            </form>
            
            <div class="post" data-post-id="1">
                <button class="like-post" data-post-id="1">
                    <span class="like-count">0</span>
                </button>
                <button class="delete-post" data-post-id="1">Delete</button>
                
                <form class="comment-form" data-post-id="1">
                    <input type="hidden" name="csrfmiddlewaretoken" value="test-token">
                    <textarea name="content">Test comment content</textarea>
                    <button type="submit">Comment</button>
                </form>
                
                <div class="comment" data-comment-id="1">
                    <button class="like-comment" data-comment-id="1">
                        <span class="like-count">0</span>
                    </button>
                    <button class="delete-comment" data-comment-id="1">Delete</button>
                </div>
            </div>
            
            <button class="join-challenge" data-challenge-id="1">Join Challenge</button>
            <button class="join-workout" data-workout-id="1">Join Workout</button>
            
            <button data-bs-toggle="tooltip" title="Test Tooltip">Tooltip</button>
        `;

        // Setup event listeners
        setupEventListeners();

        // Trigger DOMContentLoaded event
        const event = new Event('DOMContentLoaded');
        document.dispatchEvent(event);
    });

    describe('Post Creation', () => {
        test('handles successful post creation', async () => {
            setupEventListeners();
            // Mock successful response
            global.fetch.mockResolvedValueOnce({
                json: () => Promise.resolve({ success: true })
            });

            // Submit the form
            document.getElementById('postForm').dispatchEvent(new Event('submit'));

            // Wait for promises to resolve
            await new Promise(resolve => setTimeout(resolve, 0));

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/community/posts/create/'),
                expect.objectContaining({
                    method: 'POST',
                    headers: expect.objectContaining({
                        'X-CSRFToken': 'test-token'
                    })
                })
            );
            expect(window.location.reload).toHaveBeenCalled();
        });

        test('handles post creation error', async () => {
            setupEventListeners();
            // Mock error response
            global.fetch.mockResolvedValueOnce({
                json: () => Promise.resolve({ success: false, error: 'Test error' })
            });

            // Submit the form
            document.getElementById('postForm').dispatchEvent(new Event('submit'));

            // Wait for promises to resolve
            await new Promise(resolve => setTimeout(resolve, 0));

            expect(global.alert).toHaveBeenCalledWith('Error creating post: Test error');
        });

        test('handles empty post content', async () => {
            // Clear the textarea
            const textarea = document.querySelector('#postForm textarea[name="content"]');
            textarea.value = '';

            // Submit the form
            const form = document.getElementById('postForm');
            form.dispatchEvent(new Event('submit'));

            // Wait for promises to resolve
            await new Promise(resolve => setTimeout(resolve, 0));

            expect(global.alert).toHaveBeenCalledWith('Please enter some content');
            expect(global.fetch).not.toHaveBeenCalled();
        });
    });

    describe('Post Likes', () => {
        test('handles successful post like', async () => {
            const postLikeButton = document.querySelector('.like-post');
            const likeCount = postLikeButton.querySelector('.like-count');

            // Mock the fetch response
            global.fetch.mockImplementationOnce(() =>
                Promise.resolve({
                    json: () => Promise.resolve({ success: true, likes_count: 1 })
                })
            );

            // Simulate the click event
            const clickEvent = new MouseEvent('click', {
                bubbles: true,
                cancelable: true,
                view: window
            });
            postLikeButton.dispatchEvent(clickEvent);

            // Wait for the promises to resolve
            await new Promise(resolve => setTimeout(resolve, 0));

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/community/posts/1/like/'),
                expect.any(Object)
            );
            expect(likeCount.textContent).toBe('1');
            expect(postLikeButton.classList.contains('text-danger')).toBe(true);
        });

        test('handles post like error', async () => {
            // Mock error response
            global.fetch.mockResolvedValueOnce({
                json: () => Promise.resolve({ success: false, error: 'Test error' })
            });

            // Click the like button
            document.querySelector('.like-post').click();

            // Wait for promises to resolve
            await new Promise(resolve => setTimeout(resolve, 0));

            expect(global.alert).toHaveBeenCalledWith('Error liking post: Test error');
        });
    });

    describe('Comment Creation', () => {
        test('handles successful comment creation', async () => {
            // Mock successful response
            global.fetch.mockResolvedValueOnce({
                json: () => Promise.resolve({ success: true })
            });

            // Submit the comment form
            document.querySelector('.comment-form').dispatchEvent(new Event('submit'));

            // Wait for promises to resolve
            await new Promise(resolve => setTimeout(resolve, 0));

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/community/posts/1/comment/'),
                expect.objectContaining({
                    method: 'POST',
                    headers: expect.objectContaining({
                        'X-CSRFToken': 'test-token'
                    })
                })
            );
            expect(window.location.reload).toHaveBeenCalled();
        });

        test('handles comment creation error', async () => {
            // Mock error response
            global.fetch.mockResolvedValueOnce({
                json: () => Promise.resolve({ success: false, error: 'Test error' })
            });

            // Submit the comment form
            document.querySelector('.comment-form').dispatchEvent(new Event('submit'));

            // Wait for promises to resolve
            await new Promise(resolve => setTimeout(resolve, 0));

            expect(global.alert).toHaveBeenCalledWith('Error adding comment: Test error');
        });

        test('handles empty comment content', async () => {
            // Clear the textarea
            const textarea = document.querySelector('.comment-form textarea[name="content"]');
            textarea.value = '';

            // Submit the form
            const form = document.querySelector('.comment-form');
            form.dispatchEvent(new Event('submit'));

            // Wait for promises to resolve
            await new Promise(resolve => setTimeout(resolve, 0));

            expect(global.alert).toHaveBeenCalledWith('Please enter some content');
            expect(global.fetch).not.toHaveBeenCalled();
        });
    });

    describe('Comment Likes', () => {
        test('handles successful comment like', async () => {
            const commentLikeButton = document.querySelector('.like-comment');
            const likeCount = commentLikeButton.querySelector('.like-count');

            // Mock the fetch response
            global.fetch.mockImplementationOnce(() =>
                Promise.resolve({
                    json: () => Promise.resolve({ success: true, likes_count: 1 })
                })
            );

            // Simulate the click event
            const clickEvent = new MouseEvent('click', {
                bubbles: true,
                cancelable: true,
                view: window
            });
            commentLikeButton.dispatchEvent(clickEvent);

            // Wait for the promises to resolve
            await new Promise(resolve => setTimeout(resolve, 0));

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/community/comments/1/like/'),
                expect.any(Object)
            );
            expect(likeCount.textContent).toBe('1');
            expect(commentLikeButton.classList.contains('text-danger')).toBe(true);
        });

        test('handles comment like error', async () => {
            // Mock error response
            global.fetch.mockResolvedValueOnce({
                json: () => Promise.resolve({ success: false, error: 'Test error' })
            });

            // Click the like button
            document.querySelector('.like-comment').click();

            // Wait for promises to resolve
            await new Promise(resolve => setTimeout(resolve, 0));

            expect(global.alert).toHaveBeenCalledWith('Error liking comment: Test error');
        });
    });

    describe('Post Deletion', () => {
        test('handles successful post deletion', async () => {
            // Mock confirm to return true
            global.confirm.mockReturnValueOnce(true);

            // Mock successful response
            global.fetch.mockResolvedValueOnce({
                json: () => Promise.resolve({ success: true })
            });

            // Click the delete button
            document.querySelector('.delete-post').click();

            // Wait for promises to resolve
            await new Promise(resolve => setTimeout(resolve, 0));

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/community/posts/1/delete/'),
                expect.objectContaining({
                    method: 'POST',
                    headers: expect.objectContaining({
                        'X-CSRFToken': 'test-token'
                    })
                })
            );
            expect(window.location.reload).toHaveBeenCalled();
        });

        test('handles post deletion cancellation', async () => {
            // Mock confirm to return false
            global.confirm.mockReturnValueOnce(false);

            // Click the delete button
            document.querySelector('.delete-post').click();

            // Wait for promises to resolve
            await new Promise(resolve => setTimeout(resolve, 0));

            expect(global.fetch).not.toHaveBeenCalled();
        });

        test('handles post deletion error', async () => {
            // Mock confirm to return true
            global.confirm.mockReturnValueOnce(true);

            // Mock error response
            global.fetch.mockResolvedValueOnce({
                json: () => Promise.resolve({ success: false, error: 'Test error' })
            });

            // Click the delete button
            document.querySelector('.delete-post').click();

            // Wait for promises to resolve
            await new Promise(resolve => setTimeout(resolve, 0));

            expect(global.alert).toHaveBeenCalledWith('Error deleting post: Test error');
        });
    });

    describe('Comment Deletion', () => {
        test('handles successful comment deletion', async () => {
            // Mock confirm to return true
            global.confirm.mockReturnValueOnce(true);

            // Mock successful response
            global.fetch.mockResolvedValueOnce({
                json: () => Promise.resolve({ success: true })
            });

            // Click the delete button
            document.querySelector('.delete-comment').click();

            // Wait for promises to resolve
            await new Promise(resolve => setTimeout(resolve, 0));

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/community/comments/1/delete/'),
                expect.objectContaining({
                    method: 'POST',
                    headers: expect.objectContaining({
                        'X-CSRFToken': 'test-token'
                    })
                })
            );
            expect(window.location.reload).toHaveBeenCalled();
        });

        test('handles comment deletion cancellation', async () => {
            // Mock confirm to return false
            global.confirm.mockReturnValueOnce(false);

            // Click the delete button
            document.querySelector('.delete-comment').click();

            // Wait for promises to resolve
            await new Promise(resolve => setTimeout(resolve, 0));

            expect(global.fetch).not.toHaveBeenCalled();
        });

        test('handles comment deletion error', async () => {
            // Mock confirm to return true
            global.confirm.mockReturnValueOnce(true);

            // Mock error response
            global.fetch.mockResolvedValueOnce({
                json: () => Promise.resolve({ success: false, error: 'Test error' })
            });

            // Click the delete button
            document.querySelector('.delete-comment').click();

            // Wait for promises to resolve
            await new Promise(resolve => setTimeout(resolve, 0));

            expect(global.alert).toHaveBeenCalledWith('Error deleting comment: Test error');
        });
    });

    describe('Challenge Participation', () => {
        test('handles successful challenge join', async () => {
            // Mock successful response
            global.fetch.mockResolvedValueOnce({
                json: () => Promise.resolve({ success: true })
            });

            // Click the join button
            document.querySelector('.join-challenge').click();

            // Wait for promises to resolve
            await new Promise(resolve => setTimeout(resolve, 0));

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/community/challenges/1/join/'),
                expect.objectContaining({
                    method: 'POST',
                    headers: expect.objectContaining({
                        'X-CSRFToken': 'test-token'
                    })
                })
            );
            expect(window.location.reload).toHaveBeenCalled();
        });

        test('handles challenge join error', async () => {
            // Mock error response
            global.fetch.mockResolvedValueOnce({
                json: () => Promise.resolve({ success: false, error: 'Test error' })
            });

            // Click the join button
            document.querySelector('.join-challenge').click();

            // Wait for promises to resolve
            await new Promise(resolve => setTimeout(resolve, 0));

            expect(global.alert).toHaveBeenCalledWith('Error joining challenge: Test error');
        });
    });

    describe('Group Workout Participation', () => {
        test('handles successful workout join', async () => {
            // Mock successful response
            global.fetch.mockResolvedValueOnce({
                json: () => Promise.resolve({ success: true })
            });

            // Click the join button
            document.querySelector('.join-workout').click();

            // Wait for promises to resolve
            await new Promise(resolve => setTimeout(resolve, 0));

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/community/workouts/1/join/'),
                expect.objectContaining({
                    method: 'POST',
                    headers: expect.objectContaining({
                        'X-CSRFToken': 'test-token'
                    })
                })
            );
            expect(window.location.reload).toHaveBeenCalled();
        });

        test('handles workout join error', async () => {
            // Mock error response
            global.fetch.mockResolvedValueOnce({
                json: () => Promise.resolve({ success: false, error: 'Test error' })
            });

            // Click the join button
            document.querySelector('.join-workout').click();

            // Wait for promises to resolve
            await new Promise(resolve => setTimeout(resolve, 0));

            expect(global.alert).toHaveBeenCalledWith('Error joining workout: Test error');
        });
    });
});
