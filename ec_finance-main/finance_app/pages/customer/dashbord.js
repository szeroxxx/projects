import { Card, Col, Radio, Row } from "antd";
import React, { Component } from "react";
import DataGridViewer from "../../components/DataGridViewer";
import PageTitle from "../../components/PageTitle";

class CollectionDashboard extends Component {
  state = { data: [], slotSelect: "day" };

  reminderSchema = {
    listing: [
      {
        dataGridUID: "reminders",
        url: "/dt/sales/collection/dashboard_reminder_overview/?time=day",
        paging: true,
        default_sort_col: "id",
        default_sort_order: "descend",
        row_selection: false,
        bind_on_load: true,
        row_selection_type: "custom-table-body",
        columns: [
          {
            value: "id",
            text: "ID",
            show: false,
          },
          {
            value: "country__name",
            text: "Country",
          },
          {
            value: "new",
            text: "New",
            modal: {
              url: "/customer/payment_reminders/?is_model=true&index=0&status=pending",
              title_key: ["country__name"],
              queryParams: [{ key: "country__name" }, { key: "slot" }],
            },
          },
          {
            value: "follow_ups",
            text: "Follow ups",
            modal: {
              url: "/customer/payment_reminders/?is_model=true&index=1&status=due",
              queryParams: [{ key: "country__name" }, { key: "slot" }],
            },
          },
          {
            value: "processed",
            text: "Processed",
            modal: {
              url: "/customer/payment_reminders/?is_model=true&index=2&status=done",
              queryParams: [{ key: "country__name" }, { key: "slot" }],
            },
          },
          {
            value: "closed",
            text: "Closed",
            modal: {
              url: "/customer/payment_reminders/?is_model=true&index=5&status=closed",
              queryParams: [{ key: "country__name" }, { key: "slot" }],
            },
          },
          {
            value: "all",
            text: "All",
            modal: {
              url: "/customer/payment_reminders/?is_model=true&index=6&status=all",
              queryParams: [{ key: "country__name" }, { key: "slot" }],
            },
          },
        ],
      },
      {
        dataGridUID: "reminderLegal",
        url: "/dt/sales/collection/dashboard_legal_overview/?time=day",
        paging: true,
        default_sort_col: "id",
        row_selection_type: "custom-table-body",
        default_sort_order: "descend",
        row_selection: false,
        bind_on_load: true,
        columns: [
          {
            value: "id",
            text: "ID",
            show: false,
          },
          {
            value: "country__name",
            text: "Country",
          },
          {
            value: "legal_new",
            text: "New",
            modal: {
              url: "/customer/payment_reminders_legal/?is_model=true&index=0&status=pending",
              queryParams: [{ key: "country__name" }, { key: "slot" }],
            },
          },
          {
            value: "legal_follow_ups",
            text: "Follow ups",
            modal: {
              url: "/customer/payment_reminders_legal/?is_model=true&index=1&status=due",
              queryParams: [{ key: "country__name" }, { key: "slot" }],
            },
          },
          {
            value: "legal_processed",
            text: "Processed",
            modal: {
              url: "/customer/payment_reminders_legal/?is_model=true&index=2&status=done",
              queryParams: [{ key: "country__name" }, { key: "slot" }],
            },
          },
          {
            value: "closed",
            text: "Closed",
            modal: {
              url: "/customer/payment_reminders_legal/?is_model=true&index=4&status=closed",
              queryParams: [{ key: "country__name" }, { key: "slot" }],
            },
          },
          {
            value: "all",
            text: "All",
            modal: {
              url: "/customer/payment_reminders_legal/?is_model=true&index=5&status=all",
              queryParams: [{ key: "country__name" }, { key: "slot" }],
            },
          },
        ],
      },
    ],
  };
  handleChange = (e) => {
    this.reminderGridViewer.searchData({ time: ["text", e.target.value] });
    this.legalGridViewer.searchData({ time: ["text", e.target.value] });
  };
  render() {
    return (
      <>
        <PageTitle pageTitle={"Dashboard view "}></PageTitle>
        <Radio.Group style={{ float: "right" }} onChange={this.handleChange} defaultValue="day" buttonStyle="solid">
          <Radio.Button value="day">Day</Radio.Button>
          <Radio.Button value="week">Week</Radio.Button>
          <Radio.Button value="month">Month</Radio.Button>
        </Radio.Group>
        <div align="left" style={{ marginBottom: 10 }}></div>
        <Card>
          <Row gutter={24}>
            <Col span={12}>
              <p>
                <b>Payment reminder</b>
              </p>
              <DataGridViewer
                schema={this.reminderSchema.listing[0]}
                ref={(node) => {
                  this.reminderGridViewer = node;
                }}
              ></DataGridViewer>
            </Col>
            <Col span={12}>
              <p>
                <b>Payment reminder (Legal)</b>
              </p>
              <DataGridViewer
                schema={this.reminderSchema.listing[1]}
                ref={(node) => {
                  this.legalGridViewer = node;
                }}
              ></DataGridViewer>
            </Col>
          </Row>
        </Card>
      </>
    );
  }
}
export default CollectionDashboard;
