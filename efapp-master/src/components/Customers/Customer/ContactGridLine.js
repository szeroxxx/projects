import { Col, Row } from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {faEnvelopeSquare, faEdit, faTrash, faPhone} from "@fortawesome/free-solid-svg-icons";
import ContactNew from "./ContactNew";
import DeleteContact from "./ContactDelete";
import { useState } from "react";
import ToolTip from "../../Common/ToolTip";
import Notification from "../../Common/Notification";

export default function ContactGridLine(props){
    const data = props.item
    const [show_edit_model, setShowEditModal] = useState(false);
    const [show_delete_model, setShowDeleteModal] = useState(false);
    const [notification, setNotification] = useState({  show: false,  type: "",  message: "" });
    const [isNotification, setIsNotification] = useState(false);
    const handleShowEdit = () => {
        setShowEditModal(true)
    }

    const handleHideEditModal = (reload, blink) => {
      setShowEditModal(false);
      if (reload === true) {
        setNotification(blink);
        setIsNotification(true);
        setTimeout(() => {
          handleClose();
          props.getContacts();
        }, 2000);
      }
      if (reload === false) {
        setNotification(blink);
        setIsNotification(true);
        setTimeout(() => {
          handleClose();
        }, 2000);
      }
    };

    const handleHideDeleteModal = (reload, blink) => {
      setShowDeleteModal(false);
      if (reload === true) {
        setNotification(blink);
        setIsNotification(true);
        setTimeout(() => {
          handleClose();
          props.getContacts();
        }, 2000);
      }
      if (reload === false) {
        setNotification(blink);
        setIsNotification(true);
        setTimeout(() => {
          handleClose();
        }, 2000);
      }
    };

    const handleClose = () => {
      setIsNotification(false);
      setNotification({
        show: false,
        type: "",
        message: "",
      });
    };

    const handleShowDelete = () => setShowDeleteModal(true)

    return (
      <>
        {isNotification && (
          <Notification
            show={notification.show}
            onClose={handleClose}
            type={notification.type}
            message={notification.message}
          />
        )}
        <Row className="contact_grid">
          <Col md={4}>
            <div className="contact_name">
              {" "}
              {data.first_name} {data.last_name}
            </div>
            <div className="contact_created">
              Created on : &nbsp;{data.created_on}
            </div>
          </Col>
          <Col md={4}>
            <div>
              <FontAwesomeIcon
                className="customer_icon_phone"
                icon={faEnvelopeSquare}
              ></FontAwesomeIcon>{" "}
              &nbsp;<b className="customer_email">{data.email}</b>
            </div>
            <div>
              <FontAwesomeIcon
                className="customer_icon_phone"
                icon={faPhone}
              ></FontAwesomeIcon>{" "}
              &nbsp;<b className="customer_phone">{data.mobile}</b>
            </div>
          </Col>
          <Col md={3}>
            <div className="contact_created">
              Salutation : &nbsp;<b>{data.salutation}</b>
            </div>
            <div className="contact_created">
              Work Phone : &nbsp;<b>{data.work_phone}</b>
            </div>
          </Col>
          <Col md={1}>
            <Row>
              <Col md={12} sm={6}>
                <ToolTip text="Edit">
                  <FontAwesomeIcon
                    className="customer_icon"
                    icon={faEdit}
                    onClick={handleShowEdit}
                  />
                </ToolTip>
              </Col>
              <Col md={12} sm={6}>
                <ToolTip text="Delete">
                  <FontAwesomeIcon
                    className="customer_icon"
                    icon={faTrash}
                    onClick={handleShowDelete}
                  />
                </ToolTip>
              </Col>
            </Row>
          </Col>
          <DeleteContact
            show={show_delete_model}
            handler={handleHideDeleteModal}
            contact_id={data.id}
          />
          {show_edit_model && (
            <ContactNew
              show={show_edit_model}
              handler={handleHideEditModal}
              is_edit={true}
              contact_id={data.id}
            />
          )}
        </Row>
      </>
    );
}