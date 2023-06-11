import DataGridViewer from "../../components/DataGridViewer";
import ActionPanel from "../../components/ActionPanel";
import AppModal from "../../components/AppModal";
import axios from "axios";
import React, { Component } from "react";
import { Modal, Radio, Button, Form, Row, Col, Input, Upload, Select, Spin } from "antd";
import { EditOutlined } from "@ant-design/icons";
const { Option } = Select;
const { confirm } = Modal;
// const [form] = Form.useForm()
import AppIcons from "../../components/AppIcons";
import { showMessage } from "../../common/Util";
const plainOptions = ["Full", "Other", "All"];
let default_sort_col = "name";
let default_sort_order = "descend";
class UploadPaymentFile extends Component {
  constructor(props) {
    super(props);
  }
  formRef = React.createRef();
  user_id = this.props.session.user.data.user_id;
  state = {
    data: {},
    file_type: "CODA",
    isModalVisible: false,
    dataSource: [],
    coda_id: this.props.id,
    isDisabled: true,
    radio_value: "All",
    spinVisible: false,
  };

  uploadPaymentFileSchema = {
    buttons: [
      {
        dataGridUID: "uploadPaymentFile",
        name: "close_invoice",
        title: "Close Invoice",
        primary: "primary",
        tooltip: "",
        icon_code: "FileDoneOutlined",
        sequence: 1,
        class: "mr-left",
        // multi_select:true,
        click_handler: () => {
          var data = this.dataGridViewer.getSelectedRows();
          this.closeInvoice(data);
        },
      },
      {
        dataGridUID: "uploadPaymentFile",
        name: "searce_invoices",
        title: "Searce invoices",
        icon_code: "FileSearchOutlined",
        primary: "primary",
        multi_select: true,
        tooltip: "",
        sequence: 2,
        class: "mr-left",
        click_handler: () => {
          var data = this.dataGridViewer.getSelectedRows();
          this.invoiceSearch(data);
        },
      },
      {
        dataGridUID: "uploadPaymentFile",
        name: "explort_xls",
        title: "Export XLS",
        primary: "primary",
        icon_code: "ExportOutlined",
        tooltip: "",
        sequence: 3,
        class: "mr-left",
        click_handler: () => {
          this.exportXls();
        },
      },
      {
        dataGridUID: "uploadPaymentFile",
        name: "generate_xml",
        title: "Generate XML",
        primary: "primary",
        tooltip: "",
        sequence: 4,
        class: "mr-left",
        click_handler: () => {
          this.exportXml();
        },
      },
      {
        dataGridUID: "uploadPaymentFile",
        name: "mark_as_unmatch",
        title: "Mark as unmatched",
        primary: "primary",
        tooltip: "",
        sequence: 5,
        class: "mr-left",
        multi_select: true,
        confirm: {
          title: "Are you sure you want to mark as unmatch?",
          content: <>Import payment will be unmatch</>,
          okText: "Yes, Unmatch ",
          cancelText: "No, Cancel",
          onOk: () => {
            var data = this.dataGridViewer.getSelectedRows();
            this.Unmatched(data);
          },
        },
      },
    ],
    listing: [
      {
        dataGridUID: "uploadPaymentFile",
        url: "/dt/payment/import_payment/xml_payment_import/?ids=" + this.state.coda_id,
        paging: false,
        row_selection: true,
        bind_on_load: true,
        default_sort_col: default_sort_col,
        default_sort_order: default_sort_order,
        gridViewer: true,
        onRow: (record) => {
          let color = "";
          if (record.match == "No data") {
            color = "#FF0000";
          }
          if (record.match == "Amount check") {
            color = "#f5c242";
          }
          if (record.invoice_status == "Closed") {
            color = "#2A9F00";
          }
          return {
            style: {
              color: color,
            },
          };
        },
        columns: [
          {
            value: "id",
            text: "ID",
            sortable: true,
            show: false,
            row_key: true,
            sequence: 1,
          },
          {
            value: "name",
            text: "Name",
            sortable: true,
            width: 100,
            sequence: 2,
          },
          {
            value: "bank_account_nr",
            text: "Bank Account Nr.",
            sortable: true,
            width: 130,
            sequence: 3,
          },
          {
            value: "amount",
            text: "Amount",
            sortable: true,
            width: 100,
            sequence: 4,
          },
          {
            value: "message",
            text: "Message",
            sortable: true,
            width: 100,
            sequence: 5,
          },
          {
            value: "match",
            text: "Match",
            sortable: true,
            width: 100,
            sequence: 6,
          },
          {
            value: "invoice_status",
            text: "Invoice status ",
            sortable: true,
            width: 100,
            sequence: 7,
          },
          {
            value: "invoice_nr",
            text: "Invoice Nr(s)",
            sortable: true,
            width: 100,
            sequence: 8,
          },
          {
            value: "remark",
            text: "Remark",
            sortable: true,
            width: 100,
            sequence: 9,
          },
          {
            value: "id",
            text: "",
            width: 100,
            sequence: 9,
            render: (text, record, index) => {
              return (
                <div onClick={() => this.editRow(record, this.dataForm, this.user_id)}>
                  <EditOutlined />
                </div>
              );
            },
          },
        ],
      },
    ],
  };
  rowSelectionChange = (key, selectedRows) => {
    this.setState((prevState) => ({
      data: { ...prevState.data, [key]: selectedRows },
    }));
  };
  handleChange = (value) => {
    this.setState({ file_type: value });
  };
  Unmatched = (data) => {
    if (data.length == 0) {
      showMessage("No status changed.", "Please select  at least one Record", "error");
      return;
    }
    var unmatched_data = null;
    if (data) {
      unmatched_data = data;
    }
    var name = null;
    if (data) {
      name = data.name;
    }
    var post_data = {
      unmatched_data: unmatched_data,
      user_id: this.user_id,
      data_id: this.state.id,
      coda_id: this.state.coda_id,
    };
    axios.post("/dt/payment/change_match_status/", post_data).then((response) => {
      if (response.data.code == 1) {
        showMessage("Status changed.", "Status changed as unmatch", "success");
        this.dataGridViewer.refresh();
      } else {
        showMessage("No status changed.", "You selected wrong row", "error");
      }
    });
  };
  exportXls = () => {
    var coda_id = this.state.coda_id;
    window.open("/dt/base/payment_export/?coda_id=" + coda_id);
  };
  exportXml = () => {
    var coda_id = this.state.coda_id;
    window.open("/dt/base/payment_export/?coda_id=" + coda_id + "&file_type=" + "xml");
  };

