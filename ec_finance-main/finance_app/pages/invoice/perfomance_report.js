import { Card, Col, Row, Tabs } from "antd";
import axios from "axios";
import React, { Component } from "react";
import AppModal from "../../components/AppModal";
import DataGridViewer from "../../components/DataGridViewer";
const { TabPane } = Tabs;
class perfomanceReport extends Component {
  requestRef = React.createRef();

  state = { re_data: [] };
  performanceAppSchema = {
    pageTitle: "Perfomance Report",
    buttons: [],
    listing: [
      {
        dataGridUID: "orderPlaced",
        default_sort_col: "id",
        default_sort_order: "descend",
        row_selection: false,
        bind_on_load: false,
        gridViewer: true,
        columns: [
          {
            value: "id",
            text: "ID",
            show: false,
            row_key: true,
            sequence: 1,
          },
          {
            value: "TypeName",
            text: "Days",
            show: true,
            row_key: true,
            sequence: 2,
          },
          {
            value: "Order",
            text: "Orders",
            show: true,
            row_key: true,
            sequence: 3,
          },
          {
            value: "PerofTotalNumber",
            text: "% of Total",
            show: true,
            row_key: true,
            sequence: 4,
            render: (text,record,index) => {
              if (record.PerofTotalNumber == '') {
                return 0
              }else{
                return record.PerofTotalNumber.toFixed(3)
              }
            }
          },
          {
            value: "value",
            text: "Sales value",
            show: true,
            row_key: true,
            sequence: 5,
          },
          {
            value: "PerofTotalValue",
            text: "% of Total",
            show: true,
            row_key: true,
            sequence: 6,
            render: (text,record,index) => {
              if (record.PerofTotalValue == '') {
                return 0
              }else{
                return record.PerofTotalValue.toFixed(3)
              }
            }
          },
          {
            value: "AverageOrderValue",
            text: "Average",
            show: true,
            row_key: true,
            sequence: 7,
            render: (text,record,index) => {
              if (record.AverageOrderValue == '') {
                return 0
              }else{
                return record.AverageOrderValue.toFixed(3)
              }
            }
          },
        ],
      },
      {
        dataGridUID: "technologyOrderPlaces",
        paging: true,
        default_sort_col: "id",
        default_sort_order: "descend",
        row_selection: false,
        bind_on_load: false,
        gridViewer: true,
        columns: [
          {
            value: "id",
            text: "ID",
            show: false,
            row_key: true,
            sequence: 1,
          },
          {
            value: "TypeName",
            text: "WD",
            show: true,
            row_key: true,
            sequence: 2,
          },
          {
            value: "Order",
            text: "Orders",
            show: true,
            row_key: true,
            sequence: 3,
          },
          {
            value: "PerofTotalNumber",
            text: "% of Total",
            show: true,
            row_key: true,
            sequence: 4,
            render: (text,record,index) => {
              if (record.PerofTotalNumber == '') {
                return 0
              }else{
                return record.PerofTotalNumber.toFixed(3)
              }
            }
          },
          {
            value: "value",
            text: "Sales value",
            show: true,
            row_key: true,
            sequence: 5,
          },
          {
            value: "PerofTotalValue",
            text: "% of Total",
            show: true,
            row_key: true,
            sequence: 6,
            render: (text,record,index) => {
              if (record.PerofTotalValue == '') {
                return 0
              }else{
                return record.PerofTotalValue.toFixed(3)
              }
            }
          },
          {
            value: "AverageOrderValue",
            text: "Average",
            show: true,
            row_key: true,
            sequence: 7,
            render: (text,record,index) => {
              if (record.AverageOrderValue == '') {
                return 0
              }else{
                return record.AverageOrderValue.toFixed(3)
              }
            }
          },
        ],
      },
      {
        dataGridUID: "Service",
        paging: true,
        default_sort_col: "id",
        default_sort_order: "descend",
        row_selection: false,
        bind_on_load: false,
        gridViewer: true,
        columns: [
          {
            value: "id",
            text: "ID",
            show: false,
            row_key: true,
            sequence: 1,
          },
          {
            value: "TypeName",
            text: "Services",
            show: true,
            row_key: true,
            sequence: 2,
          },
          {
            value: "Order",
            text: "Orders",
            show: true,
            row_key: true,
            sequence: 3,
          },
          {
            value: "PerofTotalNumber",
            text: "% of Total",
            show: true,
            row_key: true,
            sequence: 4,
            render: (text,record,index) => {
              if (record.PerofTotalNumber == '') {
                return 0
              }else{
                return record.PerofTotalNumber.toFixed(3)
              }
            }
          },
          {
            value: "value",
            text: "Sales value",
            show: true,
            row_key: true,
            sequence: 5,
          },
          {
            value: "PerofTotalValue",
            text: "% of Total",
            show: true,
            row_key: true,
            sequence: 6,
            render: (text,record,index) => {
              if (record.PerofTotalValue == '') {
                return 0
              }else{
                return record.PerofTotalValue.toFixed(3)
              }
            }
          },
          {
            value: "AverageOrderValue",
            text: "Average",
            show: true,
            row_key: true,
            sequence: 7,
            render: (text,record,index) => {
              if (record.AverageOrderValue == '') {
                return 0
              }else{
                return record.AverageOrderValue.toFixed(3)
              }
            }
          },
        ],
      },
      {
        dataGridUID: "Layer",
        paging: true,
        default_sort_col: "id",
        default_sort_order: "descend",
        row_selection: false,
        bind_on_load: false,
        gridViewer: true,
        columns: [
          {
            value: "id",
            text: "ID",
            show: false,
            row_key: true,
            sequence: 1,
          },
          {
            value: "TypeName",
            text: "Layers",
            show: true,
            row_key: true,
            sequence: 2,
          },
          {
            value: "Order",
            text: "Orders",
            show: true,
            row_key: true,
            sequence: 3,
          },
          {
            value: "PerofTotalNumber",
            text: "% of Total",
            show: true,
            row_key: true,
            sequence: 4,
            render: (text,record,index) => {
              if (record.PerofTotalNumber == '') {
                return 0
              }else{
                return record.PerofTotalNumber.toFixed(3)
              }
            }
          },
          {
            value: "value",
            text: "Sales value",
            show: true,
            row_key: true,
            sequence: 5,
          },
          {
            value: "PerofTotalValue",
            text: "% of Total",
            show: true,
            row_key: true,
            sequence: 6,
            render: (text,record,index) => {
              if (record.PerofTotalValue == '') {
                return 0
              }else{
                return record.PerofTotalValue.toFixed(3)
              }
            }
          },
          {
            value: "AverageOrderValue",
            text: "Average",
            show: true,
            row_key: true,
            sequence: 7,
            render: (text,record,index) => {
              if (record.AverageOrderValue == '') {
                return 0
              }else{
                return record.AverageOrderValue.toFixed(3)
              }
            }
          },
        ],
      },
      {
        dataGridUID: "ExceptionRaised",
        paging: true,
        default_sort_col: "id",
        default_sort_order: "descend",
        row_selection: false,
        bind_on_load: false,
        gridViewer: true,
        columns: [
          {
            value: "id",
            text: "ID",
            show: false,
            row_key: true,
            sequence: 1,
          },
          {
            value: "Days",
            text: "Days",
            show: true,
            row_key: true,
            sequence: 2,
          },
          {
            value: "Exceptions",
            text: "Exceptions",
            show: true,
            row_key: true,
            sequence: 3,
          },
          {
            value: "ReactionTime",
            text: "Reaction time (Hour)",
            show: true,
            row_key: true,
            sequence: 4,
          },
        ],
      },
      {
        dataGridUID: "ShipmentPerfomanceCustomer",
        paging: true,
        default_sort_col: "id",
        default_sort_order: "descend",
        row_selection: false,
        bind_on_load: false,
        gridViewer: true,
        columns: [
          {
            value: "id",
            text: "ID",
            show: false,
            row_key: true,
            sequence: 1,
          },
          {
            value: "LastDays",
            text: "Days",
            show: true,
            row_key: true,
            sequence: 2,
          },
          {
            value: "shipmentorders",
            text: "Shipment order",
            show: true,
            row_key: true,
            sequence: 3,
          },
          {
            value: "Timely",
            text: "Timely",
            show: true,
            row_key: true,
            sequence: 4,
          },
          {
            value: "Delay",
            text: "Delay",
            show: true,
            row_key: true,
            sequence: 5,
          },
          {
            value: "Delaypercent",
            text: "Delay %",
            show: true,
            row_key: true,
            sequence: 6,
            render: (text,record,index) => {
              if (record.Delaypercent == '') {
                return 0
              }else{
                return record.Delaypercent.toFixed(3)
              }
            }
          },
          {
            value: "complete",
            text: "Complete",
            show: true,
            row_key: true,
            sequence: 7,
          },
          {
            value: "Partial",
            text: "Partial",
            show: true,
            row_key: true,
            sequence: 8,
          },
          {
            value: "partialpercent",
            text: "Partialn %",
            show: true,
            row_key: true,
            sequence: 9,
            render: (text,record,index) => {
              if (record.partialpercent == '') {
                return 0
              }else{
                return record.partialpercent.toFixed(3)
              }
            }
          },
          {
            value: "restart",
            text: "Restart",
            show: true,
            row_key: true,
            sequence: 10,
          },
          {
            value: "restartpercent",
            text: "Restart %",
            show: true,
            row_key: true,
            sequence: 11,
            render: (text,record,index) => {
              if (record.restartpercent == '') {
                return 0
              }else{
                return record.restartpercent.toFixed(3)
              }
            }
          },
        ],
      },
      {
        dataGridUID: "ShipmentPerfomanceAll",
        paging: true,
        default_sort_col: "id",
        default_sort_order: "descend",
        row_selection: false,
        gridViewer: true,
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
            value: "LastDays",
            text: "Days",
            show: true,
            row_key: true,
            sequence: 2,
          },
          {
            value: "shipmentorders",
            text: "Shipment order",
            show: true,
            row_key: true,
            sequence: 3,
          },
          {
            value: "Timely",
            text: "Timely",
            show: true,
            row_key: true,
            sequence: 4,
          },
          {
            value: "Delay",
            text: "Delay",
            show: true,
            row_key: true,
            sequence: 5,
          },
          {
            value: "Delaypercent",
            text: "Delay %",
            show: true,
            row_key: true,
            sequence: 6,
            render: (text,record,index) => {
              if (record.Delaypercent == '') {
                return 0
              }else{
                return record.Delaypercent.toFixed(3)
              }
            }
          },
          {
            value: "complete",
            text: "Complete",
            show: true,
            row_key: true,
            sequence: 7,
          },
          {
            value: "Partial",
            text: "Partial",
            show: true,
            row_key: true,
            sequence: 8,
          },
          {
            value: "partialpercent",
            text: "Partialn %",
            show: true,
            row_key: true,
            sequence: 9,
            render: (text,record,index) => {
              if (record.partialpercent == '') {
                return 0
              }else{
                return record.partialpercent.toFixed(3)
              }
            }
          },
          {
            value: "restart",
            text: "Restart",
            show: true,
            row_key: true,
            sequence: 10,
          },
          {
            value: "restartpercent",
            text: "Restart %",
            show: true,
            row_key: true,
            sequence: 11,
            render: (text,record,index) => {
              if (record.restartpercent == '') {
                return 0
              }else{
                return record.restartpercent.toFixed(3)
              }
            }
          },
        ],
      },
      {
        dataGridUID: "ShipmentValue",
        paging: true,
        default_sort_col: "id",
        default_sort_order: "descend",
        row_selection: false,
        bind_on_load: false,
        gridViewer: true,
        columns: [
          {
            value: "id",
            text: "ID",
            show: false,
            row_key: true,
            sequence: 1,
          },
          {
            value: "shipmentdays",
            text: "Days",
            show: true,
            row_key: true,
            sequence: 2,
          },
          {
            value: "Orders",
            text: "Orders",
            show: true,
            row_key: true,
            sequence: 3,
          },
          {
            value: "Salesvalue",
            text: "Sales value",
            show: true,
            row_key: true,
            sequence: 4,
          },
          {
            value: "AddedValue",
            text: "Added value",
            show: true,
            row_key: true,
            sequence: 5,
          },
          {
            value: "AddedValuepercentage",
            text: "Add value %",
            show: true,
            row_key: true,
            sequence: 6,
            render: (text,record,index) => {
              if (record.AddedValuepercentage == '') {
                return 0
              }else{
                return record.AddedValuepercentage.toFixed(3)
              }
            }
          },
          {
            value: "AverageOrderValue",
            text: "Average order value",
            show: true,
            row_key: true,
            sequence: 7,
            render: (text,record,index) => {
              if (record.AverageOrderValue == '') {
                return 0
              }else{
                return record.AverageOrderValue.toFixed(3)
              }
            }
          },
        ],
      },
      {
        dataGridUID: "AfterSales",
        paging: true,
        default_sort_col: "id",
        default_sort_order: "descend",
        row_selection: false,
        bind_on_load: false,
        gridViewer: true,
        columns: [
          {
            value: "id",
            text: "ID",
            show: false,
            row_key: true,
            sequence: 1,
          },
          {
            value: "claimdays",
            text: "Days",
            show: true,
            row_key: true,
            sequence: 2,
          },
          {
            value: "Claims",
            text: "Number of claims",
            show: true,
            row_key: true,
            sequence: 3,
          },
          {
            value: "claimration",
            text: "Claims / order ratio",
            show: true,
            row_key: true,
            sequence: 4,
          },
        ],
      },
      {
        dataGridUID: "Request",
        paging: true,
        default_sort_col: "id",
        default_sort_order: "descend",
        row_selection: false,
        bind_on_load: false,
        gridViewer: true,
        columns: [
          {
            value: "id",
            text: "ID",
            show: false,
            row_key: true,
            sequence: 1,
          },
          {
            value: "UserDays",
            text: "Days",
            show: true,
            row_key: true,
            sequence: 2,
          },
          {
            value: "CalculationCount",
            text: "Calculation on site",
            show: true,
            row_key: true,
            sequence: 3,
          },
          {
            value: "SaveOffer",
            text: "Saved offer",
            show: true,
            row_key: true,
            sequence: 4,
          },
          {
            value: "DirectOrderPlaced",
            text: "Orders placed",
            show: true,
            row_key: true,
            sequence: 5,
          },
          {
            value: "OndemandRequest",
            text: "On demand request",
            show: true,
            row_key: true,
            sequence: 6,
          },
          {
            value: "OfferToOrderPlaced",
            text: "Order placed",
            show: true,
            row_key: true,
            sequence: 7,
          },
        ],
      },
    ],
  };
  componentDidMount() {
    this.orderIntakeData();
  }

  async orderIntakeData() {
    const res = await axios.get("/dt/sales/order_intake/?ec_customer_id=" + this.props.ec_customer_id);
    const data = res.data.data;
    var last_order = data[0];
    this.orderPlacedGridViewer.setDataSource(data[1]);
    this.technologyGridViewer.setDataSource(data[2]);
    this.serviceGridViewer.setDataSource(data[3]);
    this.layerGridViewer.setDataSource(data[4]);
    this.exceptionGridViewer.setDataSource(data[5]);
    var WD = this.technologyGridViewer.getDataSource();
    var wd_order = 0;
    var wd_sales = 0;
    for (var row in WD) {
      wd_order = wd_order + WD[row].Order;
      wd_sales = wd_sales + WD[row].value;
    }
    var service = this.serviceGridViewer.getDataSource();
    var service_order = 0;
    var service_sales = 0;
    for (var row in service) {
      service_order = service_order + service[row].Order;
      service_sales = service_sales + service[row].value;
    }
    var layer = this.layerGridViewer.getDataSource();
    var layer_order = 0;
    var layer_sales = 0;
    for (var row in layer) {
      layer_order = layer_order + layer[row].Order;
      layer_sales = layer_sales + layer[row].value;
    }
    if (wd_order == 0 ){
      var average_sales_val = wd_sales
    }
    else{
      var average_sales_val = wd_sales/wd_order
    }
    if (service_order == 0){
      var average_service_sales_val = service_sales
    }
    else{
      var average_service_sales_val = service_sales/service_order
    }
    if (layer_order == 0){
      var average_layer_sales_val = layer_sales
    }
    else{
      var average_layer_sales_val = layer_sales/layer_order
    }
    this.setState({
      last_order_date: last_order[0].LastOrderDate,
      last_order_number: last_order[0].LastOrderNr,
      wd_order: wd_order,
      wd_sales: wd_sales,
      service_order: service_order,
      service_sales: service_sales,
      layer_order: layer_order,
      layer_sales: layer_sales,
      sales_value_avg: average_sales_val.toFixed(3),
      average_service_sales_val: average_service_sales_val.toFixed(3),
      average_layer_sales_val: average_layer_sales_val.toFixed(3),
    });
  }
  async shipmentData() {
    const res = await axios.get("/dt/sales/shipment/?ec_customer_id=" + this.props.ec_customer_id);
    const data = res.data.data;
    this.shipmentCustomerGridViewer.setDataSource(data[0]);
    this.shipmentAllGridViewer.setDataSource(data[1]);
    this.shipmentValuesGridViewer.setDataSource(data[2]);
  }
  async afterSalesData() {
    const res = await axios.get("/dt/sales/after_sales/?ec_customer_id=" + this.props.ec_customer_id);
    const data = res.data.data;
    console.log(data, "afterSalesData");
    this.afterSalesGridViewer.setDataSource(data[0]);
  }
  async requestData() {
    const res = await axios.get("/dt/sales/request_report/?ec_customer_id=" + this.props.ec_customer_id);
    const data = res.data.data;
    this.setState({ re_data: data });
    this.state.re_data.map((val, index) => {
      this[`requestGridViewer${index}`].setDataSource(val);
    });
  }
  tabChange = (key) => {
    if (key == 2) {
      this.shipmentData();
      this.setState({ re_data: [] });
    }
    if (key == 3) {
      this.requestData();
    }
    if (key == 4) {
      this.afterSalesData();
      this.setState({ re_data: [] });
    }
  };
  render() {
    return (
      <>
        <div>
          <Tabs defaultActiveKey="1" onChange={this.tabChange}>
            <TabPane tab="Order intake report" key="1">
              <Card style={{ backgroundColor: "#f2f0f0", marginBottom: 10 }}>
                <Row>
                  <Col span={12}>
                    <b>
                      <h3>Last order date : {this.state.last_order_date}</h3>
                    </b>
                  </Col>
                  <Col span={12}>
                    <b>
                      <h3>Last order number : {this.state.last_order_number}</h3>
                    </b>
                  </Col>
                </Row>
              </Card>
              <b>
                <h3>Order placed:</h3>
              </b>
              <DataGridViewer
                schema={this.performanceAppSchema.listing[0]}
                ref={(node) => {
                  this.orderPlacedGridViewer = node;
                }}
              ></DataGridViewer>
              <b>
                <h3>Technology Order placed:</h3>
              </b>
              <DataGridViewer
                schema={this.performanceAppSchema.listing[1]}
                ref={(node) => {
                  this.technologyGridViewer = node;
                }}
              ></DataGridViewer>
              <Row style={{ backgroundColor: "#eeefef", marginBottom: 10 }}>
                <Col span={2}>Orders : {this.state.wd_order}</Col>
                <Col span={3}> Sales value : {this.state.wd_sales}</Col>
                <Col>Average sales value : {this.state.sales_value_avg}</Col>
              </Row>
              <b>
                <h3>Service:</h3>
              </b>
              <DataGridViewer
                schema={this.performanceAppSchema.listing[2]}
                ref={(node) => {
                  this.serviceGridViewer = node;
                }}
              ></DataGridViewer>
              <Row style={{ backgroundColor: "#eeefef", marginBottom: 10 }}>
                <Col span={2}>Orders : {this.state.service_order}</Col>
                <Col span={3}> Sales value : {this.state.service_sales}</Col>
                <Col>Average sales value : {this.state.average_service_sales_val}</Col>
              </Row>
              <b>
                <h3>Layer:</h3>
              </b>
              <DataGridViewer
                schema={this.performanceAppSchema.listing[3]}
                ref={(node) => {
                  this.layerGridViewer = node;
                }}
              ></DataGridViewer>
              <Row style={{ backgroundColor: "#eeefef", marginBottom: 10 }}>
                <Col span={2}>Orders : {this.state.layer_order}</Col>
                <Col span={3}> Sales value : {this.state.layer_sales}</Col>
                <Col>Average sales value : {this.state.average_layer_sales_val}</Col>
              </Row>
              <b>
                <h3>Exception raised:</h3>
              </b>
              <DataGridViewer
                schema={this.performanceAppSchema.listing[4]}
                ref={(node) => {
                  this.exceptionGridViewer = node;
                }}
              ></DataGridViewer>
            </TabPane>
            <TabPane tab="Shipment report" key="2">
              <b>
                <h3>Shipment perfomance customer:</h3>
              </b>
              <DataGridViewer
                schema={this.performanceAppSchema.listing[5]}
                ref={(node) => {
                  this.shipmentCustomerGridViewer = node;
                }}
              ></DataGridViewer>
              <b>
                <h3>Shipment perfomance all:</h3>
              </b>
              <DataGridViewer
                schema={this.performanceAppSchema.listing[6]}
                ref={(node) => {
                  this.shipmentAllGridViewer = node;
                }}
              ></DataGridViewer>
              <b>
                <h3>Shipment value:</h3>
              </b>
              <DataGridViewer
                schema={this.performanceAppSchema.listing[7]}
                ref={(node) => {
                  this.shipmentValuesGridViewer = node;
                }}
              ></DataGridViewer>
            </TabPane>
            <TabPane tab="Request" key="3">
              <b>
                <h3>Request:</h3>
              </b>
              {this.state.re_data.map((currentValue, index) => (
                <>
                  <b>
                    <h3>
                      {currentValue[3]["UserName"]}- Last Login Date : {currentValue[0]["LastLoginDate"]}
                    </h3>
                  </b>
                  <DataGridViewer
                    schema={this.performanceAppSchema.listing[9]}
                    ref={(node) => {
                      this[`requestGridViewer${index}`] = node;
                    }}
                  ></DataGridViewer>
                </>
              ))}
            </TabPane>
            <TabPane tab="After sales" key="4">
              <b>
                <h3>After sales:</h3>
              </b>
              <DataGridViewer
                schema={this.performanceAppSchema.listing[8]}
                ref={(node) => {
                  this.afterSalesGridViewer = node;
                }}
              ></DataGridViewer>
            </TabPane>
          </Tabs>
          <AppModal
            callBack={this.onModelClose}
            ref={(node) => {
              this.appModal = node;
            }}
          ></AppModal>
        </div>
      </>
    );
  }
}
perfomanceReport.getInitialProps = async (context) => {
  return { ec_customer_id: context.query.ids ?? "0", isModal: true };
};
export default perfomanceReport;
