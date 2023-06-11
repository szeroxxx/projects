import AppLayout from "../../components/AppLayout";
import PageTitle from "../../components/PageTitle";
import React, { Component } from "react";
import moment from 'moment';
import AppModal from "../../components/AppModal";
import axios from "axios";
import DataGridViewer from "../../components/DataGridViewer";
import ActionPanel from "../../components/ActionPanel";
import { Tabs,  Row, Col,  Form, Input,  Select, Modal, DatePicker, notification} from "antd";
import { format } from 'date-fns'
import SearchInput from "../../components/SelectInput";
import { showMessage } from "../../common/Util";
const { TabPane } = Tabs;
const { Option } = Select;
const { confirm } = Modal;
const includeSelectData =[
{ value: "0", label: "0 days" },
{ value: "7", label: ">7 days" },
{ value: "14", label: ">14 days" },
{ value: "21", label: ">21 days" },
{ value: "30", label: ">30 days" },
]
const ExcludeSelectData =[
  { value: "0", label: "0 days" },
  { value: "7", label: "<7 days" },
  { value: "14", label: "<14 days" },
  { value: "21", label: "<21 days" },
  { value: "30", label: "<30 days" },
  ]

class SchedulePaymentReminder extends Component {
  constructor(props) {
    super(props);
  }
  user_id = this.props.session.user.data.user_id;
  state = { data: {} , handling_company:[],hand_company:7230,invoice_create:'2014-01-01',include_days:7,exclude_days:7,isPDF:true,country_id:75};
  appSchema = {
    pageTitle: "Scheduler payment reminder",
    buttons: [
      {
        name: "load",
        title: "Load",
        primary: "primary",
        icon_code:"ReloadOutlined",
        type: "primary",
        sequence: 1,
        click_handler: () => {
          this.importScheduler();
        },
      },
      {
        name: "exclude",
        title: "Exclude",
        primary: "primary",
        icon_code: "MinusCircleOutlined",
        tooltip: "",
        sequence: 2,
        multi_select: true,
        click_handler: () => {
          var data = this.dataGridViewer.getDataSource()
          var selectRows = this.dataGridViewer.getSelectedRows();
          this.excludeSchedule(selectRows)
        },
      },
      {
        name: "schedule",
        title: "Schedule",
        primary: "primary",
        tooltip: "",
        icon_code: "FieldTimeOutlined",
        multi_select:true,
        sequence: 3,
        click_handler: () => {
          var data = this.dataGridViewer.getDataSource()
          this.createScheduler(data)
        },
      },
    ],
    listing: [
      {
        dataGridUID: "schedulePaymentReminder",
        url: "/dt/sales/schedule_payment_reminder/",
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
            value: "customer_name",
            text: "Customer",
            sortable: true,
            width: 200,
            sequence: 2,
          },
          {
            value: "invoice_number",
            text: "Invoice Nr.",
            sortable: true,
            width: 200,
            sequence: 3,
          },
          {
            value: "created_on",
            text: "Invoice date",
            sortable: true,
            sequence: 3,
            width: 200,
          },
          {
            value: "company_name",
            text: "Company name",
            sortable: true,
            width: 200,
          },
          {
            value: "outstanding",
            text: "Outstanding amount",
            sortable: true,
            width: 200,
          },
          {
            value: "customer_outstanding",
            text: "Currency outstanding amount",
            sortable: true,
            width: 200,
          },
          {
            value: "outstanding_days",
            text: "Outstanding Days",
            sortable: true,
            width: 200,
          },
          {
            value: "invoice_due_date",
            text: "Invoice due date",
            sortable: true,
            width: 200,
          },
          {
            value: "invoice_value",
            text: "Invoice value",
            sortable: true,
            width: 200,
            sortable: true,
          },
          {
            value: "currency_invoice_value",
            text: "Currency invoice value",
            width: 200,
            sortable: true,
          },
          {
            value: "amount_paid",
            text: "Amount paid",
            width: 200,
            sortable: true,
          },
          {
            value: "cust_amount_paid",
            text: "Currency amount paid",
            width: 200,
            sortable: true,
          },
          {
            value: "",
            text: "Paid on",
            width: 200,
            sortable: false,
          },
          {
            value: "reminder_status",
            text: "Reminder status",
            width: 200,
            sortable: true,
          },
          {
            value: "last_rem_date",
            text: "Reminder date",
            width: 200,
            sortable: true,
          },
          {
            value: "currency_symbol",
            text: "Currency symbol",
            width: 200,
            sortable: true,
          },
          {
            value: "",
            text: "Invoice id",
            width: 200,
            sortable: true,
            show: false,
          },
          {
            value: "",
            text: "Company id",
            width: 200,
            sortable: true,
            show: false,
          },
          {
            value: 'customer__id',
            text: 'Customer id',
            width: 200,
            show: false
          }
        ],
      },
    ],
  };
  handleChanges = selectedOption => {
    this.setState({ selectedOption });
  };
  handleChangeCountry = (country_id, obj) => {
    this.setState({ country_id });
  };
  handleChangeDate = date => {
    var formatdate = format(new Date(date), 'yyyy/mm/dd HH:MM')
    this.setState({ formatdate });
  };
  handleChangeExcDays = (exclude_days, obj) => {
    this.setState({ exclude_days });
  };
  handleChangeIncDays = (include_days, obj) => {
    this.setState({ include_days });
  };
  handleChangeStatus =(status, obj) => {
    this.setState({ status });
  };
  company_handleChange = (hand_company, obj) => {
    this.setState({ hand_company });
  }
  onCheck = (isPDF,obj) =>{
    var isPDF = isPDF.target.checked
    this.setState({ isPDF });
  }
  importScheduler = () => {
    this.dataGridViewer.searchData(
      {
        handling_company:['text',this.state.hand_company] ?? null,
        country_id:['text',this.state.country_id] ?? null,
        invoice_create_on:['date',this.state.invoice_create] ?? null,
        exclude_days:['text',this.state.exclude_days] ?? null,
        include_days:['text',this.state.include_days] ?? null,
        status:['text',this.state.status]  ?? null,
        is_pdf_include:["text",this.state.isPDF],
      }
      )
  }
  showMessage=(type,message)=>{
    notification[type](message);
  }
  excludeSchedule = (data) => {
    if (data.length==0){
      this.showMessage("error", { message: "Please select at least one record" });
      return ;
    }
    confirm({
      title: "Exclude invoices",
      content: <>Are you sure you want to exclude selected Invoice(s)?</>,
      okText: "Yes, Exclude",
      cancelText: "No, Cancel",
      onOk: () => {
        var rows = this.dataGridViewer.getDataSource()
        var selectRows = this.dataGridViewer.getSelectedRows()
        let result = rows.filter(gRow => !selectRows.some(sRow => gRow.id === sRow.id));
        this.dataGridViewer.setDataSource(result)
      },
    },)
  }
  createScheduler = (object) => {
    var selectedRows = this.dataGridViewer.getSelectedRows()
    if (selectedRows.length==0){
      this.showMessage("error", { message: "Please select at least one record" });
      return ;
    }
    var value = ''
    var invoice_nr = ''
    var total_items = 0
    for (var row in selectedRows) {
      value = value + selectedRows[row].customer__id + ','
      invoice_nr = invoice_nr + selectedRows[row].id + ','
      total_items = total_items + 1
    }
    var post_data = {
      customer_ids: value.slice(0, -1),
       invoice_id: invoice_nr.slice(0, -1),
       total_items:total_items,
       is_pdf_include:this.state.isPDF,
       user_id : this.user_id
       }
       confirm({
        title: "Reminder schedule",
        content: <>Invoice payment reminder will be scheduled, are you sure you want to continue?</>,
        okText: "Yes, Schedule ",
        cancelText: "No, Cancel",
        onOk: () => {
          axios.post('/dt/sales/reminder/', post_data).then((response) => {
            if (response.data.data == 0) {
              showMessage("","Invoices are scheduled","success")
            }else{
              showMessage("No sent schedule.","Please select specific row","error")
            }
          })
        },
      },)
  }
  rowSelectionChange = (key, selectedRows) => {
    this.setState((prevState) => ({
      data: { ...prevState.data, [key]: selectedRows },
    }));
  };

  componentDidMount = () => {
  };
  render() {
    return (
      <div className="extra-fields">
        <PageTitle pageTitle={this.appSchema.pageTitle}></PageTitle>
         <Row>
          <Col span={6} style={{cursor: "pointer"}}>
            <Form.Item className="collection-input">
            <SearchInput placeholder="Handling company"  value={"Eurocircuits GmbH - CONR"} handleChange={this.company_handleChange}  fieldProps={{mode:"single",datasource:{query:"/dt/base/lookups/hand_company/"}}} style={{width:300}}></SearchInput>
            </Form.Item>
          </Col>
          <Col span={6}>
          {/* <Form.Item label="Country"> */}
          <Form.Item className="collection-input">
          <SearchInput  placeholder="Country" value={"Algeria"} handleChange={this.handleChangeCountry}  fieldProps={{mode:"single",datasource:{query:"/dt/base/lookups/country/"}}} style={{width:300}}></SearchInput>
          </Form.Item>
          </Col>
          <Col span={6}>
            <Form.Item className="collection-input">
            <SearchInput placeholder="Include invoice if overdue with" value={"7"} handleChange={this.handleChangeIncDays} fieldProps={{mode:"single",datasource:{data:includeSelectData}}} style={{width:300 }}></SearchInput>
            </Form.Item>
          </Col>
        <Col span={6}>
          <Form.Item className="collection-input" >
          <SearchInput placeholder="Exclude when last reminder sent " value={"7"} handleChange={this.handleChangeExcDays} fieldProps={{mode:"single",datasource:{data:ExcludeSelectData}}} style={{width:300 }}></SearchInput>
          </Form.Item>
        </Col>
        </Row>
      <Row >
        <Col span={3}>
          <Form.Item className="collection-input">
            <SearchInput  value={"ALL"} handleChange={this.handleChangeStatus} fieldProps={{mode:"single",datasource:{data:[{ value: "ALL", label: "All" },{ value: "INVPENDING", label: "Pending" }]}}} style={{width:150,margin:0 }}></SearchInput>
          </Form.Item>
        </Col>
        <Col span={7} offset={1} >
          <Form.Item label="Include invoice PDF" className="collection-input">
              <Input type={'checkbox'} defaultChecked={true} primary={"primary"} onChange={this.onCheck}></Input>
          </Form.Item>
        </Col>
        <Col span={13}>
            <Form.Item label="Exclude invoice before date" value={this.state.value}>
            <DatePicker defaultValue={moment('2014-01-01')} onChange={(e) => {
              if (e != null){
                  this.setState({ invoice_create: format(new Date(e._d), 'yyyy-MM-dd') });
                }
              }
              }
                ></DatePicker>
            </Form.Item>
          </Col>
        {/* <Col span={8}>
          <ActionPanel  buttons={this.appSchema.buttons} selectedRows={this.state.data[this.appSchema.listing[0].dataGridUID]}  />
        </Col> */}
      </Row>
      <Row className="sheduler-btn">
        <Col span={4} offset={20}>
          <ActionPanel buttons={this.appSchema.buttons} selectedRows={this.state.data[this.appSchema.listing[0].dataGridUID]}  />
        </Col>
      </Row>
        <DataGridViewer
          schema={this.appSchema.listing[0]}
          onRowSelectionChange={this.rowSelectionChange}
          ref={(node) => {
            this.dataGridViewer = node;
          }}
        ></DataGridViewer>
          <AppModal
           callBack = {this.onModelClose}
          ref={(node) => {
            this.appModal = node;
          }}
        >
      </AppModal>
      </div>
    );
  }
}
export default SchedulePaymentReminder;
