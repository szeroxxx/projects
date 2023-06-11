import Container from "react-bootstrap/Container";
import Nav from "react-bootstrap/Nav";
import Navbar from "react-bootstrap/Navbar";
import NavDropdown from "react-bootstrap/NavDropdown";
import logo from "./../../static/logo.svg";
import useLogout from "../../hooks/useLogout";
import useLocalStorage from "../../hooks/useLocalStorage";
import { LinkContainer } from "react-router-bootstrap";
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

function Appbar() {
  const [setLogout] = useLogout();
  const [userData, setUserData] = useLocalStorage("userdata");
  const display_name = `${userData?.first_name} ${userData?.last_name}`;
  const navigate = useNavigate();

  const handleSelect = (key) => {
    if(userData.current_org_id !== key){
      for (var org in userData.org_id) {
        if (userData.org_id[org].org_id === key) {
          userData.current_org_name = userData.org_id[org].name
        }
      }
      userData.current_org_id = key
      setUserData(userData)
      navigate("/dashboard")
      window.location.reload();
    }
  }

  return (
    <Navbar bg="light" expand="lg">
      <Container fluid>
        <Navbar.Brand href="#">
          <img src={logo} alt="Ennofab" />
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="navbarScroll" />
        <Navbar.Collapse id="navbarScroll">
          <Nav
            className="me-auto my-2 my-lg-0"
            navbarScroll
          >
            <LinkContainer to="/dashboard">
              <Nav.Link>Dashboard</Nav.Link>
            </LinkContainer>
            <LinkContainer to="/projects">
              <Nav.Link>Projects</Nav.Link>
            </LinkContainer>
            <LinkContainer to="/customers">
              <Nav.Link>Customers</Nav.Link>
            </LinkContainer>
            <LinkContainer to="/settings">
              <Nav.Link>Settings</Nav.Link>
            </LinkContainer>
          </Nav>
          <Nav className="mr-auto" >
            <NavDropdown  title={userData.current_org_name} onSelect={handleSelect}>
              {userData.org_id.map((item) => (
                <NavDropdown.Item eventKey={item.org_id} key={item.org_id} >{item.name}</NavDropdown.Item>
              ))}
            </NavDropdown >
          </Nav>
          <Nav className="mr-auto">
          
            <NavDropdown
              align={"end"}
              title={display_name}
              id="navbarScrollingDropdown"
            >
              <LinkContainer to="/settings">
                <NavDropdown.Item>Profile</NavDropdown.Item>
              </LinkContainer>
              <LinkContainer to="/settings">
                <NavDropdown.Item>Settings</NavDropdown.Item>
              </LinkContainer>
              <NavDropdown.Divider />
              <NavDropdown.Item onClick={setLogout}>Logout</NavDropdown.Item>
            </NavDropdown>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}

export default Appbar;