  editRow = (record) => {
    this.setState({ file_id: record.id });
    this.setState({ isModalVisible: true });
  };

  CloseInvoice = () => {
    
    let formData = new FormData();
    formData.append("payment_mode", this.state.payment_mode);
    formData.append("user_id", this.user_id);
    formData.append("paid_on", this.state.paid_on);
    formData.append("total_amount", this.state.total_payment_amount);
    formData.append("row_values",JSON.stringify(row_values))
    formData.append("currency_code",this.state.currency)
    formData.append("currency_rate",this.state.rate)
    formData.append("customer_id",this.state.customer_id)
    formData.append("ec_customer_id",this.state.ec_customer_id)
    row_values.push({customer_id:this.state.customer_id})

    
    if (total_payment_amount != new_payment && total_payment_amount >=0){
      showMessage("New amount total does not match with total payment", "", "error")
      return ;
    }else if(total_payment_amount != new_payment && total_payment_amount < 0){
      if(total_payment_amount != new_deference){
      showMessage("New amount total does not match with total payment", "", "error")
      return ;
      }
    }
    axios.post("/dt/sales/submit_close_invoice/coda/",formData , ).then((response) => {
      if(response.data.code=1){
        showMessage(response.data.message,"","success")
      }else{
        showMessage(response.data.message,"","success")
      }
    });

  }

