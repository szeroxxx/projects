import React from "react";
import { Image } from "antd";
// import AppLayout from "../components/AppLayout";
// import PageTitle from "../components/PageTitle";

const splash = () => {
  return (
    <div className="splash_logo">
      <Image preview={false} alt="Image" src="/logo.png" />
      <div className="loader"></div>
    </div>
  );
};
export default splash;
