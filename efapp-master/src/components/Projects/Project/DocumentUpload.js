import { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import {faCloudUpload  } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import useAxiosPrivate from "../../../hooks/useAxiosPrivate";
import ProgressBar from 'react-bootstrap/ProgressBar';
import { useCallback } from 'react';
export default function DocumentDropZone(props) {
    const project_id = props.project_id
    const axiosPrivate = useAxiosPrivate();
    const [processing, setProcessing] = useState(false);
  const [alertMsg, setAlertMsg] = useState({ class: "hide", message: "" });

    const onDrop = useCallback(acceptedFiles => {
      handleUpload(acceptedFiles[0]);
      setProcessing(true);
    }, []);

    const { getRootProps, getInputProps } = useDropzone({
      onDrop,
      accept: {
        'image/jpeg': ['.jpeg', '.png'],
        'application/pdf':[],
        'application/msword':[],
        'text/csv':[],
        'application/vnd.ms-excel':[],
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':[],
        'application/zip':[],
        'application/vnd.rar':[],
        'text/plain':[],
        'application/xml':[]
      }
     });

    const handleUpload = async (file) => {
      var formData = new FormData();
      formData.append("file",file);
      try {
        const response = await axiosPrivate.post(
          `/app/project_files/uploadfile/${project_id}/${props.org_id}`,
          formData,
          {
            headers: { "Content-Type": "multipart/form-data" },
          },
        );
        if (response.data && response.data.code == "0") {
          setProcessing(false);
          setAlertMsg({
            class: "alert alert-danger",
            message: response.data.message,
          });
          setTimeout(() => { clearMessage() }, 3000);
        } else {
          props.handler();
          setProcessing(false);
        }
      } catch(err) {
          console.error(err);
      }
    }

    const clearMessage = () => {
      setAlertMsg({
          class: "hide",
          message: "",
        });
    }

    return (
      <>
      <div>
      <div className={alertMsg.class} role="alert">
        {alertMsg.message}
      </div>
        <div {...getRootProps()}>
          <div className='bom-dropzone'>
            <input {...getInputProps()} />
              <>
                <p>Drag and drop Document files here, or click to select files
              <br></br>
              <FontAwesomeIcon className='upload-icon' icon={faCloudUpload} />
              </p>
            <p className='bom-drop-zone-allowed-files'>
                Allowed img,pdf,doc,csv,xls,xl,zip,rar,brd,cad,text,xml files only
            </p>
              {processing &&
              <div>
                <p className="upload-processing">Processing files...</p>
                <ProgressBar animated  striped variant="success" now={100} key={1} />
              </div>}
              </>
          </div>
        </div>
      </div>
      </>
  );
}