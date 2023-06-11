import { Button, Card, Col, DatePicker, Form, Input, InputNumber, Row,Divider } from "antd";
import axios from "axios";
import moment from "moment";
import React, { Component } from "react";
import { showMessage } from "../../common/Util";
import AppModal from "../../components/AppModal";
import DataGridViewer from "../../components/DataGridViewer";
class editInvoice extends Component {
  formRef = React.createRef();
  user_id = this.props.session.user.data.user_id;
  state = { invoice_ids: this.props.id, applyDisabled: true, quantity: 0 };
  editInvoiceSchema = {
    listing: [
      {
        dataGridUID: "orderLines",
        url: "/dt/sales/order_lines/?ids=" + this.state.invoice_ids,
        paging: true,
        row_selection: false,
        bind_on_load: true,
        columns: [
          {
            value: "id",
            text: "ID",
            show: true,
            row_key: true,
            sequence: 1,
            width: 60,
            editable: true,
          },
          {
            value: "order_number",
            text: "Order nr",
            sortable: true,
            width: 100,
            sequence: 2,
            editable: true,
          },
          {
            value: "",
            text: "PCB name",
            sortable: true,
            width: 100,
            sequence: 3,
          },
          {
            value: "purchase_ref",
            text: "Purchase ref",
            sortable: true,
            width: 100,
            sequence: 4,
            editable: true,
            required: true,
          },
          {
            value: "project_ref",
            text: "Project ref",
            sortable: true,
            width: 100,
            sequence: 5,
            editable: true,
          },
          {
            value: "article_ref",
            text: "Artical ref",
            sortable: true,
            width: 100,
            sequence: 6,
            editable: true,
          },
          {
            value: "order_unit_value",
            text: "Unit price",
            sortable: true,
            width: 100,
            sequence: 7,
            editable: true,
          },
          {
            value: "quantity",
            text: "Quantity",
            sortable: true,
            width: 100,
            sequence: 8,
            editable: true,
            required: true,
          },
          {
            value: "invoice_amount",
            text: "Net price",
            sortable: true,
            width: 100,
            sequence: 9,
            render: (text, record) => {
              return <>{(parseFloat(record.order_unit_value) * record.quantity).toFixed(3)}</>;
            },
          },
          {
            value: "ord_trp_value",
            text: "Transport",
            sortable: true,
            width: 100,
            sequence: 10,
            render: (text, record) => {
              this.setState((state, props) => ({ quantity: state + record.quantity + record.id }));
              return <>{text}</>;
            },
          },
          {
            sortable: true,
            width: 50,
            sequence: 10,
          },
        ],
      },
      {
        dataGridUID: "Custom",
        url: "/dt/sales/custom/?ids=" + this.state.invoice_ids,
        paging: true,
        row_selection: false,
        bind_on_load: true,
        columns: [
          {
            value: "id",
            text: "ID",
            show: false,
            row_key: true,
            sequence: 1,
            editable: true,
          },
          {
            value: "",
            text: "Invoice custom id",
            sortable: true,
            show: false,
            width: 150,
            sequence: 2,
            editable: true,
          },
          {
            value: "code",
            text: "Code",
            sortable: true,
            width: 80,
            sequence: 3,
            editable: true,
          },
          {
            value: "harm_code",
            text: "Harm code",
            sortable: true,
            width: 110,
            sequence: 4,
            editable: true,
          },
          {
            value: "intrastat",
            text: "Intrastat",
            sortable: true,
            width: 100,
            sequence: 5,
            editable: true,
          },
          {
            value: "country_of_origin",
            text: "Country of origin",
            sortable: true,
            width: 150,
            sequence: 6,
            editable: true,
          },
          {
            value: "weight",
            text: "Weight",
            sortable: true,
            width: 130,
            sequence: 7,
            editable: true,
          },
          {
            value: "value",
            text: "Value",
            sortable: true,
            width: 150,
            sequence: 8,
            editable: true,
          },
          {
            value: "vat_percentage",
            text: "Vat percentage",
            sortable: true,
            width: 150,
            sequence: 9,
            editable: true,
          },
        ],
      },
      {
        dataGridUID: "Discount",
        url: "/dt/sales/invoice_discount/?invoice_id=" + this.state.invoice_ids,
        paging: true,
        row_selection: true,
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
            text: "Discount code",
            sortable: true,
            width: 100,
            sequence: 2,
          },
          {
            value: "amount",
            text: "Discount amount",
            sortable: true,
            editable: true,
            width: 100,
            sequence: 3,
          },
          {
            value: "currency_amount",
            text: "Discount amount C",
            sortable: true,
            editable: true,
            width: 100,
            sequence: 4,
          },
        ],
      },
    ],
  };

  lookup = () => {
    var ec_customer_id = this.state.ec_customer_id;
    this.appModal.show({
      title: "Lookup discount: ",
      url: "/invoice/invoice_lookup/?ec_customer_id=" + ec_customer_id,
      style: { width: "90%", height: "70vh" },
    });
  };

  componentDidMount = () => {
    this.timerID = setTimeout(() => {
      this.invoiceNetTotal();
    }, 500);
  };
  UNSAFE_componentWillMount() {
    this.getInvoiceData();
  }

  componentDidUpdate = (preProps, preState) => {
    if (preState.quantity != this.state.quantity) {
      this.invoiceNetTotal();
    }
    if (preState.transport_cost != this.state.transport_cost) {
      this.setState({ net_total: this.state.net_total - this.state.transport_cost });
    }
  };

  componentWillUnmount() {
    clearTimeout(this.timerID);
  }

  invoiceNetTotal = () => {
    var orders = this.orderGridViewer.getDataSource();
    var discounts = this.discountGridViewer.getDataSource();
    let discount_total = 0.0;
    if (discounts.length > 0) {
      for (var disc in discounts) {
        discount_total += parseFloat(discounts[disc].amount);
      }
      this.setState({ discountTotal: discount_total });
    }
    let invoice_net = 0.0;
    let transport_cost = 0.0;

    for (var value in orders) {
      transport_cost += parseFloat(orders[value].ord_trp_value);
      invoice_net += parseFloat(orders[value].order_unit_value) * parseFloat(orders[value].quantity) + parseFloat(orders[value].ord_trp_value);
    }
    invoice_net = invoice_net - discount_total;
    let invoice_total = parseFloat(invoice_net / 100) * parseFloat(this.state.vat_percentage + 100);
    let vat_value = invoice_total - invoice_net;
    this.setState({
      invoice_net: invoice_net,
      vat_value: vat_value,
      invoice_total: invoice_total,
      transport_cost: transport_cost,
    });
    var customs_data = this.customsGridViewer.getDataSource();
    let custom_total = 0.0;
    let custom_weight = 0.0;
    if (customs_data.length > 0) {
      for (var value in customs_data) {
        custom_weight += parseFloat(customs_data[value].weight);
        custom_total += parseFloat(customs_data[value].value);
      }
      this.setState({ custom_weight: custom_weight, custom_total: custom_total });
    }
  };

  getInvoiceData = () => {
    axios.get("/dt/sales/edit_invoice/?ids=" + this.state.invoice_ids).then((response) => {
      var data = response.data.data;
      var invoice_number = data.invoice_number.split("/");
      let childNodes = null;
      if (data.meta_data) {
        var meta_data = this.parseXml(data.meta_data);
        childNodes = meta_data.documentElement.childNodes;
      }
      this.setState({
        ec_customer_id: data.customer__ec_customer_id,
        invoice_num_f: invoice_number[0],
        invoice_num_s: invoice_number[1],
        handling_company: data.hand_company__name,
        invoice_date: data.invoice_created_on,
        invoice_due_date: data.invoice_due_date,
        customer_name: data.customer__name,
        country_name: data.country__name,
        vat_no: data.vat_value,
        city: data.invoice_city,
        postal_code: data.postal_code,
        vat_percentage: data.vat_percentage,
        // invoice_net: data.invoice_value,
        // invoice_total: parseFloat(data.invoice_value / 100) * (data.vat_percentage + 100).toFixed(3),
        // custom_total: parseFloat(data.invoice_value).toFixed(3),
        // vat_value: data.vat_value,
        // transport_cost: data.transport_cost,
        street_no: data.invoice_address__street_no,
        invoice_number: invoice_number[0] + invoice_number[1],
        delivery_date: data.delivery_date ?? undefined,
        vat_message: childNodes && childNodes[0] != undefined ? childNodes[0].textContent : null,
        vat_message_handling: childNodes && childNodes[1] != undefined ? childNodes[1].textContent : null,
        remarks: data.remarks,
      });
    });
  };

  parseXml = (xmlStr) => {
    return new window.DOMParser().parseFromString(xmlStr, "text/xml");
  };
  onFinish = (values) => {
    var order_line = this.orderGridViewer.getDataSource();
    var custom_line = this.customsGridViewer.getDataSource();
    var discount_line = this.discountGridViewer.getDataSource();
    if (order_line.length == 0) {
      showMessage("Invoice has no order line(s).", "", "error");
      return;
    }
    values["order_line"] = order_line;
    values["custom_line"] = custom_line;
    values["discount_line"] = discount_line;
    values["invoice_id"] = this.state.invoice_ids;
    values["invoice_number"] = values.invoice_num_f + "/" + "" + values.invoice_num_s;
    axios.post("/dt/sales/invoice/edit_invoice/", values).then((response) => {
      if (response.data.code == 0) {
        showMessage(response.data.message, "", "error");
      } else {
        showMessage(response.data.message, "", "success");
        window.parent.postMessage(
          JSON.stringify({
            action: "close_modal",
          })
        );
      }
    });
  };
  editOnValueChange = (values) => {
    let invoice_total = (values.invoice_net / 100) * (values.vat + 100);
    let vat_value = (invoice_total - values.invoice_net).toFixed(3);
    this.formRef.current.setFieldsValue({
      invoice_total: invoice_total.toFixed(3),
      vat_value: vat_value,
    });
  };
  invoiceDiscount = (state) => {
    let discount_line = this.discountGridViewer.getDataSource();
    let newPrices = discount_line.filter((el) => el.code === this.state.discount_code);
    if (newPrices.length > 0 && state == "apply") {
      showMessage("This code is already used.", "", "error");
      return;
    }
    if (state == "remove") {
      var selectedRows = this.discountGridViewer.getSelectedRows();
      discount_line = discount_line.filter((el) => el.code !== selectedRows[0].code);
      this.discountGridViewer.setDataSource(discount_line);
      showMessage("Discount removed successfully.", "", "error");
      return;
    }
    var formData = {
      discount_code: this.state.discount_code,
      state: state,
    };
    axios.post("/dt/sales/invoice/invoice_discount_apply_and_remove/", formData).then((response) => {
      let rows = response.data.data;
      if (state == "apply") {
        let disc = [];
        let total_discount = [parseFloat(this.state.discountTotal)];
        for (var row in rows) {
          total_discount.push(rows[row].DiscountValue);

          disc.push({
            code: rows[row].DiscountCode,
            amount: String(rows[row].DiscountValue),
            currency_amount: String(rows[row].DiscountValue),
          });
        }
        this.setState({ discountTotal: total_discount.reduce((a, b) => a + b, 0) });
        let final = [...disc, ...discount_line];
        this.discountGridViewer.setDataSource(final);
      }
      if (response.data.code == 1) {
        showMessage(response.data.message, "", "success");
      } else {
        showMessage(response.data.message, "", "error");
      }
    });
  };
  render() {
    return (
      <>
        <Form
          key={this.state.formKey}
          onFinish={this.onFinish}
          onValuesChange={(_, allFields) => {
            this.editOnValueChange(allFields);
          }}
          ref={this.formRef}
          fields={[
            {
              name: ["invoice_num_f"],
              value: this.state.invoice_num_f,
            },
            {
              name: ["invoice_num_s"],
              value: this.state.invoice_num_s,
            },
            {
              name: ["invoice_date"],
              value: this.state.invoice_date ? moment(this.state.invoice_date) : undefined,
            },
            {
              name: ["delivery_date"],
              value: this.state.delivery_date ? moment(this.state.delivery_date) : undefined,
            },
            {
              name: ["invoice_due_date"],
              value: this.state.invoice_due_date ? moment(this.state.invoice_due_date) : undefined,
            },

            {
              name: ["transport_cost"],
              value: this.state.transport_cost ?? 0.0,
            },
            {
              name: ["vat"],
              value: this.state.vat_percentage ?? 0.0,
            },
            {
              name: ["vat_value"],
              value: parseFloat(this.state.vat_value).toFixed(2) ?? 0.0,
            },
            {
              name: ["invoice_net"],
              value: parseFloat(this.state.invoice_net).toFixed(3),
            },
            {
              name: ["reduce_vat"],
              value: this.state.amount ?? 0.0,
            },
            {
              name: ["reduce_vat_value"],
              value: this.state.reduce_vat_value ?? 0.0,
            },
            {
              name: ["invoice_total"],
              value: parseFloat(this.state.invoice_total).toFixed(2),
            },
            {
              name: ["vat_message"],
              value: this.state.vat_message,
            },
            {
              name: ["vat_message_handling"],
              value: this.state.vat_message_handling,
            },
            {
              name: ["remarks"],
              value: this.state.remarks,
            },
            {
              name: ["total_customs"],
              value: this.state.custom_total ?? 0.0,
            },
            {
              name: ["custom_weight"],
              value: this.state.custom_weight ?? 0.0,
            },
          ]}
        >
        <div className="edit-invoice-main">
          <Row gutter={24} className="edit-m-bottom">
            <Col span={12}>
              <Card style={{ height: "auto" ,minHeight:280}}>
                <Row gutter={24}>
                  <Col span={5}>
                    <p>Handling company</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={16}>
                    <Form.Item name="handling_company">
                      <p>{this.state.handling_company}</p>
                    </Form.Item>
                  </Col>
                </Row>
                <Row gutter={24}>
                  <Col span={5}>
                    <p>Invoice number</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col>
                    <Form.Item name="invoice_num_f">
                      <Input style={{ width: 130 }} />
                    </Form.Item>
                  </Col>
                  <Col>
                    <Form.Item name="invoice_num_s">
                      <Input style={{ width: 130 }} />
                    </Form.Item>
                  </Col>
                  <Col>
                    {/* onClick={() => }this.formRef.current.resetFields() */}
                    <Button style={{ backgroundColor: "#eeefef" }} className="load-btn"> Load</Button>
                  </Col>
                </Row>
                <Row>
                  <Col span={5}>
                    <p>Invoice date</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={16}>
                    <Form.Item name="invoice_date">
                      <DatePicker style={{ width: 130, marginLeft: 5 }} />
                    </Form.Item>
                  </Col>
                </Row>
                <Row>
                  <Col span={5}>
                    <p>Invoice due date</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={16}>
                    <Form.Item name="invoice_due_date">
                      <DatePicker style={{ width: 130, marginLeft: 5 }} />
                    </Form.Item>
                  </Col>
                </Row>
                <Row>
                  <Col span={5}>
                    <p>Delivery date</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={16}>
                    <Form.Item name="delivery_date">
                      <DatePicker style={{ width: 130, marginLeft: 5 }} />
                    </Form.Item>
                  </Col>
                </Row>
              </Card>
            </Col>
            <Col span={12}>
              <Card style={{ height: "auto" ,minHeight:280}}>
                <Row>
                  <Col span={6}>
                    <p>Customer name</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={17}>
                    {" "}
                    <p>{this.state.customer_name}</p>
                  </Col>
                </Row>
                <Row>
                  <Col span={6}>
                    <p>Contact name </p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={17}>
                    {" "}
                    <p></p>
                  </Col>
                </Row>
                <Row>
                  <Col span={6}>
                    <p>Street nr / name</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={17}>
                    {" "}
                    <p>{this.state.street_no} </p>
                  </Col>
                </Row>
                <Row>
                  <Col span={6}>
                    <p>Postal code / City</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={17}>
                    {" "}
                    <p>
                      {this.state.postal_code} {this.state.city}
                    </p>
                  </Col>
                </Row>
                <Row>
                  <Col span={6}>
                    <p>Country</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={17}>
                    {" "}
                    <p>{this.state.country_name}</p>
                  </Col>
                </Row>
                <Row>
                  <Col span={6}>
                    <p>VAT number</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={17}>
                    {" "}
                    <p>{this.state.vat_no}</p>
                  </Col>
                </Row>
              </Card>
            </Col>
          </Row>
          <Card style={{ height: "auto", marginBottom: 10, backgroundColor: "#fbfbfb" }}>
            <Row gutter={24}>
              <Col>
                <p>Transport</p>
                <Form.Item name="transport_cost" style={{ marginBottom: 2 }}>
                  <InputNumber style={{ width: 150 }} step={0.111} />
                </Form.Item>
              </Col>
              <Col>
                <p>Invoice net</p>
                <Form.Item name="invoice_net" style={{ marginBottom: 2 }}>
                  <InputNumber style={{ width: 150 }} step={0.111} />
                </Form.Item>
              </Col>
              <Col>
                <p>VAT %</p>
                <Form.Item name="vat" style={{ marginBottom: 2 }}>
                  <InputNumber style={{ width: 150 }} step={0.111} />
                </Form.Item>
              </Col>
              <Col>
                <p>VAT Value</p>
                <Form.Item name="vat_value" style={{ marginBottom: 2 }}>
                  <InputNumber style={{ width: 150 }} step={0.111} />
                </Form.Item>
              </Col>
              <Col>
                <p>Reduce vat %</p>
                <Form.Item name="reduce_vat" style={{ marginBottom: 2 }}>
                  <InputNumber style={{ width: 150 }} step={0.111} />
                </Form.Item>
              </Col>
              <Col>
                <p>Reduce vat Value</p>
                <Form.Item name="reduce_vat_value" style={{ marginBottom: 2 }}>
                  <InputNumber style={{ width: 150 }} step={0.111} />
                </Form.Item>
              </Col>
              <Col>
                <p>Invoice Total</p>
                <Form.Item name="invoice_total" style={{ marginBottom: 2 }}>
                  <InputNumber style={{ width: 150 }} step={0.111} />
                </Form.Item>
              </Col>
            </Row>
          </Card>
          <b>
            <h3>Order lines:</h3>
          </b>
          <DataGridViewer
            schema={this.editInvoiceSchema.listing[0]}
            ref={(node) => {
              this.orderGridViewer = node;
            }}
          ></DataGridViewer>
          <Row gutter={24} className="discount-table" >
            <Col span={12}>
              <b>
                <h3>Customs :</h3>
              </b>
              <DataGridViewer
                schema={this.editInvoiceSchema.listing[1]}
                ref={(node) => {
                  this.customsGridViewer = node;
                }}
              ></DataGridViewer>
            </Col>
            <Col span={12}>
              <b>
                <h3>Discount :</h3>
              </b>
              <DataGridViewer
                schema={this.editInvoiceSchema.listing[2]}
                ref={(node) => {
                  this.discountGridViewer = node;
                }}
              ></DataGridViewer>
            </Col>
          </Row>
          <br></br>
          <Row>
            <Col span={12}>
              <Row>
                <Form.Item name="custom_weight" label="Total Weight">
                  <InputNumber step={0.111} />
                </Form.Item>
                <Form.Item name="total_customs" style={{ marginLeft: 10 }} label="Total Customs">
                  <InputNumber step={0.111} />
                </Form.Item>
              </Row>
            </Col>
            <Col span={12}>
              <Row>
                <Form.Item name="discount_code" label="Discount Code" style={{marginLeft:10}}>
                  <Input
                    onChange={(e) => {
                      this.setState({
                        discount_code: e.target.value,
                      });
                    }}
                  />
                </Form.Item>
                <Button style={{ marginLeft: 10 }} onClick={this.lookup}>
                  Lookup
                </Button>
                <Button style={{ marginLeft: 10 }} onClick={() => this.invoiceDiscount("apply")}>
                  Apply
                </Button>
                <Button style={{ marginLeft: 10 }} onClick={() => this.invoiceDiscount("remove")}>
                  Remove
                </Button>
              </Row>
            </Col>
          </Row>
          <Row>
            <Col span={24}>
                <b>
                  <h3>Remarks</h3>
                </b>
                <Form.Item name="remarks" >
                  <Input.TextArea rows={2} style={{ width: "100%" }} />
                </Form.Item>
              </Col>
          </Row>
         <Row>
            <Col span={12}>
                <b>
                  <h3>VAT Message</h3>
                </b>
              <Form.Item name="vat_message" >
                      <Input.TextArea rows={2} style={{ width: "95%" }} />
              </Form.Item>
            </Col>
            <Col span={12}>
                <b>
                  <h3>VAT Message Handling Company Language</h3>
                </b>
              <Form.Item name="vat_message_handling" >
                      <Input.TextArea rows={2} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
          </Row>
          </div>
          <div className="add-space"></div>
           <div className="modal-foote" align="right">
            <Divider></Divider>
            <Button type="primary" onClick={this.submitResponse}>
              Save & Print
            </Button>
            <Button type="primary" style={{ marginLeft: 10 }} htmlType="submit">
              Save & Close
            </Button>
          </div>
        </Form>
        <AppModal
          callBack={this.onModelClose}
          ref={(node) => {
            this.appModal = node;
          }}
        ></AppModal>
      </>
    );
  }
}
editInvoice.getInitialProps = async (context) => {
  return { id: context.query.ids ?? "0", isModal: true };
};
export default editInvoice;
