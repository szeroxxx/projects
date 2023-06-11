import { Col, Row } from 'react-bootstrap'
import "./Projects.css"
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome"
import { faPeopleGroup, faLocationDot, faLink } from "@fortawesome/free-solid-svg-icons";
import { useEffect, useState } from "react";
import useLocalStorage from '../../hooks/useLocalStorage';
export default function CustomerInfoHeader() {
    const [userData] = useLocalStorage("userdata");
    const [customer, setCustomer] = useState({name: "", about: "", members: "", location: "", domain_url: "" })

    const getCustomer = () => {
        if (userData?.org_id) {
            for (var org in userData.org_id) {
                if (userData.org_id[org].org_id === userData.current_org_id) {
                    customer.name = userData.org_id[org].name
                    customer.members = userData.org_id[org].members
                    customer.location = userData.org_id[org].location
                    customer.domain_url = userData.org_id[org].domain_url
                    setCustomer(customer)
                }
            }
        }
    }

    useEffect(() => { getCustomer(); } , [] );

    return (
      <div className="d-none d-lg-block company_header">
        <Row>
          <Col md={3}>
            <div className="cust_logo">
              <img
                src="http://acmelogos.com/images/logo-3.svg"
                alt="company profile"
                onError={(e) => {
                  e.target.src = "http://acmelogos.com/images/logo-3.svg";
                }}
              />
            </div>
          </Col>
          <Col md={9} className="cust_info">
            <h1>{customer.name}</h1>
            <p>{customer.about}</p>
            <Row className="cust_info_extra">
              <Col md={3}>
                <FontAwesomeIcon icon={faPeopleGroup}></FontAwesomeIcon>{" "}
                {customer.members} members
              </Col>
              <Col md={4}>
                <FontAwesomeIcon icon={faLocationDot}></FontAwesomeIcon>{" "}
                {customer.location}
              </Col>
              <Col md={5}>
                <FontAwesomeIcon icon={faLink}></FontAwesomeIcon>{" "}
                {customer.domain_url}
              </Col>
            </Row>
          </Col>
        </Row>
      </div>
    );
}