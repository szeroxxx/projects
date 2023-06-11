import React, { useState } from "react";
import { Toast } from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
faCheckCircle, faCircleExclamation
} from "@fortawesome/free-solid-svg-icons";
import "./Common.css";
const Notification = ({ show, onClose, type, message }) => {
  const [showToast, setShowToast] = useState(show);

  const handleClose = () => {
    setShowToast(false);
    onClose();
  };

  return (
    <Toast
      show={showToast}
      onClose={handleClose}
      style={{
        position: "absolute",
        top: "5rem",
        right: "50rem",
        zIndex: 9999,
        minWidth: "250px",
      }}
    >
      <Toast.Body>
        {type === "success" ? (
          <FontAwesomeIcon icon={faCheckCircle} className="me-2 notification-success" />
        ) : (
          <FontAwesomeIcon
            icon={faCircleExclamation}
            className="me-2 text-danger"
          />
        )}
        {message}
      </Toast.Body>
    </Toast>
  );
};

export default Notification;
