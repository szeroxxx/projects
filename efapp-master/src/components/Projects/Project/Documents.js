import DocumentGridLine from "./DocumentGridLine";
import DocumentDropZone from "./DocumentUpload";
import { useEffect, useState } from "react";
import useAxiosPrivate from "../../../hooks/useAxiosPrivate";
import useLocalStorage from "../../../hooks/useLocalStorage";
import Spinner from "react-bootstrap/Spinner";

export default function Documents(props){
    const project_id = props.id
    const [userData] = useLocalStorage("userdata");
    const [documentData, setDocumentData] = useState([])
    const axiosPrivate = useAxiosPrivate();
    const [onLoad, setOnLoad] = useState(false);

    const getDocument = async () => {
        try {
            setOnLoad(true);
            const response = await axiosPrivate.get(
                `/app/project_files/project_files_get/${project_id}/${userData.current_org_id}`,
                JSON.stringify({}),
                {
                  headers: { "Content-Type": "application/json" },
                },
            )
            if (response.data && response.data.code == "0") {
                setOnLoad(false);
                setDocumentData([])
            } else {
                setOnLoad(false);
                setDocumentData(response.data)
            }
        } catch(err) {
            console.log(err);
        }
    }

    useEffect(() => {
        if(project_id !== "new"){
            getDocument();
        }
    } , [])

    return (
        <>
        <div className="document_drop_zone">
            <DocumentDropZone org_id={userData.current_org_id} project_id={project_id} handler={getDocument}></DocumentDropZone>
        </div>
        {onLoad ? (
            <Spinner
            animation="border"
            className="customer-loading-spinner"
            />
            ):(
            <DocumentGridLine data = {documentData} org_id={userData.current_org_id}/>
            )}
        </>
    )
}