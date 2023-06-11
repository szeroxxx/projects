import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import { faEdit } from "@fortawesome/free-solid-svg-icons";
import { Image } from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import "./Settings.css";
import useLocalStorage from "../../hooks/useLocalStorage";
import { useState, useRef } from "react";
import useAxiosPrivate from "../../hooks/useAxiosPrivate";
import profilePic from "../../static/profilepic.svg";

export default function Settings_Profile(props) {
  const { show } = props;
  const [userdata, setUserData] = useLocalStorage("userdata");
  const [first_name, setFirstName] = useState(userdata.first_name);
  const [last_name, setLastName] = useState(userdata.last_name);
  const [profile_pic, setProfilePic] = useState(
    `${process.env.REACT_APP_SERVER_URL}/user/avatar_get/${userdata.user_id}`
  );
  const axiosPrivate = useAxiosPrivate();
  const hiddenAvatarInput = useRef(null);
  const [alertMsg, setAlertMsg] = useState({ class: "hide", message: "" });

  const saveProfile = async (e) => {
    e.preventDefault();
    const user_details = { first_name: first_name, last_name: last_name };
    try {
      const response = await axiosPrivate.put(
        `/app/user/edit/${userdata.user_id}/${userdata.current_org_id}`,
        JSON.stringify(user_details),
        {
          headers: { "Content-Type": "application/json" },
        }
      );
      if ((response.data.code =="1")) {
        userdata.first_name = first_name;
        userdata.last_name = last_name;
        setUserData(userdata);
        setAlertMsg({
          class: "alert alert-success",
          message: response.data.message,
        });
        setTimeout(() => {
          setAlertMsg({ class: "hide", message: "" });
        }, 5000);
      } else {
        setAlertMsg({
          class: "alert alert-danger",
          message: response.data.message,
        });
      }

    } catch (err) {
      console.log(err);
    }
  };
  const handleAvatarClick = (event) => {
    hiddenAvatarInput.current.click();
  };
  const onFileChange = async (e) => {
    let files = e.target.files;
    let file = files[0];
    var formData = new FormData();
    formData.append("avatar", file);
    try {
      const response = await axiosPrivate.post(
        `/app/user/avatar_upload/${userdata.user_id}`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      setProfilePic(`${process.env.REACT_APP_SERVER_URL}/user/avatar_get/${userdata.user_id}?v=0.1`)
    } catch (error) {
      console.error(error);
    }
  };
  const handleImageError = () => {
    setProfilePic(profilePic);
  };


  if (show) {
    return (
      <div className="col-md-4">
        <div className={alertMsg.class} role="alert">
          {alertMsg.message}
        </div>
        <table>
          <thead>
          <tr>
            <td>
              <Image
                src={`${profile_pic}`}
                onError={handleImageError}
                className="avatar"
              ></Image>
            </td>
            <td style={{ paddingLeft: "10px" }}>
              <FontAwesomeIcon icon={faEdit} onClick={handleAvatarClick} />
              <input
                type="file"
                accept="image/*"
                ref={hiddenAvatarInput}
                style={{ display: "none" }}
                onChange={onFileChange}
              />
            </td>
          </tr>
          </thead>
        </table>

        <Form onSubmit={saveProfile}>
          <Form.Group className="mb-3">
            <Form.Label>First name</Form.Label>
            <Form.Control
              type="text"
              placeholder=""
              value={first_name}
              onChange={(e) => setFirstName(e.target.value)}
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Last name</Form.Label>
            <Form.Control
              type="text"
              placeholder=""
              value={last_name}
              onChange={(e) => setLastName(e.target.value)}
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Email</Form.Label>
            <Form.Control
              disabled
              type="email"
              placeholder=""
              value={userdata.user}
            />
          </Form.Group>

          <Button type="submit" variant="primary">
            Submit
          </Button>
        </Form>
      </div>
    );
  }
}
