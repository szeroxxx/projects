import { Table } from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faDownload } from "@fortawesome/free-solid-svg-icons";
import useAxiosPrivate from "../../../hooks/useAxiosPrivate";

export default function DocumentGridLine(props){

    const axiosPrivate = useAxiosPrivate();

    const document_data = props.data

    const Trigger = async (info) => {
        try {
            const response = await axiosPrivate.post(
                `/app/project_files/downloadfile/${info.id}/${props.org_id}`,
                JSON.stringify({}),
                {
                  headers: { "Content-Type": "application/json" },
                },
            )
        } catch(err) {
            console.log(err);
        }
    }

    const DocumentData =  document_data.map(
        (item,i)=>{
          return(
            <tr className="table_row" key={i}>
                <td><FontAwesomeIcon className="down_icon" icon={faDownload} onClick={()=>{Trigger(item)}}/> {item.file_name}</td>
                <td>{item.project_file_type}</td>
                <td>{item.created_by}</td>
                <td>{item.created_on}</td>
            </tr>
          )
        }
      )

    return (
        <>
            { document_data?.length ? (
                <Table hover>
                <thead>
                <tr>
                    <th>Document</th>
                    <th>File type</th>
                    <th>Created by</th>
                    <th>Created on</th>
                </tr>
                </thead>
                <tbody>
                    {DocumentData}
                </tbody>
            </Table>
            ):(
            <div className="document_table">No Document available</div>
            )}
        
        </>
    )
}