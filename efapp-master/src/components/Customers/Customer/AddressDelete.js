import {Button ,Modal} from 'react-bootstrap';
import useAxiosPrivate from "../../../hooks/useAxiosPrivate";

export default function DeleteAddress(props) {
    const show = props.show;
    const axiosPrivate = useAxiosPrivate();

    const deleteAddress = async () => {
      try {
        const response = await axiosPrivate.delete(
          `/app/addresses/addresses_delete/${props.org_id}/${props.address_id}`,
          {
            headers: { "Content-Type": "application/json" },
          }
        );
        if (response.data && response.data.code == "1") {
          var alertSuccess = {  show: true,  type: "success",  message: response.data.message };
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
        <Modal show={show} onHide={props.handler}>
          <Modal.Header closeButton>
            <Modal.Title>Delete Address</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <p>Are you sure you want to delete Address?</p>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="outline-primary" onClick={props.handler}>
              Cancel
            </Button>
            <Button variant="primary" onClick={deleteAddress}>
              Delete
            </Button>
          </Modal.Footer>
        </Modal>
      </>
    );
}