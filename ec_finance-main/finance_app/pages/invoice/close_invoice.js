import { Button, Card, Col, DatePicker, Form, Input, Modal, Row } from "antd";
import axios from "axios";
import moment from "moment";
import React, { Component } from "react";
import shortid from "shortid";
import { showMessage } from "../../common/Util";
import DataGridViewer from "../../components/DataGridViewer";
import SearchInput from "../../components/SelectInput";
const { confirm } = Modal;
class closeInvoice extends Component {
  constructor(props) {
    super(props);
  }
  user_id = this.props.session.user.data.user_id;
  state = {
    visible: false,
    invoice_ids: this.props.id,
    payment_mode: "bank",
    payment_deference_type: "INVCLOSED",
    invoice_number_payment_type: {},
    paid_on: moment().format("YYYY-MM-DD HH:mm:ss"),
  };
  closeInvoiceSchema = {
    listing: [
      {
        dataGridUID: "closedInvoice",
        url: "/dt/sales/close_invoice/?ids=" + this.state.invoice_ids,
        paging: true,
        row_selection: false,
        bind_on_load: true,
        // onRow:(record, index) => {
        //   return {
        //       onClick: (e) => {
        //           return {
        //               style: {
        //                 background: "#4287f5",
        //               },
        //             };
        //       },
        //     }
        //   },
        columns: [
          {
            value: "id",
            text: "ID",
            show: false,
            row_key: true,
            sequence: 2,
          },
          {
            value: "invoice_number",
            text: "Invoice number",
            sortable: true,
            width: 100,
            sequence: 3,
            // render: (text, record) => {
            //   return {
            //     props:{
            //       style: {
            //         background: "#4287f5",
            //       },
            //       },
            //       children:<>{text}</>
            //   };
            // },
          },
          {
            value: "invoice_created_on",
            text: "Invoice date",
            sortable: true,
            width: 100,
            sequence: 4,
            // render(text, record) {
            //   return {
            //     props: {
            //       style: { background:"#4287f5" }
            //     },
            //     children: <div>{text}</div>
            //   };
            // }
          },
          {
            value: "invoice_due_date",
            text: "Inoive due date",
            sortable: true,
            width: 100,
            sequence: 5,
            // render(text, record) {
            //   return {
            //     props: {
            //       style: { background:"#4287f5" }
            //     },
            //     children: <div>{text}</div>
            //   };
            // }
          },
          {
            value: "currency_invoice_value",
            text: "Invoice amount",
            sortable: true,
            width: 100,
            sequence: 6,
            // render(text, record) {
            //   return {
            //     props: {
            //       style: { background:"#4287f5" }
            //     },
            //     children: <div>{text}</div>
            //   };
            // }
          },
          {
            value: "cust_amount_paid",
            text: "Total paid amount",
            sortable: true,
            width: 100,
            sequence: 7,
          },
          {
            value: "outstanding",
            text: "Outstanding",
            sortable: true,
            width: 100,
            sequence: 8,
          },
          {
            value: "new_payment",
            text: "New payment",
            sortable: true,
            editable: true,
            width: 100,
            sequence: 9,
            render: (text, record) => {
              if (parseFloat(record.new_payment).toFixed(3) < 0) {
                confirm({
                  title: "Are you sure to continue with negative amount ?",
                  content: <></>,
                  cancelText: "No, Cancel",
                  okText: "Yes, Continue ",
                  onOk: () => {
                    Modal.destroyAll();
                  },
                  onCancel: () => {
                    Modal.destroyAll();
                    var rows = this.dataGridViewer.getDataSource();
                    var foundIndex = rows.findIndex((x) => x.id === record.id);
                    rows[foundIndex] = { ...rows[foundIndex], new_payment: 0.0, difference: -Math.abs(record.new_payment) };
                    let result = [];
                    for (var row in rows) {
                      result.push(rows[row]);
                    }
                    this.dataGridViewer.setDataSource(result);
                  },
                });
              }
              return <>{parseFloat(record.new_payment).toFixed(3)}</>;
            },
          },
          {
            value: "difference",
            text: "Difference",
            sortable: true,
            width: 100,
            sequence: 10,
            render: (text, record) => {
              return <>{record.difference == 0 ? (parseFloat(record.outstanding) - parseFloat(record.new_payment)).toFixed(3) : record.difference}</>;
            },
          },
          {
            value: "payment_deference_type",
            text: "Payment Difference Type",
            sortable: true,
            width: 150,
            sequence: 11,
            render: (text, record) => {
              let type = "INVCLOSED";
              if (parseFloat(record.new_payment).toFixed(3) > parseFloat(record.outstanding).toFixed(3)) {
                type = "OverPaid";
              } else if (parseFloat(record.outstanding).toFixed(3) > parseFloat(record.new_payment).toFixed(3)) {
                type = "OutStanding";
                this.setState({ payment_deference_type: "OutStanding" });
              }
              return (
                <div>
                  <SearchInput
                    key={shortid.generate()}
                    value={type}
                    fieldProps={{ mode: "single", datasource: { query: "/dt/base/choice_lookups/payment_difference_types/" } }}
                    style={{ width: 200 }}
                    handleChange={(value) => {
                      let invoice_number = record.invoice_number;
                      this.setState({ payment_deference_type: value, invoice_number_payment_type: { [invoice_number]: value } });
                    }}
                  ></SearchInput>
                </div>
              );
            },
          },
        ],
      },
    ],
  };
  componentDidMount = () => {
    this.getData();
  };
  getData = () => {
    axios.get("/dt/sales/close_invoice/?ids=" + this.state.invoice_ids).then((response) => {
      var rows = response.data.data;
      let total_amount = 0;

      let amount_paid = 0;
      for (var row in rows) {
        total_amount = parseFloat(total_amount) + parseFloat(rows[row].currency_invoice_value);
        amount_paid = parseFloat(rows[row].cust_amount_paid);
      }
      let total_payment_amount = total_amount - amount_paid;
      this.setState({
        customer: rows[0].customer_name,
        currency: rows[0].currency_name,
        rate: rows[0].curr_rate,
        total_payment_amount: total_payment_amount.toString(),
        customer_id: rows[0].customer_id,
        ec_customer_id: rows[0].ec_customer_id,
        status: rows[0].status__code,
      });
    });
  };
  CloseInvoice = (values) => {
    var row_values = [];
    var data = this.dataGridViewer.getDataSource();
    let new_payment = 0;
    let new_deference = 0;

    for (let i in data) {
      let invoice_number_payment_type = this.state.invoice_number_payment_type;
      if (invoice_number_payment_type[data[i].invoice_number] == undefined) {
        invoice_number_payment_type[data[i].invoice_number] = this.state.payment_deference_type;
      }
      row_values.push({
        invoice_number: data[i].invoice_number,
        invoice_id: data[i].id,
        ec_invoice_id: data[i].ec_invoice_id,
        new_payment: parseFloat(data[i].new_payment),
        outstanding: data[i].outstanding,
        deference: parseFloat(data[i].difference),
        currency_amount: parseFloat(data[i].currency_invoice_value),
        currency_total_amount: parseFloat(data[i].currency_invoice_value),
        payment_deference_type: invoice_number_payment_type[data[i].invoice_number],
      });
      new_payment = new_payment + parseFloat(data[i].new_payment);
    }
    let formData = new FormData();
    formData.append("payment_mode", this.state.payment_mode);
    formData.append("user_id", this.user_id);
    formData.append("paid_on", this.state.paid_on);
    formData.append("total_amount", this.state.total_payment_amount);
    formData.append("row_values", JSON.stringify(row_values));
    formData.append("currency_code", this.state.currency);
    formData.append("currency_rate", this.state.rate);
    formData.append("customer_id", this.state.customer_id);
    formData.append("ec_customer_id", this.state.ec_customer_id);
    row_values.push({ customer_id: this.state.customer_id });

    var total_payment_amount = this.state.total_payment_amount;

    if (total_payment_amount != new_payment && total_payment_amount >= 0) {
      showMessage("New amount total does not match with total payment", "", "error");
      return;
    } else if (total_payment_amount != new_payment && total_payment_amount < 0) {
      if (total_payment_amount != new_deference) {
        showMessage("New amount total does not match with total payment", "", "error");
        return;
      }
    }
    axios.post("/dt/sales/submit_close_invoice/", formData).then((response) => {
      if ((response.data.code = 1)) {
        showMessage(response.data.message, "", "success");
        window.parent.postMessage(
          JSON.stringify({
            action: "close_modal",
          })
        );
      } else {
        showMessage(response.data.message, "", "error");
      }
    });
  };
  render() {
    return (
      <>
        <Form initialValues={{ remember: true }} labelCol={{ span: 4 }} wrapperCol={{ span: 14 }} layout="horizontal">
          <Card style={{ height: 250, width: 500, marginBottom: 10 }}>
            <Row>
              <Col span={7}>
                <p>Customer</p>
              </Col>
              <Col span={2}>
                <p>:</p>
              </Col>
              <Col span={15}>
                <p>{this.state.customer}</p>
              </Col>
            </Row>
            <Row>
              <Col span={7}>
                <p>Currency</p>
              </Col>
              <Col span={2}>
                <p>:</p>
              </Col>
              <Col span={15}>
                <p>{this.state.currency}</p>
              </Col>
            </Row>
            <Row>
              <Col span={7}>
                <p>Exchange Rate</p>
              </Col>
              <Col span={2}>
                <p>:</p>
              </Col>
              <Col span={15}>
                <p>{this.state.rate}</p>
              </Col>
            </Row>
            <Row style={{ marginBottom: -20 }}>
              <Col span={7}>
                <p>Total amount</p>
              </Col>
              <Col span={2}>
                <p>:</p>
              </Col>
              <Col span={15}>
                <p>
                  <Form.Item>
                    <Input
                      value={this.state.total_payment_amount}
                      style={{ width: 200 }}
                      min="0"
                      max="11"
                      step="0.001"
                      onChange={(e) => {
                        this.setState({ total_payment_amount: e.target.value });
                      }}
                    />
                  </Form.Item>
                </p>
              </Col>
            </Row>
            <Row style={{ marginBottom: -20 }}>
              <Col span={7}>
                <p>Paid on</p>
              </Col>
              <Col span={2}>
                <p>:</p>
              </Col>
              <Col span={15}>
                <p>
                  <Form.Item name="paid_on">
                    <DatePicker
                      defaultValue={moment()}
                      style={{ width: 200 }}
                      format="YYYY-MM-DD"
                      onChange={(e) => {
                        if (e != null) {
                          this.setState({ paid_on: moment(e._d).format("YYYY-MM-DD") });
                        }
                      }}
                    />
                  </Form.Item>
                </p>
              </Col>
            </Row>
            <Row>
              <Col span={7}>
                <p>Payment mode</p>
              </Col>
              <Col span={2}>
                <p>:</p>
              </Col>
              <Col span={15}>
                <p>
                  <Form.Item>
                    <SearchInput
                      value={this.state.payment_mode}
                      fieldProps={{ mode: "single", datasource: { query: "/dt/base/choice_lookups/payments_mode/" } }}
                      style={{ width: 200 }}
                      handleChange={(value) => {
                        this.setState({ payment_mode: value });
                      }}
                    ></SearchInput>
                  </Form.Item>
                </p>
              </Col>
            </Row>
          </Card>
          <div>
            <DataGridViewer
              style={{ marginLeft: 300 }}
              schema={this.closeInvoiceSchema.listing[0]}
              ref={(node) => {
                this.dataGridViewer = node;
              }}
            ></DataGridViewer>
          </div>
          {/* onClick={this.CloseInvoice} */}
          <Button style={{ float: "left" }} type="primary" htmlType="submit" onClick={this.CloseInvoice}>
            Submit
          </Button>
        </Form>
      </>
    );
  }
}
closeInvoice.getInitialProps = async (context) => {
  return { id: context.query.ids ?? "0", isModal: true };
};
export default closeInvoice;
