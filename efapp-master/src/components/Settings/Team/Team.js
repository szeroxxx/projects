import { Col, Row, Form ,InputGroup,Button } from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {faAdd,faSearch,faPeopleGroup} from "@fortawesome/free-solid-svg-icons";
import { useEffect, useState  } from "react";
import useLocalStorage from "../../../hooks/useLocalStorage";
import useAxiosPrivate from "../../../hooks/useAxiosPrivate";
import InviteMember from "./InviteMember";
import TeamGrigLine from "./TeamGridLine";
import Dropdown from 'react-bootstrap/Dropdown'

import "./team.css";
export default function Team(props) {
  const { show } = props;
  const axiosPrivate = useAxiosPrivate();
  const [userdata] = useLocalStorage("userdata");
  const [users, setUsers] = useState();
  const [load, setLoad] = useState(false);
  const [show_invite_model, setShowInviteModel] = useState(false);
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState({});
  const [role, setRole] = useState([]);

  const getUsers = async () => {
    try {
      const response = await axiosPrivate.post(
        `/app/org/users_get/${userdata.current_org_id}`,
        JSON.stringify({ search: search, sorting:sort }),
        {
          headers: { "Content-Type": "application/json" },
        }
      );
      if (response.data && response.data.code == "0") {
        setUsers([])
      } else {
        setUsers(response.data);
        setLoad(true);
      }
    } catch (err) {
      console.log(err);
    }
  };

  const getRole = async () => {
    try {
      const response = await axiosPrivate.get(`/app/masters/roles_get_all`, {
        headers: { "Content-Type": "application/json" },
      });
      if (response.data && response.data.code == "0") {
        setRole([]);
      } else {
        setRole(response.data);
      }
    } catch (err) {
      console.log(err);
    }
  };

  const handleShowInviteModel = () => setShowInviteModel(true);
  const handleHideInviteModel = () => setShowInviteModel(false);

  useEffect(() => {
    getUsers();
  }, [userdata,search,sort]);

  useEffect(() => {
    getRole();
  }, []);

  return (
    <>
      {show && (
        <div className="col-md-10 team_container">
          <div>
            <h2>
              {" "}
              <FontAwesomeIcon icon={faPeopleGroup}></FontAwesomeIcon> Team
            </h2>
          </div>
          <Row>
            <Col md={8}>
              <InputGroup className="search_projects">
                <Form.Control
                  type="text"
                  placeholder="Search"
                  onChange={(e) => {
                    if (e.target.value.length > 2) {
                      setSearch(e.target.value);
                    } else if (e.target.value.length === 0) {
                      setSearch("");
                    }
                  }}
                />
                <Button variant="outline">
                  <FontAwesomeIcon icon={faSearch} />
                </Button>
              </InputGroup>
            </Col>
            <Col md={2}>
              <Dropdown
                className="projects_dropdown"
                onSelect={(e) => setSort({ name: e, sort: "asc" })}
              >
                <Dropdown.Toggle>Sort by</Dropdown.Toggle>
                <Dropdown.Menu>
                  <Dropdown.Item eventKey="created_on" href="#/action-1">
                    Date created
                  </Dropdown.Item>
                  <Dropdown.Item eventKey="first_name" href="#/action-3">
                    Name
                  </Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>
            </Col>
            <Col md={2} className="team_invite_member">
              <button
                className="btn btn-primary"
                onClick={handleShowInviteModel}
              >
                <FontAwesomeIcon icon={faAdd}></FontAwesomeIcon> Invite member
              </button>
            </Col>
          </Row>
          <br></br>
          {load &&
            users.map((item, i) => (
              <TeamGrigLine
                key={i}
                item={item}
                getUsers={getUsers}
                role={role}
              ></TeamGrigLine>
            ))}
          <InviteMember
            show={show_invite_model}
            handler={handleHideInviteModel}
            org_id={userdata.current_org_id}
          ></InviteMember>
        </div>
      )}
    </>
  );
}


