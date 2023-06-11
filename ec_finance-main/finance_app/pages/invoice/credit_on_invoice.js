import { PlusCircleTwoTone } from "@ant-design/icons";
import { Button, Card, Col, DatePicker, Form, Input, Row } from "antd";
import axios from "axios";
import moment from "moment";
import React, { Component } from "react";
import { showMessage } from "../../common/Util";
import AppModal from "../../components/AppModal";
import DataGridViewer from "../../components/DataGridViewer";
import SearchInput from "../../components/SelectInput";
class creditInvocie extends Component {
  constructor(props) {
    super(props);
  }
  formRef = React.createRef();
  state = { invoice_ids: this.props.id, visible: true, row: [], language: null };
  creditInvoiceSchema = {
    listing: [
      {
        dataGridUID: "creditInvoice",
        url: "/dt/sales/order_lines/?ids=" + this.props.id,
        row_selection: false,
        bind_on_load: true,
        gridViewer:true,
        columns: [
          {
            value: "id",
            text: "ID",
            show: false,
            row_key: true,
            sequence: 1,
          },
          {
            value: "detail",
            text: "Detail",
            editable: true,
            width: 100,
            sequence: 2,
            required: true,
          },
          {
            value: "purchase_ref",
            text: "Purchase reference",
            editable: true,
            width: 100,
            sequence: 3,
            required: true,
          },
          {
            value: "project_ref",
            text: "Project reference",
            editable: true,
            width: 100,
            sequence: 4,
            required: true,
          },
          {
            value: "article_ref",
            text: "Article reference",
            editable: true,
            width: 100,
            sequence: 5,
            required: true,
          },
          {
            value: "order_number",
            text: "Order no.",
            editable: true,
            width: 100,
            sequence: 6,
            required: true,
          },
          {
            value: "quantity",
            text: "Quantity",
            editable: true,
            width: 100,
            sequence: 7,
            required: true,
            render: (text, record) => {
              this.setState({ qty: record.quantity + record.id });
              return <>{record.quantity}</>;
            },
          },
          {
            value: "order_unit_value",
            text: "Unit price",
            editable: true,
            required: true,
            width: 100,
            sequence: 8,
            render: (text, record) => {
              this.setState({ qty: record.order_unit_value + record.id });
              return <>{record.order_unit_value}</>;
            },
          },
          {
            value: "code",
            text: "Code",
            width: 100,
            sequence: 9,
          },
          {
            value: "net_total",
            text: "Net total(EUR)",
            width: 100,
            sequence: 10,
            render: (text, record) => {
              return <>{parseFloat(record.order_unit_value * record.quantity).toFixed(2)}</>;
            },
          },
        ],
      },
      {
        dataGridUID: "codeInvoice",
        url: "/dt/sales/custom/?ids=" + this.props.id,
        paging: false,
        row_selection: false,
        bind_on_load: true,
        gridViewer:true,
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
            render: (text, record) => {
              this.setState({ customId: record.value + record.id });
              return <>{text}</>;
            },
          },
        ],
      },
    ],
  };
  componentDidMount = () => {
    this.getInvoiceData();
    this.timerID = setTimeout(
      () => {
        this.creditInvoiceNetTotal();
        this.invoiceCustomTotal();
      },

      500
    );
  };
  componentDidUpdate = (preProps, preState) => {
    if (preState.qty != this.state.qty) {
      this.creditInvoiceNetTotal();
    }
    if (preState.transport_cost != this.state.transport_cost) {
      this.setState({ net_total: this.state.net_total - this.state.transport_cost });
    }
    if (preState.customId != this.state.customId) {
      this.invoiceCustomTotal();
    }
  };
  componentWillUnmount() {
    clearTimeout(this.timerID);
  }
  getInvoiceData = () => {
    axios.get("/dt/sales/credit_invoice/?ids=" + this.props.id).then((response) => {
      var data = response.data.data;
      this.setState({
        invoice_number: data.invoice_number,
        customer_name: data.customer__name,
        country_name: data.country__name,
        invoice_city: data.invoice_city,
        language: data.customer__invoice_lang__name,
        postal_code: data.postal_code,
        street_address1: data.street_address1,
        street_address2: data.street_address2,
        vat_no: data.customer__vat_no,
        state: data.invoice_address__state,
        credit_note_date: data.invoice_created_on,
        delivery_date: data.delivery_date,
        invoice_due_date: data.invoice_due_date,
        hand_company: data.hand_company__name,
        hand_str1: data.address_customer__street_address1,
        hand_str2: data.address_customer__street_address2,
        hand_city: data.address_customer__city,
        hand_zip: data.address_customer__postal_code,
        hand_state: data.address_customer__state,
        hand_country: data.address_customer__country,
        hand_fax: data.address_customer__fax,
        hand_vat: data.hand_company__vat_no,
        hand_tel: data.address_customer__phone,
        // custom_weight: data.weight,
        // custom_total: data.custom_value,
        invoice_value: data.invoice_value,
        vat_percentage: data.vat_percentage,
        transport_cost: data.transport_cost,
      });
    });
  };

  creditInvoiceNetTotal() {
    let net_total = 0.0;
    let data = this.OrderLineGridViewer.getDataSource();
    for (var value in data) {
      net_total += data[value].order_unit_value * data[value].quantity;
    }
    let total_amount = parseFloat(net_total / 100) * parseFloat(this.state.vat_percentage + 100);
    let vat_value = total_amount - net_total;
    this.setState({ net_total: net_total + this.state.transport_cost, vat_value: vat_value, total_amount: total_amount });
    this.setState({ vat_value: vat_value });
  }
  invoiceCustomTotal() {
    var data = this.customGridViewer.getDataSource();
    let custom_total = 0;
    let custom_weight = 0;
    for (var value in data) {
      custom_weight += parseFloat(data[value].weight);
      custom_total += parseFloat(data[value].value);
    }
    this.setState({ custom_weight: custom_weight, custom_total: custom_total });
  }
  onFinish = (values) => {
    var order_line = this.OrderLineGridViewer.getDataSource();
    var custom_line = this.customGridViewer.getDataSource();
    var data = {
      data: values,
      order_line: order_line,
      custom_line: custom_line,
      invoice_id: this.state.invoice_ids,
    };
    axios.post("/dt/sales/invoice/generate_credit_on_invoice/", data).then((response) => {
      if (response.data.code == 0) {
        showMessage(response.data.message, "", "error");
      } else {
        showMessage(response.data.message, "", "success");
        window.parent.postMessage(
          JSON.stringify({
            action: "generate_modal",
          })
        );
      }
    });
  };
  AddLine = () => {
    var rows = this.OrderLineGridViewer.getDataSource();
    if (rows.length > 0) {
      let newRow = [{ id: null, ord_trp_value: null, invoice_amount: null, order_number: null, order_unit_value: null, quantity: null }];
      let row = rows.concat(newRow);
      this.OrderLineGridViewer.setDataSource(row);
    }
  };
  generateInvoicePreview = () => {
    this.appModal.show({
      title: "Generate invoice preview",
      url: "/invoice/generate_invoice_preview/?invoice_id=" + this.props.id,
    });
  };
  creditOnValueChange = (values) => {
    // this.setState({ net_total: this.state.net_total - values.transport_cost });
    // let net_total = values.net_total - values.transport_cost;
    let total_amount = (values.net_total / 100) * (values.vat_percentage + 100);
    this.formRef.current.setFieldsValue({
      // net_total: values.net_total,
      // vat_value: total_amount - net_total,
      total_amount: parseFloat(total_amount).toFixed(3),
    });
  };
  onModelClose = () => {
    this.dataForm.refreshTable(this.state.status);
  };
  render() {
    return (
      <>
        <Form
          key={this.state.formKey}
          onFinish={this.onFinish}
          onValuesChange={(_, allFields) => {
            this.creditOnValueChange(allFields);
          }}
          ref={this.formRef}
          fields={[
            {
              name: ["language"],
              value: this.state.language,
            },
            {
              name: ["transport_cost"],
              value: parseFloat(this.state.transport_cost).toFixed(2),
            },
            {
              name: ["vat_percentage"],
              value: parseFloat(this.state.vat_percentage).toFixed(2),
            },
            {
              name: ["custom_weight"],
              value: parseFloat(this.state.custom_weight).toFixed(2),
            },
            {
              name: ["custom_total"],
              value: parseFloat(this.state.custom_total).toFixed(2),
            },
            {
              name: ["remark"],
              value: this.state.remark,
            },
            {
              name: ["invoice_due_date"],
              value: this.state.invoice_due_date ? moment(this.state.invoice_due_date) : undefined,
            },
            {
              name: ["credit_note_date"],
              value: this.state.credit_note_date ? moment(this.state.credit_note_date) : undefined,
            },
            {
              name: ["delivery_date"],
              value: this.state.delivery_date ? moment(this.state.delivery_date) : undefined,
            },
            { name: ["total_amount"], value: parseFloat(this.state.total_amount).toFixed(3) },
            { name: ["net_total"], value: parseFloat(this.state.net_total).toFixed(3) },
            { name: ["vat_value"], value: parseFloat(this.state.vat_value).toFixed(3) },
          ]}
        >
          <Col align="center">
            <h2>
              <b>Credit note</b>
            </h2>
          </Col>
          <Col align="center">
            <h4>Correction on - {this.state.invoice_number} </h4>
          </Col>
          <Col align="right">
            <h4>Credit note number :[SQL_INVOICENR] </h4>
          </Col>
          <Row gutter={24}>
            <Col span={8}>
              <Card className="credit-card">
                <Row>
                  <Col span={7}>
                    <p>Handling company</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={16}>
                    <p>{this.state.hand_company}</p>
                  </Col>
                </Row>
                <Row>
                  <Col span={7}>
                    <p>Hand. str 1</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={16}>
                    <p>{this.state.hand_str1}</p>
                  </Col>
                </Row>
                <Row>
                  <Col span={7}>
                    <p>Hand. str 2</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={16}>
                    <p>{this.state.hand_str2}</p>
                  </Col>
                </Row>
                <Row>
                  <Col span={7}>
                    <p>Hand. city</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={16}>
                    <p>{this.state.hand_city}</p>
                  </Col>
                </Row>
                <Row>
                  <Col span={7}>
                    <p>Hand zip</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={16}>
                    <p>{this.state.hand_zip}</p>
                  </Col>
                </Row>
                <Row>
                  <Col span={7}>
                    <p>Hand. State </p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={16}>
                    <p>{this.state.hand_state}</p>
                  </Col>
                </Row>
                <Row>
                  <Col span={7}>
                    <p>Hand. country </p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={16}>
                    <p>{this.state.hand_country}</p>
                  </Col>
                </Row>
                <Row>
                  <Col span={7}>
                    <p>Hand. fax</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={16}>
                    <p>{this.state.hand_fax}</p>
                  </Col>
                </Row>
                <Row>
                  <Col span={7}>
                    <p>Hand tel.</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={16}>
                    <p>{this.state.hand_tel}</p>
                  </Col>
                </Row>
                <Row>
                  <Col span={7}>
                    <p>Hand VAT</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={16}>
                    <p>{this.state.hand_vat}</p>
                  </Col>
                </Row>
                <Row>
                  <Col span={7}>
                    <p>Hand trade reg. no </p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={16}>
                    <p></p>
                  </Col>
                </Row>
                <Row>
                  <Col span={7}>
                    <p>Hand. national no.</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={16}>
                    <p></p>
                  </Col>
                </Row>
                <Row>
                  <Col span={7}>
                    <p>Hand IBAN</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={16}>
                    <p></p>
                  </Col>
                </Row>
                <Row>
                  <Col span={7}>
                    <p>Hand BIC code</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={16}>
                    <p></p>
                  </Col>
                </Row>
              </Card>
            </Col>
            <Col span={8}>
              <Card className="credit-card">
                <p align="center">
                  <b>Credit note to </b>
                </p>
                <Row>
                  <Col span={6}>
                    <p>Customer name</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={6}>
                    <p>{this.state.customer_name}</p>
                  </Col>
                </Row>
                <Row>
                  <Col span={6}>
                    <p>Contact person</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={6}>
                    <p></p>
                  </Col>
                </Row>
                <Row>
                  <Col span={6}>
                    <p>Invoice str1</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={6}>
                    <p>{this.state.street_address1}</p>
                  </Col>
                </Row>
                <Row>
                  <Col span={6}>
                    <p>Invoice str2</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={6}>
                    <p>{this.state.street_address2}</p>
                  </Col>
                </Row>
                <Row>
                  <Col span={6}>
                    <p>Inoive city</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={6}>
                    <p>{this.state.invoice_city}</p>
                  </Col>
                </Row>
                <Row>
                  <Col span={6}>
                    <p>Inoive zip</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={6}>
                    <p>{this.state.postal_code}</p>
                  </Col>
                </Row>
                <Row>
                  <Col span={6}>
                    <p>Invoice state</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={6}>
                    <p>{this.state.state}</p>
                  </Col>
                </Row>
                <Row>
                  <Col span={6}>
                    <p>Invoice country</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={6}>
                    <p>{this.state.country_name}</p>
                  </Col>
                </Row>
                <Row>
                  <Col span={6}>
                    <p>Inoive fax</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={6}>
                    <p>{this.state.invoice_fax}</p>
                  </Col>
                </Row>
                <Row>
                  <Col span={6}>
                    <p>VAT customer</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={6}>
                    <p></p>
                  </Col>
                </Row>
                <Row>
                  <Col span={6}>
                    <p>Language</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={6}>
                    <p>
                      <Form.Item name="language">
                        <SearchInput
                          className="credit-m-bottom"
                          style={{ width: 100 }}
                          value={this.state.language}
                          fieldProps={{ mode: "single", datasource: { query: "/dt/base/choice_lookups/language/" } }}
                          handleChange={(value) => {
                            this.setState({ language: value });
                          }}
                        ></SearchInput>
                      </Form.Item>
                    </p>
                  </Col>
                </Row>
              </Card>
            </Col>
            <Col span={8}>
              <Card className="credit-card">
                <Row>
                  <Col align="right">
                    <Form.Item name="credit_note_date" label="Credit note date">
                      <DatePicker
                        className="date-picker-w"
                        onChange={(e) => {
                          if (e != null) {
                            this.setState({ credit_note_date: moment(e._d).format("YYYY-MM-DD ") });
                          }
                        }}
                      />
                    </Form.Item>
                    <Form.Item name="invoice_due_date" label="Due date">
                      <DatePicker
                        className="date-picker-w"
                        format="YYYY-MM-DD "
                        defaultValue={moment(this.state.invoice_due_date)}
                        onChange={(e) => {
                          if (e != null) {
                            this.setState({ invoice_due_date: moment(e._d).format("YYYY-MM-DD ") });
                          }
                        }}
                      />
                    </Form.Item>
                    <Form.Item name="delivery_date" label="Delivery date">
                      <DatePicker
                        className="date-picker-w"
                        onChange={(e) => {
                          if (e != null) {
                            this.setState({ delivery_date: moment(e._d).format("YYYY-MM-DD ") });
                          }
                        }}
                      />
                    </Form.Item>
                  </Col>
                </Row>
              </Card>
            </Col>
          </Row>
          <Button style={{ backgroundColor: "#eeefef" }} className="credit-top-bottom" onClick={this.AddLine}>
            <PlusCircleTwoTone />
            Add another line
          </Button>
          <DataGridViewer
            schema={this.creditInvoiceSchema.listing[0]}
            onRowSelectionChange={this.scheduleSelectionChange}
            ref={(node) => {
              this.OrderLineGridViewer = node;
            }}
          ></DataGridViewer>
          <Row gutter={24}>
            <Col span={8}>
              <Card style={{ height: "auto" }}>
                <Row>
                  <Col span={6}>
                    <p>Deliver to</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={17}>
                    <p></p>
                  </Col>
                </Row>
                <Row>
                  <Col span={6}>
                    <p>Customer name</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={17}>
                    <p></p>
                  </Col>
                </Row>
                <Row>
                  <Col span={6}>
                    <p>Contact person</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={17}>
                    <p></p>
                  </Col>
                </Row>
                <Row>
                  <Col span={6}>
                    <p>Address name</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={17}>
                    <p></p>
                  </Col>
                </Row>
                <Row>
                  <Col span={6}>
                    <p>Delivery strt1</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={17}>
                    <p></p>
                  </Col>
                </Row>
                <Row>
                  <Col span={6}>
                    <p>Delivery strt2</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={17}>
                    <p></p>
                  </Col>
                </Row>
                <Row>
                  <Col span={6}>
                    <p>Delivery city </p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={17}>
                    <p></p>
                  </Col>
                </Row>
                <Row>
                  <Col span={6}>
                    <p>Delivery zip</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={17}>
                    <p></p>
                  </Col>
                </Row>
                <Row>
                  <Col span={6}>
                    <p>Delivery country.</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={17}>
                    <p></p>
                  </Col>
                </Row>
                <Row>
                  <Col span={6}>
                    <p>Delivery state</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={17}>
                    <p></p>
                  </Col>
                </Row>
                <Row>
                  <Col span={6}>
                    <p>Delivery fax</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={17}>
                    <p></p>
                  </Col>
                </Row>
                <Row>
                  <Col span={6}>
                    <p>Delivery tel</p>
                  </Col>
                  <Col span={1}>
                    <p>:</p>
                  </Col>
                  <Col span={17}>
                    <p></p>
                  </Col>
                </Row>
              </Card>
            </Col>
            <Col span={16}>
              <Card style={{ height: 80, marginBottom: 10 }}>
                <Row gutter={24}>
                  <Col span={4} offset={1}>
                    <p>
                      <b>Transport cost</b>
                    </p>
                  </Col>
                  <Col offset={2}>
                    <Form.Item name="transport_cost">
                      <Input />
                    </Form.Item>
                  </Col>
                </Row>
              </Card>
              <Row className="credit-m-bottom" gutter={24}>
                <Col span={12} style={{ marginTop: 100 }}>
                  <p>Transport by</p>
                  <p>Shipment tracking number.</p>
                  <p>Delivery condition CPT</p>
                </Col>
                <Col span={12}>
                  <Card style={{ height: 190, backgroundColor: "#fbfbfb" }}>
                    <Row>
                      <Col span={10}>
                        <p>
                          <b>Net Total (EUR) </b>
                        </p>
                      </Col>
                      <Col span={2}>
                        <p>:</p>
                      </Col>
                      <Col span={12}>
                        <Form.Item name="net_total">
                          <Input disabled style={{ fontWeight: "bold" }} />
                        </Form.Item>
                        {/* <p>{parseFloat(this.state.net_total).toFixed(3)}</p> */}
                      </Col>
                    </Row>
                    <Row>
                      <Col span={10}>
                        <Form.Item label="VAT per (%)" name="vat_percentage" style={{ fontWeight: "bold", marginRight: 10 }}>
                          <Input />
                        </Form.Item>
                      </Col>
                      <Col span={2}>
                        <p>:</p>
                      </Col>
                      <Col span={12}>
                        <Form.Item name="vat_value">
                          <Input disabled style={{ fontWeight: "bold" }} />
                        </Form.Item>
                        {/* <p>{((this.state.net_total / 100) * (this.state.vat_percentage + 100) - this.state.net_total).toFixed(3)}</p> */}
                      </Col>
                    </Row>
                    <Row>
                      <Col span={10}>
                        <p>
                          <b>Amount</b>
                        </p>
                      </Col>
                      <Col span={2}>
                        <p>:</p>
                      </Col>
                      <Col span={12}>
                        <Form.Item name="total_amount">
                          <Input disabled style={{ fontWeight: "bold" }} />
                        </Form.Item>
                      </Col>
                    </Row>
                  </Card>
                </Col>
              </Row>

              <DataGridViewer
                schema={this.creditInvoiceSchema.listing[1]}
                onRowSelectionChange={this.scheduleSelectionChange}
                ref={(node) => {
                  this.customGridViewer = node;
                }}
              ></DataGridViewer>
            </Col>
          </Row>
          <Row gutter={24} style={{ marginBottom: 20,marginTop:10 }}>
            <Col span={14}>
              <Row gutter={24}>
                <Col>
                  <h3>
                    <b>Value for costoms</b>
                  </h3>
                </Col>
                <Col>
                  <Form.Item name="custom_weight">
                    <Input style={{ width: 100 }} />
                  </Form.Item>
                </Col>
                <Col>
                  <Form.Item name="custom_total">
                    <Input style={{ width: 100 }} />
                  </Form.Item>
                </Col>
              </Row>
            </Col>
            <Col span={10}>
              <Form.Item name="remark" label="Remark">
                <Input
                  onChange={(e) => {
                    this.setState({
                      remark: e.target.value,
                    });
                  }}
                />
              </Form.Item>
            </Col>
          </Row>
          {/* onClick={this.generateInvoicePreview} */}
          <Row style={{ marginTop: 10, float: "right" }}>
            <Button htmlType="submit" type="primary">
              Generate preview
            </Button>
          </Row>
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
creditInvocie.getInitialProps = async (context) => {
  return { id: context.query.ids ?? "0", isModal: true };
};
export default creditInvocie;
