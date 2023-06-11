import { Drawer } from "antd";
import React from "react";
import Constant from "../common/Constant";
import { FilePdfOutlined, FileTextOutlined } from "@ant-design/icons";
import AppModal from "./AppModal";
class PreViewPane extends React.Component {
  state = { visible: false, disabled: true, color: "back", selectedRowData: [] };
  constructor(props) {
    super(props);
  }
  showDrawer = () => {
    this.setState({
      visible: true,
    });
  };

  onClose = () => {
    this.setState({
      visible: false,
    });
  };
  onClick = (e) => {
    if (this.state.disabled) {
      return;
    } else {
      let docType = e.currentTarget.getAttribute("data-id");
      let url = e.currentTarget.getAttribute("data-url");
      let customer = e.currentTarget.getAttribute("data-name");
      let ec_id = e.currentTarget.getAttribute("data-ec");
      let label = e.currentTarget.getAttribute("data-label");
      let dataKey = e.currentTarget.getAttribute("data-key") ?? "0";
      let number = this.state.selectedRowData[0][dataKey];
      let name = this.state.selectedRowData[0][customer];
      let ec_customer_id = this.state.selectedRowData[0][ec_id];
      if (url != undefined) {
        this.appModal.show({
          url: url + "?ids=" + number + "&user_id=" + docType + "&ec_customer_id=" + ec_customer_id,
          title: label + " : " + name,
          style: { width: "80%", height: "80vh" },
        });
        return;
      } else {
        window.open(Constant.appUrl + "/doc/" + docType + "/?number=" + number, "_blank");
      }
    }
  };
  getDoc = (doc) => {};
  selectedData = (selectedRowData) => {
    if (selectedRowData.length == 1) {
      this.setState({
        selectedRowData: selectedRowData,
        disabled: false,
        color: "#e61b23",
        reportColor: "#8ef59d",
      });
    } else {
      this.setState({
        selectedRowData: selectedRowData,
        disabled: true,
        color: "back",
        reportColor: "back",
      });
    }
  };
  getPreViewList = (value) => {
    return (
      <div className="preViewIcon">
        <table>
          <tr>
            {value.url != undefined ? (
              <td>
                <a
                  disabled={this.state.disabled}
                  key={value}
                  data-id={value.doc}
                  data-label={value.label}
                  data-ec={value.ec}
                  data-key={value.key}
                  data-url={value.url}
                  data-name={value.name}
                  onClick={this.onClick}
                >
                  <FileTextOutlined
                    key={value + this.state.disabled}
                    disabled={this.state.disabled}
                    data-id={value}
                    style={{ fontSize: "50px", color: this.state.reportColor }}
                  />
                </a>
              </td>
            ) : (
              <td>
                <a disabled={this.state.disabled} key={value} data-id={value.doc} data-key={value.key} onClick={this.onClick}>
                  <FilePdfOutlined
                    key={value + this.state.disabled}
                    disabled={this.state.disabled}
                    data-id={value}
                    style={{ fontSize: "50px", color: this.state.color }}
                  />
                </a>
              </td>
            )}
          </tr>
          <tr>
            <td>
              <span className="preViewSpan" style={{ width: 60, overflowWrap: "normal" }}>
                {value.label}{" "}
              </span>{" "}
            </td>
          </tr>
        </table>
      </div>
    );
  };
  render() {
    return (
      <div>
        <Drawer
          title="Document"
          placement="right"
          mask={false}
          onClose={this.onClose}
          visible={this.state.visible}
          getContainer={false}
          width={220}
          style={{ position: "absolute" }}
        >
          {this.props.PreViewList.map(this.getPreViewList)}
        </Drawer>
        <AppModal
          callBack={this.onModelClose}
          ref={(node) => {
            this.appModal = node;
          }}
        ></AppModal>
      </div>
    );
  }
}

PreViewPane.getInitialProps = async (context) => {
  return { url: process.env.SECRET };
};

export default PreViewPane;
