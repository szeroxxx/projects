import DataGridViewer from "../../components/DataGridViewer";
import React, { Component } from "react";
import { Row, Col } from "antd";

class huTaxInvoiceHistory extends Component {
  constructor(props) {
    super(props);
  }
  state = { data: {} };

  appSchema = {
    pageTitle: "Hu-tax history",
    listing: [
      {
        dataGridUID: "huTaxinvoiceHistory",
        url: "",
        paging: true,
        default_sort_col: "id",
        default_sort_order: "descend",
        row_selection: false,
        bind_on_load: true,
        gridViewer: true,
        columns: [
          {
            value: "id",
            text: "ID",
            sortable: true,
            sequence: 0,
            show: false,
          },
          ,
          {
            value: "",
            text: "Sent time",
            sortable: true,
            sequence: 5,
          },
          {
            value: "",
            text: "Status",
            sortable: true,
            sequence: 3,
          },
          ,
          {
            value: "",
            text: "Error/Remark",
            sortable: true,
            sequence: 6,
          },
          {
            value: "",
            text: "Error message",
            sortable: true,
            sequence: 7,
          },
          {
            value: "",
            text: "Action",
            sortable: true,
            sequence: 8,
          },
        ],
      },
    ],
  };

  componentDidMount = () => {
    // call function if needed on component load.
  };
  render() {
    return (
      <>
        <Row>
          <Col span={5}>
            <h3>Invoice Nr. :</h3>
          </Col>
          <Col span={5}>
            <p>{this.props.invoice_number}</p>
          </Col>
        </Row>
        <Row>
          <Col span={5}>
            <h3>Customer :</h3>
          </Col>
          <Col span={5}>
            <p>{this.props.customer}</p>
          </Col>
        </Row>
        <Row>
          <Col span={5}>
            <h3>Invoice date :</h3>
          </Col>
          <Col span={5}>
            <p>{this.props.invoice_date}</p>
          </Col>
        </Row>
        <Row>
          <Col span={5}>
            <h3>Transaction id :</h3>
          </Col>
          <Col span={5}>
            <p>{this.props.transaction_id}</p>
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
huTaxInvoiceHistory.getInitialProps = async (context) => {
  return {
    id: context.query.id ?? "0",
    customer: context.query.customer,
    invoice_number: context.query.invoice_number,
    invoice_date: context.query.invoice_date,
    transaction_id: context.query.transaction_id,
    isModal: true,
  };
};
export default huTaxInvoiceHistory;
