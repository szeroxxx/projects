import { Form, Button, Row, Col, InputGroup } from 'react-bootstrap'
import { useState, useEffect } from 'react'
import useLocalStorage from "../../../hooks/useLocalStorage";
import useAxiosPrivate from "../../../hooks/useAxiosPrivate";
import AddressGridLine from './AddressGridLine';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faAdd, faSearch } from "@fortawesome/free-solid-svg-icons";
import Dropdown from 'react-bootstrap/Dropdown'
import Spinner from "react-bootstrap/Spinner";
import Notification from '../../Common/Notification';
import EditAddress from './AddressNew';

export default function Address(props){
    const [addressData, setAddressData] = useState([])
    const [show_edit_model, setShowEditModal] = useState(false);
    const [userdata] = useLocalStorage("userdata");
    const [search, setSearch] = useState("");
    const [sort, setSort] = useState({ name: "id", sort: "desc" });
    const axiosPrivate = useAxiosPrivate();
    const [onLoad, setOnLoad] = useState(false);
    const [notification, setNotification] = useState({  show: false,  type: "",  message: ""});
    const [isNotification, setIsNotification] = useState(false);

    const getAddresses = async () => {
      try {
        setOnLoad(true);
        const response = await axiosPrivate.post(
          `/app/addresses/addresses_get/${props.customer_id}/${userdata.current_org_id}`,
          JSON.stringify({ search: search, sorting:sort }),
          {
              headers: { 'Content-Type': 'application/json' },
          }
        );
        if (response.data && response.data.code == "0") {
          setAddressData([]);
          setOnLoad(false);
        } else {
          setOnLoad(false);
          setAddressData(response.data);
        }
      } catch(err) {
          console.log(err);
      }
    }

    const newCustomer = () => {
      setShowEditModal(true)
    }

    const handleHideEditModal = (reload, blink) => {
      setShowEditModal(false);
      if (reload === true) {
        setNotification(blink);
        setIsNotification(true);
        setTimeout(() => {
          handleClose();
          getAddresses();
        }, 2000);
      }
      if (reload === false) {
        setNotification(blink);
        setIsNotification(true);
        setTimeout(() => {
          handleClose();
        }, 2000);
      }
    };

    const handleClose = () => {
      setIsNotification(false);
      setNotification({ show: false, type: "", message: ""});
    };

    useEffect(() => { getAddresses(); }, [search,sort] );

    return (
      <>
        {isNotification && (
          <Notification
            show={notification.show}
            onClose={handleClose}
            type={notification.type}
            message={notification.message}
          />
        )}
        <div className="address_container">
          <div>
            <h2>Address</h2>
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
                    <Dropdown.Item eventKey="address">Address</Dropdown.Item>
                    <Dropdown.Item eventKey="city">City</Dropdown.Item>
                    <Dropdown.Item eventKey="state">State</Dropdown.Item>
                  </Dropdown.Menu>
                </Dropdown>
              </Col>
              <Col md={2} className="add_address_new">
                <button onClick={newCustomer} className="btn btn-primary">
                  <FontAwesomeIcon icon={faAdd}></FontAwesomeIcon> Add New
                  Address
                </button>
              </Col>
            </Row>
          </div>
          <div className="address-grid-line">
            {onLoad ? (
              <Spinner
                animation="border"
                className="customer-loading-spinner"
              />
            ) : addressData?.length ? (
              addressData.map((item, i) => (
                <AddressGridLine item={item} getAddresses={getAddresses} />
              ))
            ) : (
              <div className="address-grid">Address not found.</div>
            )}
          </div>

          {show_edit_model && (
            <EditAddress
              show={show_edit_model}
              customer_id={props.customer_id}
              handler={handleHideEditModal}
              is_edit={false}
              org_id={userdata.current_org_id}
            />
          )}
        </div>
      </>
    );
}