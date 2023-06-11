import DataGridViewer from "../../components/DataGridViewer";
import { Row, Col } from "antd";
import React, { Component } from "react";
class History extends Component {
  constructor(props) {
    super(props);
  }
  state = {};
  appSchema = {
    pageTitle: "Invoice detail",
    listing: [
      {
        dataGridUID: "serviceHistory",
        url: "",
        paging: true,
        default_sort_col: "id",
        default_sort_order: "descend",
        row_selection: true,
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
          {
            value: "sent_time",
            text: "Sent time",
            sortable: true,
            sequence: 2,
          },
          {
            value: "status_desc",
            text: "Error / Remark",
            sortable: true,
            sequence: 3,
          },
          {
            value: "descr",
            text: "Error message",
            sortable: true,
            sequence: 4,
          },
          {
            value: "invoice_due_date",
            text: "Action",
            sortable: true,
            sequence: 5,
          },
        ],
      },
    ],
  };
  render() {
    return (
      <>
        <Row>
          <Col align="right">
            <p style={{ marginBottom: 10 }}>Invocie number :</p>
            <p style={{ marginBottom: 10 }}>Customer :</p>
            <p style={{ marginBottom: 10 }}>Invoice date :</p>
            <p style={{ marginBottom: 10 }}>Transactio id :</p>
          </Col>
          <Col>
            <p style={{ marginBottom: 10 }}>&nbsp;</p>
            <p style={{ marginBottom: 10 }}>&nbsp;</p>
            <p style={{ marginBottom: 10 }}>&nbsp;</p>
            <p style={{ marginBottom: 10 }}>&nbsp;</p>
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
export default History;
