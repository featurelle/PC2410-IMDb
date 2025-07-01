'use strict';

const React = window.React;

const {useState, useEffect} = React;


function CommentSection({ defaultUserPic, loginUrl }) {
    const [comments, setComments] = useState([]);
    const url = `/api/rest/movies/${movieId}/comments/`
    // Comment structure:
    // {
    //     "id": 1,
    //     "movie_id": 12,
    //     "user": {
    //         "id": 2,
    //         "username": "alex",
    //         "profile": {
    //             "pic": "http://127.0.0.1:8000/media/imdb/users/Ie469oS5_400x400.jpeg"
    //         }
    //     },
    //     "timestamp": 01/01/2022 15:15,
    //     "body": "I think this movie is great!"
    // }

    // Fetch comments for the movie using an API endpoint
    const fetchComments = async () => {
        const response = await fetch(url);
        const comments = await response.json()
        setComments(comments);
    };

    useEffect(async () => await fetchComments(), []);

    // Handle form submission to post a new comment
    const handleSubmit = async (event) => {
        event.preventDefault();

        const form = event.target

        try {
            const csrfToken = document.querySelector("#csrf_token_comments").value;
            const response = await tryPostForm(form, url, csrfToken)
            const newComment = await response.json()
            setComments([newComment, ...comments]);
            // await fetchComments();
            event.target.reset();
        } 
        catch (error) {
            console.error(error);
        }
    };
    
    return (
        <React.Fragment>
            <div className="col-12 overflow-auto" style={{ maxHeight: '25vh' }}>
                {
                    comments.length ? (
                        comments.map((comment, index) => (
                            <div key={comment.id} className={`row me-0 ms-0 ${index !== 0 ? 'mt-2' : ''}`}>
                                <div className="col-12" style={{ maxHeight: '2rem' }}>
                                    <div className="row h-100 p-0">
                                        <div className="col-auto h-100 p-0">
                                            <img
                                                src={(comment.user.profile ? comment.user.profile.pic : defaultUserPic) || defaultUserPic}
                                                className="img-fluid h-100 rounded"
                                                style={{ width: '2rem', objectFit: 'cover' }}
                                            />
                                        </div>
                                        <div className="col-6 h-100 p-0">
                                            <div className="row h-100 p-0 ps-1 m-0">
                                                <div className="col-12 h-50 p-0">
                                                    <small>
                                                        <code className="text-warning align-top">{comment.user.username}</code>
                                                    </small>
                                                </div>
                                                <div className="col-12 h-50 p-0">
                                                    <small>
                                                    <code className="text-secondary align-top">
                                                        {comment.timestamp}
                                                    </code>
                                                    </small>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className="col-12 ps-0">
                                    <small>{comment.body}</small>
                                </div>
                            </div>
                        ))
                    ) : (
                        <small className="text-secondary">No comments yet... Be the first!</small>
                    )
                }
            </div>
            <hr className="text-secondary" />
            <form onSubmit={handleSubmit} method="POST" id="commentForm">
                <div className="mb-1">
                <label htmlFor="commentBodyInput" className="form-label text-warning">
                    Leave your comment:
                </label>
                <textarea
                    className="form-control"
                    name="body"
                    id="commentBodyInput"
                    placeholder="I think..."
                    required
                ></textarea>
                </div>
                <div className="col text-end">
                {
                    userId ? (
                        <button type="submit" className="btn btn-outline-warning w-100" id="commentSubmit">
                            Publish
                        </button>
                    ) : (
                        <span>
                            Please <a href={loginUrl} class="text-warning text-decoration-none fw-bold">Login or Register</a> to leave a comment
                        </span>
                    )
                }
                </div>
            </form>
        </React.Fragment>
    );
}