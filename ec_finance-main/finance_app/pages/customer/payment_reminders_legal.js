import React, { Component } from "react";
import AppModal from "../../components/AppModal";
import DataForm from "../../components/DataForm";
import PageTitle from "../../components/PageTitle";
import SearchInput from "../../components/SelectInput";

import axios from "axios";
class LegalActions extends Component {
  constructor(props) {
    super(props);
  }
  user_id = this.props.session.user.data.user_id;
  state = { data: {}, status: "pending", is_model: this.props.isModal, slot: this.props.slot };
  getPageButtons = (status) => {
    var buttons = [];
    if (status != "all" && status != "finished") {
      buttons.push(
        {
          name: "finish",
          title: "Finish",
          primary: "primary",
          tooltip: "",
          sequence: 1,
          icon_code: "CheckCircleOutlined",
          multi_select: false,
          confirm: {
            title: "Do you really want to mark this invoice(s) as finished?",
            content: <>Invoices for a specific customer will be moved to 'Finished' status.</>,
            okText: "Yes, Move to Finish",
            cancelText: "No, Cancel",
            onOk: () => {
              this.finish(status);
            },
          },
        },
        {
          name: "add_call_report",
          title: "Add Call Report",
          primary: "primary",
          type: "primary",
          tooltip: "",
          icon_code: "ReadOutlined",
          sequence: 1,
          multi_select: false,
          click_handler: () => {
            var data = this.dataForm.getSelectedRows(status);
            this.setState({ status: status });
            this.appModal.show({
              title: "Add Action: " + data[0].customer_name + " - " + data[0].invoice_number,
              url: "/customer/action/" + data[0].customer_id + "/" + data[0].id + "?is_legal=true",
              style: { width: "80%", height: "70vh" },
            });
            // Router.push('/customer/collection_action/'+data[0].customer_id+'/'+data[0].id+"?c="+data[0].customer_name);
          },
        }
      );
    }
    buttons.push({
      name: "view_history",
      title: "History",
      tooltip: "",
      icon_code: "HistoryOutlined",
      sequence: 1,
      multi_select: false,
      click_handler: () => {
        this.setState({ status: status });
        var data = this.dataForm.getSelectedRows(status);
        this.appModal.show({
          title: "History: " + data[0].invoice_number,
          url: "/customer/history/?id=" + data[0].id,
          style: { width: "60%", height: "70vh" },
        });
      },
    });
    return buttons;
  };
  getPageListing = (status) => {
    this.setState({ status: status });
    let default_sort_col = "id";
    if (status == "due" || status == "done" || status == "legal_action" || status == "all") {
      default_sort_col = "action_date";
    }
    var listing = [
      {
        search: [
          { key: "invoice_number", label: "Invoice" },
          { key: "country", label: "Country" },
          { key: "customer_name", label: "Customer" },
          { key: "action_date", label: "Action date", searchType: "datetime", is_advanced: true },
          { key: "invoice_created_on", label: "Invoice date", searchType: "datetime", is_advanced: true },
        ],
        pre_view: [{ doc: "invoice", label: "Invoice", key: "invoice_number" }],
        dataGridUID: this.props.status ? this.props.status : status,
        url: "/dt/sales/legal_actions/?status=" + status,
        paging: true,
        default_sort_col: default_sort_col,
        default_sort_order: "descend",
        row_selection: true,
        bind_on_load: this.props.isModal && this.props.status == status ? false : true,
        gridViewer: this.props.isModal ? true : undefined,
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
            value: "customer_name",
            text: "Customer",
            sortable: true,
            sequence: 3,
            width: 200,
          },
          {
            value: "invoice_number",
            text: "Invoice number",
            sortable: true,
            sequence: 2,
            width: 150,
            modal: {
              url: "/customer/legal_action/",
              title_key: ["customer_name", "invoice_number"],
              params: ["customer_id", "id"],
              queryParams: [{ key: "customer_name" }],
            },
          },
          {
            value: "status",
            sortable: true,
            text: "Invoice status",
            width: 120,
            render: (text, record) => (
              <>
                {record.status == "Closed" && <span className="color-green">{record.status}</span>}
                {record.status != "Closed" && <span>{record.status}</span>}
              </>
            ),
          },
          {
            value: "secondary_status",
            sortable: true,
            text: "Secondary status",
            width: 150,
          },
          {
            value: "email",
            text: "Email",
            sortable: true,
            width: 80,
          },
          {
            value: "contact",
            text: "Phone",
            sortable: true,
            width: 80,
          },
          {
            value: "action_status",
            sortable: true,
            text: "Action status",
            width: 120,
          },
          {
            value: "action_date",
            sortable: true,
            text: "Action date",
            width: 170,
            searchable: true,
            type: "datetime",
          },
          {
            value: "country",
            sortable: true,
            text: "Country",
            width: 100,
          },
          {
            value: "last_reminder_date",
            sortable: true,
            text: "Last reminder date",
            width: 200,
            searchable: true,
            type: "datetime",
          },
          {
            value: "total_reminder",
            sortable: true,
            text: "Total reminder(s)",
            width: 150,
          },
          {
            value: "invoice_created_on",
            sortable: true,
            text: "Invoice date",
            width: 160,
            searchable: true,
            type: "datetime",
          },
          {
            value: "amount_paid",
            sortable: true,
            text: "Amount paid",
            width: 150,
          },
          {
            value: "invoice_amount",
            sortable: true,
            text: "Invoice amount",
            width: 150,
          },
          {
            value: "customer_id",
            show: false,
            text: "customer_id amount",
          },
          {
            value: "id",
            text: "Report",
            sortable: false,
            width: 100,
            modal: {
              url: "/customer/legal_action/",
              title_key: ["customer_name", "invoice_number"],
              text: "View",
              params: ["customer_id", "id"],
              queryParams: [{ key: "customer_name" }, { key: "is_legal", value: true }],
            },
          },
        ],
      },
    ];
    return listing;
  };
  showMessage = (data) => {
    alert(data);
  };
  onModelClose = () => {
    this.dataForm.refreshTable(this.state.status);
  };
  finish = (gridID) => {
    var selectedRows = this.dataForm.getSelectedRows(gridID);
    var value = "";
    for (var row in selectedRows) {
      value = value + selectedRows[row].id + ",";
    }
    axios.post("/dt/sales/scheduler/finish_invoice/", { ids: value.slice(0, -1), user_id: this.user_id }).then((response) => {
      if (response.data.code == 0) {
        this.dataForm.showMessage("error", { message: "Failed!", description: response.data.message });
        return;
      }
      this.dataForm.showMessage("success", { message: "Success!", description: response.data.message });
      this.dataForm.refreshTable(gridID);
    });
  };
  appSchema = {
    pageTitle: "Payment reminders (Legal)",
    formSchema: {
      init_data: {},
      on_submit: {},
      edit_button: false,
      submit_button: false,
      hide_buttons: false,
      disabled: true,
      readonly: false,
      columns: 2,
      buttons_position: "top",
      tabs: [
        {
          UID: "tab_1",
          label: "New",
          buttons: this.getPageButtons("pending"),
          listing: this.getPageListing("pending"),
        },
        {
          UID: "tab_2",
          label: "Follow ups",
          buttons: this.getPageButtons("due"),
          listing: this.getPageListing("due"),
        },
        {
          UID: "tab_3",
          label: "Processed",
          buttons: this.getPageButtons("done"),
          listing: this.getPageListing("done"),
        },

        {
          UID: "tab_4",
          label: "Finished",
          buttons: this.getPageButtons("finished"),
          listing: this.getPageListing("finished"),
        },
        {
          UID: "tab_7",
          label: "Closed",
          buttons: this.getPageButtons("closed"),
          listing: this.getPageListing("closed"),
        },
        {
          UID: "tab_5",
          label: "All",
          buttons: this.getPageButtons("all"),
          listing: this.getPageListing("all"),
        },
      ],
    },
  };
  componentDidMount = () => {
    this.searchValue();
  };
  searchValue = () => {
    if (this.state.slot !== undefined) {
      if (this.props.country == "All") {
        this.dataForm.searchData(this.props.status, {
          slot: ["text", this.state.slot],
        });
      } else {
        this.dataForm.searchData(this.props.status, {
          country: ["text", this.props.country],
          slot: ["text", this.state.slot],
        });
      }
    }
    this.setState({ slot: undefined });
  };
  render() {
    return (
      <div IsModel={this.props.isModal}>
        <PageTitle pageTitle={this.appSchema.pageTitle}></PageTitle>
        <DataForm
          schema={this.appSchema}
          activeTab={this.props.index}
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
      </div>
    );
  }
}
LegalActions.getInitialProps = async (context) => {
  return {
    isModal: context.query.is_model ?? false,
    status: context.query.status,
    country: context.query.country__name,
    index: context.query.index,
    slot: context.query.slot,
  };
};

export default LegalActions;
