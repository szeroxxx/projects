import { Layout } from "antd";
import React, { useLayoutEffect, useState } from "react";
import AppHeader from "./AppHeader";
import AppSider from "./AppSider";

const { Content } = Layout;
const AppLayout = (props) => {
  const [width, height] = useWindowSize(props);
  if (props.IsModel) {
    return (
      <Layout className="site-layout">
        <Layout>
          <Content
            className="site-layout-background"
            style={{
              minHeight: "100%",
            }}
          >
            {props.children}
          </Content>
        </Layout>
      </Layout>
    );
  }

  return (
    <Layout className="site-layout">
      <AppSider></AppSider>
      <Layout>
        <AppHeader></AppHeader>
        <Content
          className="site-layout-background"
          style={{
            paddingLeft: 24,
            paddingRight: 24,
            paddingTop: 5,
            margin: 0,
            minHeight: height,
          }}
        >
          {props.children}
        </Content>
      </Layout>
    </Layout>
  );
};
function useWindowSize(props) {
  const [size, setSize] = useState([0, 0]);
  useLayoutEffect(() => {
    function updateSize() {
      if (props.IsModel) {
        setSize([window.innerWidth, window.innerHeight]);
      } else {
        setSize([window.innerWidth, window.innerHeight - 50]);
      }
    }
    window.addEventListener("resize", updateSize);
    updateSize(props);
    return () => window.removeEventListener("resize", updateSize);
  }, []);
  return size;
}
export default AppLayout;
