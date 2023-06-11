import {Button ,Modal} from 'react-bootstrap';
import useAxiosPrivate from '../../../hooks/useAxiosPrivate';
import useLocalStorage from '../../../hooks/useLocalStorage';

export default function DeleteContact(props) {
    const axiosPrivate = useAxiosPrivate();
    const [userdata] = useLocalStorage("userdata");

    const deleteContact = async () => {
      try {
        const response = await axiosPrivate.delete(
          `/app/contacts/contacts_delete/${userdata.current_org_id}/${props.contact_id}`,
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
      } catch (err) {
        console.log(err);
      }
    }

    return (
      <>
        <Modal show={props.show} onHide={props.handler}>
          <Modal.Header closeButton>
            <Modal.Title>Delete Contact</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <p>Are you sure you want to delete Contact?</p>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="outline-primary" onClick={props.handler}>
              Cancel
            </Button>
            <Button variant="primary" onClick={deleteContact}>
              Delete
            </Button>
          </Modal.Footer>
        </Modal>
      </>
    );
}
