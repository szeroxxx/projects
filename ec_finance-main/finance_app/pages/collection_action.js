import React, { Component } from "react";
import { Tabs, Row, Col, Form, Input, DatePicker, Select, Typography, Table, Button, Upload, message, Modal, Image } from "antd";
import { PlusCircleOutlined } from "@ant-design/icons";
import AppLayout from "../components/AppLayout";
import AppIcons from "../components/AppIcons";
import { Footer } from "antd/lib/layout/layout";

const { TabPane } = Tabs;
const { Title } = Typography;
const { TextArea } = Input;
const { Option } = Select;

function preventDefault(e) {
  e.preventDefault();
  console.log("Clicked! But prevent default.");
}
function handleChange(value) {
  console.log(`selected ${value}`);
}
function callback(key) {
  console.log(key);
}

const layout = {
  labelCol: {
    span: 6,
  },
  wrapperCol: {
    span: 16,
  },
};

const columns = [
  {
    title: "Action Type",
    dataIndex: "actionType",
  },
  {
    title: "Action Date",
    dataIndex: "actionDate",
  },
  {
    title: "Action By",
    dataIndex: "actionBy",
  },
  {
    title: "Next Action Type",
    dataIndex: "nextActionType",
  },
  {
    title: "Next Action By",
    dataIndex: "nextActionDate",
  },
  {
    title: "",
    dataIndex: "viewDetail",
    render: () => <a href={""}>{"view details"}</a>,
  },
  {
    title: "",
    dataIndex: "attachment",
    render: () => (
      <div>
        <Image preview={false} alt={"Image"} src={`/edit.png`} style={{ width: 15, marginRight: 10 }} />
        <Image preview={false} alt={"Image"} src={`/download.png`} style={{ width: 15, marginRight: 10 }} />
        <Image preview={false} alt={"Image"} src={`/garbage.png`} style={{ width: 15 }} />
      </div>
    ),
  },
];

const data = [];
for (let i = 0; i < 9; i++) {
  data.push({
    key: i,
    actionType: `call`,
    actionDate: `12-12-2021`,
    actionBy: `Yash Suthar`,
    nextActionType: `call`,
    nextActionDate: `31-12-2021`,
    viewDetail: ``,
    attachment: ``,
  });
}

const props = {
  name: "file",
  action: "",
  headers: {
    authorization: "authorization-text",
  },
  onChange(info) {
    if (info.file.status !== "uploading") {
      console.log(info.file, info.fileList);
    }
    if (info.file.status === "done") {
      message.success(`${info.file.name} file uploaded successfully`);
    } else if (info.file.status === "error") {
      message.error(`${info.file.name} file upload failed.`);
    }
  },
};

class collectionAction extends Component {
  state = {
    selectedRowKeys: [],
    loading: false,
  };

  start = () => {
    this.setState({ loading: true });
    setTimeout(() => {
      this.setState({
        selectedRowKeys: [],
        loading: false,
      });
    }, 1000);
  };

  onSelectChange = (selectedRowKeys) => {
    console.log("selectedRowKeys changed: ", selectedRowKeys);
    this.setState({ selectedRowKeys });
  };

  state = {
    modal2Visible: false,
  };

  setModal2Visible(modal2Visible) {
    this.setState({ modal2Visible });
  }

