import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { faCloudUpload } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import useAxiosPrivate from "../../../hooks/useAxiosPrivate";
import ProgressBar from 'react-bootstrap/ProgressBar';

function BOMDropzone(props) {
  const axiosPrivate = useAxiosPrivate();
  const [alertMsg, setAlertMsg] = useState({isAlert:false,message:""});

  const [processing, setProcessing] = useState(false);
  const onDrop = useCallback((acceptedFiles) => {
    setProcessing(true);
    uploadFile(acceptedFiles[0]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  const uploadFile = async (file) => {
    var formData = new FormData();
    formData.append("bill_of_material_file", file);
    let url =
      "/app/bom/bom_generate_file_data/" +
      props.org_id +
      "/" +
      props.project_id;
    const response = await axiosPrivate.post(url, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    if (response.data && response.data.code == "0") {

      setProcessing(false);
      setAlertMsg({isAlert:true,message:response.data.message});
      setTimeout(() => { clearMessage() }, 5000);
    } else {
      setProcessing(false);
      props.setParts(response.data);
    }
  };

  const clearMessage = () => {
    setAlertMsg({
      isAlert: false,
      message: "",
      });
  };


  return (
    <>
    <div>
      <div {...getRootProps()}>
        <div className={alertMsg.isAlert ? ("bom-dropzone-alert"):("bom-dropzone")}>
          <input {...getInputProps()}/>
          {isDragActive ? (
            <p>Drop the files here ...</p>
          ) : (
            <>
              <p>
                Drag and drop BOM files here, or click to select files
                <br></br>
                <FontAwesomeIcon className="upload-icon" icon={faCloudUpload} />
              </p>
              <p className="bom-drop-zone-allowed-files">
                Allowed csv,xls,xlsx files only
              </p>
              {processing &&
              <div>
                <p className="upload-processing">Processing files...</p>
                <ProgressBar animated  striped variant="success" now={100} key={1} />
              </div>}
              {alertMsg.isAlert ? (
                <p className="drop-alert-message">
                {alertMsg.message}
              </p>
              ):(
                <></>
              )}
            </>
          )}
        </div>
      </div>
    </div>
    </>
  );
}
export default BOMDropzone;
