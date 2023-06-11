import React from "react";
import Tooltip from "react-bootstrap/Tooltip";
import OverlayTrigger from "react-bootstrap/OverlayTrigger";

const ToolTip = ({ text, children }) => {
  const tooltip = <Tooltip id="tooltip">{text}</Tooltip>;
  return (
    <OverlayTrigger placement="top" overlay={tooltip}>
      {children}
    </OverlayTrigger>
  );
};

export default ToolTip;
