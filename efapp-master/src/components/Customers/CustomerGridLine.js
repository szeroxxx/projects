import { Col, Row } from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {faEnvelopeSquare, faEdit, faTrash, faPhone} from "@fortawesome/free-solid-svg-icons";
import { useState } from "react";
import useLocalStorage from "../../hooks/useLocalStorage";
import DeleteCustomer from "./CustomerDelete";
import { useNavigate } from "react-router-dom";
import ToolTip from "../Common/ToolTip";
import Notification from "../Common/Notification";

export default function CustomerGridLine(props) {
    const item = props.item;
    const [show_delete_model, setShowDeleteModal] = useState(false);
    const [notification, setNotification] = useState({show: false,type: "",message: ""});
    const [isNotification, setIsNotification] = useState(false);
    const [userdata] = useLocalStorage("userdata");

    const navigate = useNavigate();
    const handleShowDeleteUserModal = () => setShowDeleteModal(true);
    const handleShowEdit = () => {
        navigate(`/customer/${item.id}`)
    }
    const handleHideDeleteCustomerModal = (reload,blink) =>{
      setShowDeleteModal(false);
      if(reload === true){
        setNotification(blink);
        setIsNotification(true);
        setTimeout(() => {
          handleClose();
          props.getCustomer();
        }, 2000);
      }
      if(reload === false){
        setNotification(blink);
        setIsNotification(true);
        setTimeout(() => {
          handleClose();
        }, 2000);
      }
    }

    const handleClose = () => {
      setIsNotification(false);
      setNotification({
        show: false,
        type: "",
        message: "",
      });
    };
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
        <Row className="customer_grid">
          <Col md={4}>
            <div>
              <span className="customer_name">{item.name}</span>
            </div>
            <div className="customer_created">
              Created on : &nbsp;{item.created_on}
            </div>
          </Col>
          <Col md={4}>
            <div>
              <FontAwesomeIcon
                className="customer_icon_phone"
                icon={faEnvelopeSquare}
              ></FontAwesomeIcon>{" "}
              &nbsp;<b className="customer_email">{item.email}</b>
            </div>
            <div>
              <FontAwesomeIcon
                className="customer_icon_phone"
                icon={faPhone}
              ></FontAwesomeIcon>{" "}
              &nbsp;<b className="customer_phone">{item.phone}</b>
            </div>
          </Col>
          <Col md={3}>
            Type :&nbsp;<b>{item.type}</b>
          </Col>
          <Col md={1}>
            <Row>
              <Col md={12} sm={6}>
                <ToolTip text="Edit">
                  <FontAwesomeIcon
                    className="customer_icon"
                    icon={faEdit}
                    onClick={handleShowEdit}
                  ></FontAwesomeIcon>
                </ToolTip>
              </Col>
              <Col md={12} sm={6}>
                <ToolTip text="Delete">
                  <FontAwesomeIcon
                    className="customer_icon"
                    icon={faTrash}
                    onClick={handleShowDeleteUserModal}
                  ></FontAwesomeIcon>
                </ToolTip>
              </Col>
            </Row>
          </Col>
        </Row>
        <DeleteCustomer
          show={show_delete_model}
          customer_id={item.id}
          handler={handleHideDeleteCustomerModal}
          org_id={userdata.current_org_id}
        ></DeleteCustomer>
      </>
    );
}