import {Button, Modal, Form, Row, Col} from 'react-bootstrap';
import { useState, useEffect } from 'react';
import useAxiosPrivate from "../../../hooks/useAxiosPrivate";
import useLocalStorage from "../../../hooks/useLocalStorage";
import Spinner from "react-bootstrap/Spinner";

export default function ContactNew(props){
    const axiosPrivate = useAxiosPrivate();
    const [userdata] = useLocalStorage("userdata");
    const [formData, setFormData] = useState({salutation:"", first_name:"", last_name:"", email:"", work_phone:"", mobile:"" })
    const [alertMsg, setAlertMsg] = useState({ class: "hide", message: "" });
    const [editData, setEditData] = useState({});
    const [isEdit, setIsEdit] = useState(false)
    const [error, setError] = useState({});
    const [onLoad, setOnLoad] = useState(false);

    const handleChange = (event) => {
        setFormData({...formData, [event.target.name]: event.target.value});
        if(isEdit){
            setEditData({...editData, [event.target.name]: event.target.value});
        }
    }

    const handleUpdate = async() => {
        try{
            if(validator()){
                const response = await axiosPrivate.put(
                    `/app/contacts/contact_edit/${props.contact_id}/${userdata.current_org_id}`,
                    JSON.stringify(editData),
                    {
                        headers: { 'Content-Type': 'application/json' },
                    }
                );
                if (response.data && response.data.code == "1") {
                    var alertSuccess = { show: true,  type: "success",  message: response.data.message };
                    props.handler(true, alertSuccess);
                } else {
                    var alertDanger = { show: true,  type: "alert",  message: response.data.message };
                    props.handler(false, alertDanger);
                }
            }
        } catch(err) {
            console.log(err);
        }
    }

    const handleSubmit = async() => {
        try {
            if(validator()){
                const response = await axiosPrivate.post(
                    `/app/contacts/contact_insert/${props.customer_id}/${userdata.current_org_id}`,
                    JSON.stringify(formData),
                    {
                        headers: { 'Content-Type': 'application/json' },
                    }
                );
                if (response.data && response.data.code == "1") {
                    var alertSuccess = { show: true,  type: "success",  message: response.data.message };
                    props.handler(true, alertSuccess);
                } else {
                    var alertDanger = { show: true,  type: "alert",  message: response.data.message };
                    props.handler(false, alertDanger);
                }
            }

        } catch(err) {
            console.log(err);
        }
    }

    const getContact = async() => {
        try {
            setOnLoad(true);
            const post_data = {
                "fields": ["salutation", "first_name", "last_name", "email", "work_phone", "mobile","customer_id"]
            }
            const response = await axiosPrivate.post(
                `app/contacts/contact_get/${props.contact_id}/${userdata.current_org_id}`,
                JSON.stringify(post_data),
                {
                    headers: { 'Content-Type': 'application/json' },
                }
            );
            if (response.data && response.data.code == "0") {
              setOnLoad(false);
              setEditData([]);
            } else {
              setOnLoad(false);
              if (response.data.length > 0) {
                setEditData(response.data[0]);
                setIsEdit(true);
              }
            }
        } catch(err) {
            console.log(err);
        }
    }

    const validator = () => {
        const regex = /^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$/i;
        let tempError = {};
        if (isEdit) {
            if (!editData.first_name) {
                tempError.first_name = "First Name required"
            }
            if (!editData.first_name) {
                tempError.last_name = "Last Name required"
            }
            if (!editData.email || regex.test(editData.email) === false) {
                tempError.email = "Email required"
            }
            if (!editData.mobile) {
                tempError.last_name = "Mobile required"
            }
        } else {
            if (!formData.first_name) {
                tempError.first_name = "First Name required"
            }
            if (!formData.last_name) {
                tempError.last_name = "Last Name required"
            }
            if (!formData.email || regex.test(formData.email) === false) {
                tempError.email = "Email required"
            }
            if (!formData.mobile) {
                tempError.mobile = "Mobile required"
            }
        }
        setError(tempError)
        return Object.keys(tempError).length === 0;
    }

    useEffect(() => {
        if(props.is_edit){
            getContact();
        }
    }, [])

    return(
        <>
        <Modal
            show={props.show}
            onHide={ props.handler }
            dialogClassName="modal-80w"
            size="lg"
            aria-labelledby="contained-modal-title-vcenter"
            centered
            >
            <Modal.Header closeButton>
                <Modal.Title>{props.is_edit ? (<>Edit Contact</>):(<>Add New Contact</>)}</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                {onLoad ? (
                <Spinner
                animation="border"
                className="contact-loading-spinner"
                />
                ):(
                <div className='address_new_form'>
                    <div >
                        <Form>
                            <Form.Group as={Row} className="mb-3">
                                <Form.Label column sm={2}>First name</Form.Label>
                                <Col sm={6}>
                                    <Form.Control value={editData.first_name} type="text"  placeholder="Enter First name" name="first_name" onChange={(e) => handleChange(e)}/>
                                    <p className='contact_validation'>{error.first_name}</p>
                                </Col>
                            </Form.Group>
                            <Form.Group as={Row} className="mb-3">
                                <Form.Label column sm={2}>Last name</Form.Label>
                                <Col sm={6}>
                                    <Form.Control value={editData.last_name} type="text"  placeholder="Enter Last name" name="last_name" onChange={(e) => handleChange(e)}/>
                                    <p className='contact_validation'>{error.last_name}</p>
                                </Col>
                            </Form.Group>
                            <Form.Group as={Row} className="mb-3">
                                <Form.Label column sm={2}>Email</Form.Label>
                                <Col sm={6}>
                                    <Form.Control value={editData.email} type="text"  placeholder="Enter Email" name="email" onChange={(e) => handleChange(e)}/>
                                    <p className='contact_validation'>{error.email}</p>
                                </Col>
                            </Form.Group>
                            <Form.Group as={Row} className="mb-3">
                                <Form.Label column sm={2}>Mobile</Form.Label>
                                <Col sm={6}>
                                    <Form.Control value={editData.mobile} type="text"  placeholder="Enter Mobile" name="mobile" onChange={(e) => handleChange(e)}/>
                                    <p className='contact_validation'>{error.mobile}</p>
                                </Col>
                            </Form.Group>
                            <Form.Group as={Row} className="mb-3">
                                <Form.Label column sm={2}>Work phone</Form.Label>
                                <Col sm={6}>
                                    <Form.Control value={editData.work_phone} type="text" placeholder="Enter Work phone" name="work_phone" onChange={(e) => handleChange(e)}/>
                                </Col>
                            </Form.Group>
                            <Form.Group as={Row} className="mb-3">
                                <Form.Label column sm={2}>Salutation</Form.Label>
                                <Col sm={6}>
                                    <Form.Control value={editData.salutation} type="text" placeholder="Enter salutation" name="salutation" onChange={(e) => handleChange(e)}/>
                                </Col>
                            </Form.Group>
                        </Form>
                    </div>
                </div>
                )}
            </Modal.Body>
            <Modal.Footer>
            <div className={alertMsg.class} role="alert">
                {alertMsg.message}
            </div>
            <Button variant="outline-primary" onClick={ props.handler }>
                Cancel
            </Button>
            {props.is_edit ? (
                <Button className="btn btn-primary" onClick={ handleUpdate }>Edit Contact</Button>

            ) : (
                <Button className="btn btn-primary" onClick={ handleSubmit }>Submit</Button>
            )}
            </Modal.Footer>
        </Modal>
        </>



    )
}