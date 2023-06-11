import {Col, Row } from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {faLocationDot, faEdit, faTrash, faPhone} from "@fortawesome/free-solid-svg-icons";
import { useState } from "react";
import DeleteAddress from "./AddressDelete";
import EditAddress from "./AddressNew";
import useLocalStorage from "../../../hooks/useLocalStorage";
import ToolTip from "../../Common/ToolTip";
import Notification from "../../Common/Notification";

export default function AddressGridLine(props){
    const address = props.item
    const [show_delete_model, setShowDeleteModal] = useState(false);
    const [show_edit_model, setShowEditModal] = useState(false);
    const [notification, setNotification] = useState({  show: false,  type: "",  message: "" });
    const [isNotification, setIsNotification] = useState(false);
    const [userdata] = useLocalStorage("userdata");

    const handleShowEdit = () => setShowEditModal(true)

    const handleShowDelete = () => setShowDeleteModal(true)

    const handleHideDeleteModal = (reload, blink) => {
      setShowDeleteModal(false);
      if (reload === true) {
        setNotification(blink);
        setIsNotification(true);
        setTimeout(() => {
          handleClose();
          props.getAddresses();
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

      const handleHideEditModal = (reload, blink) => {
        setShowEditModal(false);
        if (reload === true) {
          setNotification(blink);
          setIsNotification(true);
          setTimeout(() => {
            handleClose();
            props.getAddresses();
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
        <Row className="address_grid">
          <Col md={4}>
            <div>
              <FontAwesomeIcon
                icon={faLocationDot}
                className="address_icon"
              ></FontAwesomeIcon>
              &nbsp;<span className="address_name">{address.address}</span>
            </div>
            <div>
              City : <b className="address_city">{address.city}</b>
            </div>
            <div className="address_zip">
              Zip code : <b>{address.zip_code}</b>{" "}
            </div>
          </Col>
          <Col md={4}>
            <div className="address_state">
              {" "}
              State : &nbsp;<b>{address.state}</b>
            </div>
            <div className="address_country">
              Country : &nbsp;<b>{address.country_name}</b>
            </div>
            <div className="address-created-on">
              Created on : &nbsp;{address.created_on}
            </div>
          </Col>
          <Col md={3}>
            <div className="address_state">
              {" "}
              Attention : &nbsp;<b>{address.attention}</b>
            </div>
            <div className="address_fax">
              {" "}
              Fax : &nbsp;<b>{address.fax}</b>
            </div>
            <div className="address_phone">
              <FontAwesomeIcon
                className="customer_icon_phone"
                icon={faPhone}
              ></FontAwesomeIcon>{" "}
              &nbsp;<b className="customer_phone">{address.phone}</b>
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
                  ></FontAwesomeIcon>
                </ToolTip>
              </Col>
              <Col md={12} sm={6}>
                <ToolTip text="Delete">
                  <FontAwesomeIcon
                    className="customer_icon"
                    icon={faTrash}
                    onClick={handleShowDelete}
                  ></FontAwesomeIcon>
                </ToolTip>
              </Col>
            </Row>
          </Col>
          <DeleteAddress
            show={show_delete_model}
            handler={handleHideDeleteModal}
            address_id={address.id}
            org_id={userdata.current_org_id}
          />
          {show_edit_model && (
            <EditAddress
              show={show_edit_model}
              handler={handleHideEditModal}
              address_id={address.id}
              country_id={address.country_id}
              is_edit={true}
              org_id={userdata.current_org_id}
            />
          )}
        </Row>
      </>
    );
}