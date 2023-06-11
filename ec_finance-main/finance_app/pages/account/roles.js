import DataGridViewer from "../../components/DataGridViewer";
import AppLayout from "../../components/AppLayout";
import PageTitle from "../../components/PageTitle";
import ActionPanel from "../../components/ActionPanel";
import AppModal from "../../components/AppModal";
import React, { Component } from "react";
import { showMessage } from "../../common/Util";
import { FinMessage } from "../../common/Util";
class Roles extends Component {
  state = { data: {}, visible: false };
  appSchema = {
    pageTitle: "Roles",
    buttons: [
      {
        name: "new_role",
        title: "Add new",
        type: "primary",
        icon_code: "FileProtectOutlined",
        tooltip: "",
        sequence: 1,
        click_handler: () => {
          this.appModal.show({
            title: "Role permission",
            url: "/account/role/",
            style: { width: "80%" },
          });
        },
      },
      {
        name: "edit",
        title: "Edit",
        icon_code: "EditOutlined",
        tooltip: "",
        sequence: 2,
        click_handler: () => {
          var data = this.dataGridViewer.getSelectedRows();
          this.appModal.show({
            title: "Role permission",
            url: "/account/role/?role_name=" + data[0].name + "&role_id=" + data[0].id,
            style: { width: "80%" },
          });
        },
        multi_select: false,
      },
    ],
    listing: [
      {
        search: [{ key: "role", label: "Role" }],
        dataGridUID: "roles",
        url: "/dt/accounts/roles/",
        paging: true,
        default_sort_col: "id",
        default_sort_order: "descend",
        row_selection: true,
        bind_on_load: true,
        columns: [
          {
            row_key: true,
            value: "id",
            show: false,
          },
          {
            value: "name",
            text: "Role",
            sortable: true,
            width: 300,
          },
        ],
      },
    ],
  };
  componentDidMount = () => {
    // call function if needed on component load.
  };
  onDelete = (text, record, index) => {
    alert("delete");
  };
  rowSelectionChange = (key, selectedRows) => {
    this.setState((prevState) => ({
      data: { ...prevState.data, [key]: selectedRows },
    }));
  };
  addRole = () => {};
  handleOk = () => {};
  closeModal = (e) => {
    if (e.action == "save") {
      FinMessage("Role successfully saved.", "success");
    }
  };
  render() {
    return (
      <div>
        <PageTitle pageTitle={this.appSchema.pageTitle}></PageTitle>
        <ActionPanel buttons={this.appSchema.buttons} selectedRows={this.state.data[this.appSchema.listing[0].dataGridUID]} />
        <DataGridViewer
          schema={this.appSchema.listing[0]}
          onRowSelectionChange={this.rowSelectionChange}
          ref={(node) => {
            this.dataGridViewer = node;
          }}
        ></DataGridViewer>
        <AppModal
          callBack={this.closeModal}
          ref={(node) => {
            this.appModal = node;
          }}
        ></AppModal>
      </div>
    );
  }
}

export default Roles;
