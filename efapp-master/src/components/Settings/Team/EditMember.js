import { Col, Row, Modal,Form,Button} from "react-bootstrap";
import { useState } from "react";
import useAxiosPrivate from "../../../hooks/useAxiosPrivate";
const EditMember = (props) => {
  const member_data = props.data
  const axiosPrivate = useAxiosPrivate();

  const [formData, setFormData] = useState({first_name:member_data.first_name,last_name:member_data.last_name,role_id:member_data.role_id,disabled:member_data.disabled})
  const [alertMsg, setAlertMsg] = useState({ class: "hide", message: "" });

  const handleChange = (event) => {
    if (event.target.name === "disabled") {
      const active_val = event.target.checked.toString()
      setFormData({...formData,[event.target.name]:active_val })
    } else {
      setFormData({...formData,[event.target.name]:event.target.value})
    }
  }

  const handleSubmit = async () => {
    try {
      const response = await axiosPrivate.put(
        `/app/user/edit/${props.uuid}/${props.org_id}`,
        JSON.stringify(formData),
        {
          headers: { 'Content-Type': 'application/json' },
        }
      );
    if (response.data && response.data.code == "1") {
      setAlertMsg({
        class: "alert alert-success",
        message: response.data.message,
      });
      setTimeout(() => { props.handler(true)}, 2000);
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
    <Row md={10}>
      <Modal
        show={props.show}
        onHide={props.handler}
        dialogClassName="modal-80w"
        size="lg"
        aria-labelledby="contained-modal-title-vcenter"
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>Team/Edit Member</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <div className="settings-content">
            <div>
              <Form.Group as={Row} className="mb-3">
                <Form.Label column sm={2}>
                  First name
                </Form.Label>
                <Col sm={6}>
                  <Form.Control
                    value={formData.first_name}
                    type="input"
                    placeholder="Enter First name"
                    name="first_name"
                    onChange={(e) => handleChange(e)}
                  />
                </Col>
              </Form.Group>
              <Form.Group as={Row} className="mb-3">
                <Form.Label column sm={2}>
                  Last name
                </Form.Label>
                <Col sm={6}>
                  <Form.Control
                    value={formData.last_name}
                    type="text"
                    placeholder="Enter Last name"
                    name="last_name"
                    onChange={(e) => handleChange(e)}
                  />
                </Col>
              </Form.Group>
              <Form.Group as={Row} className="mb-3">
                <Form.Label column sm={2}>
                  Email
                </Form.Label>
                <Col sm={6}>
                  <Form.Control value={member_data.email} disabled />
                </Col>
              </Form.Group>
              <Form.Group as={Row} className="mb-3">
                <Form.Label column sm={2}>
                  Role
                </Form.Label>
                <Col sm={6}>
                  <Form.Control
                    as="select"
                    name="role_id"
                    onChange={(e) => handleChange(e)}
                  >
                    {props.role.map((option, index) => {
                      return (
                        <option
                          key={index}
                          value={option.id}
                          selected={formData.role_id === option.id}
                        >
                          {option.role}
                        </option>
                      );
                    })}
                  </Form.Control>
                </Col>
              </Form.Group>
              <Form.Group as={Row} className="mb-3">
                <Form.Label column sm={2}>
                  Active
                </Form.Label>
                <Col sm={6}>
                  <Form.Check
                    checked={formData.disabled ? false : true}
                    aria-label="Text input with checkbox"
                    name="disabled"
                    onChange={(e) => handleChange(e)}
                  />
                </Col>
              </Form.Group>
            </div>
          </div>
        </Modal.Body>
        <Modal.Footer>
          <div className={alertMsg.class} role="alert">
            {alertMsg.message}
          </div>
          <Button variant="outline-primary" onClick={props.handler}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleSubmit}>
            Submit
          </Button>
        </Modal.Footer>
      </Modal>
    </Row>
  );
}

export default EditMember;