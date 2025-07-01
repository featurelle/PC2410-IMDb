'use strict';

const React = window.React;
const ReactBootstrap = window.ReactBootstrap;

const {useState} = React;
const {Alert, Form, Button} = ReactBootstrap;


function LoginMinifiedForm({ backref }) {

    const [message, setMessage] = useState('')
    const [failed, setFailed] = useState(false)

    const onSubmit = "/api/simple/auth/login/"
    const idPrefix = "login"
    const submitLabel = "Sign in"
    const successMessage = "Loading your profile! :)"
    const failureMessage = "Wrong username or password :(" 

    const handleSubmit = async (event) => {
        event.preventDefault();
        event.stopPropagation();

        const form = event.currentTarget;
        const csrfToken = document.querySelector("#csrf_token").value;

        try {
            const response = await tryPostForm(form, onSubmit, csrfToken)

            if (response.ok) {
                setFailed(false)
                setMessage(successMessage);
                backref && backref !== `b''`? location.href = backref : location.reload();
            } else {
                setFailed(true)
                setMessage(failureMessage);
            }
        } catch (error) {
            console.error(error)
            setFailed(true)
            setMessage('An error occurred while processing your request.');
        }
    };

    const handleBtnClick = (event) => {
        event.stopPropagation();
    };

    return (
        <Form id={idPrefix + "Form"} onSubmit={handleSubmit} className="text-dark text-center">
            <Form.Group className="mb-3 text-start" controlId={idPrefix + "UsernameInput"}>
                <Form.Label className="h6">Username</Form.Label>
                <Form.Control type="text" name="username" placeholder="User login" required />
            </Form.Group>

            <Form.Group className="mb-3 text-start" controlId={idPrefix + "UserPasswordInput"}>
                <Form.Label className="h6">Password</Form.Label>
                <Form.Control type="password" name="password" placeholder="User password" required />
            </Form.Group>

            <div className="my-2">
                {message && <Alert variant={failed ? 'danger' : 'warning'}>{message}</Alert>}
            </div>

            <Button type="submit" onClick={handleBtnClick} variant="warning" className="w-75" id={idPrefix + "Submit"}>
                {submitLabel}
            </Button>
        </Form>
    );
}