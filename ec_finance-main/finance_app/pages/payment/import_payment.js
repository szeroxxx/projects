import { DeleteOutlined, ExclamationCircleOutlined } from "@ant-design/icons";
import { Modal, Tooltip } from "antd";
import axios from "axios";
import React, { Component } from "react";
import { showMessage } from "../../common/Util";
import AppModal from "../../components/AppModal";
import DataForm from "../../components/DataForm";
import PageTitle from "../../components/PageTitle";
const { confirm } = Modal;
class PaymentImport extends Component {
  constructor(props) {
    super(props);
  }
  user_id = this.props.session.user.data.user_id;
  state = { data: {} };
  getPageListing = (status) => {
    this.setState({ status: status });
    let default_sort_col = "id";
    let default_sort_order = "descend";
    var listing = [
      {
        search: [
          { key: "created_on", label: "Created on", searchType: "datetime" },
          { key: "file_name", label: "File name" },
        ],
        dataGridUID: "tblImportPayment",
        url: "/dt/payment/import_payment/",
        paging: true,
        default_sort_col: default_sort_col,
        default_sort_order: default_sort_order,
        row_selection: true,
        bind_on_load: true,
        columns: [
          {
            value: "id",
            text: "ID",
            show: false,
            row_key: true,
            sequence: 1,
          },
          {
            value: "file_name",
            text: "File name",
            sortable: true,
            width: 100,
            sequence: 2,
          },
          {
            value: "created_on",
            text: "Created date",
            sortable: true,
            width: 100,
            sequence: 3,
          },
          {
            value: "full_name",
            text: "Created by",
            sortable: true,
            width: 100,
          },
          {
            value: "id",
            text: "",
            width: 100,
            render: (record) => {
              return (
                <div className="deleteIcon" onClick={() => this.deletePayment(record, this.refresh)}>
                  <Tooltip placement="top" title="delete">
                    <DeleteOutlined />
                  </Tooltip>
                </div>
              );
            },
          },
        ],
      },
    ];
    return listing;
  };

  getPageButtons = () => {
    var buttons = [];
    buttons.push(
      {
        dataGridUID: "tblImportPayment",
        name: "veiw_detail",
        title: "View detail",
        primary: "primary",
        icon_code: "ProfileOutlined",
        tooltip: "",
        sequence: 1,
        multi_select: false,
        click_handler: () => {
          var data = this.dataForm.getSelectedRows("tblImportPayment");
          this.viewDetail(data);
        },
      },
      {
        dataGridUID: "tblImportPayment",
        name: "upload",
        title: "Upload",
        primary: "primary",
        icon_code: "UploadOutlined",
        type: "primary",
        tooltip: "",
        sequence: 2,
        click_handler: () => {
          this.appModal.show({ title: "Upload File", url: "/payment/upload_payment_file/?ids=0", style: { width: "95%", height: "90vh" } });
        },
      }
    );
    return buttons;
  };

  appSchema = {
    pageTitle: "Payment Import",
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
      listing: this.getPageListing("all"),
      buttons: this.getPageButtons("all"),
    },
  };
  viewDetail = (data) => {
    var ids = data[0].id;
    this.appModal.show({
      title: "Veiw Detail: " + data[0].file_name,
      url: "/payment/upload_payment_file/?ids=" + ids + "&user_id=" + this.user_id + "&file_name=" + data[0].file_name,
      style: { width: "100%", height: "90vh" },
    });
  };

  refresh = () => {
    this.dataForm.refreshTable("tblImportPayment");
  };
  deletePayment = (data, callback) => {
    confirm({
      title: "Are you sure want to delete this record?",
      icon: <ExclamationCircleOutlined />,
      content: <></>,
      cancelText: "No, Cancel",
      okText: "Yes, Delete",
      onOk() {
        axios.post("/dt/payment/import_payment/delete_payment/", { ids: data }).then((response) => {
          if (response.data.code == 1) {
            showMessage("Deleted.", "successfully deleted", "success");
            callback();
          } else {
            showMessage("No deleted.", "Something went wrong", "error");
          }
        });
      },
      onCancel() {},
    });
  };
  render() {
    return (
      <div>
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
      </div>
    );
  }
}
PaymentImport.getInitialProps = async (context) => {
  return { file_name: context.query.file_name, isModal: false };
};
export default PaymentImport;
