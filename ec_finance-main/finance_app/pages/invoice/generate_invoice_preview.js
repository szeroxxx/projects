import { Button, Card, Col, Row } from "antd";
import axios from "axios";
import React from "react";
import DataGridViewer from "../../components/DataGridViewer";

class generateInvoicePreview extends React.Component {
  constructor(props) {
    super(props);
    this.child = React.createRef();
  }
  //   onClose = () => {
  //     this.child.current.hideModal();
  //   };
  state = { invoice_data: {} };
  generateInvoicePreviewSchema = {
    listing: [
      {
        dataGridUID: "creditInvoice",
        url: "/dt/sales/order_lines/?ids=" + this.props.invoice_id,
        row_selection: false,
        bind_on_load: true,
        columns: [
          {
            value: "id",
            text: "ID",
            show: false,
            row_key: true,
            sequence: 1,
          },
          {
            value: "",
            text: "Detail",
            editable: true,
            width: 100,
            sequence: 2,
          },
          {
            value: "",
            text: "Purchase reference",
            editable: true,
            width: 100,
            sequence: 3,
          },
          {
            value: "",
            text: "Project reference",
            editable: true,
            width: 100,
            sequence: 4,
          },
          {
            value: "",
            text: "Article reference",
            editable: true,
            width: 100,
            sequence: 5,
          },
          {
            value: "order_number",
            text: "Order no.",
            editable: true,
            width: 100,
            sequence: 6,
          },
          {
            value: "quantity",
            text: "Quantity",
            editable: true,
            width: 100,
            sequence: 7,
          },
          {
            value: "order_unit_value",
            text: "Unit price",
            editable: true,

            width: 100,
            sequence: 8,
          },
          {
            value: "",
            text: "Code",
            editable: true,
            width: 100,
            sequence: 9,
          },
          {
            value: "",
            text: "Net total(EUR)",
            editable: true,
            width: 100,
            sequence: 10,
          },
        ],
      },
      {
        dataGridUID: "codeInvoice",
        url: "/dt/sales/custom/?ids=" + this.props.id,
        paging: false,
        row_selection: false,
        bind_on_load: true,
        columns: [
          {
            value: "id",
            text: "ID",
            show: false,
            row_key: true,
            sequence: 1,
          },
          {
            value: "code",
            text: "code",
            width: 100,
            sequence: 2,
          },
          {
            value: "intrastat",
            text: "Intrastat",
            width: 100,
            sequence: 3,
          },
          {
            value: "country_of_origin",
            text: "Origin",
            width: 100,
            sequence: 4,
          },
          {
            value: "weight",
            text: "Weight",
            width: 100,
            sequence: 5,
          },
          {
            value: "value",
            text: "Value",
            width: 100,
            sequence: 6,
          },
        ],
      },
    ],
  };
  componentDidMount = () => {
    this.getInvoiceData();
  };
  getInvoiceData = () => {
    axios.get("/dt/sales/credit_invoice/?ids=" + this.props.invoice_id).then((response) => {
      var data = response.data.data;
      this.setState({
        invoice_data: data,
      });
      console.log(this.state.language, "lllllllll");
    });
  };

  render() {
    return (
      <>
        <Card style={{ textAlign: "center", alignContent: "center" }}>
          <h2 style={{ marginTop: 10 }}>
            <b>Credit note</b>
          </h2>
          <Card.Grid style={{ width: "33%", marginLeft: 5, textAlign: "center", minHeight: 450 }}>
            <b>{this.state.invoice_data.customer__name}</b>
            <p>{this.state.invoice_data.country__name}</p>
            <p>{this.state.invoice_data.customer__name}</p>
            <p>{this.state.invoice_data.customer__name}</p>
            <p>{this.state.invoice_data.customer__name}</p>
            <p>{this.state.invoice_data.customer__name}</p>
            <p>{this.state.invoice_data.customer__name}</p>
            <p>{this.state.invoice_data.customer__name}</p>
            <p>{this.state.invoice_data.customer__name}</p>
            <p>{this.state.invoice_data.customer__name}</p>
          </Card.Grid>
          <Card.Grid style={{ width: "33%", textAlign: "center", minHeight: 450 }}>
            <h3>
              <b>Credit note</b>
            </h3>
            <p>{this.state.invoice_data.customer__name}</p>
            <p>{this.state.invoice_data.country__name}</p>
            <p>{this.state.invoice_data.customer__name}</p>
            <p>{this.state.invoice_data.customer__name}</p>
            <p>{this.state.invoice_data.customer__name}</p>
            <p>{this.state.invoice_data.customer__name}</p>
            <p>{this.state.invoice_data.customer__name}</p>
            <p>{this.state.invoice_data.customer__name}</p>
            <p>{this.state.invoice_data.customer__name}</p>
            <p>{this.state.invoice_data.customer__name}</p>
          </Card.Grid>
          <Card.Grid style={{ width: "33%", textAlign: "center", minHeight: 450 }}>
            <p>
              <span style={{ fontWeight: 500 }}>Credit note date</span> / Credit note date : {this.state.invoice_data.customer__name}
            </p>
            <p>
              <span style={{ fontWeight: 500 }}>Due date</span> / Due date : {this.state.invoice_data.customer__name}
            </p>
            <p>
              <span style={{ fontWeight: 500 }}>Shipment date</span> / {null} : {this.state.invoice_data.customer__name}
            </p>
          </Card.Grid>
        </Card>
        <Row style={{ marginTop: 10 }}>
          <Col span={18}>
            {" "}
            <DataGridViewer
              schema={this.generateInvoicePreviewSchema.listing[0]}
              onRowSelectionChange={this.scheduleSelectionChange}
              ref={(node) => {
                this.orderInvoiceGrid = node;
              }}
            ></DataGridViewer>
          </Col>
          <Col span={6}>
            {" "}
            <Card style={{ minHeight: 250, backgroundColor: "#fbfbfb" }}>
              <Row>
                <Col span={10}>
                  <p>
                    <b>Net Total (EUR)</b>
                  </p>
                </Col>
                <Col span={1}>
                  <p>:</p>
                </Col>
                <Col>
                  <p></p>
                </Col>
              </Row>
              <Row>
                <Col span={10}>
                  <p>
                    {/* <Form.Item name="vat_per"> */}
                    <p>
                      <b>VAT per (%)</b>
                      {/* <Input
                          style={{ width: 50, marginLeft: 20 }}
                          onChange={(e) => {
                            this.setState({ vat: e.target.value });
                          }}
                        /> */}
                    </p>
                    {/* </Form.Item> */}
                  </p>
                </Col>
                <Col span={1}>
                  <p>:</p>
                </Col>
                <Col>
                  {" "}
                  <p></p>
                </Col>
              </Row>
              <Row>
                <Col span={10}>
                  <p>
                    <b>Amount</b>
                  </p>
                </Col>
                <Col span={1}>
                  <p>:</p>
                </Col>
                <Col>
                  <p></p>
                </Col>
              </Row>
            </Card>
          </Col>
        </Row>

        <Button type="primary" className="gip-model-footer" htmlType="submit" onClick={this.props.onCancel}>
          Save & Close
        </Button>
        <Button type="primary" className="gip-model-footer" onClick={this.submitResponse}>
          Save & Print
        </Button>
      </>
    );
  }
}
export default generateInvoicePreview;

generateInvoicePreview.getInitialProps = async (context) => {
  return { invoice_id: context.query.invoice_id ?? "0", isModal: true };
};
