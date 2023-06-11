import { Form, Button } from 'react-bootstrap'
import { useState, useEffect } from 'react'
import useLocalStorage from "../../hooks/useLocalStorage";
import useAxiosPrivate from "../../hooks/useAxiosPrivate";
import { useParams } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import Spinner from "react-bootstrap/Spinner";
import Notification from '../Common/Notification';

export default function ProjectNew() {
    const { project_id }  = useParams();
    const [userData] = useLocalStorage("userdata");
    const [formData, setFormData] = useState({name:"",description:"",type:"",quantity:"",tags:"",remarks:"", priority:""});
    const [customer, setCustomer] = useState({customer_id:""})
    const [editData, setEditData] = useState({})
    const [isEdit, setIsEdit] = useState(false)
    const axiosPrivate = useAxiosPrivate();
    const [error, setError] = useState({});
    const [customerLookup, setCustomerLookup] = useState([])
    const [onLoad, setOnLoad] = useState(false);
    const [notification, setNotification] = useState({show:false,type:"",message:""})
    const [isNotification, setIsNotification] = useState(false)
    const navigate = useNavigate();

    const handleChange = (event) => {
      if (isEdit) {
          setEditData({...editData, [event.target.name]: event.target.value});
      } else {
          setFormData({...formData, [event.target.name]: event.target.value});
      }
    }

    const handleSubmit = async (event) => {
      try {
        event.preventDefault();
        if(validator()){
          const response = await axiosPrivate.post(
              `/app/projects/project_insert/${customer.customer_id}/${userData.current_org_id}`,
              JSON.stringify(formData),
              {
                  headers: { 'Content-Type': 'application/json' },
              }
          );
          if (response.data && response.data.code == "1") {
            setNotification({  show: true,  type: "success",  message: response.data.message });
            setIsNotification(true);
            setTimeout(() => { handleClose(); }, 2000);
            navigate(`/project/${response.data.project_id}`)
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
      try {
        if (validator()) {
          const response = await axiosPrivate.put(
            `/app/projects/project_edit/${project_id}/${userData.current_org_id}`,
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

    const editProject = async () => {
      try {
        setOnLoad(true);
        const post_data = {
          "fields": ["name", "description", "type", "quantity", "tags", "remarks","customer_id","priority"]
        }
        const response = await axiosPrivate.post(
          `/app/projects/project_get/${project_id}/${userData.current_org_id}`,
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

    const validator = () => {
      let tempError = {};
      if (isEdit) {
        if (!editData.name) {
            tempError.name = "Project Name required"
        }
        if (!editData.quantity) {
            tempError.quantity = "Quantity required"
        }
        if (!editData.customer_id) {
            tempError.customer_id = "Customer required"
        }
      } else {
        if (!formData.name) {
            tempError.name = "Project Name required"
        }
        if (!formData.quantity) {
            tempError.quantity = "Quantity required"
        }
        if (!customer.customer_id) {
            tempError.customer_id = "Customer required"
        }
      }
      setError(tempError)
      return Object.keys(tempError).length === 0;
    }

    useEffect(() => {
      getCustomers();
      if(project_id !== "new"){
        editProject();
        setIsEdit(true)
      }
    } , [] );

    const handleTag = (event) => {
      setFormData({...formData, [event.target.name]:[event.target.value]})
      if (isEdit) {
          setEditData({...editData, [event.target.name]: event.target.value});
      }
    }

    const customerChange = (event) => {
      setCustomer({...customer, [event.target.name]:[event.target.value]})
      if (isEdit) {
          setEditData({...editData, [event.target.name]: event.target.value});
      }
    }

    const getCustomers = async () => {
        try {
            const response = await axiosPrivate.get(
                `/app/masters/customer_get_all/${userData.current_org_id}`,
                {
                  headers: { 'Content-Type': 'application/json' },
                }
            )
            if (response.data && response.data.code == "0") {
                setCustomerLookup([])
            } else {
                setCustomerLookup(response.data)
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
    };

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
        <div className="project_new_container">
          {onLoad ? (
            <Spinner animation="border" className="address-loading-spinner" />
          ) : (
            <div className="project_new_form">
              <div>
                <Form.Group>
                  <Form.Label>Project Name</Form.Label>
                  <Form.Control
                    value={editData.name}
                    type="text"
                    placeholder="Enter project name"
                    name="name"
                    onChange={(e) => handleChange(e)}
                  />
                  <p className="project_validation">{error.name}</p>
                </Form.Group>
                <Form.Group>
                  <Form.Label>Description</Form.Label>
                  <Form.Control
                    value={editData.description}
                    type="text"
                    placeholder="Enter project description"
                    name="description"
                    onChange={(e) => handleChange(e)}
                  />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label column sm={2}>
                    Customer
                  </Form.Label>
                  <Form.Control
                    as="select"
                    name="customer_id"
                    onChange={(e) => customerChange(e)}
                  >
                    <option value="">-Select Customer-</option>
                    {customerLookup.map((option, index) => {
                      return (
                        <option
                          key={index}
                          value={option.id}
                          selected={editData.customer_id === option.id}
                        >
                          {option.name}
                        </option>
                      );
                    })}
                  </Form.Control>
                  <p className="project_validation">{error.customer_id}</p>
                </Form.Group>
                <Form.Group>
                  <Form.Label>Project Type</Form.Label>
                  <Form.Control
                    value={editData.type}
                    as="select"
                    name="type"
                    onChange={(e) => handleChange(e)}
                  >
                    <option>-Select Project Type-</option>
                    <option value={1}>Hardware</option>
                    <option value={2}>Software</option>
                  </Form.Control>
                </Form.Group>
                <Form.Group>
                  <Form.Label>Project Priority</Form.Label>
                  <Form.Control
                    value={editData.priority}
                    as="select"
                    name="priority"
                    onChange={(e) => handleChange(e)}
                  >
                    <option>-Select Project Priority-</option>
                    <option value="normal">Normal</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </Form.Control>
                </Form.Group>
                <Form.Group>
                  <Form.Label>Quantity</Form.Label>
                  <Form.Control
                    value={editData.quantity}
                    type="number"
                    placeholder="Enter project quantity"
                    name="quantity"
                    onChange={(e) => handleChange(e)}
                  />
                  <p className="project_validation">{error.quantity}</p>
                </Form.Group>
                <Form.Group>
                  <Form.Label>Tags</Form.Label>
                  <Form.Control
                    value={editData.tags}
                    type="text"
                    placeholder="Enter project tags"
                    name="tags"
                    onChange={(e) => handleTag(e)}
                  />
                </Form.Group>
                <Form.Group>
                  <Form.Label>Remarks</Form.Label>
                  <Form.Control
                    value={editData.remarks}
                    type="text"
                    placeholder="Enter project remarks"
                    name="remarks"
                    onChange={(e) => handleChange(e)}
                  />
                </Form.Group>
                <Form.Group>
                  {isEdit ? (
                    <Button className="btn btn-primary" onClick={handleEdit}>
                      Edit project
                    </Button>
                  ) : (
                    <Button className="btn btn-primary" onClick={handleSubmit}>
                      Create project
                    </Button>
                  )}
                </Form.Group>
              </div>
            </div>
          )}
        </div>
      </>
    );
}