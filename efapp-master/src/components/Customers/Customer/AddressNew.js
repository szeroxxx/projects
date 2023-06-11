import {Button, Modal, Form, Row, Col} from 'react-bootstrap';
import { useState, useEffect } from 'react';
import useAxiosPrivate from "../../../hooks/useAxiosPrivate";
import Spinner from "react-bootstrap/Spinner";

export default function EditAddress(props) {
    const address_id = props.address_id
    const org_id = props.org_id
    const [editData, setEditData] = useState({});
    const [isEdit, setIsEdit] = useState(false)
    const [formData, setFormData] = useState({address:"", city:"", state:"", zip_code:"", phone:"", fax:"", attention:"",country_id:""});
    const [countries, setCountries] = useState([])
    const axiosPrivate = useAxiosPrivate();
    const [error, setError] = useState({});
    const [onLoad, setOnLoad] = useState(false);

    const handleChange = (event) => {
      setFormData({...formData, [event.target.name]: event.target.value});
      if(isEdit){
          setEditData({...editData, [event.target.name]: event.target.value});
      }
    }

    const handleUpdate = async () => {
      try {
        if (validator()) {
          const response = await axiosPrivate.put(
            `/app/addresses/address_edit/${address_id}/${org_id}`,
            JSON.stringify(editData),
            {
              headers: { "Content-Type": "application/json" },
            }
          );
          if (response.data && response.data.code == "1") {
            var alertSuccess = { show: true,  type: "success",  message: response.data.message };
            props.handler(true, alertSuccess);
          } else {
            var alertDanger = { show: true,  type: "alert",  message: response.data.message };
            props.handler(false, alertDanger);
          }
        }
      } catch (err) {
        console.log(err);
      }
    };

    const handleSubmit = async () => {
      try {
        if(validator()){
          const response = await axiosPrivate.post(
            `/app/addresses/address_insert/${props.customer_id}/${org_id}`,
            JSON.stringify(formData),
            {
              headers: { 'Content-Type': 'application/json' },
            }
          );
          if (response.data && response.data.code == "1") {
            var alertSuccess = { show: true,  type: "success",  message: response.data.message };
            props.handler(true, alertSuccess);
          } else {
            var alertDanger = { show: true,  type: "alert",  message: response.data.message };
            props.handler(false, alertDanger);
          }
        }
      } catch(err) {
          console.log(err);
      }
    }

    const getAddress = async () => {
      try {
        setOnLoad(true);
        const post_data = {
            "fields": ["address", "city", "state", "zip_code", "phone", "fax", "attention","country_id"]
        }
        const response = await axiosPrivate.post(
          `/app/addresses/address_get/${address_id}/${org_id}`,
          JSON.stringify(post_data),
          {
              headers: { 'Content-Type': 'application/json' },
          }
        );
        if (response.data && response.data.code == "0") {
          setOnLoad(false);
          setEditData([]);
        } else {
          if (response.data.length > 0) {
            setOnLoad(false);
            setEditData(response.data[0]);
            setIsEdit(true);
          }
        }
      } catch(err) {
          console.log(err);
      }
    }


    const validator = () => {
      let tempError = {};
      if (isEdit) {
        if (!editData.address) {
            tempError.address = "Address required"
        }
        if (!editData.city) {
            tempError.city = "City required"
        }
        if (!editData.state) {
            tempError.state = "State required"
        }
        if (!editData.country_id) {
          tempError.country_id = "Country required";
        }
        if (!editData.attention) {
          tempError.attention = "Attention required";
        }
      } else {
        if (!formData.address) {
            tempError.address = "Address required"
        }
        if (!formData.city) {
            tempError.city = "City required"
        }
        if (!formData.state) {
            tempError.state = "State required"
        }
        if (!formData.country_id) {
          tempError.country_id = "Country required";
        }
        if (!formData.attention) {
          tempError.attention = "Attention required";
        }
      }
      setError(tempError)
      return Object.keys(tempError).length === 0;
    }

    const countryLookup = async () => {
      try {
        const response = await axiosPrivate.get(
          `/app/masters/country_get_all`,
          {
            headers: { 'Content-Type': 'application/json' },
          }
        )
        if(response.data){
          setCountries(response.data)
        }
      } catch(err) {
        console.log(err);
      }
      }

    useEffect(() => {
      if(props.is_edit){
          getAddress();
      }
      countryLookup();
    } , [])

    return (
      <>
        <Modal
          show={props.show}
          onHide={props.handler}
          dialogClassName="modal-80w"
          size="lg"
          aria-labelledby="contained-modal-title-vcenter"
          centered
        >
          <Modal.Header closeButton>
            <Modal.Title>
              {props.is_edit ? <>Edit Address</> : <>Add New Address</>}
            </Modal.Title>
          </Modal.Header>
          <Modal.Body>
            {onLoad ? (
              <Spinner animation="border" className="address-loading-spinner" />
            ) : (
              <div className="address_new_form">
                <Form>
                  <Form.Group as={Row} className="mb-3">
                    <Form.Label column sm={2}>
                      Address
                    </Form.Label>
                    <Col sm={6}>
                      <Form.Control
                        value={editData.address}
                        type="text"
                        placeholder="Enter Address"
                        name="address"
                        onChange={(e) => handleChange(e)}
                      />
                      <p className="address_validation">{error.address}</p>
                    </Col>
                  </Form.Group>
                  <Form.Group as={Row} className="mb-3">
                    <Form.Label column sm={2}>
                      City
                    </Form.Label>
                    <Col sm={6}>
                      <Form.Control
                        value={editData.city}
                        type="text"
                        placeholder="Enter City"
                        name="city"
                        onChange={(e) => handleChange(e)}
                      />
                      <p className="address_validation">{error.city}</p>
                    </Col>
                  </Form.Group>
                  <Form.Group as={Row} className="mb-3">
                    <Form.Label column sm={2}>
                      State
                    </Form.Label>
                    <Col sm={6}>
                      <Form.Control
                        value={editData.state}
                        type="text"
                        placeholder="Enter State"
                        name="state"
                        onChange={(e) => handleChange(e)}
                      />
                      <p className="address_validation">{error.state}</p>
                    </Col>
                  </Form.Group>
                  <Form.Group as={Row} className="mb-3">
                    <Form.Label column sm={2}>
                      Zip code
                    </Form.Label>
                    <Col sm={6}>
                      <Form.Control
                        value={editData.zip_code}
                        type="text"
                        placeholder="Enter Zip code"
                        name="zip_code"
                        onChange={(e) => handleChange(e)}
                      />
                    </Col>
                  </Form.Group>
                  <Form.Group as={Row} className="mb-3">
                    <Form.Label column sm={2}>
                      Phone
                    </Form.Label>
                    <Col sm={6}>
                      <Form.Control
                        value={editData.phone}
                        type="text"
                        placeholder="Enter Phone"
                        name="phone"
                        onChange={(e) => handleChange(e)}
                      />
                    </Col>
                  </Form.Group>
                  <Form.Group as={Row} className="mb-3">
                    <Form.Label column sm={2}>
                      Fax
                    </Form.Label>
                    <Col sm={6}>
                      <Form.Control
                        value={editData.fax}
                        type="text"
                        placeholder="Enter Fax"
                        name="fax"
                        onChange={(e) => handleChange(e)}
                      />
                    </Col>
                  </Form.Group>
                  <Form.Group as={Row} className="mb-3">
                    <Form.Label column sm={2}>
                      Country
                    </Form.Label>
                    <Col sm={6}>
                      <Form.Control
                        as="select"
                        name="country_id"
                        onChange={(e) => handleChange(e)}
                      >
                        <option value="">-Select Country-</option>
                        {countries.map((option, index) => {
                          return (
                            <option
                              key={index}
                              value={option.id}
                              selected={props.country_id === option.id}
                            >
                              {option.name}
                            </option>
                          );
                        })}
                      </Form.Control>
                      <p className="address_validation">{error.country_id}</p>
                    </Col>
                  </Form.Group>
                  <Form.Group as={Row} className="mb-3">
                    <Form.Label column sm={2}>
                      Attention
                    </Form.Label>
                    <Col sm={6}>
                      <Form.Control
                        value={editData.attention}
                        type="text"
                        placeholder="Enter Attention"
                        name="attention"
                        onChange={(e) => handleChange(e)}
                      />
                      <p className="address_validation">{error.attention}</p>
                    </Col>
                  </Form.Group>
                </Form>
              </div>
            )}
          </Modal.Body>
          <Modal.Footer>
            <Button variant="outline-primary" onClick={props.handler}>
              Cancel
            </Button>
            {props.is_edit ? (
              <Button className="btn btn-primary" onClick={handleUpdate}>
                Edit Address
              </Button>
            ) : (
              <Button className="btn btn-primary" onClick={handleSubmit}>
                Submit
              </Button>
            )}
          </Modal.Footer>
        </Modal>
      </>
    );
}