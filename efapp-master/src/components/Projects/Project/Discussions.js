import React from "react";
import { ListGroup, Container, Row, Col } from "react-bootstrap";
import useAxiosPrivate from "../../../hooks/useAxiosPrivate";
import { useState, useEffect } from "react";
import { EditorState } from "draft-js";
import { Editor } from "react-draft-wysiwyg";
import "react-draft-wysiwyg/dist/react-draft-wysiwyg.css";
import { convertToHTML } from "draft-convert";
import Spinner from "react-bootstrap/Spinner";

const GroupMessageList = (props) => {
  const axiosPrivate = useAxiosPrivate();
  const [messages, setMessages] = useState([]);
  const [alertMsg, setAlertMsg] = useState({ class: "hide", message: "" });
  const [isDiscussion, setIsDiscussion] = useState("hide");
  const [indexing, setIndexing] = useState("");
  const [editorState, setEditorState] = useState(() => EditorState.createEmpty());
  const [onLoad, setOnLoad] = useState(false);
  const [messageReplyState, setMessageReplyState] = useState(() =>
    EditorState.createEmpty()
  );
  const [MSG, setMSG] = useState({ message: "", msgReply: "" });

  const getDiscussions = async () => {
    try {
        setOnLoad(true);
        const response = await axiosPrivate.post(
            `/app/project_chats/project_chats_get/${props.id}/${props.org_id.current_org_id}`,
            JSON.stringify({ sorting:{
              "name": "created_on",
              "sort": "asc"
            }, }),
            {
              headers: { "Content-Type": "application/json" },
            }
        );
        if (response.data && response.data.code == "0") {
          setOnLoad(false);
          setAlertMsg({
            class: "alert alert-danger",
            message: response.data.message,
          });
          setTimeout(() => { clearMessage() }, 3000);
        } else {
          if (props.data.isChatOn === true) {
            setIsDiscussion("show");
          }
          setOnLoad(false);
          setMessages(response.data)
        }
    } catch(err) {
        console.log(err);
    }
  };

  const handleMessageSubmit = async () => {
    try {
      if (MSG.message !== "<p></p>") {
        const time = new Date();
        const date =
          time.toJSON().slice(0, 10) + " " + time.toLocaleTimeString();
        const chat_text = {
          message: {
            msg: MSG.message,
            mpn: props.data.MPNNo,
            reply: [],
          },
          created_on: date,
          created_by: {
            first_name: props.org_id.first_name,
            last_name: props.org_id.last_name,
          },
        };
        messages.push(chat_text);
        const response = await axiosPrivate.post(
          `/app/project_chats/project_chat_insert/${props.id}/${props.org_id.current_org_id}`,
          JSON.stringify(chat_text),
          {
            headers: { "Content-Type": "application/json" },
          }
        );
        if (response.data && response.data.code == "1") {
          setMSG({ message: "", msgReply: "" });
          setEditorState(EditorState.createEmpty());
        } else {
          setAlertMsg({
            class: "alert alert-danger",
            message: response.data.message,
          });
          setTimeout(() => {
            clearMessage();
          }, 3000);
        }
      }

    } catch(err) {
        console.log(err);
    }
  };

  const handleMessageReplySubmit = async (chatID, index) => {
    try {
      if (MSG.msgReply !== "<p></p>") {
        const chat_text = messages[index];
        const time = new Date();
        const date =
          time.toJSON().slice(0, 10) + " " + time.toLocaleTimeString();
        const reply_chat = {
          reply_msg: MSG.msgReply,
          created_on: date,
          created_by: {
            first_name: props.org_id.first_name,
            last_name: props.org_id.last_name,
          },
        };
        const rep_msg = chat_text.message.reply;
        rep_msg.push(reply_chat);
        const response = await axiosPrivate.put(
          `/app/project_chats/project_chat_edit/${chatID}/${props.org_id.current_org_id}`,
          JSON.stringify(chat_text),
          {
            headers: { "Content-Type": "application/json" },
          }
        );
        if (response.data && response.data.code == "1") {
          setMSG({ message: "", msgReply: "" });
          setMessageReplyState(EditorState.createEmpty());
          setIndexing("")
        } else {
          setAlertMsg({
            class: "alert alert-danger",
            message: response.data.message,
          });
          setTimeout(() => {
            clearMessage();
          }, 3000);
        }

      }
    } catch (err) {
      console.log(err);
    }
  };

  useEffect(() => {
    let msg = convertToHTML(editorState.getCurrentContent());
    MSG.message = msg;
    setMSG(MSG);
  }, [editorState]);

  useEffect(() => {
    let rep = convertToHTML(messageReplyState.getCurrentContent());
    MSG.msgReply = rep;
    setMSG(MSG);
  }, [messageReplyState]);

  useEffect(() => { getDiscussions(); }, [props.data.isChatOn]);

  const setReply =(index) => {
    setIndexing(index);
  };

  const clearMessage = () => {
    setAlertMsg({class: "hide", message: ""});
  };

  const handleMessageKeyPress = e => {
    if (e.keyCode === 13) {
      handleMessageSubmit();
    }
  };

  const handleReplyMessageKeyPress = (e, chatID, index) => {
    if (e.keyCode === 13) {
      handleMessageReplySubmit(chatID, index);
    }
  };


  return (
    <div>
      <div className={alertMsg.class} role="alert">
        {alertMsg.message}
      </div>
      {onLoad ? (
        <Spinner animation="border" className="customer-loading-spinner" />
      ) : (
        <>
          {!messages?.length && (
            <div className="discussion-grid">Discussion not found.</div>
          )}
          <Container
            className={
              isDiscussion === "show" ? "discussion" : "discussion-fix"
            }
            id="discussion-id"
          >
            <Row>
              <Col>
                <ListGroup>
                  {messages?.length ? (
                    messages.map((message, index) => (
                      <ListGroup.Item key={index}>
                        <div className="message-icon">
                          <span className="test">
                            <span>
                              {message.created_by.first_name[0]}{" "}
                              {message.created_by.last_name[0]}
                            </span>
                          </span>
                          <div className="created-by-msg">
                            {message.created_by.first_name}{" "}
                            {message.created_by.last_name}
                            <span className="mpn-span">
                              MPN : <b>{message.message.mpn}</b>
                            </span>
                            <span className="discussion-created-on">
                              {message.created_on}
                            </span>
                          </div>
                          <div>
                            <div
                              dangerouslySetInnerHTML={{
                                __html: message.message.msg,
                              }}
                            ></div>
                          </div>
                          {message.message.reply?.length ? (
                            message.message.reply.map((rep, i) => (
                              <div className="reply-div-right" key={i}>
                                <br></br>
                                <span className="test">
                                  <b>
                                    {rep.created_by.first_name[0]}{" "}
                                    {rep.created_by.last_name[0]}
                                  </b>
                                </span>
                                {rep.created_by.first_name}{" "}
                                {rep.created_by.last_name}
                                <span className="reply-created-right">
                                  {rep.created_on}
                                </span>
                                <div className="reply-msg-txt">
                                  <div
                                    dangerouslySetInnerHTML={{
                                      __html: rep.reply_msg,
                                    }}
                                  ></div>
                                </div>
                              </div>
                            ))
                          ) : (
                            <></>
                          )}
                          {props.org_id.first_name ===
                            message.created_by.first_name &&
                          props.org_id.last_name ===
                            message.created_by.last_name ? (
                            <></>
                          ) : (
                            <>
                              <span className="discussion-reply">
                                <a href="#/" onClick={() => setReply(index)}>
                                  Reply
                                </a>
                              </span>
                              <br />
                              {indexing === index ? (
                                <div id={index}>
                                  <Editor
                                    editorState={messageReplyState}
                                    onEditorStateChange={setMessageReplyState}
                                    wrapperClassName="wrapperClassName"
                                    editorClassName="editorClassName"
                                    toolbarClassName="toolbarClassName"
                                    toolbar={{
                                      options: ["inline"],
                                    }}
                                    keyBindingFn={(e) =>
                                      handleReplyMessageKeyPress(
                                        e,
                                        message.id,
                                        index
                                      )
                                    }
                                  />
                                </div>
                              ) : (
                                <></>
                              )}
                            </>
                          )}
                        </div>
                        <hr></hr>
                      </ListGroup.Item>
                    ))
                  ) : (
                    <></>
                  )}
                </ListGroup>
              </Col>
            </Row>
          </Container>

          <div className={isDiscussion}>
            <div className="draft-editor-div">
              <Editor
                editorState={editorState}
                onEditorStateChange={setEditorState}
                wrapperClassName="wrapperClassName"
                editorClassName="editorClassName"
                toolbarClassName="toolbarClassName"
                keyBindingFn={handleMessageKeyPress}
                toolbar={{
                  options: ["inline"],
                }}
              />
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default GroupMessageList;
