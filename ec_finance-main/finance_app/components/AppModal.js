import { Modal } from "antd";
import React from "react";
import shortid from "shortid";
import DataForm from "./DataForm";
let iframeURL = "";
let schema = "";
let style = { width: "98%", height: "90vh" };
let isFrame = false;
class AppModal extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      title: "",
      visible: false,
      key: shortid.generate(),
    };
  }
  componentDidMount = () => {
    window.removeEventListener("message", this.postMessageHandler);
    window.addEventListener("message", this.postMessageHandler);
  };
  postMessageHandler = (event) => {
    const data = "";
    if (event.data != "") {
      data = JSON.parse(event.data);
    }
    this.hideModal(data);
  };
  showModal = (title, url) => {
    style = { width: "98%", height: "90vh" };
    iframeURL = url;
    schema = "";
    isFrame = true;
    this.setState({ title: title, visible: true, key: shortid.generate() });
  };
  show = (object) => {
    style = { width: "98%", height: "90vh" };
    iframeURL = "";
    schema = "";
    isFrame = false;
    let title = "";
    if (object.schema) {
      schema = object.schema;
      title = object.schema.pageTitle;
      if (object.schema.style) {
        style = object.schema.style;
      }
    } else {
      isFrame = true;
      iframeURL = object.url;
      title = object.title;
      if (object.style) {
        style = object.style;
      }
    }
    this.setState({ title: title, visible: true, key: shortid.generate() });
  };
  hideModal = (data) => {
    if (this.props.callBack) {
      this.props.callBack(data);
    }
    this.setState({ visible: false });
  };
  render() {
    return (
      <div>
        <Modal
          key={this.state.key}
          centered
          width={style.width ?? "95%"}
          bodyStyle={{ height: style.height ?? "90vh" }}
          title={this.state.title}
          visible={this.state.visible}
          onCancel={this.hideModal}
          footer={null}
        >
          {iframeURL != "" && <iframe src={iframeURL} style={{ width: "100%", height: "100%", border: 0 }} />}
          {schema != "" && (
            <DataForm
              key={shortid.generate()}
              schema={schema}
              isModal={true}
              isFrame={isFrame}
              ref={(node) => {
                this.dataForm = node;
              }}
            ></DataForm>
          )}
        </Modal>
      </div>
    );
  }
}

export default AppModal;
