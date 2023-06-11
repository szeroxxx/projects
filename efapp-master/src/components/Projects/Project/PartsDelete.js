
import {Button} from 'react-bootstrap';
import Overlay from "react-bootstrap/Overlay";
import Popover from 'react-bootstrap/Popover';
import { axiosPrivate } from '../../../api/axios';
import useLocalStorage from '../../../hooks/useLocalStorage';
const PartDelete = (props) => {
    const [userData] = useLocalStorage("userdata");
    const deletePart = async () => {
        try {
            props.parts.splice(props.index, 1);
            const response = await axiosPrivate.put(
                `/app/bom/bill_of_material_edit/${props.bomID}/${userData.current_org_id}`,
                JSON.stringify({bom:props.parts}),
                {
                    headers: { 'Content-Type': 'application/json' },
                }
            )
            if(response.data && response.data.code == "1"){
                props.handler(true);
            }
            if(response.data && response.data.code == "0"){
                var msg = { msg: response.data.message, code:"0" };
                props.handler(msg);
            }
        } catch(err) {
            console.log(err);
        }
    };
    return(
        <>
        <Overlay show={props.show} target={props.target} placement="bottom" containerPadding={20}>
            <Popover id="popover-contained">
                <Popover.Body>
                    <p>Are you sure you want to delete selected record ?</p>
                    <Button variant="primary" className='delete-part-button' onClick={deletePart}>
                    Yes
                    </Button>
                    <Button variant="outline-primary" onClick={props.handler} >
                    No
                    </Button>
                </Popover.Body>
            </Popover>
        </Overlay>
        </>
    )
}
export default PartDelete;
