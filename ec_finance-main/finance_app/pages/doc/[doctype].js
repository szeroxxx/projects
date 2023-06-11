import React, { useState } from "react";
import { Image, Form, Input, Button } from "antd";
import axios from "axios";
function Document({ doctype, docNumber, dataUrl }) {
  let iframeURL = dataUrl;
  return (
    <>
      <iframe src={iframeURL} style={{ width: "100%", height: "1000px", border: 0 }} />
    </>
  );
}

export default Document;
export async function getServerSideProps(context) {
  let docType = context.query.doctype;
  let docNumber = context.query.number ?? "";
  console.log("context.query.doctype", context.query.doctype);
  const res = await axios.post(process.env.APP_API_END_POINT + "/dt/attachment/get_doc/", { doctype: docType, number: docNumber }).then((response) => {
    console.log("context.query.doctype", response);
    return response;
  });
  let dataUrl = "";
  if (res.data.code == 1) {
    dataUrl = JSON.parse(res.data.data).url;
  }
  console.log(dataUrl);
  return {
    props: { docType, docNumber, dataUrl, is_open: true },
  };
}
