
import { Row, Col, Card } from "antd";
import React, { Component } from "react";
import axios from "axios";
import DataGridViewer from "../../components/DataGridViewer";
class financeReport extends Component {
    constructor(props) {
        super(props);
      }
  state = {customer_id:this.props.id,report_data:{}}
  financeReportSchema = {
    listing: [
        {
            dataGridUID: "financeReport",
            url: "/dt/sales/financial_report/?customer_id="+ this.state.customer_id,
            paging: true,
            gridViewer:true,
            row_selection: false,
            bind_on_load: false,
            columns: [
              {
                value: "id",
                text: "ID",
                show: false,
                row_key: true,
                sequence: 1,
              },
              {
                value: "Invoice_number",
                text: "Invoice number",
                sortable: true,
                width: 100,
                sequence: 2,
                modal: {
                  url: "/doc/invoice/",
                  title_key: ["number"],
                  queryParams: [{ key: "number" },],
                },
              },
              {
                value: "Invoice_date",
                text: "Invoice date",
                sortable: true,
                width: 100,
                sequence: 3,
              },
              {
                value: "Due_date",
                text: "Due date",
                sortable: true,
                width: 100,
                sequence: 4,
              },
              {
                value: "Financial_blocked",
                text: "Financial blocked",
                sortable: true,
                width: 100,
                sequence: 5,
              },
              {
                value: "Reminder",
                text: "Reminder",
                sortable: true,
                width: 100,
                sequence: 6,
              },
              {
                value: "Invoice_amount",
                text: "Invoice amount",
                sortable: true,
                width: 100,
                sequence: 7,
              },
              {
                value: "Open_amount",
                text: "Open amount",
                sortable: true,
                width: 100,
                sequence: 8,
              },
              {
                value: "Days_outstanding",
                text: "Days outstanding",
                sortable: true,
                width: 100,
                sequence: 9,
              },
              {
                value: "Status",
                text: "Status",
                sortable: true,
                width: 100,
                sequence: 10,
              },
              {
                value: "Secondary_status",
                text: "Secondary status",
                sortable: true,
                width: 100,
                sequence: 11,
              },
            ],
          },
    ],
  };
  onModelClose = () => {
    this.financeReport()
  };
  componentDidMount = () => {
    this.financeReport()
  };
  async financeReport (){
    const res = await axios.get("/dt/sales/finance_report/?ec_customer_id="+ this.props.ec_customer_id,)
    const table_data = res.data.data.outstanding_data
    const report_data = res.data.data.report_data[0]
    this.dataGridViewer.setDataSource(table_data)
    let total_invoice_amount =0
    let total_open_amount =0
    for(var row in table_data){
      total_invoice_amount = total_invoice_amount + table_data[row].Invoice_amount
      total_open_amount = total_open_amount + table_data[row].Open_amount
    }
    this.setState({
      report_data:report_data,
      total_invoice : table_data.length,
      total_invoice_amount:total_invoice_amount,
      total_open_amount:total_open_amount
    })
  }
  render() {
    return (
    <>
       <Row gutter={24}>
           <Col span={8}>
             <Card title="Credit limit" className="card-height">
              <Row>
                  <Col span={12}><p>System limit </p></Col>
                  <Col span={1}><p>:</p></Col>
                  <Col span={11}><p>{this.state.report_data["creditLimit"]}</p></Col>
              </Row>
              <Row>
                  <Col span={12}><p>Insurance limit </p></Col>
                  <Col span={1}><p>:</p></Col>
                  <Col span={11}><p>{this.state.report_data["InsuranceLimit"]}</p></Col>
              </Row>
              <Row>
                <Col span={12}><p>Credit available</p></Col>
                <Col span={1}><p>:</p></Col>
                <Col span={11}><p>{this.state.report_data["availableCredit"]}</p></Col>
              </Row>
              <Row>
                <Col span={12}><p>Credit usage 90 days</p></Col>
                <Col span={1}><p>:</p></Col>
                <Col span={11}><p>{this.state.report_data["90daycreaditusage"]}</p></Col>
              </Row>
              <Row>
                <Col span={12}><p>Credit usage 180 days</p></Col>
                <Col span={1}><p>:</p></Col>
                <Col span={11}><p>{this.state.report_data["180daycreaditusage"]}</p></Col>
              </Row>
              <Row>
                <Col span={12}><p>Credit usage 360 days</p></Col>
                <Col span={1}><p>:</p></Col>
                <Col span={11}><p>{this.state.report_data["360daycreaditusage"]}</p></Col>
              </Row>
              <Row>
                <Col span={12}><p>Turnover 90 days</p></Col>
                <Col span={1}><p>:</p></Col>
                <Col span={11}><p>{this.state.report_data["90orderintake"]}</p></Col>
              </Row>
              <Row>
                <Col span={12}><p>Turnover 180 days</p></Col>
                <Col span={1}><p>:</p></Col>
                <Col span={11}><p>{this.state.report_data["180orderintake"]}</p></Col>
              </Row>
              <Row>
                <Col span={12}><p>Turnover 360 days</p></Col>
                <Col span={1}><p>:</p></Col>
                <Col span={11}><p>{this.state.report_data["360orderintake"]}</p></Col>
              </Row>
              </Card>
           </Col>
           <Col span={8}>
               <Card title="Payment items" className="card-height">
                <Row>
                    <Col span={13}><p>Average term</p></Col>
                    <Col span={1}><p>:</p></Col>
                    <Col span={10}><p>{this.state.report_data["PaymentTerm"]}</p></Col>
                </Row>
                <Row>
                    <Col span={13}><p>Average payment term 90 days</p></Col>
                    <Col span={1}><p>:</p></Col>
                    <Col span={10}><p>{this.state.report_data["90dayspaymentterm"]}</p></Col>
                </Row>
                <Row>
                    <Col span={13}><p>Average payment term 180 days</p></Col>
                    <Col span={1}><p>:</p></Col>
                    <Col span={10}><p>{this.state.report_data["180dayspaymentterm"]}</p></Col>
                </Row>
                <Row>
                    <Col span={13}><p>Average payment term 360 days</p></Col>
                    <Col span={1}><p>:</p></Col>
                    <Col span={10}><p>{this.state.report_data["360dayspaymentterm"]}</p></Col>
                </Row>
                <Row>
                    <Col span={13}><p>Maximum payment delay 90 days</p></Col>
                    <Col span={1}><p>:</p></Col>
                    <Col span={10}><p>{this.state.report_data["90dayoustanding"]}</p></Col>
                </Row>
                <Row>
                    <Col span={13}><p>Maximum payment delay 180 days</p></Col>
                    <Col span={1}><p>:</p></Col>
                    <Col span={10}><p>{this.state.report_data["180dayoustanding"]}</p></Col>
                </Row>
                <Row>
                    <Col span={13}><p>Maximum payment delay 360 days</p></Col>
                    <Col span={1}><p>:</p></Col>
                    <Col span={10}><p>{this.state.report_data["360dayoustanding"]}</p></Col>
                </Row>
               </Card>
           </Col>
           <Col span={8}>
              <Card title="Reminder status" className="card-height">
                <Row>
                    <Col span={13}><p>Last 1st reminder</p></Col>
                    <Col span={1}><p>:</p></Col>
                    <Col span={10}><p>{this.state.report_data["Reminder1"]}</p></Col>
                </Row>
                <Row>
                    <Col span={13}><p>Last 2nd reminder</p></Col>
                    <Col span={1}><p>:</p></Col>
                    <Col span={10}><p>{this.state.report_data["Reminder2"]}</p></Col>
                </Row>
                <Row>
                    <Col span={13}><p>Last 3rd reminder</p></Col>
                    <Col span={1}><p>:</p></Col>
                    <Col span={10}><p>{this.state.report_data["Reminder3"]}</p></Col>
                </Row>
                <Row>
                    <Col span={13}><p>Account blocked</p></Col>
                    <Col span={1}><p>:</p></Col>
                    <Col span={10}><p>{this.state.report_data["AccountBlock"]}</p></Col>
                </Row>
                <Row>
                    <Col span={13}><p>Last payment date</p></Col>
                    <Col span={1}><p>:</p></Col>
                    <Col span={10}><p>{this.state.report_data["LastPayment"]}</p></Col>
                </Row>
                <Row>
                    <Col span={13}><p>Invoice number</p></Col>
                    <Col span={1}><p>:</p></Col>
                    <Col span={10}><p>{this.state.report_data["InvoiceNo"]}</p></Col>
                </Row>
                <Row>
                    <Col span={13}><p>Paid amount</p></Col>
                    <Col span={1}><p>:</p></Col>
                    <Col span={10}><p>{this.state.report_data["PaidAmt"]}</p></Col>
                </Row>
               </Card>
           </Col>
       </Row>
      <br></br>
      <b><h3>Outstanding invoices</h3></b>
       <DataGridViewer
          style={{ marginLeft:300}}
          schema={this.financeReportSchema.listing[0]}
          ref={(node) => {
              this.dataGridViewer = node;
            }}>
      </DataGridViewer>
      <Row>
        <Col span={8}>No of Invoice : {this.state.total_invoice}</Col>
        <Col span={8}>Total Invoice amount : {parseFloat(this.state.total_invoice_amount).toFixed(2)}</Col>
        <Col span={8}>Total Open amount : {parseFloat(this.state.total_open_amount).toFixed(2)}</Col>
      </Row>
    </>
    );
  }
}
financeReport.getInitialProps = async (context) => {
    return { id: context.query.ids??"0",isModal:true, ec_customer_id : context.query.ec_customer_id};
  };
export default financeReport;