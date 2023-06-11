import { MenuOutlined } from "@ant-design/icons";
import { Modal, Button, Dropdown, Menu, Space } from "antd";
import { ExclamationCircleOutlined, PoweroffOutlined } from "@ant-design/icons";
import shortid from "shortid";
const { confirm } = Modal;
import React from "react";
import AppIcons from "./AppIcons";

class ActionPanel extends React.Component {
  state = {
    loadings: [],
  };
  componentDidMount() {}

  shouldDisable(isMultiSelection) {
    // If no selection defined then always enable
    if (isMultiSelection === undefined) {
      return false;
    }
    // If selection defined but no row selected then disable
    if (this.props.selectedRows === undefined && isMultiSelection !== undefined) {
      return true;
    }

    // Disable when multiple/zero row selected and multi selection is not allowed
    if (isMultiSelection == false && this.props.selectedRows.length != 1) {
      return true;
    }

    // Disable when multiple allowed and no row selected
    if (isMultiSelection && this.props.selectedRows.length == 0) {
      return true;
    }
    // If none of the case meet the condition, always enable it.
    return false;
  }

  clickHanlder = (button) => {
    this.showButtonLoading(button.name);
    if (button.click_handler) {
      button.click_handler();
    } else if (button.confirm) {
      let icon = <ExclamationCircleOutlined />;
      if (button.confirm.icon) {
        icon = button.confirm.icon;
      }
      confirm({
        title: button.confirm.title,
        icon: icon,
        content: button.confirm.content,
        okText: button.confirm.okText ?? "Ok",
        cancelText: button.confirm.cancelText ?? " cancel",
        onOk() {
          button.confirm.onOk();
        },
        onCancel() {
          console.log("Cancel");
        },
      });
    }
  };
  showButtonLoading = (name) => {
    this.setState(({ loadings }) => {
      const newLoadings = [...loadings];
      newLoadings[name] = true;
      return {
        loadings: newLoadings,
      };
    });
    setTimeout(() => {
      this.setState(({ loadings }) => {
        const newLoadings = [...loadings];
        newLoadings[name] = false;
        return {
          loadings: newLoadings,
        };
      });
    }, 500);
  };

  render() {
    let mainButtons = this.props.buttons.filter((button) => button.position != "menu");
    let menuButtons = this.props.buttons.filter((button) => button.position == "menu");

    const menu = (
      <Menu>
        {menuButtons.map((button) => (
          <Menu.Item key={shortid.generate()} disabled={this.shouldDisable(button.multi_select)}>
            <a className="ant-dropdown-link" onClick={() => this.clickHanlder(button)}>
              <span style={{ marginRight: 5 }}>
                <AppIcons code={button.icon_code} />
              </span>
              {button.title}
            </a>
          </Menu.Item>
        ))}
      </Menu>
    );

    return (
      <>
        <div style={{ float: "right" }}>
          <Space>
            {mainButtons.map((button) => (
              <Button
                key={shortid.generate()}
                loading={(this.state.loadings && this.state.loadings[button.name]) ?? false}
                disabled={this.shouldDisable(button.multi_select)}
                danger={button.style == "danger" ? true : false}
                type={button.type}
                onClick={() => this.clickHanlder(button)}
                icon={<AppIcons code={button.icon_code} />}
              >
                {button.title}
              </Button>
            ))}

            {menuButtons.length > 0 ? (
              <Dropdown overlay={menu} placement="bottomCenter">
                <Button>
                  <MenuOutlined />
                </Button>
              </Dropdown>
            ) : (
              <></>
            )}
          </Space>
        </div>
      </>
    );
  }
}
export default ActionPanel;
