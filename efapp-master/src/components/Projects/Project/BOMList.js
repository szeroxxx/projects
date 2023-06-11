import {Col,Row,ListGroup,Image,Button} from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {  faFilePdf,faTrashAlt,faSearch,faEdit,faCommentDots } from "@fortawesome/free-solid-svg-icons";
import { useEffect, useState } from "react";
import useAxiosPrivate from "../../../hooks/useAxiosPrivate";
import BOMDropzone from "./BOMDropzone";
import SearchParts from "./PartsSearch";
import PartDelete from "./PartsDelete";
import PartEdit from "./PartsEdit";
import ToolTip from "../../Common/ToolTip";
import Spinner from "react-bootstrap/Spinner";

export default function Project(props) {
  const [target, setTarget] = useState(null);
  const [parts, setParts] = useState([]);
  const [isSearchParts, setIsSearchParts] = useState(false);
  const [searchParts, setSearchParts] = useState({part:"",MPN:"",cat_name:null});
  const [isDelete, setIsDelete] = useState(false);
  const [isEdit, setIsEdit] = useState(false);
  const [bomID, setBomID] = useState();
  const [index, setIndex] = useState();
  const [isAdd, setIsAdd] = useState(false);
  const [isNew, setIsNew] = useState(false);
  const axiosPrivate = useAxiosPrivate();
  const [alertMsg, setAlertMsg] = useState({ class: "hide", message: "" });
  const [onLoad, setOnLoad] = useState(false);
  const [isDropzone, setIsDropZone] = useState(false)
  useEffect(() => { getBOMList(); }, [props.project_id] );

  const getBOMList = async () => {
    try {
      setOnLoad(true)
        const response = await axiosPrivate.post(
            `/app/bom/bill_of_materials_get/${props.org_id}/${props.project_id}`,
            {
              headers: { "Content-Type": "application/json" },
            }
        );
        if (response.data && response.data.code == "0") {
          setOnLoad(false);
          setParts([])
        } else if(response.data) {
          setOnLoad(false);
          if (response.data.length === 0){
            setIsDropZone(true);
          }
          if (response.data?.length) {
            if (response.data[0].bom !== null) {
              setParts(response.data[0].bom);
              setBomID(response.data[0].id);
            }
            if (response.data[0].bom === null) {
              setIsDropZone(true);
            }
          }
        }
    } catch(err) {
        console.log(err);
    }
  };

  const handleDelete = (index,event) => {
    setIsDelete(true);
    setTarget(event.target)
    setIndex(index)
  }

  const handleEdit = (index) => {
    setIsEdit(true);
    if (index === "new") {
      setIsNew(true);
    } else {
      setIsNew(false);
      setIndex(index);
    }
  }

  const hideDeleteModal = (reload) => {
    setIsDelete(false);
    if(reload === true){
      if (parts.length === 0){
        getBOMList();
      } ;
    }
    if(reload.code === "0") {
      setAlertMsg({
        class: "alert alert-danger",
        message: reload,
    });
    setTimeout(() => { clearMessage() }, 3000);
    }
  }

  const clearMessage = () => {
    setAlertMsg({
        class: "hide",
        message: "",
    });
  }

  const hideEditModal = (reload) => {
    setIsNew(false);
    setIsEdit(false);
    if(reload){
      console.log("success");
    }
  }

  const showSearchModal = (index,partName,MPNNo, cat_name) => {
    setIndex(index)
    searchParts.part = partName;
    searchParts.MPN = MPNNo;
    searchParts.cat_name = cat_name;
    setSearchParts(searchParts);
    setIsSearchParts(true)
  }

  const addNewPart = () => {
    searchParts.part = "";
    searchParts.MPN = "";
    searchParts.cat_name = null;
    setSearchParts(searchParts);
    setIsAdd(true)
    setIsSearchParts(true)
  }

  const hideSearchModal = () => {
    setIsSearchParts(false)
    setIsAdd(false)
  }

  const handleComment = (mpn) => {
    props.handler(mpn);
  };
  return (
    <>
      <div className={alertMsg.class} role="alert">
        {alertMsg.message}
      </div>
      {onLoad ? (
        <Spinner animation="border" className="customer-loading-spinner" />
      ) : (
        <Row>
          <Col>
            {parts?.length ? (
              <>
                <Row>
                  <Col>
                    <Button className="add-new-part-btn" onClick={addNewPart}>
                      Add New Part
                    </Button>
                  </Col>
                </Row>
                <div className="bom-list-grid">
                  <Row>
                    <Col>
                      <ListGroup className="bom-list">
                        <Row className="bom-list-header">
                          <Col md={3} className="bom-list-header-name">
                            MPN
                          </Col>
                          <Col md={1} className="bom-list-header-img">
                            Image
                          </Col>
                          <Col md={3} className="bom-list-header-desc">
                            Description
                          </Col>
                          <Col md={2} className="bom-list-header-type">
                            Type
                          </Col>
                          <Col md={1} className="bom-list-header-qty">
                            Order Qty
                          </Col>
                          <Col md={1} className="bom-list-header-price">
                            Price
                          </Col>
                          <Col md={1}></Col>
                        </Row>
                        {parts.map((part, index) => (
                          <ListGroup.Item key={index}>
                            <Row>
                              {part.part && (
                                <>
                                  <Col md={3}>
                                    <ToolTip text="MPN">
                                      <b>{part.part.name}</b>
                                    </ToolTip>
                                    <br></br>
                                    <span className="bom-list-spn">
                                      SPN:{part.sku} <br></br>
                                    </span>
                                    <span className="bom-list-cat">
                                      {part.part.cat_id ? (
                                        part.part.cat_id.name
                                      ) : (
                                        <></>
                                      )}
                                      <br></br>
                                    </span>
                                    <span>
                                      {part.part.package_id ? (
                                        part.part.package_id.ipc_name
                                      ) : (
                                        <></>
                                      )}
                                      <br></br>
                                    </span>
                                    <span
                                      className="bom-list-alter-natives"
                                      onClick={() =>
                                        showSearchModal(
                                          index,
                                          part.part.descr,
                                          part.mpn,
                                          part.part.cat_id
                                            ? part.part.cat_id.name
                                            : null
                                        )
                                      }
                                    >
                                      {" "}
                                      <FontAwesomeIcon
                                        icon={faSearch}
                                      ></FontAwesomeIcon>{" "}
                                      Find alternatives{" "}
                                    </span>
                                  </Col>
                                  <Col md={1} className="bom-list-center">
                                    <Image src={part.part.imgurl} />
                                  </Col>
                                  <Col md={3} className="bom-list-center">
                                    <span>{part.part.descr}</span>
                                  </Col>
                                  <Col md={2} className="bom-list-center">
                                    <span className="bom-list-type">
                                      <b>{part.part.type}</b>
                                    </span>
                                  </Col>
                                </>
                              )}
                              {!part.part && (
                                <>
                                  <Col md={3}>
                                    {part.mpn ? (
                                    <ToolTip text="MPN">
                                      <b>{part.mpn}</b>
                                    </ToolTip>
                                    ) : (
                                      <span className="red">Unidentified</span>
                                    )}
                                    <br></br>
                                    {part.sku ? (
                                      <span className="bom-list-spn">
                                        SPN:{part.sku} <br></br>
                                      </span>
                                    ) : (
                                      ""
                                    )}
                                    <span className="bom-list-cat"></span>
                                    <span
                                      className="bom-list-alter-natives"
                                      onClick={() =>
                                        showSearchModal(
                                          index,
                                          part.description,
                                          part.mpn
                                        )
                                      }
                                    >
                                      <FontAwesomeIcon
                                        icon={faSearch}
                                      ></FontAwesomeIcon>{" "}
                                      Find alternatives{" "}
                                    </span>
                                  </Col>
                                  <Col md={1}>
                                    <></>
                                  </Col>
                                  <Col md={3} className="bom-list-center">
                                    <span>{part.description}</span>
                                  </Col>
                                  <Col md={2} className="bom-list-center">
                                    <span className="bom-list-type"></span>
                                  </Col>
                                </>
                              )}
                              <Col md={1} className="bom-list-center">
                                <span className="bom-list-qty">
                                  <b>{part.quantity}</b>
                                </span>
                              </Col>
                              <Col md={1} className="bom-list-center">
                                <span className="bom-list-qty">
                                  <b>₹ {parseFloat(part.price).toFixed(2)}</b>
                                </span>
                              </Col>
                              <Col md={1} className="bom-list-data-right-col">
                                <Row>
                                  <Col md={12} sm={6}>
                                    <a
                                      className="bom-list-data-sheet"
                                      href={part?.part?.datasheet_url}
                                      target="_blank"
                                      rel="noreferrer"
                                    >
                                      <ToolTip text="Download pdf">
                                        <FontAwesomeIcon icon={faFilePdf} />
                                      </ToolTip>
                                    </a>
                                  </Col>
                                  <Col md={12} sm={6}>
                                    <ToolTip text="Edit">
                                      <FontAwesomeIcon
                                        className="bom-list-edit"
                                        icon={faEdit}
                                        onClick={() => handleEdit(index)}
                                      />
                                    </ToolTip>
                                  </Col>
                                  <Col md={12} sm={6}>
                                    <ToolTip text="Delete">
                                      <FontAwesomeIcon
                                        className="bom-list-remove"
                                        icon={faTrashAlt}
                                        onClick={(event) =>
                                          handleDelete(index, event)
                                        }
                                      />
                                    </ToolTip>
                                  </Col>
                                  <Col md={12} sm={6}>
                                    <ToolTip text="Discuss">
                                      <FontAwesomeIcon
                                        className="bom-list-comment"
                                        icon={faCommentDots}
                                        onClick={() =>
                                          handleComment(
                                            part.part ? part.part.name : null
                                          )
                                        }
                                      />
                                    </ToolTip>
                                  </Col>
                                </Row>
                              </Col>
                            </Row>
                          </ListGroup.Item>
                        ))}
                      </ListGroup>
                    </Col>
                  </Row>
                </div>
              </>
            ) : (
              isDropzone && (
                <>
                  <BOMDropzone
                    project_id={props.project_id}
                    org_id={props.org_id}
                    setParts={setParts}
                  />
                  <div className="bom-data-not-available">
                    No Bill of material available
                  </div>
                </>
              )
            )}
          </Col>
        </Row>
      )}
      {isDelete && (
        <PartDelete
          show={isDelete}
          handler={hideDeleteModal}
          target={target}
          index={index}
          parts={parts}
          bomID={bomID}
        />
      )}
      {isEdit && (
        <PartEdit
          show={isEdit}
          handler={hideEditModal}
          isNew={isNew}
          index={index}
          parts={parts}
          bomID={bomID}
        />
      )}
      {isSearchParts && (
        <SearchParts
          show={isSearchParts}
          isAdd={isAdd}
          handleEdit={handleEdit}
          handler={hideSearchModal}
          index={index}
          parts={parts}
          searchParts={searchParts}
          org_id={props.org_id}
          project_id={props.project_id}
          bomID={bomID}
        />
      )}
    </>
  );
}
