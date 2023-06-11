import {Button, Modal, Form, Row, Col} from 'react-bootstrap';
import { useState, useEffect } from 'react';
import { axiosPrivate } from '../../../api/axios';
import useLocalStorage from '../../../hooks/useLocalStorage';

const PartEdit = (props) => {
    const [userData] = useLocalStorage("userdata");
    const [alertMsg, setAlertMsg] = useState({ class: "hide", message: "" });
    const [editData, setEditData] = useState({mpn:"", ipc:"", spn : "", description : "", type : "", quantity : "", price : ""})
    const part = props.parts[props.index];

    useEffect(() => {
        if (!props.isNew) {
            setEditData({
              mpn: part.part ? part.part.name : part.mpn,
              ipc: part.part ? part.part.package_id.ipc_name : "",
              description: part.part ? part.part.descr : part.description,
              type: part.part ? part.part.type : "",
              spn: part.sku,
              quantity: part.quantity,
              price: part.price,
            });
        }
    },[] )

    const handleChange = (event) => {
        setEditData({...editData, [event.target.name]: event.target.value});
    }

    const handleUpdate = async () => {
        try {
            if(!props.isNew){
              if (props.parts[props.index].part){
                props.parts[props.index].part.type = editData.type;
                props.parts[props.index].part.descr = editData.description;
                props.parts[props.index].part.name = editData.mpn;
                props.parts[props.index].part.package_id = {
                  ipc_name: editData.ipc,
                };
              } else {
                props.parts[props.index].part = {
                  type: editData.type,
                  descr: editData.description,
                  name: editData.mpn,
                  package_id: {
                    ipc_name: editData.ipc,
                  },
                };
              }
              props.parts[props.index].description = editData.description;
              props.parts[props.index].mpn = editData.mpn;
              props.parts[props.index].quantity = editData.quantity
              props.parts[props.index].sku = editData.spn;
              props.parts[props.index].price = editData.price;
            } else {
              var part_node = props.parts
              part_node.push({
                description : editData.description,
                mpn : editData.mpn,
                sku : editData.spn,
                price: editData.price,
                quantity: editData.quantity,
                part: {
                  type: editData.type,
                  descr: editData.description,
                  name: editData.mpn,
                  package_id: {
                    ipc_name: editData.ipc,
                  },
                },
              });
            }
            const response = await axiosPrivate.put(
                `/app/bom/bill_of_material_edit/${props.bomID}/${userData.current_org_id}`,
                JSON.stringify({bom:props.parts}),
                {
                    headers: { 'Content-Type': 'application/json' },
                }
            )
            if (response.data && response.data.code == "1") {
                setAlertMsg({
                    class: "alert alert-success footer-edit-parts",
                    message: response.data.message,
                });
                setTimeout(() => { props.handler(true) }, 2000);
            } else {
                setAlertMsg({
                    class: "alert alert-danger footer-edit-parts",
                    message: response.data.message,
                });
            }
        } catch(err) {
            console.log(err);
        }
    }

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
            <Modal.Title>Edit Parts</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <div className="address_new_form">
              <div>
                <Form>
                  <Form.Group as={Row} className="mb-3">
                    <Form.Label column sm={3}>
                      MPN
                    </Form.Label>
                    <Col sm={9}>
                      <Form.Control
                        value={editData.mpn}
                        type="text"
                        placeholder="Enter MPN"
                        name="mpn"
                        onChange={(e) => handleChange(e)}
                      />
                    </Col>
                  </Form.Group>
                  <Form.Group as={Row} className="mb-3">
                    <Form.Label column sm={3}>
                      SPN
                    </Form.Label>
                    <Col sm={9}>
                      <Form.Control
                        value={editData.spn}
                        type="text"
                        placeholder="Enter SPN"
                        name="spn"
                        onChange={(e) => handleChange(e)}
                      />
                    </Col>
                  </Form.Group>
                  <Form.Group as={Row} className="mb-3">
                    <Form.Label column sm={3}>
                      IPC
                    </Form.Label>
                    <Col sm={9}>
                      <Form.Control
                        value={editData.ipc}
                        type="text"
                        placeholder="Enter IPC"
                        name="ipc"
                        onChange={(e) => handleChange(e)}
                      />
                    </Col>
                  </Form.Group>
                  <Form.Group as={Row} className="mb-3">
                    <Form.Label column sm={3}>
                      Description
                    </Form.Label>
                    <Col sm={9}>
                      <Form.Control
                        value={editData.description}
                        type="text"
                        placeholder="Enter Quantity"
                        name="description"
                        onChange={(e) => handleChange(e)}
                      />
                    </Col>
                  </Form.Group>
                  <Form.Group as={Row} className="mb-3">
                    <Form.Label column sm={3}>
                      Type
                    </Form.Label>
                    <Col sm={9}>
                      <Form.Control
                        value={editData.type}
                        type="text"
                        placeholder="Enter Type"
                        name="type"
                        onChange={(e) => handleChange(e)}
                      />
                    </Col>
                  </Form.Group>
                  <Form.Group as={Row} className="mb-3">
                    <Form.Label column sm={3}>
                      Order Qty
                    </Form.Label>
                    <Col sm={9}>
                      <Form.Control
                        value={editData.quantity}
                        type="number"
                        placeholder="Enter Order Qty"
                        name="quantity"
                        onChange={(e) => handleChange(e)}
                      />
                    </Col>
                  </Form.Group>
                  <Form.Group as={Row} className="mb-3">
                    <Form.Label column sm={3}>
                      Price
                    </Form.Label>
                    <Col sm={9}>
                      <Form.Control
                        value={editData.price}
                        type="number"
                        placeholder="Enter Price"
                        name="price"
                        onChange={(e) => handleChange(e)}
                      />
                    </Col>
                  </Form.Group>
                </Form>
              </div>
            </div>
          </Modal.Body>
          <Modal.Footer>
            <div className={alertMsg.class} role="alert">
              {alertMsg.message}
            </div>
            <Button variant="outline-primary" onClick={props.handler}>
              Cancel
            </Button>
            {props.isNew ? (
              <Button className="btn btn-primary" onClick={handleUpdate}>
                Add Parts
              </Button>
            ) : (
              <Button className="btn btn-primary" onClick={handleUpdate}>
                Edit Parts
              </Button>
            )}
          </Modal.Footer>
        </Modal>
      </>
    );
}
export default PartEdit;