import { Col, Row,Image  } from "react-bootstrap";
import {faCalendarDays,faEnvelopeSquare,faCheckCircle, faUser,faEdit, faTrash} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useState } from "react";
import DeleteUser from "./DeleteMember";
import EditMember from "./EditMember";
import useLocalStorage from "../../../hooks/useLocalStorage";
import ToolTip from "../../Common/ToolTip";
import profilePic from "../../../static/profilepic.svg";

const TeamGrigLine = (props) => {
    const item = props.item;
    const [userdata] = useLocalStorage("userdata");
    const [show_delete_model, setShowDeleteModal] = useState(false);
    const [show_edit_model, setShowEditModal] = useState(false);
    const handleShowDeleteUserModal = () => setShowDeleteModal(true);

    const handleHideDeleteUserModal = (reload) =>{
      setShowDeleteModal(false)
      if(reload){
        props.getUsers();
      }
    };

    const handleHideEditUserModal = (reload) =>{
      setShowEditModal(false)
      if(reload){
        props.getUsers();
      }
    };
    const handleShowEditMember = () => setShowEditModal(true)

    const [imageSrc, setImageSrc] = useState(
      `${process.env.REACT_APP_SERVER_URL}/user/avatar_get/${item.uuid}`
    );
    const handleImageError = () => {
      setImageSrc(profilePic);
    };
    return (
      <>
        <Row className="team_list">
          <Col md={2}>
            <div className="user_profile">
              <Image
                src={imageSrc}
                onError={handleImageError}
                className="avatar"
              ></Image>
            </div>
          </Col>
          <Col md={10} className="user_info">
            <Row className="user_info_extra">
              <Col md={4}>
                <div>
                  <FontAwesomeIcon icon={faUser}></FontAwesomeIcon>
                  <b>
                    {" "}
                    {item.first_name} {item.last_name}{" "}
                  </b>
                </div>
                <FontAwesomeIcon icon={faEnvelopeSquare}> </FontAwesomeIcon>
                <b> {item.email}</b>
              </Col>
              <Col md={5}>
                <div>
                  <FontAwesomeIcon icon={faCalendarDays}></FontAwesomeIcon>{" "}
                  Created on: <b> {item.created_on}</b>
                </div>
                <div>
                  <FontAwesomeIcon icon={faCalendarDays}></FontAwesomeIcon> Last
                  login on: <b> {item.last_login}</b>
                </div>
              </Col>
              <Col md={2}>
                <Row>
                    <Col md={12} sm={6}>
                      <FontAwesomeIcon
                        className={item.is_invited ? "green" : ""}
                        icon={faCheckCircle}
                      ></FontAwesomeIcon>
                      <b> Invited</b>
                    </Col>
                  <Col md={12} sm={6}>
                    <FontAwesomeIcon
                      className={item.is_verified ? "green" : ""}
                      icon={faCheckCircle}
                    ></FontAwesomeIcon>
                    <b> Verified</b>
                  </Col>
                  <Col md={12} sm={6}>
                    <FontAwesomeIcon
                      className={item.disabled ? "" : "green"}
                      icon={faCheckCircle}
                    ></FontAwesomeIcon>
                    <b> Active</b>
                  </Col>
                </Row>
              </Col>
              <Col md={1}>
                <Row>
                  <Col md={12} sm={6}>
                    <ToolTip text="Edit">
                      <FontAwesomeIcon
                        icon={faEdit}
                        onClick={handleShowEditMember}
                      ></FontAwesomeIcon>
                    </ToolTip>
                  </Col>
                  <Col md={12} sm={6}>
                    <ToolTip text="Delete">
                      <FontAwesomeIcon
                        icon={faTrash}
                        onClick={handleShowDeleteUserModal}
                      ></FontAwesomeIcon>
                    </ToolTip>
                  </Col>
                </Row>
              </Col>
            </Row>
          </Col>
        </Row>
        <DeleteUser
          show={show_delete_model}
          handler={handleHideDeleteUserModal}
          user_id={item.uuid}
          org_id={userdata.current_org_id}
        ></DeleteUser>
        <EditMember
          show={show_edit_model}
          handler={handleHideEditUserModal}
          data={item}
          role={props.role}
          uuid={item.uuid}
          org_id={userdata.current_org_id}
        ></EditMember>
      </>
    );
  };
  export default TeamGrigLine;