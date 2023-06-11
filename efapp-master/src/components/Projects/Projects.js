import Layout from "../Layout/Layout"
import "./Projects.css"
import CustomerInfoHeader from "./CustomerInfoHeader";
import ProjectLine from "./ProjectLine";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faAdd, faSearch } from "@fortawesome/free-solid-svg-icons";
import { Col, Row, InputGroup } from 'react-bootstrap'
import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'
import Dropdown from 'react-bootstrap/Dropdown'
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import useAxiosPrivate from "../../hooks/useAxiosPrivate";
import useLocalStorage from "../../hooks/useLocalStorage";
import Spinner from "react-bootstrap/Spinner";
export default function Projects() {
    const axiosPrivate = useAxiosPrivate();
    const [userData] = useLocalStorage("userdata");
    const [projects, setProjects] = useState([]);
    const [search, setSearch] = useState("");
    const [sort, setSort] = useState({ name: "id", sort: "desc" });
    const [load, setLoad] = useState(false);
    const [onLoad, setOnLoad] = useState(false);

    const navigate = useNavigate();
    const toNewProject = () => {
        navigate("/project/new")
    }

    const getProjects = async () => {
        try {
            setOnLoad(true);
            const response = await axiosPrivate.post(
                `/app/projects/projects_get_all/${userData.current_org_id}`,
                JSON.stringify({ search: search, sorting:sort }),
                {
                  headers: { "Content-Type": "application/json" },
                },
            );
            if (response.data && response.data.code == "0") {
                setProjects([])
                setOnLoad(false);
            } else {
                setProjects(response.data);
                setLoad(true);
                setOnLoad(false);
              }
        } catch (err){
            console.log(err);
        }
    }

    useEffect(() => { getProjects(); } , [search,sort] );

    return (
        <Layout>
            <CustomerInfoHeader />
            <div className="project_list_container">
                <div>
                    <h2>Projects</h2>
                </div>
                <div>
                    <Row>
                        <Col md={8}>
                            <InputGroup className="search_projects">
                                <Form.Control type="text" placeholder="Search"
                                    onChange={(e) => {
                                        if(e.target.value.length>2){
                                            setSearch(e.target.value)
                                        } else if (e.target.value.length===0){
                                            setSearch("")
                                        }
                                        }}/>
                                <Button variant="outline" ><FontAwesomeIcon icon={faSearch} /></Button>
                            </InputGroup>
                        </Col>
                        <Col md={2}>
                            <Dropdown className="projects_dropdown" onSelect={(e)=>setSort({name:e, sort: "asc"})}>
                                <Dropdown.Toggle>
                                    Sort by
                                </Dropdown.Toggle>
                                <Dropdown.Menu >
                                    <Dropdown.Item eventKey="created_on" href="#/action-1">Date created</Dropdown.Item>
                                    <Dropdown.Item eventKey="updated_on" href="#/action-2">Date updated</Dropdown.Item>
                                    <Dropdown.Item eventKey="name" href="#/action-3">Name</Dropdown.Item>
                                </Dropdown.Menu>
                            </Dropdown>
                        </Col>

                        <Col md={2} className="project_new">
                            <button onClick={toNewProject} className="btn btn-primary"><FontAwesomeIcon icon={faAdd}></FontAwesomeIcon> New</button>
                        </Col>
                    </Row>
                </div>
                <div className="project-line-grid">
                {onLoad ? (
                    <Spinner
                    animation="border"
                    className="projects-loading-spinner"
                    />
                ) : (
                    load && projects.map((item,i) => ( <ProjectLine data={item} key={i} />))
                )
                }
                </div>
            </div>
        </Layout>
    )
}