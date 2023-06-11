import {Button ,Modal} from 'react-bootstrap';
import useAxiosPrivate from "../../../hooks/useAxiosPrivate";
import React, { useState  } from 'react';

const DeleteMember = (props) => {
    const [alertMsg, setAlertMsg] = useState({ class: "hide", message: "" });
    const axiosPrivate = useAxiosPrivate();
    const show = props.show;
    const deleteUser = async() => {
        try {
            const response = await axiosPrivate.delete(
                `/app/org/user_delete/${props.user_id}/${props.org_id}`,
                {
                  headers: { "Content-Type": "application/json" },
                },
            );
            if (response.data && response.data.code == "1") {
                setAlertMsg({
                    class: "alert alert-success",
                    message: response.data.message,
                });
                props.handler(true);
            } else {
                setAlertMsg({
                    class: "alert alert-danger",
                    message: response.data.message,
                });
            }
        } catch(err) {
            console.log(err);
        }
    }
    return (
        <>
        <Modal show={show} onHide={ props.handler }>
            <Modal.Header closeButton>
                <Modal.Title>Delete User</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <div class={alertMsg.class} role="alert">
                    {alertMsg.message}
                </div>
                <p>Are you sure you want to delete your user?</p>
            </Modal.Body>
            <Modal.Footer>
                <Button variant="outline-primary" onClick={ props.handler }>
                     Cancel
                </Button>
                <Button variant="primary" onClick={deleteUser} >
                     Delete
                </Button>
            </Modal.Footer>
        </Modal>
        </>
    )
}
export default DeleteMember;