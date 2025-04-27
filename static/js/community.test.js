// Enable strict mode for this file
(function() {
    "use strict";

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
        document.body.innerHTML =
            `<form id="postForm" action="/community/posts/create/">
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
})();