  handleChange(value) {}
  closeInvoice = () => {
    if (this.state.radio_value === "Full") {
      var row_values = [];
      var rows = this.dataGridViewer.getDataSource();
      console.log(rows, "rows");
      for (var row in rows) {
        row_values.push({
          invoice_nr: rows[row].invoice_nr,
          total_amount: rows[row].amount,
          id: rows[row].id,
          bank_account_number: rows[row].bank_account_nr,
          amaunt: rows[row].amount,
          message: rows[row].message,
          customer_name: rows[row].name,
        });
      }
      let formData = new FormData();
      formData.append("id", row[0].id);
      formData.append("user_id", this.user_id);
      formData.append("file_name", this.props.file_name);
      formData.append("coda_id", this.state.coda_id);
      formData.append("row_values", JSON.stringify(row_values));

      axios.post("/dt/sales/close_coda_invoices/", formData).then((response) => {
        if ((response.data.code = 1)) {
          showMessage(response.data.message, "", "success");
          this.dataGridViewer.refresh();
        } else {
          showMessage(response.data.message, "", "error");
        }
      });
    } else {
      showMessage("Select invoice with full check.", "", "error");
    }
  };

  invoiceSearch = (data) => {
    if (data.length == 0) {
      showMessage("Select at least one row.", "(click on check box at the beginning of row to do so)", "error");
      return;
    }
    var name = null;
    if (data[0]) {
      name = data[0].name;
    }
    var invoice_status = null;
    if (data[0]) {
      invoice_status = data[0].invoice_status;
    }
    this.appModal.show({
      title: "Search Invoices: " + name,
      url: "/invoice/search_invoice/?name=" + name + "&is_model=true",
      style: { width: "90%", height: "85vh" },
    });
    return;
  };
  componentDidMount = () => {
    axios.get("/dt/payment/import_payment/xml_payment_import/?ids=" + this.state.coda_id).then((res) => {
      let data = res.data.data;
      this.setState({
        dataSource: data,
      });
    });
  };

  getData = () => {
    if (this.state.dataSource.length <= 0) {
      var rows = this.dataGridViewer.getDataSource();
      this.setState({
        dataSource: rows,
      });
    }
  };
  onChange = ({ target: { value } }) => {
    this.setState({
      radio_value: value,
    });
    var rows = this.state.dataSource;
    if ("Full" === value) {
      let result = rows.filter((gRow) => gRow.match === "Full");
      this.dataGridViewer.setDataSource(result);
    } else if ("Other" === value) {
      let result = rows.filter((gRow) => gRow.match !== "Full");
      this.dataGridViewer.setDataSource(result);
    } else {
      this.dataGridViewer.setDataSource(rows);
    }
  };

