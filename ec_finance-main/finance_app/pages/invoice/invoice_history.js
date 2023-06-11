import DataGridViewer from "../../components/DataGridViewer";
import React, { Component } from "react";
import AppModal from "../../components/AppModal";
import { PlusOutlined } from "@ant-design/icons";
import moment from "moment";
class InvoiceHistory extends Component {
  constructor(props) {
    super(props);
  }
  state = { data: {} };

  appSchema = {
    pageTitle: "Invoice History",
    listing: [
      {
        dataGridUID: "invoiceHistory",
        url: "/dt/auditlog/invoice_history/?id=" + this.props.id,
        paging: true,
        default_sort_col: "id",
        default_sort_order: "descend",
        row_selection: false,
        bind_on_load: true,
        gridViewer: true,
        columns: [
          {
            value: "id",
            text: "ID",
            row_key: true,
            sequence: 0,
            show: false,
          },
          {
            value: "document_no",
            width: 40,
            sequence: 1,
            render: (text, record, index) => {
              if (record.document_no) {
                return (
                  <div>
                    <PlusOutlined
                      onClick={() =>
                        this.appModal.show({
                          title: "",
                          url:
                            "/invoice/invoice_full_history/?id=" +
                            record.id +
                            "&cust_name=" +
                            record.customer_name +
                            "&payment_id=" +
                            record.document_no +
                            "&object_id=" +
                            record.object_id,
                          style: { width: "100%", height: "90vh" },
                        })
                      }
                    />
                  </div>
                );
              }
            },
          },
          {
            value: "invoice_number",
            text: "Number",
            sortable: true,
            sequence: 2,
          },
          {
            value: "status_desc",
            text: "Status",
            sequence: 3,
          },
          {
            value: "descr",
            text: "Action",
            sortable: true,
            sequence: 4,
          },
          {
            value: "invoice_due_date",
            text: "Invoice date",
            sortable: true,
            sequence: 5,
            render: (text, record) => <>{moment(record.invoice_due_date).format("YYYY/MM/DD kk:mm")}</>,
          },
          {
            value: "invoice_value",
            text: "Base amount",
            sortable: true,
            sequence: 6,
          },
          {
            value: "customer_name",
            text: "Customer",
            sortable: true,
            sequence: 7,
          },
          {
            value: "created_by",
            text: "User name",
            sortable: true,
            sequence: 8,
          },
          {
            value: "ip_addr",
            text: "IP address",
            sortable: true,
            sequence: 9,
          },
          {
            value: "action_on",
            text: "Created on",
            sortable: true,
            sequence: 10,
          },
        ],
      },
    ],
  };
  onModelClose = () => {
    // this.dataForm.refreshTable(this.state.status);
  };
  componentDidMount = () => {
    // call function if needed on component load.
  };
  render() {
    return (
      <>
        <DataGridViewer
          schema={this.appSchema.listing[0]}
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
InvoiceHistory.getInitialProps = async (context) => {
  return {
    id: context.query.id ?? "0",
    customer_name: context.query.cust_name,
    payment_id: context.query.payment_id,
    object_id: context.query.object_id,
    isModal: true,
  };
};
export default InvoiceHistory;
