import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import "./Settings.css";
import useLocalStorage from "../../hooks/useLocalStorage";
import useAxiosPrivate from "../../hooks/useAxiosPrivate";
import { useEffect, useState, useRef } from "react";
import { Image } from "react-bootstrap";
import profilePic from "../../static/profilepic.svg";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEdit } from "@fortawesome/free-solid-svg-icons";

export default function SettingsOrg(props) {
  const { show } = props;
  const [userdata] = useLocalStorage("userdata");
  const [orgData, setOrgData] = useState(false);
  const [alertMsg, setAlertMsg] = useState({ class: "hide", message: "" });
  const axiosPrivate = useAxiosPrivate();
  const hiddenAvatarInput = useRef(null);

  const handleChange = (event) => {
    setOrgData({ ...orgData, [event.target.name]: event.target.value });
    setAlertMsg({ class: "hide", message: "" });
  };

  const getOrganizationDetails = async () => {
    try {
      const response = await axiosPrivate.get(
        `/app/org/get/${userdata.current_org_id}`,
        {
          headers: { "Content-Type": "application/json" },
        }
      );
      setOrgData(response.data[0]);
    } catch (err) {
      console.log(err);
    }
  };

  const saveOrgDetails = async (e) => {
    e.preventDefault();
    try {
      const response = await axiosPrivate.put(
        `/app/org/edit/${userdata.current_org_id}`,
        JSON.stringify({
          name: orgData.name,
          location: orgData.location,
          domain_url: orgData.domain_url,
        }),
        {
          headers: { "Content-Type": "application/json" },
        }
      );
      if ((response.data.code == "1")) {
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
    } catch (err) {
      console.log(err);
    }
  };

  const [logo, setLogo] = useState(
    `${process.env.REACT_APP_SERVER_URL}/org/logo_get/${userdata.current_org_id}`
  );

  const onFileChange = async (e) => {
    let files = e.target.files;
    let file = files[0];
    var formData = new FormData();
    formData.append("logo", file);
    try {
      const response = await axiosPrivate.post(
        `/logo_upload/${userdata.current_org_id}`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      if(response.data.code == "1"){
        setLogo(
          `${process.env.REACT_APP_SERVER_URL}/org/logo_get/${userdata.current_org_id}?v=0.1`
        );
        setAlertMsg({
          class: "alert alert-success",
          message: response.data.message,
        });
        setTimeout(() => {
          clearMessage();
        }, 3000);

      } else {
        setAlertMsg({
          class: "alert alert-danger",
          message: response.data.message,
        });
        setTimeout(() => {
          clearMessage();
        }, 3000);

      }

    } catch (error) {
      console.error(error);
    }
  };

  const handleLogoClick = (event) => {
    hiddenAvatarInput.current.click();
  };

  const handleImageError = () => {
    setLogo(profilePic);
  };

  useEffect(() => {
    getOrganizationDetails();
  },[]);

  const clearMessage = () => {
    setAlertMsg({
      class: "hide",
      message: "",
    });
  };

  return (
    <>
      <div className={alertMsg.class} role="alert">
        {alertMsg.message}
      </div>
      {show && orgData && (
        <div className="col-md-4">
          <table>
            <thead>
              <tr>
                <td>
                  <Image
                    src={`${logo}`}
                    onError={handleImageError}
                    className="avatar"
                  ></Image>
                </td>
                <td style={{ paddingLeft: "10px" }}>
                  <FontAwesomeIcon icon={faEdit} onClick={handleLogoClick} />
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

          <Form onSubmit={saveOrgDetails}>
            <Form.Group className="mb-3">
              <Form.Label>Organization</Form.Label>
              <Form.Control
                type="text"
                name="name"
                value={orgData.name}
                onChange={handleChange}
                placeholder=""
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Location</Form.Label>
              <Form.Control
                type="text"
                name="location"
                value={orgData.location}
                onChange={handleChange}
                placeholder=""
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Website</Form.Label>
              <Form.Control
                type="text"
                name="domain_url"
                value={orgData.domain_url}
                onChange={handleChange}
                placeholder=""
              />
            </Form.Group>
            <Button variant="primary" type="submit">
              Submit
            </Button>
          </Form>
        </div>
      )}
    </>
  );
}
