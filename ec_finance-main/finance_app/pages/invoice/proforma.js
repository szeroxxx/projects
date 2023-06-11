
import PageTitle from "../../components/PageTitle";
import DataForm from "../../components/DataForm";
import React, { Component } from "react";
import AppModal from "../../components/AppModal";
import axios from "axios";
import {Modal, Radio, Button, Form, Row,  Col , Input  } from "antd";
import { showMessage } from "../../common/Util";
import SearchInput from "../../components/SelectInput";
const plainOptions = ['From invoice date', "First day of the month following invoice due date"];


class invoiceProforma extends Component {
  user_id = this.props.session.user.data.user_id;
  state = { data: {} };
  getPageListing = (status) => {
    this.setState({ status: status });
    let default_sort_col = "id";
    let default_sort_order = "descend";
      var listing = [
        {
          search: [
            { key: "invoice_number", label: "Invoice" },
            { key: "invoice_created_on", label: "From invoice date" },
            { key: "invoice_due_date", label: "Till invoice date" },
            { key: "order_nrs", label: "Order-Nr." },
            // { key: "", label: "PCB name" },
            { key: "invoice_value", label: "Invoice value" },
            // { key: "", label: "Username" },
            { key: "customer_name", label: "Customer" },
            { key: "country", label: "Country" },
            // { key: "", label: "Service" },
            { key: "hand_company", label: "Handling company" },
            { key: "root_company", label: "Root company" },
            { key: "address_line_1", label: "Address line 1" },
            { key: "address_line_2", label: "Address line 2" },
            { key: "postal_code", label: "Postal code" },
            { key: "city", label: "City" },
            { key: "phone", label: "Phone" },
            { key: "fax", label: "Fax" },
            { key: "vat_no", label: "VAT" },
            // { key: "", label: "Include deleted proforma" },
            // { key: "", label: "Outstanding only" },
          ],
          pre_view:[
          {doc:'deliverynote',label:"Delivery note",key:"delivery_no"},
          {doc:'invoice',label:"Invoice",key:"invoice_number"},
          ],
          dataGridUID: "invoiceProforma",
          url: "/dt/sales/search_invoice/",
          paging: true,
          default_sort_col: default_sort_col,
          default_sort_order: default_sort_order,
          row_selection: true,
          bind_on_load: true,
          onRow: (record, rowIndex) => {
            let bg = "";
            if (record.status == "Closed") {
              bg = "#F8FEF4";
            }
            return {
              style: {
                background: bg,
              },
            };
          },
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
                sortable: true,
                sequence: 1,
                width: 150,
              },
              {
                value: "customer_name",
                text: "Customer",
                sortable: true,
                width: 150,
              },
              {
                value: "delivery_no",
                text: "Delivery Nr.",
                sortable: true,
                width: 150,
              },
              {
                value: "customer_type",
                text: "Customer type",
                width: 150,
              },
              {
                value: "vat_no",
                text: "VAT",
                width: 100,
              },
              {
                value: "invoice_value",
                text: "Invoice value",
                width: 100,
              },
              {
                value: "status",
                text: "Status",
                width: 100,
              },
          ],
        },
      ]
      return listing;
  };
  getPageButtons = (status) => {
    var buttons = [];
    buttons.push(
      {
        dataGridUID: "invoiceProforma",
        name : "edit_profile",
        title :"Edit profile",
        icon_code: "UserOutlined",
        multi_select: false,
        click_handler: () => {
          var data = this.dataForm.getSelectedRows("invoiceProforma");
          this.editProfile(data);
        }
      },
      {
        dataGridUID:"invoiceProforma",
        name: "export_xls",
        title: "Export XLS",
        icon_code:"ExportOutlined",
        sequence: 2,
        click_handler: () => {
          this.exportXls();
      }
      },
      {
        dataGridUID:"invoiceProforma",
        name: "export_xml",
        title: "Export XML",
        icon_code:"ExportOutlined",
        sequence: 2,
        click_handler: () => {
          this.exportXml();
      }
      },
      {
        dataGridUID:"invoiceProforma",
        name: "export_csv",
        title: "Export CSV",
        icon_code:"ExportOutlined",
        sequence: 2,
        click_handler: () => {
          this.exportCsv();
      }
      },
      {

        dataGridUID:"invoiceProforma",
        name: "credit_limit",
        title: "Credit limit",
        position :"menu",
        icon_code: "EuroCircleOutlined",
        multi_select: false,
        click_handler :() => {
        this.setState({isCreditLimitModalVisible:true})
      }
      },
      {

        dataGridUID:"invoiceProforma",
        name: "credit_status",
        title: "Credit status",
        position :"menu",
        icon_code: "EuroCircleOutlined",
        multi_select:false,
        click_handler: () => {
          this.setState({ status: status });
          var data = this.dataForm.getSelectedRows("invoiceProforma");
          if (data.length == 0 ){
            showMessage("Select one.","Please select Record","error")
          }else{
          this.setState({customer_id:data[0].customer_id})
          this.appModal.show({ title: "Credit Status " , url: "/invoice/credit_status/?customer_id="+ data[0].customer_id + "&creditlimit=" + data[0].credit_limit +
         "&customercreditlimit=" + data[0].customer_credit_limit +
         "&cust_outstanding=" + data[0].customer_outstanding +"&ec_customer_id=" +
                data[0].ec_customer_id,style:{width:"90%", height:"70vh"} });
          }
        },
      },
      {
        dataGridUID:"invoiceProforma",
        name: "customer_login",
        title: "Customer Login",
        icon_code: "UserSwitchOutlined",
        sequence: 3,
        multi_select: false,
        click_handler: () => {
          var data = this.dataForm.getSelectedRows("invoiceProforma");
          this.customerLogin(data);
        }
      },
      {
        dataGridUID:"invoiceProforma",
        name: "change_status",
        title: "Change status",
        icon_code: "RetweetOutlined",
        position :"menu",
        multi_select: true,
        click_handler:() => {
          this.setState({ status: status });
          var data = this.dataForm.getSelectedRows("invoiceProforma");
          if (data.length == 0){
            showMessage("Select one.","Please select Record","error")
          }else{
          this.setState({invoice_number:data[0].invoice_number})
          this.setState({invoice_id:data[0].id})
          this.setState({isChangeModalVisible:true})
          }
        }

      },
      {
        dataGridUID:"invoiceProforma",
        name: "edit_invoice",
        title: "Edit Invoice",
        multi_select: false,
        position :"menu",
        icon_code: "EditOutlined",
        click_handler: () => {
          this.setState({ status: status });
          var data = this.dataForm.getSelectedRows("invoiceProforma");
          this.editInvoice(data)
        },
      },
      {
        dataGridUID:"invoiceProforma",
        name : "close_invoice",
        title :"Close invoice",
        icon_code:"FileDoneOutlined",
        multi_select: true,
        click_handler: () => {
          var data = this.dataForm.getSelectedRows(status);
          var customers = []
          for (let i in data){
            customers.push(data[i].customer_id)
          }
          const is_same_customer = arr => arr.every( (val, i, arr) => val === arr[0] )
          if (is_same_customer(customers) == false){
            showMessage("Not allowed.","Select invoices for one customer at a time","error")
            return;
          }
          if(data[0].status =="Closed" ){
          confirm({
            title: "This invoice" + " "+ data[0].invoice_number + " " + "is already closed ",
            icon: <></>,
            content: <>Are you sure you want to close it again ?</>,
            cancelText: "No, Cancel",
            okText: "Yes, Close",
            onOk : ()=> {
            this.setState({ status:status });
            this.closeInvoice(data)
            },
            onCancel() {
            },
          });
        }else{
            this.setState({ status: status });
            var data = this.dataForm.getSelectedRows(status);
            this.closeInvoice(data)
        }
        },
      },
      {
        dataGridUID: "invoiceProforma",
        name: "history",
        title: "History",
        icon_code: "HistoryOutlined",
        position:"menu",
        multi_select:true,
        click_handler: () => {
          this.setState({ status: status });
          var data = this.dataForm.getSelectedRows("invoiceProforma");
          this.appModal.show({ title: "Invoice History: "+ data[0].invoice_number, url: "/invoice/invoice_history/?id=" + data[0].id ,style:{width:"90%", height:"70vh"} });
        },
      },
    );
    return buttons;
  };
  appSchema = {
    pageTitle: "Proforma",
    formSchema: {
      init_data: {},
      on_submit: {},
      edit_button: false,
      submit_button: false,
      hide_buttons: false,
      disabled: true,
      readonly: false,
      buttons_position: "top",
      buttons: this.getPageButtons("invoiceProforma"),
      listing: this.getPageListing("invoiceProforma"),
    },
  };
  refresh=()=>{
    this.dataForm.refreshTable();
  }
  editProfile = (data)=>{
    var ec_customer_id = null
    if (data[0]){
      ec_customer_id = data[0].ec_customer_id
    }
    var customer_name = null
    if (data[0]){
      customer_name = data[0].customer_name
    }
    var post_data = {
      ec_customer_id : ec_customer_id
    }
    axios.post("/dt/customer/edit_profile/", post_data).then((response) => {
      if (response.data.code == 1) {
        console.log(response.data.data);
         this.appModal.show(
              {
                url: response.data.data,
                title:"Edit Profile :" + " "+ customer_name,
                style:{width:"90%", height:"85vh"}
              });
        return;
      }
    });
  }
  exportXls = ()=>{
    var data = this.dataForm.getDataSource("invoiceProforma")
    var ids = ""
    for (var row in data){
      ids = ids + data[row].id +","
    }
    window.open("/dt/base/proforma_invoice_export/?invoice_id=" + ids + "&file_type=" + "xls")
  }
  exportXml = ()=>{
    var data = this.dataForm.getDataSource("invoiceProforma")
    var ids = ""
    for (var row in data){
      ids = ids + data[row].id +","
    }
    window.open("/dt/base/proforma_invoice_export/?invoice_id=" + ids + "&file_type=" + "xml")
  }
  exportCsv = ()=>{
    var data = this.dataForm.getDataSource("invoiceProforma")
    var ids = ""
    for (var row in data){
      ids = ids + data[row].id +","
    }
    window.open("/dt/base/proforma_invoice_export/?invoice_id=" + ids + "&file_type=" + "csv")
  }
  customerLogin = (data) => {
    var ec_customer_id = null
    if (data[0]){
      ec_customer_id = data[0].ec_customer_id
    }
    axios.post("/dt/customer/customer_login/", {ec_customer_id : ec_customer_id}).then((response) => {
      if(response.data.code == 1){

        window.open(response.data.data.url)
      }
    });
  }
  closeInvoice = (data) => {
    var  invoice_ids = ""
    for (var row in data) {
      invoice_ids = invoice_ids + data[row].id +','
    }
        this.appModal.show({
          title: "Close Invoice: "+ data[0].invoice_number,
          url: "/invoice/close_invoice/?ids="+invoice_ids.slice(0, -1)+"&user_id="+this.user_id,
          style:{width:"90%", height:"70vh"}
        });
  }
  editInvoice = (data) => {
    var  invoice_id =  data[0].id
    var invoice_number = data[0].invoice_number
    this.appModal.show({
      title: "Edit Invoice:" +" "+ invoice_number,
      url: "/invoice/edit_invoice/?ids="+invoice_id+"&user_id="+this.user_id,
      style:{width:"90%", height:"80vh"}
    });
  }
  changeStatus_handleChange = (row) => {
    this.setState({ status_id : row});
  };
  updateStatus = () => {
    var post_data = {
       user_id : this.user_id,
       status_id : this.state.status_id,
       invoice_number : this.state.invoice_number,
       invoice_id : this.state.invoice_id,
       }
        axios.post('/dt/sales/change_invoice_status/', post_data).then((response) => {
            if (response.data.data == 0) {
              showMessage("Status updated.","Status successfully updated","success")
              this.setState({isChangeModalVisible	:false})
              this.dataForm.refreshTable(this.state.status);
            }else{
              showMessage("No update.","Something went wrong","error")
            }
      },)
  }
  refresh=()=>{
    this.dataForm.refreshTable();
  }
  handleCancel = () =>{
    this.setState({isCreditLimitModalVisible :false})
    this.setState({isChangeModalVisible	:false})
  }
  componentDidMount = () => {
  };
  render() {
    return (
      <div >
        <PageTitle pageTitle={this.appSchema.pageTitle}></PageTitle>
        <DataForm
          schema={this.appSchema}
          initData={this.state}
          ref={(node) => {
            this.dataForm = node;
          }}
        ></DataForm>
        <AppModal
          callBack={this.onModelClose}
          ref={(node) => {
            this.appModal = node;
          }}
        ></AppModal>
        <Modal
          title="Credit limit"
          visible={this.state.isCreditLimitModalVisible}
          onOk={this.handleOk}
          onCancel={this.handleCancel}
          footer={null}>
          <Form >
          {/* labelCol={{ xs: { span: 6 } }} wrapperCol={{ xs: { span: 12 } }} form={this.form} onFinish={this.handleOk} scrollToFirstError */}
            <Form.Item style={{marginLeft:20}}>
            <h3 style={{marginLeft:0}}>Credit limit level-Customer Level</h3><br/>
            <Row>
              <Col span={10}>
                <p>Base system</p>
              </Col>
              <Col span={6}>
                <Input placeholder="500.00" style={{width:100}}/>
              </Col>
              <Col span={3} style>
                <p>EUR</p >
              </Col>
            </Row>
            <Row>
              <Col span={10} style>
                <p>Base Graydon Credit limit</p >
              </Col>
              <Col span={6}>
                <Input placeholder="500.00" style={{width:100}}/>
              </Col>
              <Col span={3} style>
                <p>EUR</p >
              </Col>
            </Row><br/>
            <h3>Invoice due date</h3><br/>
            <Row>
              <Col span={10}>
                <p>Days starting</p>
              </Col>
              <Col span={12}>
                <Input placeholder="30" style={{width:50}}/>
              </Col>
            </Row>
            <Row>
              <Radio.Group options={plainOptions} onChange={this.onChange} defaultValue="All" style={{marginLeft:10}} />
            </Row><br/>
            <Row>
              <Col span={4} style={{marginLeft:0}}>
                 <Button type="primary" htmlType="submit" >
                 Save
                 </Button>
              </Col>
              <Col span={4} style={{marginLeft:0}}>
                 <Button onClick={this.handleCancel}>
                  Cancel
                 </Button>
               </Col>
             </Row>

           </Form.Item>
           </Form>
        </Modal>
        <Modal
          title="Change status"
          visible={this.state.isChangeModalVisible}
          onOk={this.handleOk}
          onCancel={this.handleCancel}
          footer={null}>
          <Form labelCol={{ xs: { span: 6 } }} wrapperCol={{ xs: { span: 12 } }} form={this.form} onFinish={this.handleOk} scrollToFirstError>
            <Form.Item style={{marginLeft:20}}>
            <Form.Item className="collection-input" >
            <SearchInput placeholder="Status"  handleChange={this.changeStatus_handleChange}  fieldProps={{mode:"single",datasource:{query:"/dt/base/lookups/change_status/"}}} style={{width:300}}></SearchInput>
            </Form.Item>
            <Row>
              <Col span={9} style={{marginLeft:0}}>
                 <Button type="primary" htmlType="submit" onClick={this.updateStatus}>
                 Save
                 </Button>
              </Col>
              <Col span={9} style={{marginLeft:20}}>
                 <Button onClick={this.handleCancel}>
                  Cancel
                 </Button>
               </Col>
             </Row>
           </Form.Item>
           </Form>
        </Modal>
      </div>
    );
  }
}
invoiceProforma.getInitialProps = async (context) => {
  return { creditlimit:context.query.creditlimit,customercreditlimit:context.query.customercreditlimit,cust_outstanding:context.query.cust_outstanding};
};
export default invoiceProforma;