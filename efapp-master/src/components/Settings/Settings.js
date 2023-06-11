import Layout from "../Layout/Layout";
import { faSliders } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import "./Settings.css";
import { Nav, Col, Row } from "react-bootstrap";
import SettingsProfile from "./SettingsProfile";
import SettingsPassword from "./SettingsPassword";
import { useState } from "react";
import SettingsOrg from "./SettingsOrg";
import Team from "./Team/Team";

export default function Settings() {
  const [show_profile, setShowProfile] = useState(true);
  const [show_password, setShowPassword] = useState(false);
  const [show_org, setShowOrg] = useState(false);
  const [show_team, setShowTeam] = useState(false);

  const onTabChange = (item) => {
    if(item ==='profile'){
      setShowProfile(true);
      setShowPassword(false);
      setShowOrg(false);
      setShowTeam(false);
    }else if(item ==='password'){
      setShowProfile(false);
      setShowPassword(true);
      setShowOrg(false);
      setShowTeam(false);
    }else if (item ==='org') {
      setShowProfile(false);
      setShowPassword(false);
      setShowOrg(true);
      setShowTeam(false);
    }else if (item ==='team') {
      setShowProfile(false);
      setShowPassword(false);
      setShowOrg(false);
      setShowTeam(true);
    }
  };

  return (
    <Layout>
      <div className="title-bar">
        <div>
          <FontAwesomeIcon icon={faSliders} />
        </div>
        <div>Settings</div>
      </div>
      <div className="settings-content">
        <Row>
          <Col md={2}>
            <div className="side-nav">
              <Nav className="flex-column">
                  <Nav.Link className={show_profile? 'active-tab' : ""} onClick={(e)=>onTabChange('profile')}>My profile</Nav.Link>
                  <Nav.Link className={show_password? 'active-tab' : ""} onClick={(e)=>onTabChange('password')}>Password</Nav.Link>
                  <Nav.Link className={show_org? 'active-tab' : ""} onClick={(e)=>onTabChange('org')}>Organization</Nav.Link>
                  <Nav.Link className={show_team? 'active-tab' : ""} onClick={(e)=>onTabChange('team')}>Team</Nav.Link>
              </Nav>
            </div>
          </Col>
          <Col md={10}>
           <SettingsProfile show={show_profile}></SettingsProfile>
           <SettingsPassword show={show_password}></SettingsPassword>
           <SettingsOrg show={show_org}></SettingsOrg>
           <Team show={show_team}></Team>
          </Col>
        </Row>
      </div>
    </Layout>
  );
}
