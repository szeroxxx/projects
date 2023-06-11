import { MenuFoldOutlined, MenuUnfoldOutlined } from "@ant-design/icons";
import { Layout, Menu } from "antd";
import axios from "axios";
import Link from "next/link";
import React from "react";
import AppIcons from "./AppIcons";
import { getSession } from "next-auth/react";
const { SubMenu } = Menu;
const { Sider } = Layout;
class AppSider extends React.Component {
  state = {
    openKeys: [localStorage.getItem("openKeys")],
    collapsed: localStorage.getItem("collapsed") == "true" ? true : false,
    menuItems: [],
    current: localStorage.getItem("default_key"),
    current_sub: localStorage.getItem("default_sub_key"),
  };

  toggle = () => {
    if (localStorage.getItem("collapsed") == "false") {
      localStorage.setItem("collapsed", true);
    } else {
      localStorage.setItem("collapsed", false);
    }
    this.setState({
      collapsed: !this.state.collapsed,
    });
  };
  componentDidMount() {
    getSession().then((session) => {
      let { user_id } = session.user.data;
      this.setMenu(user_id);
    });
  }
  setMenu(user_id) {
    axios.get("/dt/accounts/get_menu/?user_id=" + user_id).then((result) => {
      this.setState({ menuItems: result.data.data });
      if (localStorage.getItem("default_key") === null) {
        localStorage.setItem("default_key", ["payment_reminders", "collections"]);
        this.setState({
          openKeys: ["collections"],
        });
      }
    });
  }
  handleClick = (e) => {
    localStorage.setItem("default_key", e.keyPath[1]);
    localStorage.setItem("default_sub_key", e.keyPath[0]);
    localStorage.setItem("openKeys", e.keyPath[1]);
  };
  onOpenChange = (items) => {
    const latestOpenKey = items.find((key) => this.state.openKeys.indexOf(key) === -1);
    this.setState({ openKeys: latestOpenKey ? [latestOpenKey] : [] });
  };
  render() {
    const { menuItems } = this.state;
    return (
      <Sider
        width={253}
        trigger={null}
        collapsible
        collapsed={this.state.collapsed}
        style={{ overflow: "auto", position: "relative", left: 0, top: 0, bottom: 0 }}
      >
        <div className="header-height d-flex justify-center align-items-baseline">
          {!this.state.collapsed && (
            <div className="logo">
              <span>Finance App</span>
            </div>
          )}
          <div className="collapsible-icon">
            {React.createElement(this.state.collapsed ? MenuUnfoldOutlined : MenuFoldOutlined, {
              className: "trigger",
              onClick: this.toggle,
            })}
          </div>
        </div>

        <Menu
          theme="dark"
          mode="inline"
          onClick={this.handleClick}
          defaultSelectedKeys={[this.state.current_sub, this.state.current]}
          defaultOpenKeys={[this.state.current_sub, this.state.current]}
          style={{ borderRight: 0 }}
          openKeys={this.state.openKeys}
          onOpenChange={this.onOpenChange}
        >
          {menuItems.map((level1Item) =>
            level1Item.menu.length > 0 ? (
              //TODO: Load icon dynamically as per defined in the DB
              <SubMenu key={level1Item.code} icon={<AppIcons code={level1Item.ico} />} title={level1Item.name}>
                {level1Item.menu.map((level2Item) =>
                  level2Item.menu.length > 0 ? (
                    <SubMenu key={level2Item.code} title={level2Item.name} icon={<AppIcons code={level2Item.ico} />}>
                      {level2Item.menu.map((level3Item) => (
                        <Menu.Item key={level3Item.code}>
                          <Link prefetch={false} href={level3Item.url}>
                            {level3Item.name}
                          </Link>
                        </Menu.Item>
                      ))}
                    </SubMenu>
                  ) : (
                    <Menu.Item key={level2Item.code} icon={<AppIcons code={level2Item.ico} />}>
                      <Link prefetch={false} href={level2Item.url}>
                        {level2Item.name}
                      </Link>
                    </Menu.Item>
                  )
                )}
              </SubMenu>
            ) : (
              <Menu.Item key={level1Item.code} icon={<AppIcons code={level1Item.ico} />}>
                <Link prefetch={false} href={level1Item.url}>
                  {level1Item.name}
                </Link>
              </Menu.Item>
            )
          )}
        </Menu>
      </Sider>
    );
  }
}
export default AppSider;
