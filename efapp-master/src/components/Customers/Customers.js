import Layout from "../Layout/Layout"
import "./customers.css"
import CustomerInfoHeader from "../Projects/CustomerInfoHeader";
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
import CustomerGridLine from "./CustomerGridLine";
import Spinner from "react-bootstrap/Spinner";
export default function Customers() {
    const axiosPrivate = useAxiosPrivate();
    const [userData] = useLocalStorage("userdata");
    const [customerData, setCustomerData] = useState([])
    const [search, setSearch] = useState("");
    const [sort, setSort] = useState({ name: "id", sort: "desc" });
    const [onLoad, setOnLoad] = useState(false);
    const navigate = useNavigate();

    const getCustomer = async () => {
      try {
        setOnLoad(true);
        const response = await axiosPrivate.post(
            `/app/customers/customers_get_all/${userData.current_org_id}`,
            JSON.stringify({ search: search, sorting:sort }),
            {
              headers: { "Content-Type": "application/json" },
            }
        );
        if (response.data && response.data.code == "0") {
            setOnLoad(false);
            setCustomerData([])
        } else {
            setOnLoad(false);
            setCustomerData(response.data)
        }
      } catch(err) {
          console.log(err);
      }
    };

    useEffect(() => { getCustomer(); }, [search,sort] );

    const newCustomer = () => {
        navigate("/customer/new")
    }

    return (
      <>
        <Layout>
          <CustomerInfoHeader />
          <div className="customer_container">
            <div>
              <h2>Customers</h2>
            </div>
            <div>
              <Row>
                <Col md={8}>
                  <InputGroup className="search_customers">
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
                    className="customers_dropdown"
                    onSelect={(e) => setSort({ name: e, sort: "asc" })}
                  >
                    <Dropdown.Toggle>Sort by</Dropdown.Toggle>
                    <Dropdown.Menu>
                      <Dropdown.Item eventKey="created_on" href="#/action-1">
                        Date created
                      </Dropdown.Item>
                      <Dropdown.Item eventKey="name" href="#/action-3">
                        Name
                      </Dropdown.Item>
                    </Dropdown.Menu>
                  </Dropdown>
                </Col>
                <Col md={2} className="customer_new">
                  <button onClick={newCustomer} className="btn btn-primary">
                    <FontAwesomeIcon icon={faAdd}></FontAwesomeIcon> New
                  </button>
                </Col>
              </Row>
            </div>
            <div className="customer-grid-line">
            {onLoad ? (
                <Spinner
                animation="border"
                className="customer-loading-spinner"
              />
              ):(
                customerData.map((item, i) => (
                <CustomerGridLine
                    item={item}
                    getCustomer={getCustomer}
                    key={item.id}
                />
            ))
              )}
            </div>
          </div>
        </Layout>
      </>
    );
}