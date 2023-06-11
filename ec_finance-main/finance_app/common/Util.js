import axios from "axios";
import { notification, message } from "antd";

class PostQuery {
  constructor() {
    this.postData = {};
  }
  addQuery(queryCode, params, options) {
    this.postData = params;
  }
  getPostQueries() {
    return this.postData;
  }
}
export default PostQuery;

class AppModelFuc {
  onCloseForm(action) {
    // If form opened in iframe, communicate with parent to close form using postMessage API
    window.parent.postMessage(
      JSON.stringify({
        action: action,
      }),
      "*"
    );
  }
}
class Core {
  Post(api, postData, callback) {
    axios.post(api, postData).then((result) => {
      if (callback) {
        callback(result);
      }
    });
  }
}
export const showMessage = (message, description, type) => {
  notification[type]({
    message: message,
    description: description,
  });
};

export const FinMessage = (msg, type) => {
  message[type](msg, 10);
};
