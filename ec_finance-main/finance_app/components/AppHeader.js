import Icon, { Layout, Avatar, Badge, Affix, Menu, Dropdown, Image } from "antd";
const { Header } = Layout;
import React from "react";
import { BellOutlined, QuestionCircleOutlined, SearchOutlined, LogoutOutlined, UserOutlined, BugOutlined } from "@ant-design/icons";
import Link from "next/link";
import { Tooltip } from "antd";
import { getSession, signOut } from "next-auth/react";
import AppIcons from "./AppIcons";

const menu = (
  <Menu>
    <Menu.Item>
      <UserOutlined className="mr-5" />
      <Link prefetch={false} href="/account/my_profile">
        My Profile
      </Link>
    </Menu.Item>
    <Menu.Item>
      <a
        target="_blank"
        rel="noopener noreferrer"
        onClick={() =>
          signOut({
            callbackUrl: `${window.location.origin}`,
          })
        }
      >
        <LogoutOutlined className="mr-5" /> Logout
      </a>
    </Menu.Item>
  </Menu>
);

class AppHeader extends React.Component {
  constructor(props) {
    super(props);

    this.state = { display_name: " ", name_initial: " " };
  }
  componentDidMount() {
    getSession().then((session) => {
      let { user__first_name, user__last_name, profile_image } = session.user.data;
      this.setState({
        display_name: user__first_name + " " + user__last_name,
        name_initial: user__first_name.charAt(0) + "" + user__last_name.charAt(0),
        profile_image: profile_image,
      });
    });
  }

  render() {
    const { display_name, name_initial, profile_image } = this.state;

    return (
      <Affix offsetTop={0}>
        <Header className="site-layout-background header-height">
          <div className="header-menu">
            <Tooltip title="Report an issue">
              <BugOutlined
                style={{ color: "#EC7070" }}
                onClick={() => window.open("https://forms.clickup.com/3333355/f/35q7b-7604/NQS3VUTKT2J6HMKXNS", "_blank")}
              />
            </Tooltip>

            <Tooltip title="Release note">
              <Image
                preview={false}
                alt="Image"
                code={"release"}
                src={`/releases-icon.svg`}
                style={{ width: 20, cursor: "pointer" }}
                onClick={() => window.open("https://doc.clickup.com/3333355/d/h/35q7b-6924/02e987e267be7e4", "_blank")}
              />
            </Tooltip>

            <SearchOutlined style={{ display: "none" }} />
            <QuestionCircleOutlined style={{ display: "none" }} />
            <Badge count={1} style={{ display: "none" }}>
              <BellOutlined size={10} style={{ display: "none" }} />
            </Badge>
            <Dropdown overlay={menu}>
              <a className="ant-dropdown-link" onClick={(e) => e.preventDefault()}>
                <span className="avatar-item d-flex align-items-center">
                  <Avatar src={profile_image} shape="circle">
                    {name_initial}
                  </Avatar>
                  <span className="customer-name">{display_name}</span>
                </span>
              </a>
            </Dropdown>
          </div>
        </Header>
      </Affix>
    );
  }
}
export default React.memo(AppHeader);