  uploadFile = () => {
    let formData = new FormData();
    formData.append("file", this.state.file);
    formData.append("user_id", this.user_id);
    formData.append("file_type", this.state.file_type);
    this.setState({ spinVisible: true });
    axios
      .post("/dt/payment/upload_payment_file/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
      .then((response) => {
        if (response.data.code == 0) {
          showMessage(response.data.message, "", "error");
          this.setState({ spinVisible: false });
          return;
        }
        this.setState({ coda_id: response.data.data });
        this.dataGridViewer.searchData({ ids: ["text", response.data.data] });
        showMessage(response.data.message, "", "success");
        this.setState({ spinVisible: false });
      });
  };
  handleOk = (e, data) => {
    let formData = new FormData();
    formData.append("remarks", e.remarks);
    formData.append("invoice_nr", e.invoice_nr);
    formData.append("coda_id", this.state.coda_id);
    formData.append("file_id", this.state.file_id);
    formData.append("user_id", this.user_id);
    axios.post("/dt/payment/update_payment_xml/", formData).then((response) => {
      if (response.data.code == 0) {
        this.setState({ isModalVisible: true });
        return;
      } else {
        this.setState({ isModalVisible: false });
        this.dataGridViewer.refresh();
        this.formRef.current.resetFields();
      }
    });
  };
  handleCancel = () => {
    this.setState({ isModalVisible: false });
  };

  upload = () => {
    if (this.state.file_name == "undefined") {
      this.setState({
        isDisabled: true,
      });
    } else {
      this.setState({
        isDisabled: false,
      });
    }
  };
  render() {
    const { value1 } = this.state;
    return (
      <div>
        <Spin tip="Fetching..." spinning={this.state.spinVisible} size="large" wrapperClassName="ant-layout-content">
          <Row>
            <ActionPanel buttons={this.uploadPaymentFileSchema.buttons} selectedRows={this.state.data[this.uploadPaymentFileSchema.listing[0].dataGridUID]} />
          </Row>
          <Row style={{ marginTop: 15, marginBottom: 10 }} justify="space-between">
            <Col>
              <Row>
                <Col>
                  <h4>Filter match</h4>
                </Col>
                <Col>
                  <Radio.Group options={plainOptions} onChange={this.onChange} value={this.state.radio_value} style={{ marginLeft: 10 }} />
                </Col>
              </Row>
            </Col>
            <Col>
              <Row justify="end">
                <Col>
                  <Select defaultValue="CODA" style={{ width: 130 }} onChange={this.handleChange}>
                    <Option value="CODA">CODA</Option>
                    <Option value="STA">BVCS</Option>
                    <Option value="CODADEFR">CODA (DE-FR)</Option>
                    <Option value="CAM">CAM</Option>
                    <Option value="UK940">UK940</Option>
                  </Select>
                </Col>
                <Col style={{ marginLeft: 10, marginRight: 10 }}>
                  <Input value={this.state.file_name} />
                </Col>
                <Col>
                  <Upload
                    onChange={this.upload}
                    showUploadList={false}
                    action={this.uploadPaymentFile}
                    beforeUpload={(file) => {
                      this.setState({ file_name: file.name, file: file });
                      const reader = new FileReader();
                      reader.onload = (e) => {};
                      return false;
                    }}
                  >
                    <Button>Browse</Button>
                  </Upload>
                </Col>
                <Col style={{ marginLeft: 10 }}>
                  <Button onClick={this.uploadFile} icon={<AppIcons code={"UploadOutlined"} />} disabled={this.state.isDisabled}>
                    Upload
                  </Button>
                </Col>
              </Row>
            </Col>
          </Row>
          <DataGridViewer
            schema={this.uploadPaymentFileSchema.listing[0]}
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
          <Modal title="" visible={this.state.isModalVisible} onOk={this.handleOk} onCancel={this.handleCancel} footer={null}>
            <Form labelCol={{ xs: { span: 6 } }} wrapperCol={{ xs: { span: 12 } }} ref={this.formRef} onFinish={this.handleOk} scrollToFirstError>
              <Form.Item name="remarks" label="Remarks">
                <Input />
              </Form.Item>

              <Form.Item name="invoice_nr" label="Invoice Nr(s)">
                <Input />
              </Form.Item>
              <Form.Item style={{ marginLeft: 200 }}>
                <Row>
                  <Col span={9} style={{ marginLeft: 0 }}>
                    <Button type="primary" htmlType="submit">
                      Save
                    </Button>
                  </Col>
                  <Col span={9} style={{ marginLeft: 20 }}>
                    <Button onClick={this.handleCancel}>Cancel</Button>
                  </Col>
                </Row>
              </Form.Item>
            </Form>
          </Modal>
        </Spin>
      </div>
    );
  }
}
UploadPaymentFile.getInitialProps = async (context) => {
  return { id: context.query.ids ?? "0", file_name: context.query.file_name, isModal: true };
};
export default UploadPaymentFile;
