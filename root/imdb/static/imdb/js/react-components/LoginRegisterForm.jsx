'use strict';

const React = window.React;
const ReactBootstrap = window.ReactBootstrap;

const {useState, useEffect} = React;
const {Tab, Nav, Alert, Form, Button} = ReactBootstrap;


function LoginRegisterTab({ onSubmit, successMessage, 
    failureMessage, idPrefix, submitLabel, backref }) {

    const [message, setMessage] = useState('')
    const [failed, setFailed] = useState(false)

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
                backref && backref !== `b''`? location.href = backref : location.href = encodeURI('/');
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

    return (
        <Tab.Pane eventKey={idPrefix + "Tab"}>
            <Form id={idPrefix + "Form"} onSubmit={handleSubmit} className="p-4 pb-5 text-dark text-center">
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

                <Button type="submit" variant="warning" className="w-75" id={idPrefix + "Submit"}>
                    {submitLabel}
                </Button>
            </Form>
        </Tab.Pane>
    );
}

function LoginRegisterForm({ backref }) {
    const [activeKey, setActiveKey] = useState('loginTab');

    const handleTabSelect = (selectedKey) => {
        setActiveKey(selectedKey);
    };

    useEffect(() => {
        if (location.hash === '#register') {
            setActiveKey('registerTab')
        }
      }, []);

    return (
        <Tab.Container activeKey={activeKey} onSelect={handleTabSelect}>
            <Nav variant="tabs" id="tabs">
                <Nav.Item className="w-50 text-center">
                    <Nav.Link eventKey="loginTab" href="#login">Login</Nav.Link>
                </Nav.Item>
                <Nav.Item className="w-50 text-center">
                    <Nav.Link eventKey="registerTab" href="#register">Register</Nav.Link>
                </Nav.Item>
            </Nav>

            <Tab.Content className="bg-light">
                <LoginRegisterTab
                    onSubmit="/api/simple/auth/login/"
                    idPrefix="login"
                    submitLabel="Sign in"
                    successMessage="Loading your profile! :)"
                    failureMessage="Wrong username or password :("
                    backref={backref}
                />

                <LoginRegisterTab
                    onSubmit="/api/simple/auth/register/"
                    idPrefix="register"
                    submitLabel="Register"
                    successMessage="Whoa! Now you're with us! :)"
                    failureMessage="Looks like this username is already taken :("
                    backref={backref}
                />
            </Tab.Content>
        </Tab.Container>
    );
}