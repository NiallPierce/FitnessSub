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

    const setupDOM = () => {
        document.body.innerHTML = `
            <form id="postForm">
                <textarea name="content">Test post content</textarea>
                <input type="hidden" name="csrfmiddlewaretoken" value="test-token">
            </form>
            <div class="post" data-post-id="1">
                <button class="like-post" data-post-id="1">
                    <span class="like-count">0</span>
                </button>
                <button class="delete-post" data-post-id="1">Delete</button>
                <form class="comment-form" data-post-id="1">
                    <textarea name="content">Test comment</textarea>
                    <input type="hidden" name="csrfmiddlewaretoken" value="test-token">
                </form>
                <div class="comment" data-comment-id="1">
                    <button class="like-comment" data-comment-id="1">
                        <span class="like-count">0</span>
                    </button>
                    <button class="delete-comment" data-comment-id="1">Delete</button>
                </div>
            </div>
        `;

        // Mock form actions
        const postForm = document.getElementById('postForm');
        Object.defineProperty(postForm, 'action', {
            get: () => '/community/posts/create/'
        });

        const commentForm = document.querySelector('.comment-form');
        Object.defineProperty(commentForm, 'action', {
            get: () => '/community/posts/1/comment/'
        });
    };

    describe('Community Features', () => {
        beforeEach(() => {
            setupDOM();
            jest.clearAllMocks();
            // Trigger DOMContentLoaded event
            const event = new Event('DOMContentLoaded');
            document.dispatchEvent(event);
        });

        describe('Post Creation', () => {
            test('handles successful post creation', async () => {
                const form = document.getElementById('postForm');
                form.dispatchEvent(new Event('submit'));
                await Promise.resolve();
                expect(global.fetch).toHaveBeenCalledWith(
                    '/community/posts/create/',
                    expect.objectContaining({
                        method: 'POST',
                        headers: expect.objectContaining({
                            'X-CSRFToken': 'test-token'
                        })
                    })
                );
            });

            test('handles post creation error', async () => {
                const mockResponse = {
                    json: () => Promise.resolve({ success: false, error: 'Test error' })
                };
                global.fetch.mockImplementationOnce(() => Promise.resolve(mockResponse));
                
                const form = document.getElementById('postForm');
                form.dispatchEvent(new Event('submit'));
                
                // Wait for all promises to resolve
                await new Promise(resolve => setTimeout(resolve, 0));
                await new Promise(resolve => setTimeout(resolve, 0));
                
                expect(global.alert).toHaveBeenCalledWith('Error creating post: Test error');
            });

            test('handles empty post content', async () => {
                const form = document.getElementById('postForm');
                form.querySelector('textarea[name="content"]').value = '';
                form.dispatchEvent(new Event('submit'));
                await Promise.resolve();
                expect(global.alert).toHaveBeenCalledWith('Please enter some content');
            });
        });

        describe('Post Likes', () => {
            test('handles successful post like', async () => {
                const likeButton = document.querySelector('.like-post');
                likeButton.click();
                await Promise.resolve();
                expect(global.fetch).toHaveBeenCalledWith(
                    '/community/posts/1/like/',
                    expect.objectContaining({
                        method: 'POST',
                        headers: expect.objectContaining({
                            'X-CSRFToken': 'test-token'
                        })
                    })
                );
            });

            test('handles post like error', async () => {
                const mockResponse = {
                    json: () => Promise.resolve({ success: false, error: 'Like error' })
                };
                global.fetch.mockImplementationOnce(() => Promise.resolve(mockResponse));
                
                const likeButton = document.querySelector('.like-post');
                likeButton.click();
                
                // Wait for all promises to resolve
                await new Promise(resolve => setTimeout(resolve, 0));
                await new Promise(resolve => setTimeout(resolve, 0));
                
                expect(global.alert).toHaveBeenCalledWith('Error liking post: Like error');
            });
        });

        describe('Comment Creation', () => {
            test('handles successful comment creation', async () => {
                const commentForm = document.querySelector('.comment-form');
                commentForm.dispatchEvent(new Event('submit'));
                await Promise.resolve();
                expect(global.fetch).toHaveBeenCalledWith(
                    '/community/posts/1/comment/',
                    expect.objectContaining({
                        method: 'POST',
                        headers: expect.objectContaining({
                            'X-CSRFToken': 'test-token'
                        })
                    })
                );
            });

            test('handles empty comment content', async () => {
                const commentForm = document.querySelector('.comment-form');
                commentForm.querySelector('textarea[name="content"]').value = '';
                commentForm.dispatchEvent(new Event('submit'));
                await Promise.resolve();
                expect(global.alert).toHaveBeenCalledWith('Please enter some content');
            });
        });

        describe('Comment Likes', () => {
            test('handles successful comment like', async () => {
                const likeButton = document.querySelector('.like-comment');
                likeButton.click();
                await Promise.resolve();
                expect(global.fetch).toHaveBeenCalledWith(
                    '/community/comments/1/like/',
                    expect.objectContaining({
                        method: 'POST',
                        headers: expect.objectContaining({
                            'X-CSRFToken': 'test-token'
                        })
                    })
                );
            });
        });

        describe('Post Deletion', () => {
            test('handles post deletion with confirmation', async () => {
                global.confirm.mockReturnValueOnce(true);
                const deleteButton = document.querySelector('.delete-post');
                deleteButton.click();
                await Promise.resolve();
                expect(global.fetch).toHaveBeenCalledWith(
                    '/community/posts/1/delete/',
                    expect.objectContaining({
                        method: 'POST',
                        headers: expect.objectContaining({
                            'X-CSRFToken': 'test-token'
                        })
                    })
                );
            });

            test('cancels post deletion when not confirmed', async () => {
                global.confirm.mockReturnValueOnce(false);
                const deleteButton = document.querySelector('.delete-post');
                deleteButton.click();
                await Promise.resolve();
                expect(global.fetch).not.toHaveBeenCalled();
            });
        });

        describe('Comment Deletion', () => {
            test('handles comment deletion with confirmation', async () => {
                global.confirm.mockReturnValueOnce(true);
                const deleteButton = document.querySelector('.delete-comment');
                deleteButton.click();
                await Promise.resolve();
                expect(global.fetch).toHaveBeenCalledWith(
                    '/community/comments/1/delete/',
                    expect.objectContaining({
                        method: 'POST',
                        headers: expect.objectContaining({
                            'X-CSRFToken': 'test-token'
                        })
                    })
                );
            });
        });
    });
})();
