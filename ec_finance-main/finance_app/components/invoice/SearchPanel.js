import { CheckOutlined } from "@ant-design/icons";
import React, { useState } from "react";
import {Form, Input,Col, Button,InputNumber,Checkbox } from "antd";

const SearchPanel = ({ data,customValue}) => {
  const [selectedRow, setValue] = useState(customValue);
  console.log('customValue',customValue);
  console.log('customValue',data);
  let outstanding =0;
  let invoiceValue =0;
  let Currency='';
  let differentCurr=false;
  if(customValue){
  for (var row in customValue[data]) {
    outstanding = outstanding + parseFloat(customValue[data][row].outstanding);
    invoiceValue= invoiceValue + parseFloat(customValue[data][row].invoice_value);
    if(Currency==''||Currency==customValue[data][row].currency_symbol){
      Currency=customValue[[data]][row].currency_symbol;
    }
    else{
      differentCurr=true;
    }
  }
}
if(differentCurr){
  outstanding=0;
  invoiceValue=0;
  Currency='';
}
  return (
  
    <div style={{width:980}}>
<Form
      layout="inline"
    >
      <Col>
      <Form.Item label="Outstanding">
        <span className="invoiceTopBar"> {outstanding.toFixed(3) +" "+  Currency}</span>
      </Form.Item>
      </Col>
      <Col span={6}>
      <Form.Item label="Invoice value">
      <span className="invoiceTopBar">{invoiceValue.toFixed(3) +" "+ Currency}</span>
      </Form.Item>
      </Col>
      {/* <Col span={3}>
      <Form.Item >
        <InputNumber placeholder="Invoices"/>
      </Form.Item>
      </Col>
      <Col span={3}>
      <Form.Item>
        <InputNumber placeholder="Tolerance"/>
      </Form.Item>
      </Col>
      <Col span={3}>
      <Form.Item>
        <InputNumber placeholder="Payment" />
      </Form.Item>
      </Col>
      <Col span={3}>
      <Form.Item >
        <Button >Match</Button>
      </Form.Item>
      </Col>
      <Col span={2}>
      <Form.Item label="Private" >
        <Checkbox />
      </Form.Item>
      </Col> */}
    </Form>
    </div>
  );
};
export default SearchPanel;