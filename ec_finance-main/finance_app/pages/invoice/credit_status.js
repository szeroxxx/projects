import { Col, Row , Card} from "antd";
import axios from "axios";
import React, { Component } from "react";
import DataGridViewer from "../../components/DataGridViewer";
class CreditStatus extends Component {
  constructor(props) {
    super(props);
  }
  state = { data: {} };

  appSchema = {
    pageTitle: "Credit Status",
    listing: [
      {
        dataGridUID: "OutstandingInvoice",
        url: "/dt/sales/credit_status/?customer_id=" + this.props.customer_id + "&ec_customer_id=" + this.props.ec_customer_id ,
        paging: true,
        default_sort_col: "id",
        default_sort_order: "descend",
        row_selection: false,
        bind_on_load: true,
        gridViewer:true,
        columns: [
          {
            value: "id",
            text: "ID",
            sortable: true,
            sequence: 0,
            show: false,
          },
          {
            value: "invoice_number",
            text: "Invoice no.",
            sortable: true,
            width: 120,
          },
          {
            value: "invoice_created_on",
            text: "Invoice Date",
            sortable: true,
            width: 150,
          },
          {
            value: "invoice_due_date",
            text: "Invoice Due Date",
            width: 150,
            sortable: true,
            sequence: 5,
          },
          {
            value: "invoice_value",
            text: "Invoice amount",
            sortable: true,
            width: 170,
          },
          {
            value: "currency_invoice_value",
            text: "Cust Invoice amount",
            sortable: true,
            width: 170,
          },
          {
            value: "outstanding",
            text: "Outstanding",
            sortable: true,
            width: 170,
          },
          {
            value: "customer_outstanding",
            text: "Cust Outstanding",
            sortable: true,
            width: 170,
          },
          {
            value: "",
            text: "Note",
            sortable: true,
            width: 100,
          },
        ],
      },
    ],
  };
  componentDidMount = () => {
    this.getCreditStatusData();
  };
  async getCreditStatusData() {
    const res = await axios.get("/dt/sales/get_credit_status/?ec_customer_id=" + this.props.ec_customer_id);
    this.setState({
      credit_limit: res.data.data[0].CreditLimit.toFixed(2),
      customer_credit_limit: res.data.data[0].Customer_CreditLimit.toFixed(2),
      running_ord_price: res.data.data[0].RunningOrdPrice.toFixed(2),
      cust_running_ord_price: res.data.data[0].Customer_RunningOrdPrice.toFixed(2),
      open_invoices: res.data.data[0].OpenInvoices.toFixed(2),
      cust_open_invoices: res.data.data[0].Customer_OpenInvoices.toFixed(2),
      available_credit: res.data.data[0].AvailableCredit.toFixed(2),
      cust_available_credit: res.data.data[0].Customer_AvailableCredit.toFixed(2),
      payment_terms: res.data.data[0].PaymentTerms,
      currency_sym: res.data.data[0].CustomerSymbol,
    });
  }
  render() {
    return (
      <>
          <Row style={{ marginLeft: 10 }}>
            <Col span={4}>
              <h2>Amount in</h2>
            </Col>
            <Col span={4}>
              <h2>EUR</h2>
            </Col>
            <Col span={4}>
              <h2>{this.state.currency_sym}</h2>
            </Col>
          </Row>
          <Row style={{ marginLeft: 10 }}>
            <Col span={4}>
              <h4>Credit limit</h4>
            </Col>
            <Col span={4}>
              <p>{this.state.credit_limit}</p>
            </Col>
            <Col span={4}>
              <p>{this.state.customer_credit_limit}</p>
            </Col>
          </Row>
          <Row style={{ marginLeft: 10 }}>
            <Col span={4}>
              <h4>Outstanding invoices</h4>
            </Col>
            <Col span={4}>
              <p>{this.state.open_invoices}</p>
            </Col>
            <Col span={4}>
              <p>{this.state.cust_open_invoices}</p>
            </Col>
          </Row>
          <Row style={{ marginLeft: 10 }}>
            <Col span={4}>
              <h4>Running orders</h4>
            </Col>
            <Col span={4}>
              <p>{this.state.running_ord_price}</p>
            </Col>
            <Col span={4}>
              <p>{this.state.cust_running_ord_price}</p>
            </Col>
          </Row>
          <Row style={{ marginLeft: 10 }}>
            <Col span={4}>
              <h4>Available credit</h4>
            </Col>
            <Col span={4}>
              <p>{this.state.available_credit}</p>
            </Col>
            <Col span={4}>
              <p>{this.state.cust_available_credit}</p>
            </Col>
          </Row>
          <Row style={{ marginLeft: 10 }}>
            <Col span={4}>
              <h4>Payment terms</h4>
            </Col>
            <Col span={4}>
              <p>
                {this.state.payment_terms}
                <span style={{ marginLeft: 10 }}>Days</span>
              </p>
            </Col>
          </Row>
        <div><h3>Details of outstanding invoices</h3></div>
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
CreditStatus.getInitialProps = async (context) => {
  return {
    customer_id: context.query.ids ?? "0",
    creditlimit: context.query.creditlimit,
    customercreditlimit: context.query.customercreditlimit,
    cust_outstanding: context.query.cust_outstanding,
    ec_customer_id: context.query.ec_customer_id,
    invoice_id: context.query.invoice_id,
    isModal: true,
  };
};
export default CreditStatus;
