import React, { useState ,useEffect } from 'react';
import {Button ,Form,Modal} from 'react-bootstrap';
import useAxiosPrivate from "../../../hooks/useAxiosPrivate";
const InviteMember=(props) =>{

  const show=props.show;
  const [userInfo, setUserInfo] = useState({email: ""});
  const [email, setEmail] = useState("");
  const [alertMsg, setAlertMsg] = useState({ class: "hide", message: "" });
  const axiosPrivate = useAxiosPrivate();

  useEffect(() => {
    setEmail("")
    setUserInfo({email: "",firstName: "",lastName: ""});
    setAlertMsg({ class: "hide", message: "" })
  },[show]);
  const inviteMember=async()=>{
    try {
      if(email !== ""){
        const response = await axiosPrivate.post(
          `/app/org/user_invite/?org_id=${props.org_id}&email=${email}`,
          {
            headers: { "Content-Type": "application/json" },
          }
        );
        if ((response.data && response.data.code == "1")) {
            setAlertMsg({
              class: "alert alert-success",
              message: response.data.message,
            });
          } else {
            setAlertMsg({
              class: "alert alert-danger",
              message: response.data.message,
            });
          }
      }
      } catch (err) {
        console.log(err);
      }
  }
  return (
    <>
      <Modal show={show} onHide={props.handler}>
        <Modal.Header closeButton>
          <Modal.Title>Invite member</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <div className={alertMsg.class} role="alert">
            {alertMsg.message}
          </div>
          <Form>
            <Form.Group className="mb-3"></Form.Group>
            <Form.Group className="mb-3">
              <Form.Control
                type="email"
                placeholder="Enter Email address"
                required
                name="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="primary" onClick={inviteMember}>
            Invite
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
}

export default InviteMember;