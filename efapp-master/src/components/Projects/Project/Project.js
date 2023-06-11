import Layout from "../../Layout/Layout";
import "../Projects.css";
import { Row, Tab, Tabs } from "react-bootstrap";
import { useEffect, useState } from "react";
import ProjectNew from "../ProjectNew";
import Documents from "./Documents";
import BOMList from "./BOMList";
import Discussions from "./Discussions";
import useLocalStorage from "../../../hooks/useLocalStorage";
import { useParams } from "react-router-dom";
import useAxiosPrivate from "../../../hooks/useAxiosPrivate";

export default function Project() {
    const { project_id }  = useParams();
    const [isEdit, setIsEdit] = useState(true)
    const axiosPrivate = useAxiosPrivate();
    const [userData] = useLocalStorage("userdata");
    const [project, setProject] = useState()
    const [activeTab, setActiveTab] = useState("general");
    const [discussionState, setDiscussionState] = useState({
      isChatOn: false,
      MPNNo: ""
    });
    const getProject = async () => {
      try {
          const post_data = {
              "fields": ["name", ]
          }
          const response = await axiosPrivate.post(
              `/app/projects/project_get/${project_id}/${userData.current_org_id}`,
              JSON.stringify(post_data),
              {
                  headers: { 'Content-Type': 'application/json' },
              }
          );
          setProject(response.data[0]["name"])
      } catch(err) {
          console.log(err);
      }
  }
    useEffect(() => {
      if(project_id !== "new"){
        getProject();
        setIsEdit(false)
      }
   } , [project_id] );

   const onDiscussion = (mpn) => {
    discussionState.isChatOn = true
    discussionState.MPNNo = mpn;
    setDiscussionState(discussionState);
    setActiveTab("discussion");
   }
    return (
      <>
        <Layout>
          <div className="project_container">
            <Row>
              <h3> {project} </h3>
            </Row>
            <Row>
              <Tabs
                defaultActiveKey={activeTab}
                transition={false}
                activeKey={activeTab}
                onSelect={(k) => setActiveTab(k)}
                id="project-page"
                className="mb-3"
              >
                <Tab eventKey="general" title="General">
                  {activeTab === "general" && (
                    <ProjectNew id={project_id}></ProjectNew>
                  )}
                </Tab>
                <Tab eventKey="bom" title="Bill of material" disabled={isEdit}>
                  {activeTab === "bom" && (
                    <BOMList
                      handler={onDiscussion}
                      project_id={project_id}
                      org_id={userData.current_org_id}
                    ></BOMList>
                  )}
                </Tab>
                {/* <Tab eventKey="operations" title="Operations" disabled={isEdit}>
                  Operations
                </Tab> */}
                <Tab eventKey="documents" title="Documents" disabled={isEdit}>
                  {activeTab === "documents" && <Documents id={project_id} />}
                </Tab>
                <Tab eventKey="discussion" title="Discussion" disabled={isEdit}>
                  {activeTab === "discussion" && (
                    <Discussions
                      id={project_id}
                      org_id={userData}
                      data={discussionState}
                    />
                  )}
                </Tab>
              </Tabs>
            </Row>
          </div>
        </Layout>
      </>
    );
}
