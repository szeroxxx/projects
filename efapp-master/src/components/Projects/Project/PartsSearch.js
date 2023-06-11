import {Button, Modal, Form, Row, Col, InputGroup, Image, ListGroup} from 'react-bootstrap';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSearch, faFilePdf } from "@fortawesome/free-solid-svg-icons";
import "../Projects.css";
import useAxiosPrivate from '../../../hooks/useAxiosPrivate';
import { useState, useEffect } from "react";
import Spinner from 'react-bootstrap/Spinner';
import useLocalStorage from '../../../hooks/useLocalStorage';
import ToolTip from '../../Common/ToolTip';
import CustomPagination from '../../Common/Pagination';

export default function SearchParts(props) {
    const axiosPrivate = useAxiosPrivate();
    const [searchParts, setSearchParts] = useState([]);
    const [search, setSearch] = useState(props.searchParts.part);
    const [alertMsg, setAlertMsg] = useState({ class: "hide", message: "" });
    const [userData] = useLocalStorage("userdata");
    const [onLoad, setOnLoad] = useState(false)
    const [isAddManually, setIsAddManually] = useState(false)
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);

    const getSearchPart = async () => {
      try {
          setSearchParts([])
          setOnLoad(true)
          if(search){
              const response = await axiosPrivate.get(
                `/bom/search_alternative_parts?search_data=${search}&size=20&page=${currentPage}&cat_name=${props.searchParts.cat_name}`,
                {
                  headers: { "Content-Type": "application/json" },
                }
              );
              if( response.data && response.data.code == "0"){
                  setIsAddManually(true);
                  setOnLoad(false);
                  setAlertMsg({
                      class: "alert alert-danger",
                      message: response.data.message,
                    });
                  setSearchParts([])
              } else {
                setIsAddManually(true);
                setOnLoad(false);
                setSearchParts(response.data.items);
                setAlertMsg({
                  class: "hide",
                  message: "",
                });
                setTotalPages(response.data.pages);
              }
            }
        setOnLoad(false);

      } catch(err) {
          console.log(err);
      }
    };

    const selectPart = async (index) => {
        try {
            if(props.isAdd === true){
                var parts_data = props.parts
                parts_data.push({
                  price: 0,
                  quantity:1,
                  part: searchParts[index].part,
                });
            } else {
                props.parts[props.index].part = searchParts[index].part
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
                    class: "alert alert-success",
                    message: response.data.message,
                });
                props.handler(true);
            } else {
                setAlertMsg({
                    class: "alert alert-danger",
                    message: response.data.message,
                });
            }
        } catch(err) {
            console.log(err);
        }
    }

    const addManually = () => {
        props.handler();
        props.handleEdit("new");
    }

    const handleKeypress = e => {
        if (e.keyCode === 13) {
            getSearchPart();
        }
    };

    useEffect(() => {
      getSearchPart();
    }, [currentPage]);

    const handlePageChange = (pageNumber) => {
      setCurrentPage(pageNumber);
      getSearchPart();
    };

    return (
      <>
        <Modal
          show={props.show}
          onHide={props.handler}
          size="xl"
          className="my-modal-search"
          scrollable={true}
        >
          <Modal.Header closeButton>
            <Modal.Title>
              Search Parts{" "}
              {!props.isAdd && <b>MPN : {props.searchParts.MPN}</b>}
            </Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <div>
              <InputGroup className="search_parts">
                <Form.Control
                  type="text"
                  placeholder="Search"
                  value={search}
                  onChange={(e) => {
                    setSearch(e.target.value);
                  }}
                  onKeyUp={handleKeypress}
                />
                <Button
                  className="bom-search-button"
                  variant="primary"
                  onClick={getSearchPart}
                >
                  <FontAwesomeIcon icon={faSearch} /> Search
                </Button>
              </InputGroup>
            </div>
            <div className={alertMsg.class} role="alert">
              {alertMsg.message}
            </div>
            {searchParts?.length ? (
              <div>
                <ListGroup className="search-parts-list">
                  {searchParts.map((part, index) => (
                    <ListGroup.Item key={index}>
                      <Row>
                        {part.part && (
                          <>
                            <Col md={3}>
                              <b>{part.part.name}</b>
                              <br></br>
                              <span className="search-parts-list-spn">
                                SPN:{part.part.name}
                                <br></br>
                              </span>
                              <span className="search-parts-list-cat">
                                {part.part.cat_id.name}
                                <br></br>
                              </span>
                            </Col>
                            <Col md={2}>
                              <Image src={part.part.imgurl} />
                            </Col>
                            <Col md={3} className="search-select-div">
                              <span>{part.part.descr}</span>
                            </Col>
                            <Col md={2} className="search-select-div">
                              <span className="search-parts-list-type">
                                Type:<b>{part.part.type}</b>
                              </span>
                            </Col>
                            <Col md={1} className="search-select-div">
                              <a
                                className="bom-list-data-sheet"
                                href={part?.part?.datasheet_url}
                                target="_blank"
                                rel="noreferrer"
                              >
                                <ToolTip text="PDF">
                                  <FontAwesomeIcon icon={faFilePdf} />
                                </ToolTip>
                              </a>
                            </Col>
                            <Col md={1} className="search-select-div">
                              <Button
                                size="sm"
                                className="search-select"
                                onClick={() => selectPart(index)}
                              >
                                Select
                              </Button>
                            </Col>
                          </>
                        )}
                      </Row>
                    </ListGroup.Item>
                  ))}
                </ListGroup>
              </div>
            ) : (
              onLoad && (
                <Spinner animation="border" className="loading-spinner" />
              )
            )}
            <div className="custom-pagination-part-search">
              <Row>
                <Col>
                  <CustomPagination
                    currentPage={currentPage}
                    totalPages={totalPages}
                    onPageChange={handlePageChange}
                  />
                </Col>
              </Row>
            </div>
          </Modal.Body>
          {isAddManually && (
            <Modal.Footer>
              <a
                className="search-part-manually"
                href="#/"
                onClick={addManually}
              >
                In case of part not found, define your part manually
              </a>
            </Modal.Footer>
          )}
        </Modal>
      </>
    );
}