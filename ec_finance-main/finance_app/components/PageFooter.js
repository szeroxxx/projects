import {

  Space

} from "antd";
const PageFooter = (props) => {
  return (
    <div className="modal-footer details-footer">
      <Space>
      {props.children}
      </Space>
    </div>
  );
};

export default PageFooter;
