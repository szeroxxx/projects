import FullCalendar, { formatDate } from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import timeGridPlugin from "@fullcalendar/timegrid";
import React from "react";
import { Row, Col } from "antd";
class Calendar extends React.Component {
  state = { height: window.innerHeight - 90 };
  render() {
    return (
      <div className="calendar-container">
        <Row>
          <Col lg={24} sm={24} md={24}>
            <FullCalendar
              plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
              headerToolbar={{
                left: "prev,next today",
                center: "title",
                right: "dayGridMonth,timeGridWeek,timeGridDay",
              }}
              initialView="dayGridMonth"
              themeSystem="Simplex"
              editable={false}
              selectable={true}
              selectMirror={true}
              // dayMaxEvents={true}
              eventResizableFromStart={true}
              nowIndicator={true}
              {...this.props}
              // slotLabelInterval={{
              //   hours: 4,
              // }}
              // slotDuration={{
              //   minute: 40,
              // }}
              // slotEventOverlap={true}
              // handleWindowResize={true}
              // height={"100%"}

              // weekends={this.state.weekendsVisible}
              // called after events are initialized/added/changed/removed
              /* you can update a remote database when these fire:
            eventAdd={function(){}}
            eventChange={function(){}}
            eventRemove={function(){}}
            */
            />
          </Col>
        </Row>
      </div>
    );
  }
}
export default Calendar;
