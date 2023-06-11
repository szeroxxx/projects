import { useRef, useState, useEffect } from "react";
import {
  faCheck,
  faTimes,
  faInfoCircle,
  faCheckCircle,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import axios from "../../api/axios";
import { Link } from "react-router-dom";
import OverlayTrigger from "react-bootstrap/OverlayTrigger";
import Tooltip from "react-bootstrap/Tooltip";
import "./Register.css";
const PWD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%]).{8,24}$/;
const REGISTER_URL = "auth/register";
const VERIFYOTP_URL = "/auth/email_verification";
const Register = () => {
  const errRef = useRef();
  const [userInfo, setUserInfo] = useState({
    user: "",
    firstName: "",
    lastName: "",
    pwd: "",
    matchPwd: "",
    otp: "",
    userId: "",
  });
  const [validPwd, setValidPwd] = useState(false);
  const [validMatch, setValidMatch] = useState(false);
  const [matchFocus, setMatchFocus] = useState(false);
  const [errMsg, setErrMsg] = useState("");
  const [success, setSuccess] = useState(false);
  const [isOtpVerified, setIsOtpVerified] = useState(false);
  const [userId, setUserId] = useState("");
  useEffect(() => {
    setValidPwd(PWD_REGEX.test(userInfo.pwd));
    setValidMatch(userInfo.pwd === userInfo.matchPwd);
    setErrMsg("");
  }, [userInfo]);

  const handleChange = (event) => {
    setUserInfo({ ...userInfo, [event.target.name]: event.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const v2 = PWD_REGEX.test(userInfo.pwd);
    if (!v2) {
      setErrMsg("Invalid Entry");
      return;
    }
    try {
      const response = await axios({
        method: "post",
        url: REGISTER_URL,
        data: JSON.stringify({
          first_name: userInfo.firstName,
          last_name: userInfo.lastName,
          email: userInfo.user,
          password: userInfo.pwd,
        }),
        headers: {
          "Content-Type": "application/json",
        },
      });
      if (response?.data?.code == 0) {
        setErrMsg(response?.data?.message);
      } else {
        setSuccess(true);
        setUserId(response.data.user_id );
      }
    } catch (err) {
      if (!err?.response) {
        setErrMsg("No Server Response");
      } else if (err.response?.status === 409) {
        setErrMsg("Username Taken");
      } else {
        setErrMsg("Registration Failed");
      }
      errRef.current.focus();
    }
  };

  const verifyOTP = async () => {
    try {
      const response = await axios({
        method: "post",
        url: VERIFYOTP_URL + "/" + userId + "?otp=" + userInfo.otp,
        headers: {
          "Content-Type": "application/json",
        },
      });
      if (response?.data?.code == 0) {
        setErrMsg(response?.data?.message);
      } else {
        setIsOtpVerified(true);
      }
    } catch (err) {
      if (!err?.response) {
        setErrMsg("No Server Response");
      } else if (err.response?.status === 409) {
        setErrMsg("Username Taken");
      } else {
        setErrMsg("Registration Failed");
      }
      errRef.current.focus();
    }
  };
  return (
    <>
      <div className="signup-container">
        {success && isOtpVerified && (
          <section>
            <h1>
              {" "}
              <FontAwesomeIcon icon={faCheckCircle} /> Success!
            </h1>
            <div>Your account has been successfully created.</div>
            <p>
              <Link to="/login">Sign In</Link>
            </p>
          </section>
        )}

        {success && !isOtpVerified && (
          <section>
            <h3>
              {" "}
              <FontAwesomeIcon icon={faCheckCircle} /> Verify Email Address
            </h3>
            <div>
              Please enter the OTP we've send to
              <br></br>
              <b>{userInfo.user}</b>
              <br></br>
              <br></br>
            </div>
            <div>
              <div className="form-group">
                <input
                  type="text"
                  name="otp"
                  autoComplete="off"
                  value={userInfo.otp}
                  required
                  onChange={(e) => handleChange(e)}
                  className="form-control"
                />
              </div>
            </div>
            <div>
              <button className="btn btn-primary" onClick={verifyOTP}>
                Verify
              </button>
            </div>
          </section>
        )}
        {!success && !isOtpVerified && (
          <>
            <p
              ref={errRef}
              className={errMsg ? "errmsg" : "offscreen"}
              aria-live="assertive"
            >
              {errMsg}
            </p>
            <h1>Register</h1>
            <form onSubmit={handleSubmit} className="signup-form">
              <div className="form-group">
                <label htmlFor="firstName">First name:</label>
                <input
                  type="text"
                  name="firstName"
                  autoComplete="off"
                  value={userInfo.firstName}
                  required
                  onChange={(e) => handleChange(e)}
                  className="form-control"
                />
              </div>
              <div className="form-group">
                <label htmlFor="lastName">Last name:</label>
                <input
                  type="text"
                  name="lastName"
                  autoComplete="off"
                  value={userInfo.lastName}
                  required
                  onChange={(e) => handleChange(e)}
                  className="form-control"
                />
              </div>
              <div className="form-group">
                <label htmlFor="email">Email:</label>
                <input
                  type="email"
                  name="user"
                  autoComplete="off"
                  value={userInfo.user}
                  required
                  onChange={(e) => handleChange(e)}
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
                  className={validPwd || !userInfo.pwd ? "hide" : "invalid"}
                />
                <OverlayTrigger
                  key="pwdnote"
                  placement="right"
                  overlay={
                    <Tooltip id={`tooltip-pwdnote`}>
                      8 to 24 characters.
                      <br />
                      Must include uppercase and lowercase letters, a number and
                      a special character.
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
                value={userInfo.pwd}
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
                  className={validMatch && userInfo.matchPwd ? "valid" : "hide"}
                />
                <FontAwesomeIcon
                  icon={faTimes}
                  className={
                    validMatch || !userInfo.matchPwd ? "hide" : "invalid"
                  }
                />
              </label>
              <input
                type="password"
                name="matchPwd"
                onChange={(e) => handleChange(e)}
                value={userInfo.matchPwd}
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

              <button
                className="btn btn-primary"
                disabled={!validPwd || !validMatch ? true : false}
              >
                Sign Up
              </button>
            </form>
            <p>
              Already registered?
              <br />
              <span className="line-sign-in">
                <Link to="/login">Sign In</Link>
              </span>
            </p>
          </>
        )}
      </div>
    </>
  );
};

export default Register;
