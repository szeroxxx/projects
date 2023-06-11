import { ReloadOutlined } from "@ant-design/icons";
import { Button, Card, Checkbox, DatePicker, Form, Input, InputNumber, Row ,Col} from "antd";
import axios from "axios";
import { format } from "date-fns";
import moment from "moment";
import React, { Component } from "react";
import ActionPanel from "../../components/ActionPanel";
import AppModal from "../../components/AppModal";
import DataGridViewer from "../../components/DataGridViewer";
import PageTitle from "../../components/PageTitle";

class zeroBooking extends Component {
  state = { data: {}, status: "all", is_model: this.props.is_model, to_date: "2022-01-01", from_date: "2022-01-01" };
  appSchema = {
    pageTitle: "Xero booking",
    buttons: [
      {
        dataGridUID: "xero_booking",
        name: "edit_profile",
        title: "Edit profile",
        primary: "primary",
        multi_select: false,
        icon_code: "UserOutlined",
        click_handler: () => {
          var data = this.dataGridViewer.getSelectedRows("xero_booking");
          this.editProfile(data);
        },
      },
      {
        name: "generate_csv",
        title: "Generate CSV",
        primary: "primary",
        icon_code: "ExportOutlined",
        click_handler: () => {
          var data = this.dataGridViewer.getDataSource("xero_booking");
          console.log(data, "data");
          this.generateCsv(data);
        },
      },
    ],
    listing: [
      {
        dataGridUID: "xero_booking",
        url: "/dt/sales/xero_booking/",
        paging: true,
        default_sort_col: "id",
        default_sort_order: "descend",
        row_selection: true,
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
            value: "invoice_number",
            text: "Invoice Nr.",
            width: 100,
            sequence: 3,
          },
          {
            value: "",
            text: "Contact name",
            width: 200,
            sequence: 2,
          },
          {
            value: "handling_company",
            text: "Handling company",
            sequence: 3,
            width: 150,
          },
          {
            value: "invoice_created_on",
            text: "Invoice date",
            sequence: 3,
            width: 150,
          },
          {
            value: "invoice_due_date",
            text: "Invoice due date",
            sequence: 3,
            width: 200,
          },
          {
            value: "",
            text: "Prod date",
            width: 200,
          },
          {
            value: "vat_no",
            text: "Tax number",
            width: 200,
          },
          {
            value: "vat_percentage",
            text: "Vat percentage",
            width: 200,
          },
          {
            value: "",
            text: "Quentity",
            width: 200,
          },
          {
            value: "",
            text: "Description",
            width: 200,
          },
          {
            value: "",
            text: "Account code",
            width: 200,
          },
          {
            value: "",
            text: "Unit price",
            width: 200,
          },
        ],
      },
    ],
  };
  onCheck = (isDate, obj) => {
    var is_date = isDate.target.checked;
    this.setState({ is_date });
  };
  getXeroBookingData = () => {
    this.dataGridViewer.searchData({
      from_date: ["text", this.state.from_date] ?? null,
      to_date: ["text", this.state.to_date] ?? null,
      is_date: ["text", this.state.is_date],
      prefix: ["text", this.state.prefix],
      from_number: ["text", this.state.from_number],
      to_number: ["text", this.state.to_number],
    });
  };
  editProfile = (data) => {
    var ec_customer_id = null;
    if (data[0]) {
      ec_customer_id = data[0].ec_customer_id;
    }
    var customer_name = null;
    if (data[0]) {
      customer_name = data[0].customer_name;
    }
    var post_data = {
      ec_customer_id: ec_customer_id,
    };
    axios.post("/dt/customer/edit_profile/", post_data).then((response) => {
      if (response.data.code == 1) {
        this.appModal.show({
          url: response.data.data,
          title: "Edit Profile :" + " " + customer_name,
          style: { width: "90%", height: "85vh" },
        });
        return;
      }
    });
  };
  generateCsv = (data) => {
    var ids = "";
    for (var row in data) {
      ids = ids + data[row].id + ",";
    }
    window.open("/dt/base/xero_booking/?invoice_id=" + ids);
  };
  refresh = () => {
    this.dataForm.refreshTable();
  };
  componentDidMount = () => {};
  rowSelectionChange = (key, selectedRows) => {
    this.setState((prevState) => ({
      data: { ...prevState.data, [key]: selectedRows },
    }));
  };

  render() {
    return (
      <div className="extra-fields">
        <PageTitle pageTitle={this.appSchema.pageTitle}></PageTitle>
        <ActionPanel buttons={this.appSchema.buttons} selectedRows={this.state.data[this.appSchema.listing[0].dataGridUID]} />

        <Form style={{ marginTop: 20 }}>
          {/* <Row className="onelineform"> */}
            {/* <Card> */}
            <Row >
              <Col xs={28} sm={16} md={12} lg={10} xl={10}>
                <Row>
                  <Col span={10}><p>Select date range</p></Col>
                </Row>
                <Row>
                  <Col>
                    <Form.Item style={{marginLeft:10}}>
                      <Checkbox primary={"primary"} onChange={this.onCheck}></Checkbox>
                    </Form.Item>
                  </Col>
                  <Col>
                    <Form.Item label="From date :" name="from_date" style={{ marginLeft: 10 }}>
                      <DatePicker
                        style={{ width: 120 }}
                        defaultValue={moment().subtract(1, "days")}
                        onChange={(e) => {
                          if (e != null) {
                            this.setState({ from_date: format(new Date(e._d), "yyyy-MM-dd") });
                          }
                        }}
                      ></DatePicker>
                    </Form.Item>
                  </Col>
                  <Col>
                    <Form.Item label="To date :" style={{ marginLeft: 10 }}>
                      <DatePicker
                        style={{ width: 120 }}
                        defaultValue={moment()}
                        onChange={(e) => {
                          if (e != null) {
                            this.setState({ to_date: format(new Date(e._d), "yyyy-MM-dd") });
                          }
                        }}
                      ></DatePicker>
                    </Form.Item>
                  </Col>
                  <Col>
                    <Form.Item style={{marginLeft:10}}>OR</Form.Item>
                  </Col>
                </Row>
              </Col>
              <Col span={13} xs={10} sm={13} md={6} lg={10} xl={13}>
                  <Row>
                    <Col ><p >Invoice number range</p></Col>
                  </Row>
                  <Row>
                    <Col>
                      <Form.Item label="Prefix :" style={{marginLeft:10}}>
                        <Input
                          style={{ width: 100 }}
                          type={"text"}
                          onChange={(e) => {
                            if (e != null) {
                              console.log(e);
                              this.setState({ prefix: e.target.value });
                            }
                          }}
                        />
                      </Form.Item>
                    </Col>
                    <Col>
                      <Form.Item label="From number :" style={{ marginLeft: 10 }}>
                        <InputNumber
                          type={"number"}
                          onChange={(e) => {
                            if (e != null) {
                              console.log(e);
                              this.setState({ to_number: e });
                            }
                          }}
                        />
                      </Form.Item>
                    </Col>
                    <Col>
                      <Form.Item label="To number :" style={{ marginLeft: 10 }}>
                        <InputNumber
                          type={"number"}
                          onChange={(e) => {
                            if (e != null) {
                              console.log(e);
                              this.setState({ from_number: e });
                            }
                          }}
                        />
                      </Form.Item>
                    </Col>
                  </Row>
              </Col>
              <Col span={1} xs={2} sm={1} md={6} lg={8} xl={1} >
              <Row>&nbsp;</Row>
              <Row style={{ marginLeft: 10 ,float:"right",marginTop:11}}>
                <Form.Item className="button" type="button" >
                  <Button onClick={this.getXeroBookingData} type="primary" icon={<ReloadOutlined />}>
                    Load
                  </Button>
                </Form.Item>
                </Row>
              <Row></Row>
                {/* <Form.Item className="button" type="button" >
                  <Button onClick={this.getXeroBookingData} type="primary">
                    Load
                  </Button>
                </Form.Item> */}
              </Col>
            </Row>



              {/* <Row>
                <Col span={10}><p>Select date range</p></Col>
                <Col span={14}><p >Invoice number range</p></Col>
              </Row> */}
              {/* <Row > */}
                {/* <Col>
                 <Form.Item label="Select date range"></Form.Item>
                </Col> */}
              {/* </Row>
              <Row> */}
              {/* <Col>
                <Form.Item style={{marginLeft:10}}>
                  <Checkbox primary={"primary"} onChange={this.onCheck}></Checkbox>
                </Form.Item>
              </Col> */}
              {/* <Col>
                <Form.Item label="From date :" name="from_date" style={{ marginLeft: 10 }}>
                  <DatePicker
                    style={{ width: 120 }}
                    defaultValue={moment().subtract(1, "days")}
                    onChange={(e) => {
                      if (e != null) {
                        this.setState({ from_date: format(new Date(e._d), "yyyy-MM-dd") });
                      }
                    }}
                  ></DatePicker>
                </Form.Item>
              </Col> */}
              {/* <Col>
                <Form.Item label="To date :" style={{ marginLeft: 10 }}>
                  <DatePicker
                    style={{ width: 120 }}
                    defaultValue={moment()}
                    onChange={(e) => {
                      if (e != null) {
                        this.setState({ to_date: format(new Date(e._d), "yyyy-MM-dd") });
                      }
                    }}
                  ></DatePicker>
                </Form.Item>
              </Col> */}
              {/* </Row> */}
            {/* </Card> */}
              {/* <Col>
                <Form.Item style={{marginLeft:10}}>OR</Form.Item>
              </Col> */}
            {/* <Col> */}
            {/* <Card> */}
              {/* <Row> */}
                {/* <Form.Item label="Invoice number range"></Form.Item> */}
              {/* </Row>
              <Row gutter={24}> */}
              {/* </Col> */}
              {/* <Col>
                <Form.Item label="Prefix :" style={{marginLeft:10}}>
                  <Input
                    style={{ width: 100 }}
                    type={"text"}
                    onChange={(e) => {
                      if (e != null) {
                        console.log(e);
                        this.setState({ prefix: e.target.value });
                      }
                    }}
                  />
                </Form.Item>
                </Col>
                <Col>
                <Form.Item label="From number :" style={{ marginLeft: 10 }}>
                  <InputNumber
                    type={"number"}
                    onChange={(e) => {
                      if (e != null) {
                        console.log(e);
                        this.setState({ to_number: e });
                      }
                    }}
                  />
                </Form.Item>
                </Col> */}
                {/* <Col>
                <Form.Item label="To number :" style={{ marginLeft: 10 }}>
                  <InputNumber
                    type={"number"}
                    onChange={(e) => {
                      if (e != null) {
                        console.log(e);
                        this.setState({ from_number: e });
                      }
                    }}
                  />
                </Form.Item>
                </Col> */}
                {/* <Col>
                  <Form.Item className="button" type="button" >
                    <Button onClick={this.getXeroBookingData} type="primary">
                      Load
                    </Button>
                  </Form.Item>
                </Col>
              </Row> */}

            {/* </Card> */}

            {/* <Form.Item className="button" type="button" >
              <Button onClick={this.getXeroBookingData} type="primary">
                Load
              </Button>
            </Form.Item> */}
          {/* </Row> */}
        </Form>

        {/* <br></br> */}
        <DataGridViewer
          schema={this.appSchema.listing[0]}
          onRowSelectionChange={this.rowSelectionChange}
          ref={(node) => {
            this.dataGridViewer = node;
          }}
        ></DataGridViewer>
        <AppModal
          callBack={this.onModelClose}
          ref={(node) => {
            this.appModal = node;
          }}
        ></AppModal>
      </div>
    );
  }
}
zeroBooking.getInitialProps = async (context) => {
  return { is_model: context.query.is_model ?? false };
};
export default zeroBooking;
