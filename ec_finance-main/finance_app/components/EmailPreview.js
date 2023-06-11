import { Typography, Row, Col, Image, Table, Modal, Space } from "antd";
const { Paragraph, Link } = Typography;
import axios from "axios";
import DataGridViewer from "./DataGridViewer";
import React from "react";
class EmailPreview extends React.Component {
  state = {
    visible: true,
    data: [],
  };
  AppSchema = {
    listing: [
      {
        dataGridUID: "previewReminder",
        url: "/dt/sales/reminder_preview/?customer_id=" + this.props.customer,
        row_selection: false,
        default_sort_col: "id",
        default_sort_order: "descend",
        bind_on_load: true,
        gridViewer: true,
        columns: [
          {
            text: "Reminder",
            value: "reminder_status",
            width: 100,
          },
          {
            text: "Invoice number",
            value: "invoice_number",
            width: 100,
          },
          {
            text: "Invoice date",
            value: "invoice_created_on",
            width: 100,
          },
          {
            text: "Outstanding amount",
            value: "outstanding_amount",
            width: 100,
          },
          {
            text: "Outstanding days",
            value: "outstanding_days",
            width: 100,
          },
          {
            text: "Due date",
            value: "invoice_due_date",
            width: 100,
          },
          {
            text: "Invoice amount",
            value: "invoice_value",
            width: 100,
          },
          {
            text: "Amount paid",
            value: "amount_paid",
            width: 100,
          },
          {
            text: "Payment date",
            value: "payment_date",
            width: 100,
          },
          {
            text: "Orders",
            value: "order_nrs",
            width: 100,
          },
        ],
      },
    ],
  };
  async componentDidMount() {
    let customer_id = this.props.customer ?? null;
    let hand_company_id = this.props.hand_company ?? null;
    const res = await axios.get("/dt/sales/customer_reminder_preview/?customer_id=" + customer_id + "&hand_company_id=" + hand_company_id);
    const data = res.data.data.data;
    this.setState({
      customer_name: data.customer_name,
      email: data.email,
      fax: data.fax,
      outstanding_amount: data.outstanding_amount,
      paid_amount: data.paid_amount,
      invoice_amount: data.invoice_amount,
      phone: data.contact,
      address: data.address,
      hand_company: data.hand_com_name,
    });
  }
  handleCancel = () => {
    this.setState({ visible: false });
    this.props.onFalse;
  };

  render() {
    return (
      <div>
        <Modal
          centered
          width={"90%"}
          bodyStyle={{ height: "90vh", overflowX: "scroll" }}
          visible={this.state.visible}
          footer={null}
          onCancel={this.props.onFalse}
        >
          <Row>
            <Col span={8}>
              <Image alt="Image" preview={false} src="/logo.png" />
            </Col>
            <Col span={4} offset={12}>
              <Paragraph>
                <Link href="https://be.eurocircuits.com/shop/eclogin.aspx">Your Account </Link> |{" "}
                <Link href="https://www.eurocircuits.com/"> Eurocircuits home </Link>
              </Paragraph>
              {/* <Paragraph><Link>Your Account </Link> | <Link> Eurocircuits home  </Link></Paragraph> */}
              <Paragraph style={{ fontSize: 20 }}>
                <b>invoice payment reminder</b>
              </Paragraph>
              <Paragraph>Customer : {this.state.customer_name}</Paragraph>
            </Col>
          </Row>
          <Row>
            <Col>
              <Paragraph>
                <b>Outstanding invoice reminder for:</b>
              </Paragraph>
              <Row>
                <Col span={3}>
                  <p>Customer</p>
                </Col>
                <Col span={1}>
                  <p>:</p>
                </Col>
                <Col span={20}>
                  <Paragraph>{this.state.customer_name} </Paragraph>
                </Col>
              </Row>
              <Row>
                <Col span={3}>
                  <p>Address</p>
                </Col>
                <Col span={1}>
                  <p>:</p>
                </Col>
                <Col span={20}>
                  <Paragraph>{this.state.address}</Paragraph>
                </Col>
              </Row>
              <Row>
                <Col span={3}>
                  <p>Fax</p>
                </Col>
                <Col span={1}>
                  <p>:</p>
                </Col>
                <Col span={20}>
                  <Paragraph>{this.state.fax}</Paragraph>
                </Col>
              </Row>
              <Row>
                <Col span={3}>
                  <p>Phone</p>
                </Col>
                <Col span={1}>
                  <p>:</p>
                </Col>
                <Col span={20}>
                  <Paragraph>{this.state.phone}</Paragraph>
                </Col>
              </Row>
              <Paragraph>Dear Customer , According to our administration, the following invoices are outstanding for payment: </Paragraph>
            </Col>
          </Row>
          {/* <Table columns={columns} dataSource={this.state.data} pagination={false} bordered size="small" >
        </Table> */}
          <DataGridViewer
            schema={this.AppSchema.listing[0]}
            ref={(node) => {
              this.dataGrid = node;
            }}
          ></DataGridViewer>
          <Row></Row>
          <Row>
            <Col>
              <Paragraph>Outstanding amount : {this.state.outstanding_amount} </Paragraph>
              <Paragraph>Invoice amount : {this.state.invoice_amount}</Paragraph>
              <Paragraph>Amount Paid : {this.state.paid_amount}</Paragraph>
            </Col>
            <Col>
              Please pay the amount outstanding, outstanding invoices can prevent from new orders are placed on your account. In case of any discrepancy between
              your administration and ours, do reply to this mail with your remarks. Payments can be made by wire transfer to the account mentioned on the
              invoice. Payments with credit card are also possible. Login to your account on the website, go to the pending invoices and select{" "}
              <b>pay online.</b>
            </Col>
          </Row>

          <Paragraph italic>
            <p>Kind regards </p>
            <p>for {this.state.hand_company}</p>
            <p>Katleen Laureys</p>
          </Paragraph>
        </Modal>
      </div>
    );
  }
}

export default EmailPreview;
