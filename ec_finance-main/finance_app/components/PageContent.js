import { Layout } from "antd";
import React, { useLayoutEffect, useState } from "react";
const PageContent = (props) => {
  const [width, height] = useWindowSize(props);
  return (
    <Layout className="site-layout-background">
      <div style={{ height: height, overflowY: "scroll" }}>{props.children}</div>
    </Layout>
  );
};
function useWindowSize(props) {
  const [size, setSize] = useState([0, 0]);
  useLayoutEffect((props) => {
    function updateSize() {
      if (props.IsModel) {
        setSize([window.innerWidth, window.innerHeight - 90]);
      } else {
        setSize([window.innerWidth, window.innerHeight - 250]);
      }
    }
    window.addEventListener("resize", updateSize);
    updateSize(props);
    return () => window.removeEventListener("resize", updateSize);
  }, []);
  return size;
}
export default PageContent;
