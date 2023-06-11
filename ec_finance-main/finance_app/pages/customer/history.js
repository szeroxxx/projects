import DataGridViewer from "../../components/DataGridViewer";
import React, { Component } from "react";
class History extends Component {
  constructor(props) {
    super(props);
  }
  state = { data: {} };

  appSchema = {
    pageTitle: "History",
    listing: [
      {
        dataGridUID: "history",
        url: "/dt/auditlog/logs/?id=" + this.props.id,
        paging: true,
        default_sort_col: "id",
        default_sort_order: "descend",
        row_selection: false,
        bind_on_load: true,
        gridViewer: true,
        columns: [
          {
            value: "action_by",
            text: "Action by",
            sortable: true,
            width: 300,
            sequence: 0,
          },
          {
            value: "action_on",
            text: "Action on",
            sortable: true,
            sequence: 3,
          },
          {
            value: "descr",
            text: "Action",
            sortable: true,
            sequence: 4,
          },
          {
            value: "ip_addr",
            text: "Ip",
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
  render() {
    return (
      <>
        <DataGridViewer
          schema={this.appSchema.listing[0]}
          ref={(node) => {
            this.dataGridViewer = node;
          }}
        ></DataGridViewer>
      </>
    );
  }
}
History.getInitialProps = async (context) => {
  return { id: context.query.id ?? "0", isModal: true };
};
export default History;
