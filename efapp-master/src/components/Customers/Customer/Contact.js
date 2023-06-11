import { Form, Button, Row, Col, InputGroup } from 'react-bootstrap'
import { useState, useEffect } from 'react'
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faAdd, faSearch } from "@fortawesome/free-solid-svg-icons";
import Dropdown from 'react-bootstrap/Dropdown'
import useAxiosPrivate from "../../../hooks/useAxiosPrivate";
import useLocalStorage from "../../../hooks/useLocalStorage";
import ContactGridLine from './ContactGridLine';
import ContactNew from './ContactNew';
import Spinner from "react-bootstrap/Spinner";
import Notification from '../../Common/Notification';

export default function Contact(props){
    const [search, setSearch] = useState("");
    const [sort, setSort] = useState({ name: "id", sort: "desc" });
    const [contactData, setContactData] = useState([])
    const axiosPrivate = useAxiosPrivate();
    const [userdata] = useLocalStorage("userdata");
    const [show_edit_model, setShowEditModal] = useState(false);
    const [onLoad, setOnLoad] = useState(false);
    const [notification, setNotification] = useState({show: false,type: "",message: ""});
    const [isNotification, setIsNotification] = useState(false);

    const newContact = () => {
      setShowEditModal(true)
    }

    const getContacts = async() => {
      try {
        setOnLoad(true);
        const response = await axiosPrivate.post(
          `/app/contacts/contacts_get/${props.customer_id}/${userdata.current_org_id}`,
          JSON.stringify({ search: search, sorting:sort }),
          {
              headers: { 'Content-Type': 'application/json' },
          }
        );
        if (response.data && response.data.code == "0") {
          setOnLoad(false);
          setContactData([])
        } else {
          setOnLoad(false);
          setContactData(response.data);
        }
      } catch(err) {
          console.log(err);
      }
    }

    const handleHideEditModal = (reload, blink) => {
      setShowEditModal(false);
      if (reload === true) {
        setNotification(blink);
        setIsNotification(true);
        setTimeout(() => {
          handleClose();
          getContacts();
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
      setNotification({ show: false, type: "", message: "" });
    };

    useEffect(() => { getContacts(); }, [search,sort] );


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
        <div className="contact_container">
          <div>
            <h2>Contact</h2>
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
                    <Dropdown.Item eventKey="created_on">
                      Date created
                    </Dropdown.Item>
                    <Dropdown.Item eventKey="first_name">Name</Dropdown.Item>
                  </Dropdown.Menu>
                </Dropdown>
              </Col>
              <Col md={2} className="add_address_new">
                <button onClick={newContact} className="btn btn-primary">
                  <FontAwesomeIcon icon={faAdd}></FontAwesomeIcon> Add New
                  Contact
                </button>
              </Col>
            </Row>
          </div>
          <div className="contact-grid-line">
            {onLoad ? (
              <Spinner
                animation="border"
                className="customer-loading-spinner"
              />
            ) : contactData?.length ? (
              contactData.map((item, i) => (
                <ContactGridLine item={item} getContacts={getContacts} />
              ))
            ) : (
              <div className="contact-grid">Contact not found.</div>
            )}
          </div>

          {show_edit_model && (
            <ContactNew
              show={show_edit_model}
              handler={handleHideEditModal}
              is_edit={false}
              customer_id={props.customer_id}
            />
          )}
        </div>
      </>
    );
}