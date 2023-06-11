import { useRef, useState, useEffect } from 'react';
import useAuth from '../../hooks/useAuth';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import './Login.css';
import useLocalStorage from "../../hooks/useLocalStorage";

import axios from '../../api/axios';
const LOGIN_URL = '/auth/login';

const Login = () => {
    const { setAuth, persist, setPersist } = useAuth();
    const [userdata, setUserData] = useLocalStorage('userdata','');
    const [refreshtoken, setRefreshToken] = useLocalStorage('refresh_token','');

    const navigate = useNavigate();
    const location = useLocation();
    let from = location.state?.from?.pathname || "/";
    from=from+ (location.state?.from?.search || "");
    const userRef = useRef();
    const errRef = useRef();

    const [user, setUser] = useState('');
    const [pwd, setPwd] = useState('');
    const [errMsg, setErrMsg] = useState('');
    const [IaSignIn, setIsSignIn] = useState(false);

    useEffect(() => {
        userRef.current.focus();
    }, [])

    useEffect(() => {
        setErrMsg('');
        if(user !== "" && pwd !== ""){
            setIsSignIn(true)
        }
    }, [user, pwd])

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const response = await axios.post(LOGIN_URL,
                JSON.stringify({ username: user, password: pwd }),
                {
                    headers: { 'Content-Type': 'application/json' },
                    withCredentials: true
                }
            );
            if(response?.data?.org_id){
                for(var org in response.data.org_id){
                    if (response.data.org_id[org].is_default === "true") {
                        var current_org_id = response.data.org_id[org].org_id
                        var current_org_name = response.data.org_id[org].name
                    }
                }
            }
            const access_token = response?.data?.access_token;
            const refresh_token = response?.data?.refresh_token;
            const first_name = response?.data?.first_name;
            const last_name = response?.data?.last_name;
            const org_id = response?.data?.org_id;
            const user_id = response?.data?.user_id;
            setAuth({ access_token });
            setRefreshToken(refresh_token);
            setUserData({user, first_name, last_name, org_id, user_id, current_org_id, current_org_name});
            setPersist(prev => !prev);
            setUser('');
            setPwd('');
            navigate("/dashboard");
        } catch (err) {
            if (!err?.response) {
                console.log(err);
                setErrMsg('No Server Response');
            } else if (err.response?.status === 400) {
                setErrMsg('Missing Username or Password');
            } else if (err.response?.status === 401) {
                setErrMsg('Unauthorized');
            } else {
                setErrMsg('Login Failed');
            }
            errRef.current.focus();
        }
    }

    useEffect(() => {
        localStorage.setItem("persist", persist);
    }, [persist])

    return (
      <div className="login-container">
        <p
          ref={errRef}
          className={errMsg ? "errmsg" : "offscreen"}
          aria-live="assertive"
        >
          {errMsg}
        </p>
        <h1>Sign In</h1>
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Username:</label>
            <input
              className="form-control"
              type="text"
              id="username"
              ref={userRef}
              autoComplete="off"
              onChange={(e) => setUser(e.target.value)}
              value={user}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password:</label>
            <input
              className="form-control"
              type="password"
              id="password"
              onChange={(e) => setPwd(e.target.value)}
              value={pwd}
              required
            />
          </div>
          <button className="btn btn-primary" disabled={!IaSignIn ? true:false}>
            Sign In
          </button>
        </form>
        <div className="login-form-footer">
          <span className="line">
            <Link className="login-form-footer-link" to="/password_reset">
              Forgot password?
            </Link>
          </span>
        </div>
        <div className="login-form-footer">
          Need an Account?
          <br />
          <span className="line">
            <Link className="login-form-footer-link" to="/register">
              Sign Up
            </Link>
          </span>
        </div>
        <div className="login-form-google">
          {/* <button type="button" className="btn btn-google">
            <i className="fab fa-google"></i>
            Sign in with Google
          </button> */}
        </div>
      </div>
    );
}

export default Login
