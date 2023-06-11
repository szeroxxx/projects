import { Button, Col, Form, Input, Row } from "antd";
import React, { Component } from "react";
import DataGridViewer from "../../components/DataGridViewer";
class editInvoice extends Component {
  constructor(props) {
    super(props);
  }
  user_id = this.props.session.user.data.user_id;
  state = { ec_customer_id: this.props.id, group_code: null, discount_code: null };
  formRef = React.createRef();
  editInvoiceSchema = {
    listing: [
      {
        dataGridUID: "discount",
        url: "/dt/sales/discount_lookup/?ec_customer_id=" + this.state.ec_customer_id,
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
            value: "GroupCode",
            text: "Discount group",
            sortable: true,
            width: 100,
            sequence: 2,
            editable: true,
          },
          {
            value: "DiscountCode",
            text: "Coupen code",
            sortable: true,
            width: 100,
            sequence: 3,
            editable: true,
          },
          {
            value: "Description",
            text: "Description",
            sortable: true,
            width: 100,
            sequence: 4,
            editable: true,
          },
          {
            value: "StartDate",
            text: "Start date",
            sortable: true,
            width: 100,
            sequence: 5,
            editable: true,
          },
          {
            value: "ExpireDate",
            text: "Expiry date",
            sortable: true,
            width: 100,
            sequence: 6,
            editable: true,
          },
          {
            value: "DiscountValue",
            text: "Discount value",
            sortable: true,
            width: 100,
            sequence: 7,
            editable: true,
          },
        ],
      },
    ],
  };
  onFinish = (value) => {
    this.discountGridViewer.searchData({
      is_search: ["text", true],
      group_code: ["text", value.group_code ? value.group_code : ""],
      discount_code: ["text", value.discount_code ? value.discount_code : ""],
    });
  };
  clearSearch = () => {
    this.formRef.current.resetFields();
    this.discountGridViewer.searchData({});
  };
  render() {
    return (
      <>
        <Form onFinish={this.onFinish} ref={this.formRef}>
          <Row>
            <Col flex={4}>
              <Row gutter={10}>
                <Col>
                  <p>Discount group :</p>
                </Col>
                <Col>
                  <Form.Item name="group_code">
                    <Input
                      value={this.state.group_code}
                      onChange={(e) => {
                        this.setState({ group_code: e.target.value });
                      }}
                    />
                  </Form.Item>
                </Col>
                <Col>
                  <p>Discount code :</p>
                </Col>
                <Col>
                  <Form.Item name="discount_code">
                    <Input
                      value={this.state.discount_code}
                      onChange={(e) => {
                        this.setState({ discount_code: e.target.value });
                      }}
                    />
                  </Form.Item>
                </Col>
                <Col>
                  <Button htmlType="submit">Search</Button>
                  <span style={{ marginLeft: 10 }}>
                    <Button onClick={this.clearSearch}>Clear Search</Button>
                  </span>
                </Col>
              </Row>
            </Col>
            <DataGridViewer
              schema={this.editInvoiceSchema.listing[0]}
              ref={(node) => {
                this.discountGridViewer = node;
              }}
            ></DataGridViewer>
          </Row>
        </Form>
      </>
    );
  }
}
editInvoice.getInitialProps = async (context) => {
  return { id: context.query.ec_customer_id ?? "0", isModal: true };
};
export default editInvoice;
