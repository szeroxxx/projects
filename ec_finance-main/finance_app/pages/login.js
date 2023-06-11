import React, { useState } from "react";
import { getProviders, signIn, getCsrfToken } from "next-auth/react";
import { Image, Form, Input, Button } from "antd";
import axios from "axios";
function Login({ providers, csrfToken }) {
  const [useCredential, setUseCredential] = useState(true);
  function useCredentials() {
    // do something here
    setUseCredential(true);
  }
  return (
    <div className="background-login">
      <meta charSet="UTF-8" />
      <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>Finance - Login</title>
      <link rel="preconnect" href="https://fonts.googleapis.com" />
      <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin />
      <div className="loginPage">
        <div className="loginForm">
          <div className="text-center">
            <Image preview={false} alt="Image" src="/logo.png" />
            <div className="text-center">
              {useCredential && (
                <>
                  <div>
                    <br></br>
                    <form method="post" action="/api/auth/callback/credentials">
                      <input name="csrfToken" type="hidden" defaultValue={csrfToken} />
                      <label>
                        <input className="login-text" name="username" type="text" placeholder="User name" required />
                      </label>
                      <br></br>
                      <label>
                        <input className="login-text" name="password" type="password" placeholder="Password" required />
                      </label>
                      <button className="signin_btn" type="submit">
                        <span className="signInWithGoogle-text">Sign in</span>
                      </button>
                    </form>
                  </div>
                  {!useCredential && (
                    <div className="text-center line_separator" id="linSaperator">
                      Or
                    </div>
                  )}
                </>
              )}

              {!useCredential &&
                Object.values(providers).map((provider) => (
                  <>
                    {provider.id == "google" && (
                      <button key={provider.id} className="signInWithGoogle" id={provider.id} type="button" onClick={() => signIn(provider.id)}>
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 48 48"
                          width="35px"
                          height="35px"
                          style={{
                            background: "#fff",
                            borderRadius: "25px",
                            marginTop: "5px",
                          }}
                        >
                          <path
                            fill="#FFC107"
                            d="M43.611,20.083H42V20H24v8h11.303c-1.649,4.657-6.08,8-11.303,8c-6.627,0-12-5.373-12-12c0-6.627,5.373-12,12-12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C12.955,4,4,12.955,4,24c0,11.045,8.955,20,20,20c11.045,0,20-8.955,20-20C44,22.659,43.862,21.35,43.611,20.083z"
                          />
                          <path
                            fill="#FF3D00"
                            d="M6.306,14.691l6.571,4.819C14.655,15.108,18.961,12,24,12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C16.318,4,9.656,8.337,6.306,14.691z"
                          />
                          <path
                            fill="#4CAF50"
                            d="M24,44c5.166,0,9.86-1.977,13.409-5.192l-6.19-5.238C29.211,35.091,26.715,36,24,36c-5.202,0-9.619-3.317-11.283-7.946l-6.522,5.025C9.505,39.556,16.227,44,24,44z"
                          />
                          <path
                            fill="#1976D2"
                            d="M43.611,20.083H42V20H24v8h11.303c-0.792,2.237-2.231,4.166-4.087,5.571c0.001-0.001,0.002-0.001,0.003-0.002l6.19,5.238C36.971,39.205,44,34,44,24C44,22.659,43.862,21.35,43.611,20.083z"
                          />
                        </svg>
                        <span className="signInWithGoogle-text">Sign in with Google</span>
                      </button>
                    )}
                  </>
                ))}
              {!useCredential && (
                <div id="orDivPrev">
                  Or,{" "}
                  <span className=" link-credentials underlinelink " onClick={useCredentials}>
                    sign in with your credentials
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
export async function getServerSideProps(context) {
  const providers = await getProviders();
  const csrfToken = await getCsrfToken(context);
  return {
    props: { providers, csrfToken, is_open: true },
  };
}
