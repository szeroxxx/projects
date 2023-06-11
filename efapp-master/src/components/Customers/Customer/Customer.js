import { Row, Tab ,Tabs } from "react-bootstrap";
import Layout from "../../Layout/Layout"
import CustomerNew from "../CustomerNew";
import Address from "./Address";
import Contact from "./Contact";
import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";

export default function Customer() {
    const [isEdit, setIsEdit] = useState(true)
    const [activeTab, setActiveTab] = useState("customer");

    const { customer_id }  = useParams();
    useEffect(() => {
      if(customer_id !== "new"){
        setIsEdit(false)
      }
     } , [customer_id] );

    return (
      <>
        <Layout>
          <div className="customer_container">
            <Row>
              <h3>Customer Name</h3>
            </Row>
            <Row>
              <Tabs
                defaultActiveKey={activeTab}
                transition={false}
                activeKey={activeTab}
                onSelect={(k) => setActiveTab(k)}
                id="project-page"
              >
                <Tab title="Customer" eventKey="customer">
                  {activeTab === "customer" && (
                    <CustomerNew customer_id={customer_id} />
                  )}
                </Tab>
                <Tab title="Address" eventKey="address" disabled={isEdit}>
                  {activeTab === "address" && (
                    <Address customer_id={customer_id} />
                  )}
                </Tab>
                <Tab title="Contacts" eventKey="contact" disabled={isEdit}>
                  {activeTab === "contact" && (
                    <Contact customer_id={customer_id} />
                  )}
                </Tab>
              </Tabs>
            </Row>
          </div>
        </Layout>
      </>
    );
}