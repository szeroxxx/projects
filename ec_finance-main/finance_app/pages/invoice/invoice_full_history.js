import DataGridViewer from "../../components/DataGridViewer";
import { Form,Row,Col} from "antd";
import React, { Component } from "react";
import { ExclamationCircleOutlined} from "@ant-design/icons";
import axios from "axios";
import {Modal } from "antd";
import { showMessage } from "../../common/Util";
import moment from 'moment';
const { confirm } = Modal;
class InvoiceFullHistory extends Component {
    constructor(props) {
        super(props);
      }
  state = { data: {} };  
  appSchema = {
    pageTitle: "Invoice History",
    listing: [
      {
        dataGridUID: "invoiceFullHistory",
        url: "/dt/auditlog/payment_history/?id=" + this.props.payment_id,
        paging: true,
        default_sort_col: "id",
        default_sort_order: "descend",
        row_selection: false,
        bind_on_load: true,
        columns: [ 
          {
            value: "id",
            text: "ID",
            sortable: true,
            sequence: 0,
            show :false,
          },
          {
            value: "invoice_number",
            text: "Number",
            sortable: true,
            sequence: 2,
            width :160
          },
          {
            value: "invoice_date",
            text: "Invoice date",
            sortable: true,
            sequence: 5,
            width :160
          }
          ,{
            value: "invoice_due_date",
            text: "Invoice due date",
            sortable: true,
            sequence: 5,
            width :160
          },
          {
              value :"currency",
              text : "Currency",
              width :100
          },
          {
              value :"invoice_value",
              text : "Invoice amount",
              width :120
          },
          {
              value :"currency_invoice_value",
              text : "Customer Invoice amount",
              width :190
          },
          {
              value :"outstanding",
              text : "Outstanding",
              width :100
          },
          {
              value :"customer_outstanding",
              text : "Customer outstanding",
              width :160
          },
          {
              value :"total_amount",
              text : "Total paid amount",
              width :160
          },
          {
              value :"currency_total_amount",
              text : "Customer total paid amount",
              width :200
          },
          // {
          //   value: "id",
          //   text: "",
          //   width: 100,
          //   render: (text, record, index) => {
          //     return (
          //       <div className="deleteIcon" onClick={() => this.deletePayment(record,this.refresh)}>
          //         Delete
          //       </div>
          //     );
          //   }, 
          // },
        ],
      },
    ],
  };
  deletePayment = (data,callback) => {  
    confirm({
      title: "Are you sure want to delete this record ?",
      icon: <ExclamationCircleOutlined/>,
      content:  <></>,
      cancelText: "No, Cancel",
      okText: "Yes, Delete",
      onOk() {
        axios.post("/dt/auditlog/delete_payment/ ", { ids: data.id}).then((response) => {
          if (response.data.code == 1) {
            // callback();
            showMessage("Scheduler deleted.","Payment successfully deleted","success")

          }else{
            showMessage("No delete.","Something went wrong","error")
          }
        });
      },
      onCancel() {
      },
    });
  }
  componentDidMount = () => {
    this.getData()
    // call function if needed on component load.
  };
  getData = () => {
    axios.get( "/dt/auditlog/payment_history/?id=" + this.props.payment_id + "&object_id=" +this.props.object_id ).then((response) => {
      var rows = response.data.data
      this.setState({
            total_amount:rows[0].total_amount,
            customer_total_amount:rows[0].currency_total_amount,
            payment_mode:rows[0].payment_mode,
            paid_on:moment(rows[0].paid_on).format("YYYY-MM-DD")
          })
    });
  }
  render() {
    return (
      <>
            <Row style={{marginLeft:10}}>
              <Col span={4}>
                <h4>Customer :</h4>
              </Col>
              <Col span={4}>
                <h4>{this.props.customer_name}</h4>
              </Col>
            </Row>
            <Row style={{marginLeft:10}}>
              <Col span={4}>
                <h4>Total amount :</h4>
              </Col>
              <Col span={4}>
                <h4>{this.state.total_amount}</h4>
              </Col>
              <Col span={4}>
                <h4>{this.state.currency}</h4>
              </Col>
            </Row>
            <Row style={{marginLeft:10}}>
              <Col span={4}>
                <h4>Customer Total amount :</h4>
              </Col>
              <Col span={4}>
                <h4>{this.state.customer_total_amount}</h4>
              </Col>
              <Col span={4}>
                <h4>{this.state.currency}</h4>
              </Col>
            </Row>
            <Row style={{marginLeft:10}}>
              <Col span={4}>
                <h4>Paid on :</h4>
              </Col>
              <Col span={4}>
                <h4>{this.state.paid_on}</h4>
              </Col>
            </Row>
            <Row style={{marginLeft:10}}>
              <Col span={4}>
                <h4>Payment mode :</h4>
              </Col>
              <Col span={4}>
                <h4>{this.state.payment_mode}</h4>
              </Col>
            </Row>
        <DataGridViewer
          schema={this.appSchema.listing[0]}
          ref={(node) => {
            this.dataGridViewer = node;
          }}
        ></DataGridViewer>
      </>
    );
  }
}
InvoiceFullHistory.getInitialProps = async (context) => {
    return { id: context.query.id??"0",customer_name:context.query.cust_name,payment_id:context.query.payment_id,object_id:context.query.object_id,isModal:true};
  };
export default InvoiceFullHistory;
