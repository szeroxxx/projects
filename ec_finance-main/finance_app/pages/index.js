import AppLayout from "../components/AppLayout";
import React, { Component } from "react";

import { Image, Typography } from "antd";
const { Title } = Typography;
class index extends Component {
  state = { data: {} };
  render() {
    return (
      <>
        <div className="index_logo">
          <Image src="/logo.png" alt={"Image"} />
        </div>
        <span className="index_title">
          <Image preview={false} src="/waving-hand.svg" alt={"Image"} style={{ marginBottom: 10, marginRight: 5 }} />
          <Title>Welcome!</Title>
        </span>
        <Title level={4} className="index_title">
          Financial App from Eurocircuits.
        </Title>
      </>
    );
  }
}

export default index;