  render() {
    const { selectedRowKeys } = this.state;
    const rowSelection = {
      selectedRowKeys,
      onChange: this.onSelectChange,
    };

    return (
      <AppLayout>
        <Title level={4} className="collectionAction-title">
          Schedular - XYZ_12
        </Title>
        <Tabs defaultActiveKey="1" onChange={callback} className="collection-tabs">
          <TabPane tab="Info" key="1" className="collectionAction-layout">
            <Row>
              <Col span={11}>
                <Form {...layout} name="nest-messages" className="collection-form">
                  <Form.Item label="Customer" className="collection-input">
                    <Input className="ml-30" />
                  </Form.Item>
                  <Form.Item label="Email ID" className="collection-input">
                    <Input className="ml-30" />
                  </Form.Item>
                  <Form.Item label="Contact" className="collection-input">
                    <Input className="ml-30" />
                  </Form.Item>
                  <Form.Item label="Country" className="collection-input">
                    <Input className="ml-30" />
                  </Form.Item>
                </Form>
              </Col>
              <Col span={11} offset={1}>
                <Form {...layout} name="nest-messages" className="collection-form">
                  <Form.Item label="Total Invoices" className="collection-input">
                    <Input className="ml-30" onclick="window.location.href = 'www.google.com';" value={55} />
                  </Form.Item>
                  <Form.Item label="Invoice Amount" className="collection-input">
                    <Input className="ml-30" />
                  </Form.Item>
                  <Form.Item label="Paid Amount" className="collection-input">
                    <Input className="ml-30" />
                  </Form.Item>
                  <Form.Item label="Total Reminders" className="collection-input">
                    <Input className="ml-30" />
                  </Form.Item>
                  <Form.Item label="Last Reminder" className="collection-input">
                    <Input className="ml-30" />
                  </Form.Item>
                </Form>
              </Col>
            </Row>
            <Tabs defaultActiveKey="1" onChange={callback}>
              <TabPane tab="Actions" key="1">
                <Table rowSelection={rowSelection} columns={columns} dataSource={data} className="collection-table" />
              </TabPane>
            </Tabs>
          </TabPane>
          <TabPane tab="Invoices" key="2">
            Content of Tab Pane 2
          </TabPane>
          <TabPane tab="Reminders" key="3">
            Content of Tab Pane 3
          </TabPane>
        </Tabs>
        <Footer className="collectionAction-footer">
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <div onClick={() => this.setModal2Visible(true)} className="action-modal">
                <PlusCircleOutlined /> Add Action
              </div>
              <Modal
                className="addAction-modal"
                title="Add Action"
                centered
                visible={this.state.modal2Visible}
                onOk={() => this.setModal2Visible(false)}
                onCancel={() => this.setModal2Visible(false)}
                width={1200}
                footer={[
                  <Button key="cancel" type="" onClick={this.handleCancel}>
                    Cancel
                  </Button>,
                  <Button key="save" type="primary" onClick={this.handleOk}>
                    Save
                  </Button>,
                ]}
              >
                <Row>
                  <Col span={11}>
                    <Form {...layout} name="nest-messages" className="collection-form">
                      <Form.Item label="Action Type" className="collection-input">
                        <Select defaultValue="Call" onChange={handleChange} className="ml-30">
                          <Option value="call">Call</Option>
                          <Option value="chat">Chat</Option>
                          <Option value="offlinemsg">Offline Message</Option>
                          <Option value="ticket">Ticket</Option>
                          <Option value="planfollowup">Plan Follow up</Option>
                        </Select>
                      </Form.Item>
                      <Form.Item label="Action By" className="collection-input">
                        <Select defaultValue="Payanshi Shah" onChange={handleChange} className="ml-30">
                          <Option value="ps">Payanshi Shah</Option>
                          <Option value="jp">Jahnvi Patel</Option>
                          <Option value="sb">Sakshi Bambharoliya</Option>
                          <Option value="pp">Priya Desai</Option>
                        </Select>
                      </Form.Item>
                      <Form.Item label="Action Date" className="collection-datepicker">
                        <DatePicker className="ml-30" />
                      </Form.Item>
                      <Form.Item label="Reference" className="collection-input">
                        <Input className="ml-30" />
                      </Form.Item>
                      <Form.Item label="Summary">
                        <TextArea rows={2} className="ml-30" />
                      </Form.Item>
                      <Form.Item label="Add Attachment">
                        <Upload {...props} className="ml-30 d-flex flex-wrap attch-file">
                          <Button className="attachment-btn">Choose File</Button> No file chosen
                        </Upload>
                      </Form.Item>
                    </Form>
                  </Col>
                  <Col span={11} offset={1}>
                    <Form {...layout} name="nest-messages" className="collection-form">
                      <Form.Item label="Next Action Type" className="collection-input">
                        <Select defaultValue="Call" onChange={handleChange} className="ml-30">
                          <Option value="call">Call</Option>
                          <Option value="chat">Chat</Option>
                          <Option value="offlinemsg">Offline Message</Option>
                          <Option value="ticket">Ticket</Option>
                          <Option value="planfollowup">Plan Follow up</Option>
                        </Select>
                      </Form.Item>
                      <Form.Item label="Next Action Date" className="collection-datepicker">
                        <DatePicker className="ml-30" />
                      </Form.Item>
                      <Form.Item label="Reference" className="collection-input">
                        <Input className="ml-30" />
                      </Form.Item>
                      <Form.Item label="Notes">
                        <TextArea rows={2} className="ml-30" />
                      </Form.Item>
                      <Form.Item label="Add Attachment">
                        <Upload {...props} className="ml-30 d-flex flex-wrap attch-file">
                          <Button className="attachment-btn">Choose File</Button> No file chosen
                        </Upload>
                      </Form.Item>
                    </Form>
                  </Col>
                </Row>
              </Modal>
            </div>
            <div>
              <Button className="mr-5 history-btn">
                <Image preview={false} alt="Image" width={15} src="/history.png" className="history-icon" />
              </Button>
              <Button className="mr-5">Close</Button>
              <Button type="primary" icon={<AppIcons code={"CopyrightOutlined"} />}>
                Send to Legal Action
              </Button>
            </div>
          </div>
        </Footer>
      </AppLayout>
    );
  }
}
export default collectionAction;
