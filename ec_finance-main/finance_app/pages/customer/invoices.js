import DataGridViewer from "../../components/DataGridViewer";
import AppModal from "../../components/AppModal";
import React, { Component } from "react";
import { LinkOutlined } from "@ant-design/icons";
class Invoices extends Component {
  constructor(props) {
    super(props);
  }
  state = { data: {} };

  appSchema = {
    pageTitle: "History",
    buttons: [],
    listing: [
      {
        dataGridUID: "history",
        url: "/dt/sales/collection_actions/?customer_id=" + this.props.customerId + "&reminder_id=" + this.props.reminderId ,
        paging: true,
        default_sort_col: "id",
        default_sort_order: "descend",
        row_selection: false,
        bind_on_load: true,
        gridViewer: true,
        columns: [
          {
            value: "invoice_number",
            text: "Invoice number",
            sortable: true,
            width: 300,
            sequence: 0,
            render: (text, record, index) => {
              return (
                <div>
                  {record.invoice_number}
                  <LinkOutlined
                    className="on-hover-color"
                    style={{ marginLeft: 10 }}
                    onClick={() => window.open("https://mail.google.com/mail/u/0/?#search/" + record.invoice_number.replace("/", "%2F"), "_blank")}
                  />
                </div>
              );
            },
          },
          {
            value: "customer_name",
            text: "Customer name",
            sortable: true,
            sequence: 3,
          },
          {
            value: "status",
            text: "Status",
            sortable: true,
            sequence: 4,
          },
          {
            value: "secondary_status",
            sortable: true,
            text: "Secondary status",
            width: 150,
          },
          {
            value: "invoice_amount",
            text: "invoice amount",
            sortable: true,
            sequence: 4,
          },

          {
            value: "invoice_created_on",
            text: "Invoice date",
            sortable: true,
            sequence: 5,
          },
        ],
      },
    ],
  };

  componentDidMount = () => {
    // call function if needed on component load.
  };

  rowSelectionChange = (key, selectedRows) => {
    this.setState((prevState) => ({
      data: { ...prevState.data, [key]: selectedRows },
    }));
  };

  render() {
    return (
      <>
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
      </>
    );
  }
}
Invoices.getInitialProps = async (context) => {
  return { customerId: context.query.customer_id ?? "0", reminderId: context.query.id ?? "0", isModal: true };
};
export default Invoices;
