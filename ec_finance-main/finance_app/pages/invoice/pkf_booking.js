
import { Button, Card, Checkbox, DatePicker, Form, Input, InputNumber, Row ,Col} from "antd";
import axios from "axios";
import { format } from "date-fns";
import moment from "moment";
import React, { Component } from "react";
import ActionPanel from "../../components/ActionPanel";
import AppModal from "../../components/AppModal";
import DataGridViewer from "../../components/DataGridViewer";
import PageTitle from "../../components/PageTitle";
import { ReloadOutlined } from "@ant-design/icons";


class pkfBooking extends Component {
  user_id = this.props.session.user.data.user_id;
   state = {
    data: {},
    from_date: {},
    isDate: false,
    hungarian: false,
    from_date: moment().subtract(1, "days").toISOString(),
    to_date: moment().toISOString(),
  };
  appSchema = {
    pageTitle: "PKF Booking",
    buttons: [
      {
        dataGridUID: "pkfBooking",
        name: "edit_profile",
        title: "Edit profile",
        multi_select: false,
        icon_code: "UserOutlined",
        tooltip: "",
        sequence: 1,
        click_handler: () => {
          var data = this.dataGridViewer.getDataSource("pkfBooking");
          this.editProfile(data);
        },
      },
      {
        dataGridUID: "pkfBooking",
        name: "generate_xml",
        title: "Generate XML",
        icon_code: "ExportOutlined",
        sequence: 2,
        click_handler: () => {
          var data = this.dataGridViewer.getDataSource();
          this.exportXml(data);
        },
      },
    ],
    listing: [
      {
        pre_view: [{ doc: "invoice", label: "Invoice", key: "invoice_number" }],
        dataGridUID: "pkfBooking",
        url: "/dt/sales/pkf_booking/",
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
            text: "invoice number",
            sortable: true,
            sequence: 2,
            width: 150,
          },
          {
            value: "customer",
            text: "Customer name",
            sortable: true,
            sequence: 3,
            width: 150,
          },
          {
            value: "hand_company",
            text: "Handling company",
            sequence: 4,
            sortable: true,
            width: 160,
          },
          {
            value: "invoice_created_on",
            sortable: true,
            sequence: 6,
            text: "Invoice date",
            width: 120,
          },
          {
            value: "invoice_due_date",
            sortable: true,
            sequence: 7,
            text: "Invoice due date",
            width: 150,
          },
          {
            value: "",
            sortable: true,
            sequence: 8,
            text: "Prod date",
            width: 100,
          },
          {
            value: "",
            sortable: true,
            sequence: 9,
            text: "Tax number",
            width: 120,
          },
          {
            value: "postal_code",
            sortable: true,
            sequence: 10,
            text: "Postal code",
            width: 120,
          },
          {
            value: "",
            sortable: true,
            sequence: 11,
            text: "town",
            width: 100,
          },
          {
            value: "street_address1",
            sortable: true,
            sequence: 12,
            text: "Street address1",
            width: 130,
          },
          {
            value: "street_address2",
            sortable: true,
            sequence: 13,
            text: "Street address2",
            width: 130,
          },
          {
            value: "street_no",
            sortable: true,
            sequence: 14,
            text: "Street number",
            width: 130,
          },
          {
            value: "street_name",
            sortable: true,
            sequence: 15,
            text: "Street name",
            width: 120,
          },
          {
            value: "vat_percentage",
            sortable: true,
            sequence: 16,
            text: "VAT percentage",
            width: 140,
          },
        ],
      },
    ],
  };
  onFinish = () => {
    this.dataGridViewer.searchData({
      from_date: ["text", this.state.from_date] ?? null,
      to_date: ["text", this.state.to_date] ?? null,
      is_date: ["text", this.state.is_date],
      prefix: ["text", this.state.prefix],
      from_number: ["text", this.state.from_number],
      to_number: ["text", this.state.to_number],
    });
  };
  onCheck = (e) => {
    var is_date = e.target.checked;
    this.setState({ is_date });
  };
  onclick = (e) => {
    var hungarian = e.target.checked;
    this.setState({ hungarian });
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
  exportXml = (data) => {
    var ids = "";
    for (var row in data) {
      ids = ids + data[row].id + ",";
    }
    window.open("/dt/base/pkf_booking_generate/?invoice_id=" + ids + "&is_hungarian=" + this.state.hungarian);
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


        <Form style={{ marginTop: 20 }} onFinish={this.onFinish}>
          {/* <Row className="onelineform"> */}
            {/* <Card> */}
            <Row>
              <Col xs={1} sm={10} md={6} lg={6} xl={10}>
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
                    <Form.Item name="from_date" label="From date" style={{ marginLeft: 10 }}>
                      <DatePicker
                        defaultValue={moment().subtract(1, "days")}
                        style={{ width: 120 }}
                        className="date-picker-w"
                        onChange={(e) => {
                          if (e != null) {
                            this.setState({ from_date: format(new Date(e._d), "yyyy-MM-dd") });
                          }
                        }}
                      />
                    </Form.Item>
                  </Col>
                  <Col>
                    <Form.Item name="to_date" label="To date" style={{ marginLeft: 10 }}>
                      <DatePicker
                        style={{ width: 120 }}
                        defaultValue={moment()}
                        className="date-picker-w"
                        onChange={(e) => {
                          if (e != null) {
                            this.setState({ to_date: format(new Date(e._d), "yyyy-MM-dd") });
                          }
                        }}
                      />
                    </Form.Item>
                  </Col>
                  <Col>
                    <Form.Item style={{marginLeft:10}}>OR</Form.Item>
                  </Col>
                </Row>
              </Col>
              <Col xs={10} sm={13} md={6} lg={10} xl={13}>
                  <Row>
                    <Col ><p >Invoice number range</p></Col>
                  </Row>
                  <Row>
                    <Col>
                      <Form.Item name="prefix" label="Prefix" style={{marginLeft:10}}>
                        <Input
                          style={{ width: 100 }}
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
                    <Form.Item name="from_number" label="From number" style={{ marginLeft: 10 }}>
                      <InputNumber
                        onChange={(e) => {
                          if (e != null) {
                            console.log(e);
                            this.setState({ from_number: e });
                          }
                        }}
                      />
                    </Form.Item>
                    </Col>
                    <Col>
                      <Form.Item name="to_number" label="To number" style={{ marginLeft: 10 }}>
                        <InputNumber
                          onChange={(e) => {
                            if (e != null) {
                              console.log(e);
                              this.setState({ to_number: e });
                            }
                          }}
                        />
                      </Form.Item>
                    </Col>
                  </Row>
              </Col>
              <Col xs={2} sm={1} md={6} lg={8} xl={1} >
              <Row>&nbsp;</Row>
              <Row style={{ marginLeft: 10 ,float:"right",marginTop:11}}>
                <Form.Item style={{ marginLeft: 10 }}>
                  <Button htmlType="submit" type="primary" icon={<ReloadOutlined />} >
                  Load
                  </Button>
                </Form.Item>
                </Row>
              </Col>
            </Row>
            {/* <Row style={{float:"right"}}> */}
              <div align="right" className="checkBox">
                <Checkbox onChange={this.onclick}>
                  <h1>Hungarian</h1>
                </Checkbox>
              </div>
            {/* </Row> */}
        </Form>




        {/* <Form style={{ marginTop: 20 }} onFinish={this.onFinish}>
          <Row className="onelineform">
            <Card>
              <Row>
                <p>Select date range</p>
              </Row>
              <Row>
                <Form.Item>
                  <Checkbox primary={"primary"} onChange={this.onCheck}></Checkbox>
                </Form.Item>
                <Form.Item name="from_date" label="From date" style={{ marginLeft: 10 }}>
                  <DatePicker
                    defaultValue={moment().subtract(1, "days")}
                    style={{ width: 120 }}
                    className="date-picker-w"
                    onChange={(e) => {
                      if (e != null) {
                        this.setState({ from_date: format(new Date(e._d), "yyyy-MM-dd") });
                      }
                    }}
                  />
                </Form.Item>
                <Form.Item name="to_date" label="To date" style={{ marginLeft: 10 }}>
                  <DatePicker
                    style={{ width: 120 }}
                    defaultValue={moment()}
                    className="date-picker-w"
                    onChange={(e) => {
                      if (e != null) {
                        this.setState({ to_date: format(new Date(e._d), "yyyy-MM-dd") });
                      }
                    }}
                  />
                </Form.Item>
              </Row>
            </Card>
            <p>OR</p>
            <Card>
              <Row>
                <p>Invoice number range</p>
              </Row>
              <Row gutter={24}>
                <Form.Item name="prefix" label="Prefix">
                  <Input
                    style={{ width: 100 }}
                    onChange={(e) => {
                      if (e != null) {
                        console.log(e);
                        this.setState({ prefix: e.target.value });
                      }
                    }}
                  />
                </Form.Item>
                <Form.Item name="from_number" label="From number" style={{ marginLeft: 10 }}>
                  <InputNumber
                    onChange={(e) => {
                      if (e != null) {
                        console.log(e);
                        this.setState({ from_number: e });
                      }
                    }}
                  />
                </Form.Item>
                <Form.Item name="to_number" label="To number" style={{ marginLeft: 10 }}>
                  <InputNumber
                    onChange={(e) => {
                      if (e != null) {
                        console.log(e);
                        this.setState({ to_number: e });
                      }
                    }}
                  />
                </Form.Item>
              </Row>
            </Card>
            <Form.Item style={{ marginLeft: 10 }}>
              <Button htmlType="submit" type="primary">
                Load
              </Button>
            </Form.Item>
          </Row>

          <div align="right">
            <Checkbox onChange={this.onclick}>
              <h1>Hungarian</h1>
            </Checkbox>
          </div>
        </Form> */}
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
export default pkfBooking;
