import Layout from "../Layout/Layout"
import CustomerInfoHeader from "../Projects/CustomerInfoHeader";
import RecentProject from "./RecentProject";
import { Row } from 'react-bootstrap'
import "./Dashboard.css";
import { useEffect, useState } from "react";
export default function Dashboard() {
  const [load, setLoad] = useState(false)
  useEffect(() => {  }, [load] );
  setTimeout(() => {
    setLoad(true)
  }, 50);  
    return (
      <Layout>
        <CustomerInfoHeader />
        <Row>
          <RecentProject></RecentProject>
        </Row>
      </Layout>
    );
}