import { useRef, useState, useEffect } from 'react';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {faCheck,faTimes,faInfoCircle,faCheckCircle,} from "@fortawesome/free-solid-svg-icons";
import { Link} from 'react-router-dom';
import OverlayTrigger from "react-bootstrap/OverlayTrigger";
import Tooltip from "react-bootstrap/Tooltip";
import './Login.css';
import axios from '../../api/axios';
const PWD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%]).{8,24}$/;
const ResetPassword = () => {
    const errRef = useRef();
    const [errMsg, setErrMsg] = useState('');
    const [hasOTP, setHasOTP] = useState(false);
    const [formInfo, setFormInfo] = useState({user: "",pwd: "",matchPwd: "",otp: "",userId: "",});
    const [validPwd, setValidPwd] = useState(false);
    const [validMatch, setValidMatch] = useState(false);
    const [matchFocus, setMatchFocus] = useState(false);
    useEffect(() => {
        setValidPwd(PWD_REGEX.test(formInfo.pwd));
        setValidMatch(formInfo.pwd === formInfo.matchPwd);
        setErrMsg("");
      }, [formInfo]);

    const handleChange = (event) => {
      setFormInfo({ ...formInfo, [event.target.name]: event.target.value });
    };

    const sendPasswordResetOTP  = async () => {

      if (formInfo.user === "") {
        setErrMsg("Please fill out this Username")
      } else {
        const response = await axios.post(`/app/otp_using_email?email=${formInfo.user}`,
            {
              headers: { 'Content-Type': 'application/json' },
            }
        );
        if (response.data.code == "0") {
          setErrMsg(response.data.message)
        } else {
          setFormInfo({...formInfo , userId: response.data.user_id });
          setHasOTP(true);
        }
      }
    }

    const resetPassword = async () => {
      if (formInfo.otp === "" ) {
        setErrMsg("Please fill out this OTP")
      } else if (formInfo.pwd === "") {
        setErrMsg("Please fill out this Password")
      } else if (formInfo.matchPwd === "") {
        setErrMsg("Please fill out this Confirm Password")
      } else {
        const response = await axios.put(`/auth/password_reset/${formInfo.userId}?new_password=${formInfo.pwd}&otp=${formInfo.otp}`,
          {
            headers: { 'Content-Type': 'application/json' },
          }
        );
        if (response.data && response.data.code == "0") {
          setErrMsg(response.data.message)
        } else {
          setHasOTP(false);
          setErrMsg(response.data.message)
        }
      }
    }

    return (
      <div className="login-container">
        <p
          ref={errRef}
          className={errMsg ? "errmsg" : "offscreen"}
          aria-live="assertive"
        >
          {errMsg}
        </p>
        <h3>Reset your password</h3>
        <div className={hasOTP ? "hide" : "login-form"}>
          <div className="form-group">
            <label htmlFor="user">Username:</label>
            <input
              type="text"
              id="user"
              name="user"
              onChange={(e) => handleChange(e)}
              required
              className="form-control"
            />
          </div>
          <button className="btn btn-primary" onClick={sendPasswordResetOTP}>
            Send password reset OTP
          </button>
        </div>
        <div className={hasOTP ? "login-form" : "hide"}>
          <div className="form-group">
            <label htmlFor="username">OTP:</label>
            <input
              type="text"
              name="otp"
              onChange={(e) => handleChange(e)}
              value={formInfo.otp}
              required
              className="form-control"
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">
              Password:
              <FontAwesomeIcon
                icon={faCheck}
                className={validPwd ? "valid" : "hide"}
              />
              <FontAwesomeIcon
                icon={faTimes}
                className={validPwd || !formInfo.pwd ? "hide" : "invalid"}
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
              </OverlayTrigger>
            </label>
            <input
              type="password"
              name="pwd"
              onChange={(e) => handleChange(e)}
              value={formInfo.pwd}
              required
              aria-invalid={validPwd ? "false" : "true"}
              className="form-control"
            />
          </div>
          <div className="form-group">
            <label htmlFor="confirm_pwd">
              Confirm Password:
              <FontAwesomeIcon
                icon={faCheck}
                className={validMatch && formInfo.matchPwd ? "valid" : "hide"}
              />
              <FontAwesomeIcon
                icon={faTimes}
                className={
                  validMatch || !formInfo.matchPwd ? "hide" : "invalid"
                }
              />
            </label>
            <input
              type="password"
              name="matchPwd"
              onChange={(e) => handleChange(e)}
              value={formInfo.matchPwd}
              required
              aria-invalid={validMatch ? "false" : "true"}
              onFocus={() => setMatchFocus(true)}
              onBlur={() => setMatchFocus(false)}
              className="form-control"
            />
            <p
              id="confirmnote"
              className={
                matchFocus && !validMatch ? "instructions" : "offscreen"
              }
            >
              <FontAwesomeIcon icon={faInfoCircle} />
              Must match the first password input field.
            </p>
          </div>
          <button className="btn btn-primary" onClick={resetPassword}>
            Submit
          </button>
        </div>
        <div className="login-form-footer">
          <span className="line">
            <Link className="login-form-footer-link" to="/login">
              Back to sign in
            </Link>
          </span>
        </div>
      </div>
    );
}

export default ResetPassword
