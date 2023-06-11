import { Col, Row } from 'react-bootstrap'
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome"
import { faCircle, faFlag } from "@fortawesome/free-solid-svg-icons";
import "./Projects.css"
import ToolTip from '../Common/ToolTip';
export default function ProjectLine(props) {
    return (
      <Row className="project_line">
        <Col md={4}>
          <div className="project_name">
            <ToolTip text="View project details">
              <a href={`../project/${props.data.id}`}>{props.data.name}</a>
            </ToolTip>{" "}
          </div>

          <div className="project_updated">
            {props.data.updated_on.date != "" && (
              <>
                Last updated <b>{props.data.updated_on.date}</b> ago by{" "}
                <b>{props.data.updated_by}</b>
              </>
            )}
          </div>
        </Col>
        <Col md={4}>
          <div>
            Customer :{" "}
            <b className="project_cus_name">{props.data.customer_name}</b>
          </div>
        </Col>
        <Col md={4}>
          <div className="project_status">
            {props.data.priority === "normal" && (
              <ToolTip text="Normal Priority">
                <FontAwesomeIcon
                  className="priority egg_blue"
                  icon={faFlag}
                ></FontAwesomeIcon>
              </ToolTip>
            )}
            {props.data.priority === "high" && (
              <ToolTip text="High Priority">
                <FontAwesomeIcon
                  className="priority yellow"
                  icon={faFlag}
                ></FontAwesomeIcon>
              </ToolTip>
            )}
            {props.data.priority === "urgent" && (
              <ToolTip text="Urgent Priority">
                <FontAwesomeIcon
                  className="priority red"
                  icon={faFlag}
                ></FontAwesomeIcon>
              </ToolTip>
            )}
            Currently in
            <ToolTip text="Status">
              <FontAwesomeIcon
                className="status green"
                icon={faCircle}
              ></FontAwesomeIcon>
            </ToolTip>
            <b> Preparation</b>
            <div className="badge">{props.data.tags[0]}</div>
          </div>
          <div className="project_created">
            Created <b>{props.data.created_on.date}</b> ago by{" "}
            <b> {props.data.created_by}</b>
          </div>
        </Col>
      </Row>
    );
}