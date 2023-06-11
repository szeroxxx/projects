import { Avatar, Checkbox, Tooltip } from "antd";
import axios from "axios";
import React from "react";
import AppIcons from "../../components/AppIcons";
import AppModal from "../../components/AppModal";
import Calendar from "../../components/Calendar";

class CollectionCalendar extends React.Component {
  getCalenderInvoice = (from_date, to_date) => {
    axios.post("/dt/sales/collection/calender_view", { from_date: from_date, to_date: to_date }).then((response) => {
      let data = response.data;
      if (data.code == 1) {
        this.setState({
          data: data.data,
        });
        this.followupShow(true, false);
      }
    });
  };
  state = {
    weekendsVisible: true,
    Follow_upChecked: true,
  };
  onCalChange = (arg) => {
    this.getCalenderInvoice(arg.view.currentStart, arg.view.currentEnd);
  };
  handleWeekendsToggle = () => {
    this.setState({
      weekendsVisible: !this.state.weekendsVisible,
    });
  };

  handleDateSelect = (selectInfo) => {
    let title = prompt("Please enter a new title for your event");
    let calendarApi = selectInfo.view.calendar;

    calendarApi.unselect();

    if (title) {
      calendarApi.addEvent({
        id: 0,
        title,
        start: selectInfo.startStr,
        end: selectInfo.endStr,
        allDay: selectInfo.allDay,
      });
    }
  };
  handleEventClick = (clickInfo) => {
    clickInfo.jsEvent.preventDefault();
    clickInfo.jsEvent.stopPropagation();
    if (clickInfo.event.extendedProps.is_legal == false) {
      this.appModal.show({
        title: clickInfo.event.title,
        url:
          "/customer/collection_action/" +
          clickInfo.event.extendedProps.customer_id +
          "/" +
          clickInfo.event.id +
          "/?customer_name=" +
          clickInfo.event.extendedProps.customer_name,
      });
    } else {
      this.appModal.show({
        title: clickInfo.event.title,
        url:
          "/customer/legal_action/" +
          clickInfo.event.extendedProps.customer_id +
          "/" +
          clickInfo.event.id +
          "/?customer_name=" +
          clickInfo.event.extendedProps.customer_name,
      });
    }
  };

  renderEventContent = (eventInfo) => {
    eventInfo.view.display = null;
    if (eventInfo.event.extendedProps.is_legal == true) {
      return (
        <Tooltip placement="bottom" title={eventInfo.event.extendedProps.action_desc}>
          <div style={{ display: "flex", height: 20, marginBottom: 2 }}>
            <Avatar style={{ marginTop: 2, background: "#BABBBF" }} size={15} icon={<AppIcons code="BellOutlined"></AppIcons>} />
            <p style={{ marginLeft: 5 }}>{eventInfo.event.title + " (Legal)"}</p>
          </div>
        </Tooltip>
      );
    } else {
      return (
        <Tooltip placement="bottom" title={eventInfo.event.extendedProps.action_desc}>
          <div style={{ display: "flex", height: 20, marginBottom: 2 }}>
            <Avatar style={{ marginTop: 2, background: "#BABBBF" }} size={15} icon={<AppIcons code="BellOutlined"></AppIcons>} />
            <p style={{ marginLeft: 5 }}>{eventInfo.event.title}</p>
          </div>
        </Tooltip>
      );
    }
  };

  onModelClose = (e) => {};
  handleEvents = (events) => {};

  followupShow = (follow_up, legal_follow_up) => {
    this.setState({ Follow_upChecked: follow_up, Follow_upLegalChecked: legal_follow_up });
    let filter_data = [];
    let intial_data = this.state.data;
    for (var value in intial_data) {
      if (follow_up == true && legal_follow_up == true) {
        delete intial_data[value]["className"];
        filter_data.push(intial_data[value]);
      } else if (follow_up == false && legal_follow_up == false) {
        intial_data[value]["className"] = ["legal-follow-up", "follow-up"];
        filter_data.push(intial_data[value]);
      } else {
        if (intial_data[value].is_legal == true) {
          if (legal_follow_up == true) {
            delete intial_data[value]["className"];
            filter_data.push(intial_data[value]);
          } else {
            intial_data[value]["className"] = ["follow-up"];
            filter_data.push(intial_data[value]);
          }
        } else {
          if (follow_up == true) {
            delete intial_data[value]["className"];
            filter_data.push(intial_data[value]);
          } else {
            intial_data[value]["className"] = ["legal-follow-up"];
            filter_data.push(intial_data[value]);
          }
        }
      }
    }
    this.setState({ data: filter_data });
  };
  render() {
    return (
      <>
        <div style={{ marginBottom: 5 }}>
          <Checkbox
            checked={this.state.Follow_upChecked}
            style={{ fontSize: 16 }}
            onChange={(e) => {
              this.followupShow(e.target.checked, this.state.Follow_upLegalChecked);
            }}
          >
            Follow up
          </Checkbox>
          <Checkbox
            checked={this.state.Follow_upLegalChecked}
            value="legal_follow_up"
            style={{ marginLeft: 30, fontSize: 16 }}
            onChange={(e) => {
              this.followupShow(this.state.Follow_upChecked, e.target.checked);
            }}
          >
            Follow up (Legal)
          </Checkbox>
        </div>
        <Calendar
          eventClick={this.handleEventClick}
          datesSet={this.onCalChange}
          events={this.state.data}
          eventContent={this.renderEventContent}
          dayMaxEventRows={false}
        ></Calendar>
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
export default CollectionCalendar;
