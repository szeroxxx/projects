import { useState, useEffect } from 'react';
import { Form, Button } from 'react-bootstrap'
import useLocalStorage from "../../hooks/useLocalStorage";
import useAxiosPrivate from "../../hooks/useAxiosPrivate";
import { useParams } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import Spinner from "react-bootstrap/Spinner";
import Notification from '../Common/Notification';

export default function CustomerNew (props) {
    const [formData, setFormData] = useState({name:"", phone:"", email:"", display_name:"", type:"", remarks:"", website:"", primary_contact_id:""});
    const [isEdit, setIsEdit] = useState(false);
    const [editData, setEditData] = useState({});
    const { customer_id }  = useParams();
    const [userdata] = useLocalStorage("userdata");
    const axiosPrivate = useAxiosPrivate();
    const [error, setError] = useState({});
    const [onLoad, setOnLoad] = useState(false);
    const [notification, setNotification] = useState({show:false,type:"",message:""})
    const [isNotification, setIsNotification] = useState(false)
    const navigate = useNavigate();

    const handleChange = (event) => {
      setFormData({...formData, [event.target.name]: event.target.value});
      if(isEdit){
          setEditData({...editData, [event.target.name]: event.target.value});
      }
    }

    const handleSubmit = async () => {
      try {
        if(validator()){
          const response = await axiosPrivate.post(
            `/app/customers/customer_insert/${userdata.current_org_id}`,
            JSON.stringify(formData),
            {
                headers: { 'Content-Type': 'application/json' },
            }
          );
          if (response.data && response.data.code == "1") {
            setNotification({  show: true,  type: "success",  message: response.data.message });
            setIsNotification(true);
            setTimeout(() => { handleClose(); }, 2000);
            navigate(`/customer/${response.data.customer_id}`)
          } else {
            setNotification({  show: true,  type: "alert",  message: response.data.message });
            setIsNotification(true);
            setTimeout(() => { handleClose(); }, 2000);
          }
          }
      } catch(err) {
          console.log(err);
      }
    }

    const handleEdit = async () => {
      try{
        if(validator()){
          const response = await axiosPrivate.put(
            `/app/customers/customer_edit/${customer_id}/${userdata.current_org_id}`,
            JSON.stringify(editData),
            {
                headers: { 'Content-Type': 'application/json' },
            }
          );
          if (response.data && response.data.code == "1") {
            setNotification({  show: true,  type: "success",  message: response.data.message });
            setIsNotification(true);
            setTimeout(() => {  handleClose(); }, 2000);
          } else {
            setNotification({  show: true,  type: "alert",  message: response.data.message });
            setIsNotification(true);
            setTimeout(() => { handleClose(); }, 2000);
          }
        }
      } catch(err) {
          console.log(err);
      }
    }

    const validator = () => {
      const regex = /^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$/i;
      let tempError = {};
      if (isEdit) {
        if (!editData.name) {
            tempError.name = "Customer Name required"
        }
        if (!editData.email || regex.test(editData.email) === false) {
            tempError.email = "Email required"
        }
        if (!editData.primary_contact_id) {
            tempError.primary_contact_id = "Contact required"
        }
        if (!editData.type) {
          tempError.type = "Type required";
          }
      } else {
        if (!formData.name) {
            tempError.name = "Customer Name required";
        }
        if (!formData.email || regex.test(formData.email) === false) {
            tempError.email = "Email required"
        }
        if (!formData.primary_contact_id) {
            tempError.primary_contact_id = "Contact required"
        }
        if (!formData.type) {
          tempError.type = "Type required";
        }
      }
      setError(tempError)
      return Object.keys(tempError).length === 0;
    }

    const getCustomer = async () => {
      try {
        setOnLoad(true);
        const post_data = {
          "fields": ["type", "name", "display_name", "email", "phone", "website", "remarks", "primary_contact_id"]
        }
        const response = await axiosPrivate.post(
          `/app/customers/customers_get/${customer_id}/${userdata.current_org_id}`,
          JSON.stringify(post_data),
          {
              headers: { 'Content-Type': 'application/json' },
          }
        );
        if (response.data && response.data.code == "0") {
          setOnLoad(false);
          setEditData([]);
        } else {
          setOnLoad(false);
          setEditData(response.data[0]);
        }
      } catch(err) {
          console.log(err);
      }
    }

    const handleClose = () => {
      setIsNotification(false);
      setNotification({
        show: false,
        type: "",
        message: "",
      });
    }

    useEffect(() => {
      if( props.customer_id !== "new"){
        getCustomer();
        setIsEdit(true)
      }
    }, [] )

    return (
      <>
        {isNotification &&
          <Notification
          show={notification.show}
          onClose={handleClose}
          type={notification.type}
          message={notification.message}
          />
        }
        {onLoad ? (
          <Spinner animation="border" className="customer-loading-spinner" />
        ) : (
          <div className="customer_new_form">
            <Form>
              <Form.Group>
                <Form.Label>Customer Name</Form.Label>
                <Form.Control
                  value={editData.name}
                  type="text"
                  placeholder="Enter customer name"
                  name="name"
                  onChange={(e) => handleChange(e)}
                />
                <p className="customer_validation">{error.name}</p>
              </Form.Group>
              <Form.Group>
                <Form.Label>Email</Form.Label>
                <Form.Control
                  value={editData.email}
                  type="email"
                  placeholder="Enter email"
                  name="email"
                  onChange={(e) => handleChange(e)}
                />
                <p className="customer_validation">{error.email}</p>
              </Form.Group>
              <Form.Group>
                <Form.Label>Primary contact</Form.Label>
                <Form.Control
                  value={editData.primary_contact_id}
                  type="number"
                  placeholder="Enter primary contact"
                  name="primary_contact_id"
                  onChange={(e) => handleChange(e)}
                />
                <p className="customer_validation">
                  {error.primary_contact_id}
                </p>
              </Form.Group>
              <Form.Group>
                <Form.Label>Phone</Form.Label>
                <Form.Control
                  value={editData.phone}
                  type="tel"
                  pattern="[0-9]{3}-[0-9]{3}-[0-9]{4}"
                  placeholder="Enter phone"
                  name="phone"
                  onChange={(e) => handleChange(e)}
                />
              </Form.Group>
              <Form.Group>
                <Form.Label>Display Name</Form.Label>
                <Form.Control
                  value={editData.display_name}
                  type="text"
                  placeholder="Enter display name"
                  name="display_name"
                  onChange={(e) => handleChange(e)}
                />
              </Form.Group>
              <Form.Group>
                <Form.Label>Type</Form.Label>
                <Form.Control
                  value={editData.type}
                  type="text"
                  placeholder="Enter type"
                  name="type"
                  onChange={(e) => handleChange(e)}
                />
                <p className="customer_validation">{error.type}</p>
              </Form.Group>
              <Form.Group>
                <Form.Label>Website</Form.Label>
                <Form.Control
                  value={editData.website}
                  type="text"
                  placeholder="Enter website"
                  name="website"
                  onChange={(e) => handleChange(e)}
                />
              </Form.Group>
              <Form.Group>
                <Form.Label>Remarks</Form.Label>
                <Form.Control
                  value={editData.remarks}
                  type="text"
                  placeholder="Enter remark"
                  name="remarks"
                  onChange={(e) => handleChange(e)}
                />
              </Form.Group>
              {isEdit ? (
                <Button className="btn btn-primary" onClick={handleEdit}>
                  Edit Customer
                </Button>
              ) : (
                <Button className="btn btn-primary" onClick={handleSubmit}>
                  Create Customer
                </Button>
              )}
            </Form>
          </div>
        )}
      </>
    );
}