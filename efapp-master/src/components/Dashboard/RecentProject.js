import Card from "react-bootstrap/Card";
import { Row,  Col } from "react-bootstrap";
import useAxiosPrivate from "../../hooks/useAxiosPrivate";
import { useState, useEffect } from "react";
import useLocalStorage from "../../hooks/useLocalStorage";
import Spinner from "react-bootstrap/Spinner";
import { useNavigate } from "react-router-dom";

export default function RecentProject() {
  const [Project, setProject] = useState([])
  const [userData] = useLocalStorage("userdata");
  const axiosPrivate = useAxiosPrivate();
  const [onLoad, setOnLoad] = useState(false);
  const navigate = useNavigate();

  useEffect(() => { getProjects(); } , [] );

  const getProjects = async () => {
    try {
        setOnLoad(true);
        const response = await axiosPrivate.post(
            `/app/projects/projects_get_all/${userData.current_org_id}`,
            JSON.stringify({"sorting": {"name": "id", "sort": "desc"}, "limit": 3}),
            {
              headers: { "Content-Type": "application/json" },
            },
        );
        if (response.data && response.data.code == "0") {
          setProject([])
          setOnLoad(false);
        } else {
          setProject(response.data);
          setOnLoad(false);
        }
    } catch (err){
        console.log(err);
    }
}

const redirect = (id) => {
  navigate(`../project/${id}`);
}

  return (
    <div>
      <div className="recent-project">Recent Projects</div>
      <Row>
        {Project?.length
          ? Project.map((item, i) => (
              <Col md={4} key={i}>
                <Card
                  className="recent-project-card"
                  onClick={() => redirect(item.id)}
                >
                  <Card.Body>
                    <Card.Title>
                      <div className="recent-project-name">{item.name}</div>
                    </Card.Title>
                    <Card.Text>
                      <span className="recent-project-customer-name">
                        Customer name : <b>{item.customer_name}</b>
                      </span>
                      <br></br>
                      <small>
                        Created <b>{item.created_on.date}</b> ago by{" "}
                        <b>{item.created_by}</b>
                      </small>
                    </Card.Text>
                  </Card.Body>
                </Card>
              </Col>
            ))
          : onLoad && (
              <Spinner
                animation="border"
                className="dashboard-loading-spinner"
              />
            )}
      </Row>
    </div>
  );
}
