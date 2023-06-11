import { Button, Row, Col, Image, Container } from "react-bootstrap";
import "../Settings.css";
import useAxiosPrivate from "../../../hooks/useAxiosPrivate";
import {useLocation } from 'react-router-dom';
import { useEffect, useState } from "react";
import Form from "react-bootstrap/Form";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import OverlayTrigger from "react-bootstrap/OverlayTrigger";
import Tooltip from "react-bootstrap/Tooltip";
import {
  faCheck,
  faTimes,
  faInfoCircle,
} from "@fortawesome/free-solid-svg-icons";
import { useNavigate } from "react-router-dom";

const PWD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%]).{8,24}$/;

export default function Invitation() {
  const location = useLocation();
  let from = location?.search || "/";
  const userId=new URLSearchParams(from).get('s').split('#S#')[1];
  const orgId=new URLSearchParams(from).get('s').split('#S#')[0];
  const axiosPrivate = useAxiosPrivate();
  const navigate = useNavigate();

  const [orgData, setOrgData] = useState(false);
  const [alertMsg, setAlertMsg] = useState({ class: "hide", message: "" });
  const [Reset, setReset] = useState(false)
  const [pwd, setPwd] = useState("");
  const [validPwd, setValidPwd] = useState(false);
  const [matchPwd, setMatchPwd] = useState("");
  const [validMatch, setValidMatch] = useState(false);
  const [reSetCounter, setReSetCounter] = useState(0);
  const [isOTP, setIsOTP] = useState(false);
  const [otp, setOtp] = useState("");
  const [isPwdChanged, setIsPwdChanged] = useState(false);


  const getInvitations = async () => {
     let url="/org/users_invitation/"+ orgId+"%23S%23"+userId;
    try {
      const response = await axiosPrivate.post(
        url,
        {
          headers: { "Content-Type": "application/json" },
        }
      );
      if(response.data.code == "0"){
        setAlertMsg({
          class: "alert alert-danger",
          message: response.data.message,
        });
      } else {
      setOrgData(response.data[0]);
      }
    } catch (err) {
      console.log(err);
    }
  };

  const saveAccept = async (e) => {
    e.preventDefault();
    let url="/org/validate_invitation/"+orgId+"%23S%23"+userId;
    try {
      const response = await axiosPrivate.post(
        url,
        {
          headers: { "Content-Type": "application/json" },
        }
      );
      if (response.data.code == "1") {
        setAlertMsg({
          class: "alert alert-success",
          message: response.data.message,
        });
        setTimeout(() => {
          navigate("/login");
        }, 2000);
      } else if (response.data.code == "2") {
        setAlertMsg({
          class: "alert alert-success",
          message: response.data.message,
        });
        setTimeout(() => {
          navigate("/login");
        }, 2000);
      } else if (response.data.code == "3") {
        setOrgData(false);
        setReset(true);
        clearMessage();
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

  const cancelInvitation = async (e) => {
    e.preventDefault();
    let url="/app/org/cancel_invitation/"+ userId +"/"+orgId;
    try {
      const response = await axiosPrivate.post(
        url,
        {
          headers: { "Content-Type": "application/json" },
        }
      );
      if (response.data.code == "1") {
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

  const requestOTP = async () => {
     try {
       const response = await axiosPrivate.post(`/app/otp_mail/${userId}`);
       console.log('response: ', response);
       if (response.data.code == "1") {
          setReSetCounter(60);
          setIsOTP(true);
          setReset(false);
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

    const resetPassword = async () => {
      try {
        const response = await axiosPrivate.post(
          `/org/accept_invitation?org_id=${orgId}&user_id=${userId}&password=${pwd}&otp=${otp}`,
          {
            headers: { "Content-Type": "multipart/form-data" },
          }
        );
        if (response.data.code == "1") {
          setAlertMsg({
            class: "alert alert-success",
            message: response.data.message,
          });
          setOtp("");
          setPwd("");
          setMatchPwd("");
          setIsOTP(false);
          setIsPwdChanged(true);
          setTimeout(() => {
            setIsPwdChanged(false);
            setAlertMsg({ class: "hide", message: "" });
          }, 5000);
          navigate("/login");

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

    useEffect(() => {
      setValidPwd(PWD_REGEX.test(pwd));
      setValidMatch(pwd === matchPwd);
    }, [pwd, matchPwd, isOTP]);

    useEffect(() => {
      getInvitations();
    }, [userId]);

    useEffect(() => {
      reSetCounter > -1 &&
        setTimeout(() => setReSetCounter(reSetCounter - 1), 1000);
    }, [reSetCounter]);

    const cancel = () => {
      setOtp("");
      setPwd("");
      setMatchPwd("");
      setIsOTP(false);
    };

    const clearMessage = () => {
      setAlertMsg({
        class: "hide",
        message: "",
      });
    };

    const [imageSrc, setImageSrc] = useState(
      `${process.env.REACT_APP_SERVER_URL}/user/avatar_get/111`
    );
    const handleImageError = () => {
      setImageSrc(imageSrc);
    };

  return (
    <>
      <Row md={12} style={{ textAlign: "center" }}>
        <div className={alertMsg.class} role="alert">
          {alertMsg.message}
        </div>
        <Col md={3}></Col>
        {orgData && (
          <Col md={6}>
            <div className="invitations_container">
              <div className="invite_by_user_image">
                <Image
                  src={`${process.env.REACT_APP_SERVER_URL}/user/avatar_get/111`}
                  onError={handleImageError}
                  className="avatar"
                ></Image>
              </div>
              <div className="invite_by_user_image">
                <b>{orgData.invited_by} </b>invited you to join{" "}
                <b>{orgData.organization}</b>.
              </div>
              <Row className="inv_btn_container">
                <Col className="md-2 sm-2">
                  <Button type="button" onClick={saveAccept}>
                    Accept
                  </Button>
                </Col>
                <Col className="md-2 sm-2">
                  <Button
                    variant="outline-primary"
                    type="button"
                    onClick={cancelInvitation}
                  >
                    Reject
                  </Button>
                </Col>
              </Row>
            </div>
          </Col>
        )}
        <Col md={3}></Col>
      </Row>

      <div className="col-md-4 set-password-invitation">
        <Form>
          {Reset && (
            <Container>
              <Form.Group className="mb-4">
                <Form.Label>
                  Password{" "}
                  <FontAwesomeIcon
                    icon={faCheck}
                    className={validPwd ? "valid" : "hide"}
                  />
                  <FontAwesomeIcon
                    icon={faTimes}
                    className={validPwd || !pwd ? "hide" : "invalid"}
                  />
                  <OverlayTrigger
                    key="pwdnote"
                    placement="right"
                    overlay={
                      <Tooltip id={`tooltip-pwdnote`}>
                        8 to 24 characters.
                        <br />
                        Must include uppercase and lowercase letters, a number
                        and a special character.
                        <br />
                        Allowed special characters:{" "}
                        <span aria-label="exclamation mark">!</span>{" "}
                        <span aria-label="at symbol">@</span>{" "}
                        <span aria-label="hashtag">#</span>{" "}
                        <span aria-label="dollar sign">$</span>{" "}
                        <span aria-label="percent">%</span>
                      </Tooltip>
                    }
                  >
                    <FontAwesomeIcon icon={faInfoCircle} />
                  </OverlayTrigger>
                </Form.Label>
                <Form.Control
                  type="password"
                  value={pwd}
                  onChange={(e) => setPwd(e.target.value)}
                  placeholder=""
                />
                <Form.Group className="mb-4">
                  <Form.Label>
                    Confirm
                    <FontAwesomeIcon
                      icon={faCheck}
                      className={validMatch && matchPwd ? "valid" : "hide"}
                    />
                    <FontAwesomeIcon
                      icon={faTimes}
                      className={validMatch || !matchPwd ? "hide" : "invalid"}
                    />
                  </Form.Label>
                  <Form.Control
                    type="password"
                    value={matchPwd}
                    onChange={(e) => setMatchPwd(e.target.value)}
                    placeholder=""
                  />
                  <p
                    id="confirmnote"
                    className={!validMatch ? "instructions" : "offscreen"}
                  >
                    <FontAwesomeIcon icon={faInfoCircle} />
                    Must match the first password input field.
                  </p>
                </Form.Group>
                <Button
                  onClick={requestOTP}
                  disabled={!validPwd || !validMatch ? true : false}
                  type="button"
                >
                  Reset Password
                </Button>
              </Form.Group>
            </Container>
          )}
          <Container className={isOTP ? "" : "hide"}>
            <span>
              Please enter the OTP (one-time password) sent to your email to
              verify your identity and proceed with changing your password.
            </span>
            <br></br>
            <Form.Group className="mb-4">
              <Form.Label>OTP</Form.Label>
              <Form.Control
                type="text"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                placeholder=""
              />
              <span className={reSetCounter > 0 ? "hide" : ""}>
                {" "}
                <a className="btn-resend-otp" onClick={requestOTP}>
                  Resend OTP
                </a>{" "}
              </span>{" "}
              <span className={reSetCounter > 0 ? "" : "hide"}>
                {" "}
                Resend OTP in {reSetCounter}s
              </span>
            </Form.Group>

            <Button
              variant="primary"
              className="btn-verify"
              onClick={resetPassword}
              type="button"
            >
              Verify
            </Button>
            <Button variant="outline-primary" onClick={cancel} type="button">
              Cancel
            </Button>
          </Container>
        </Form>
      </div>
    </>
  );
}