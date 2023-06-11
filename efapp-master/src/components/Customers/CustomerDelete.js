import {Button ,Modal} from 'react-bootstrap';
import useAxiosPrivate from "../../hooks/useAxiosPrivate";
import React from 'react';

const DeleteCustomer = (props) => {
    const axiosPrivate = useAxiosPrivate();
    const deleteCustomer = async() => {
      try {
        const response = await axiosPrivate.delete(
          `/app/customers/customers_delete/${props.org_id}/${props.customer_id}`,
          {
            headers: { "Content-Type": "application/json" },
          }
        );
        if (response.data && response.data.code == "1") {
            var alertSuccess = {  show: true,  type: "success",  message: response.data.message }
            props.handler(true, alertSuccess);
        } else {
          var alertDanger = {  show: true,  type: "alert",  message: response.data.message };
          props.handler(false, alertDanger);
        }
      } catch(err) {
          console.log(err);
      }
    }
    return (
      <>
        <Modal show={props.show} onHide={props.handler}>
          <Modal.Header closeButton>
            <Modal.Title>Delete Customer</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <p>Are you sure you want to delete Customer?</p>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="outline-primary" onClick={props.handler}>
              Cancel
            </Button>
            <Button variant="primary" onClick={deleteCustomer}>
              Delete
            </Button>
          </Modal.Footer>
        </Modal>
      </>
    );
}
export default DeleteCustomer;