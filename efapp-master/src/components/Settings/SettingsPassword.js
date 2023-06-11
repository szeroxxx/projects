import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import {Container } from "react-bootstrap";

import { useState,useEffect } from "react";
import "./Settings.css";
import OverlayTrigger from "react-bootstrap/OverlayTrigger";
import Tooltip from "react-bootstrap/Tooltip";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {faCheck,faTimes,faInfoCircle} from "@fortawesome/free-solid-svg-icons";
import useLocalStorage from "../../hooks/useLocalStorage";
import useAxiosPrivate from "../../hooks/useAxiosPrivate";
const PWD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%]).{8,24}$/;
export default function Settings_Password(props) {
  const {show} = props;
  const [userdata] = useLocalStorage("userdata");
  const axiosPrivate = useAxiosPrivate();
  const [pwd, setPwd] = useState("");
  const [matchPwd, setMatchPwd] = useState("");
  const [validPwd, setValidPwd] = useState(false);
  const [validMatch, setValidMatch] = useState(false);
  const [alertMsg, setAlertMsg] = useState({ class: "hide", message: "" });
  const [otp, setOtp] = useState("");
  const [isOTP, setIsOTP] = useState(false);
  const [isPwdChanged, setIsPwdChanged] = useState(false);
  const [reSetCounter, setReSetCounter] = useState(0);


  useEffect(() => {
    reSetCounter > -1 && setTimeout(() => setReSetCounter(reSetCounter-1), 1000);
  }, [reSetCounter]);

  useEffect(() => {
    setValidPwd(PWD_REGEX.test(pwd));
    setValidMatch(pwd === matchPwd);
  }, [pwd,matchPwd,isOTP]);
  const requestOTP=async()=>{
    try {
      const response = await axiosPrivate.post(
       `/app/otp_mail/${userdata.user_id}`
      );
      if ((response.data.code =="1")) {
        setReSetCounter(60);
        setIsOTP(true);
      } else {
        setAlertMsg({
          class: "alert alert-danger",
          message: response.data.message,
        });
      }
    } catch (err) {
      console.log(err);
    }
  }
  const cancel=()=>{
    setOtp("");
    setPwd("");
    setMatchPwd("");
    setIsOTP(false);

  }
  const resetPassword=async()=>{
    try {
      const response = await axiosPrivate.put(
       `/auth/password_reset/${userdata.user_id}?new_password=${pwd}&otp=${otp}`,
       {
          headers: {   "Content-Type": "multipart/form-data" },
       }
      );
      if ((response.data.code == "1")) {
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
      } else {
        setAlertMsg({
          class: "alert alert-danger",
          message: response.data.message,
        });
      }
    } catch (err) {
      console.log(err);
    }

  }
  return (
    <>
      {show && (
        <div className="col-md-4">
         <div className={alertMsg.class} role="alert">
            {alertMsg.message}
          </div>
          <Form  className={isPwdChanged?'hide':''} >
            <Container className={isOTP?'hide':''} >
            <Form.Group className="mb-4">
              <Form.Label>New password      <FontAwesomeIcon
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
                    Must include uppercase and lowercase letters, a number and a
                    special character.
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
              </OverlayTrigger></Form.Label>
              <Form.Control type="password" value={pwd}    onChange={(e) => setPwd(e.target.value)} placeholder="" />
            </Form.Group>

            <Form.Group className="mb-4">
              <Form.Label>Confirm
              <FontAwesomeIcon
                icon={faCheck}
                className={validMatch && matchPwd ? "valid" : "hide"}
              />
              <FontAwesomeIcon
                icon={faTimes}
                className={
                  validMatch || !matchPwd ? "hide" : "invalid"
                }
              />

              </Form.Label>
              <Form.Control type="password" value={matchPwd}    onChange={(e) => setMatchPwd(e.target.value)} placeholder="" />
              <p
              id="confirmnote"
              className={
                 !validMatch ? "instructions" : "offscreen"
              }
            >
              <FontAwesomeIcon icon={faInfoCircle} />
              Must match the first password input field.
            </p>
            </Form.Group>
            <Button  onClick={requestOTP}  disabled={!validPwd || !validMatch ? true : false} type="button">
              Reset Password
            </Button>
            </Container>
            <Container className={isOTP?'':'hide'} >
              <span>
              Please enter the OTP (one-time password) sent to your email to verify your identity and proceed with changing your password.
              </span>
              <br></br>
            <Form.Group className="mb-4">
              <Form.Label>OTP</Form.Label>
              <Form.Control type="text" value={otp}    onChange={(e) => setOtp(e.target.value)} placeholder="" />
              <span className={reSetCounter>0?'hide':''}> <a className="btn-resend-otp" onClick={requestOTP} >Resend OTP</a> </span> <span className={reSetCounter>0?'':'hide'}> Resend OTP in {reSetCounter}s</span>
            </Form.Group>


            <Button variant="primary" className="btn-verify" onClick={resetPassword} type="button">
              Verify
            </Button>
            <Button variant="outline-primary" onClick={cancel} type="button">
              Cancel
            </Button>
           </Container>
          </Form>
        </div>
        )}</>

        )
}
