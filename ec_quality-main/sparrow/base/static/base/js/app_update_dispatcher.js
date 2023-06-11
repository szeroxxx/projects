var CustomWebSocket = function (url) {
    var conn = new WebSocket(url);

    var callbacks = {};
    this.websocketUrl = url;

    this.bind = function (event_name, callback) {
        callbacks[event_name] = callbacks[event_name] || [];
        callbacks[event_name].push(callback);
        return this; // chainable
    };

    this.send = function (event_name, event_data) {
        var payload = JSON.stringify({ event: event_name, data: event_data });
        conn.send(payload); // <= send JSON data to socket server
        return this;
    };

    // dispatch to the right handlers
    conn.onmessage = function (e) {
        var json = JSON.parse(e.data);
        dispatch(json.event, json.data);
    };

    conn.onclose = function () {
        dispatch('close', null);
    };
    conn.onopen = function () {
        dispatch('open', null);
    };

    var dispatch = function (event_name, message) {
        var chain = callbacks[event_name];
        if (typeof chain == 'undefined') return; // no callbacks for this event
        for (var i = 0; i < chain.length; i++) {
            chain[i](message);
        }
    };
};

function getAppName() {
    var appName = document.getElementById('srvUpdateDispatcher').src.split('?a=');
    if (appName.length == 1) {
        return null;
    }
    appName = appName[1].split('&t')[0];
    return appName;
}

function appUpdateDispatcher(username, hashChangeListener) {
    var appName = getAppName();
    if (appName == null) {
        return;
    }

    if (!username) {
        return;
    }

    var pagePath = location.pathname + location.hash;

    webSocketSparrowService.bind('open', function (data) {
        var isAppUpdateDispatcherConnected = true;
        webSocketSparrowService.send('ws_onconnect', {
            groupName: appName,
            event: 'ws_onconnect',
            username: username,
            pagePath: pagePath,
        });
    });

    if (hashChangeListener == true) {
        window.onhashchange = function () {
            var pagePath = location.pathname + location.hash;
            webSocketSparrowService.send('ws_pagechanged', {
                groupName: appName,
                event: 'ws_pagechanged',
                username: username,
                pagePath: pagePath,
            });
        };
    }
}

function sendMessage(message, group_name, code) {
    webSocketSparrowService.send('ws_message', { code: code, message: message, groupName: group_name, event: 'ws_message' });
}

function getNotifInstance() {
    var notyf = new Notyf({
        position: {
            x: 'right',
            y: 'top',
        },
        types: [
            {
                type: 'info',
                background: 'blue',
                icon: false,
            },
        ],
    });
    return notyf;
}

function onUpdateFinish(data) {
    // var notyf = getNotifInstance();
    if (!notyf) {
        notyf = getNotifInstance();
    }

    var messsage =
        data.message +
        ' <br> Please <a style = "color:#FFF7AE"class="update-reload" href="javascript:window.location.reload();">click here </a> to reload the page to get the latest changes.';

    notyf.open({
        type: 'success',
        message: messsage,
        dismissible: true,
        duration: 0,
        icon: false,
    });
}
var webSocketSparrowService = null;
var isAppUpdateDispatcherConnected = false;
var notyf = null;

(function webSocketInit() {
    var appName = getAppName();
    if (appName == null) {
        return;
    }
    var websocketEndPoint = 'wss://demo.sparrowerp.com/websocket/';
    if (location.hostname === 'localhost' || location.hostname === '127.0.0.1' || location.hostname.indexOf('192.168.1') != -1) {
        websocketEndPoint = 'ws://' + location.hostname + ':8002/websocket/';
        // websocketEndPoint = 'ws://192.168.1.57:8006/websocket/';
    }
    websocketEndPoint += appName + '/';
    webSocketSparrowService = new CustomWebSocket(websocketEndPoint);

    webSocketSparrowService.bind('ws_message', function (data) {
        data = data['data'];
        if (data.groupName == appName) {
            if (data.code == 'updateStarts') {
                notyf = getNotifInstance();

                notyf.open({
                    type: 'success',
                    message: data.message,
                    dismissible: true,
                    duration: 0,
                    icon: false,
                });
            } else if (data.code == 'updateFinished') {
                if (notyf) {
                    notyf.dismissAll();
                }

                onUpdateFinish(data);
            }
        }
    });
})();

//
// Notifier Lib
//
// prettier-ignore
var Notyf=function(){"use strict";var e,o=function(){return(o=Object.assign||function(t){for(var i,e=1,n=arguments.length;e<n;e++)for(var o in i=arguments[e])Object.prototype.hasOwnProperty.call(i,o)&&(t[o]=i[o]);return t}).apply(this,arguments)},n=(t.prototype.on=function(t,i){var e=this.listeners[t]||[];this.listeners[t]=e.concat([i])},t.prototype.triggerEvent=function(t,i){var e=this;(this.listeners[t]||[]).forEach(function(t){return t({target:e,event:i})})},t);function t(t){this.options=t,this.listeners={}}(i=e=e||{})[i.Add=0]="Add",i[i.Remove=1]="Remove";var f,i,s=(a.prototype.push=function(t){this.notifications.push(t),this.updateFn(t,e.Add,this.notifications)},a.prototype.splice=function(t,i){i=this.notifications.splice(t,i)[0];return this.updateFn(i,e.Remove,this.notifications),i},a.prototype.indexOf=function(t){return this.notifications.indexOf(t)},a.prototype.onUpdate=function(t){this.updateFn=t},a);function a(){this.notifications=[]}(i=f=f||{}).Dismiss="dismiss";var r={types:[{type:"success",className:"notyf__toast--success",backgroundColor:"#3dc763",icon:{className:"notyf__icon--success",tagName:"i"}},{type:"error",className:"notyf__toast--error",backgroundColor:"#ed3d3d",icon:{className:"notyf__icon--error",tagName:"i"}}],duration:2e3,ripple:!0,position:{x:"right",y:"bottom"},dismissible:!(i.Click="click")},c=(p.prototype.on=function(t,i){var e;this.events=o(o({},this.events),((e={})[t]=i,e))},p.prototype.update=function(t,i){i===e.Add?this.addNotification(t):i===e.Remove&&this.removeNotification(t)},p.prototype.removeNotification=function(t){var i,e,n=this,t=this._popRenderedNotification(t);t&&((e=t.node).classList.add("notyf__toast--disappear"),e.addEventListener(this.animationEndEventName,i=function(t){t.target===e&&(e.removeEventListener(n.animationEndEventName,i),n.container.removeChild(e))}))},p.prototype.addNotification=function(t){var i=this._renderNotification(t);this.notifications.push({notification:t,node:i}),this._announce(t.options.message||"Notification")},p.prototype._renderNotification=function(t){var i=this._buildNotificationCard(t),e=t.options.className;return e&&(t=i.classList).add.apply(t,e.split(" ")),this.container.appendChild(i),i},p.prototype._popRenderedNotification=function(t){for(var i=-1,e=0;e<this.notifications.length&&i<0;e++)this.notifications[e].notification===t&&(i=e);if(-1!==i)return this.notifications.splice(i,1)[0]},p.prototype.getXPosition=function(t){return(null===(t=null==t?void 0:t.position)||void 0===t?void 0:t.x)||"right"},p.prototype.getYPosition=function(t){return(null===(t=null==t?void 0:t.position)||void 0===t?void 0:t.y)||"bottom"},p.prototype.adjustContainerAlignment=function(t){var i=this.X_POSITION_FLEX_MAP[this.getXPosition(t)],e=this.Y_POSITION_FLEX_MAP[this.getYPosition(t)],t=this.container.style;t.setProperty("justify-content",e),t.setProperty("align-items",i)},p.prototype._buildNotificationCard=function(n){var o=this,t=n.options,i=t.icon;this.adjustContainerAlignment(t);var e=this._createHTMLElement({tagName:"div",className:"notyf__toast"}),s=this._createHTMLElement({tagName:"div",className:"notyf__ripple"}),a=this._createHTMLElement({tagName:"div",className:"notyf__wrapper"}),r=this._createHTMLElement({tagName:"div",className:"notyf__message"});r.innerHTML=t.message||"";var c,p,d,l,u=t.background||t.backgroundColor;i&&(c=this._createHTMLElement({tagName:"div",className:"notyf__icon"}),("string"==typeof i||i instanceof String)&&(c.innerHTML=new String(i).valueOf()),"object"==typeof i&&(p=i.tagName,d=i.className,l=i.text,i=void 0===(i=i.color)?u:i,l=this._createHTMLElement({tagName:void 0===p?"i":p,className:d,text:l}),i&&(l.style.color=i),c.appendChild(l)),a.appendChild(c)),a.appendChild(r),e.appendChild(a),u&&(t.ripple?(s.style.background=u,e.appendChild(s)):e.style.background=u),t.dismissible&&(s=this._createHTMLElement({tagName:"div",className:"notyf__dismiss"}),u=this._createHTMLElement({tagName:"button",className:"notyf__dismiss-btn"}),s.appendChild(u),a.appendChild(s),e.classList.add("notyf__toast--dismissible"),u.addEventListener("click",function(t){var i,e;null!==(e=(i=o.events)[f.Dismiss])&&void 0!==e&&e.call(i,{target:n,event:t}),t.stopPropagation()})),e.addEventListener("click",function(t){var i,e;return null===(e=(i=o.events)[f.Click])||void 0===e?void 0:e.call(i,{target:n,event:t})});t="top"===this.getYPosition(t)?"upper":"lower";return e.classList.add("notyf__toast--"+t),e},p.prototype._createHTMLElement=function(t){var i=t.tagName,e=t.className,t=t.text,i=document.createElement(i);return e&&(i.className=e),i.textContent=t||null,i},p.prototype._createA11yContainer=function(){var t=this._createHTMLElement({tagName:"div",className:"notyf-announcer"});t.setAttribute("aria-atomic","true"),t.setAttribute("aria-live","polite"),t.style.border="0",t.style.clip="rect(0 0 0 0)",t.style.height="1px",t.style.margin="-1px",t.style.overflow="hidden",t.style.padding="0",t.style.position="absolute",t.style.width="1px",t.style.outline="0",document.body.appendChild(t),this.a11yContainer=t},p.prototype._announce=function(t){var i=this;this.a11yContainer.textContent="",setTimeout(function(){i.a11yContainer.textContent=t},100)},p.prototype._getAnimationEndEventName=function(){var t,i=document.createElement("_fake"),e={MozTransition:"animationend",OTransition:"oAnimationEnd",WebkitTransition:"webkitAnimationEnd",transition:"animationend"};for(t in e)if(void 0!==i.style[t])return e[t];return"animationend"},p);function p(){this.notifications=[],this.events={},this.X_POSITION_FLEX_MAP={left:"flex-start",center:"center",right:"flex-end"},this.Y_POSITION_FLEX_MAP={top:"flex-start",center:"center",bottom:"flex-end"};var t=document.createDocumentFragment(),i=this._createHTMLElement({tagName:"div",className:"notyf"});t.appendChild(i),document.body.appendChild(t),this.container=i,this.animationEndEventName=this._getAnimationEndEventName(),this._createA11yContainer()}function d(t){var e=this;this.dismiss=this._removeNotification,this.notifications=new s,this.view=new c;var i=this.registerTypes(t);this.options=o(o({},r),t),this.options.types=i,this.notifications.onUpdate(function(t,i){return e.view.update(t,i)}),this.view.on(f.Dismiss,function(t){var i=t.target,t=t.event;e._removeNotification(i),i.triggerEvent(f.Dismiss,t)}),this.view.on(f.Click,function(t){var i=t.target,t=t.event;return i.triggerEvent(f.Click,t)})}return d.prototype.error=function(t){t=this.normalizeOptions("error",t);return this.open(t)},d.prototype.success=function(t){t=this.normalizeOptions("success",t);return this.open(t)},d.prototype.open=function(i){var t=this.options.types.find(function(t){return t.type===i.type})||{},t=o(o({},t),i);this.assignProps(["ripple","position","dismissible"],t);t=new n(t);return this._pushNotification(t),t},d.prototype.dismissAll=function(){for(;this.notifications.splice(0,1););},d.prototype.assignProps=function(t,i){var e=this;t.forEach(function(t){i[t]=(null==i[t]?e.options:i)[t]})},d.prototype._pushNotification=function(t){var i=this;this.notifications.push(t);var e=(void 0!==t.options.duration?t:this).options.duration;e&&setTimeout(function(){return i._removeNotification(t)},e)},d.prototype._removeNotification=function(t){t=this.notifications.indexOf(t);-1!==t&&this.notifications.splice(t,1)},d.prototype.normalizeOptions=function(t,i){t={type:t};return"string"==typeof i?t.message=i:"object"==typeof i&&(t=o(o({},t),i)),t},d.prototype.registerTypes=function(t){var i=(t&&t.types||[]).slice();return r.types.map(function(e){var n=-1;i.forEach(function(t,i){t.type===e.type&&(n=i)});var t=-1!==n?i.splice(n,1)[0]:{};return o(o({},e),t)}).concat(i)},d}();

// prettier-ignore
(function resolveNotifierCSS() {
    // prettier-ignore
    document.head.insertAdjacentHTML(
        "beforeend",
        '<style>.notyf__wrapper{font-size:14px;};@-webkit-keyframes notyf-fadeinup{0%{opacity:0;transform:translateY(25%)}to{opacity:1;transform:translateY(0)}}@keyframes notyf-fadeinup{0%{opacity:0;transform:translateY(25%)}to{opacity:1;transform:translateY(0)}}@-webkit-keyframes notyf-fadeinleft{0%{opacity:0;transform:translateX(25%)}to{opacity:1;transform:translateX(0)}}@keyframes notyf-fadeinleft{0%{opacity:0;transform:translateX(25%)}to{opacity:1;transform:translateX(0)}}@-webkit-keyframes notyf-fadeoutright{0%{opacity:1;transform:translateX(0)}to{opacity:0;transform:translateX(25%)}}@keyframes notyf-fadeoutright{0%{opacity:1;transform:translateX(0)}to{opacity:0;transform:translateX(25%)}}@-webkit-keyframes notyf-fadeoutdown{0%{opacity:1;transform:translateY(0)}to{opacity:0;transform:translateY(25%)}}@keyframes notyf-fadeoutdown{0%{opacity:1;transform:translateY(0)}to{opacity:0;transform:translateY(25%)}}@-webkit-keyframes ripple{0%{transform:scale(0) translateY(-45%) translateX(13%)}to{transform:scale(1) translateY(-45%) translateX(13%)}}@keyframes ripple{0%{transform:scale(0) translateY(-45%) translateX(13%)}to{transform:scale(1) translateY(-45%) translateX(13%)}}.notyf{position:fixed;top:0;left:0;height:100%;width:100%;color:#fff;z-index:9999;display:flex;flex-direction:column;align-items:flex-end;justify-content:flex-end;pointer-events:none;box-sizing:border-box;padding:20px}.notyf__icon--error,.notyf__icon--success{height:21px;width:21px;background:#fff;border-radius:50%;display:block;margin:0 auto;position:relative}.notyf__icon--error:after,.notyf__icon--error:before{content:"";background:currentColor;display:block;position:absolute;width:3px;border-radius:3px;left:9px;height:12px;top:5px}.notyf__icon--error:after{transform:rotate(-45deg)}.notyf__icon--error:before{transform:rotate(45deg)}.notyf__icon--success:after,.notyf__icon--success:before{content:"";background:currentColor;display:block;position:absolute;width:3px;border-radius:3px}.notyf__icon--success:after{height:6px;transform:rotate(-45deg);top:9px;left:6px}.notyf__icon--success:before{height:11px;transform:rotate(45deg);top:5px;left:10px}.notyf__toast{display:block;overflow:hidden;pointer-events:auto;-webkit-animation:notyf-fadeinup .3s ease-in forwards;animation:notyf-fadeinup .3s ease-in forwards;box-shadow:0 3px 7px 0 rgba(0,0,0,.25);position:relative;padding:0 15px;border-radius:2px;max-width:300px;transform:translateY(25%);box-sizing:border-box;flex-shrink:0}.notyf__toast--disappear{transform:translateY(0);-webkit-animation:notyf-fadeoutdown .3s forwards;animation:notyf-fadeoutdown .3s forwards;-webkit-animation-delay:.25s;animation-delay:.25s}.notyf__toast--disappear .notyf__icon,.notyf__toast--disappear .notyf__message{-webkit-animation:notyf-fadeoutdown .3s forwards;animation:notyf-fadeoutdown .3s forwards;opacity:1;transform:translateY(0)}.notyf__toast--disappear .notyf__dismiss{-webkit-animation:notyf-fadeoutright .3s forwards;animation:notyf-fadeoutright .3s forwards;opacity:1;transform:translateX(0)}.notyf__toast--disappear .notyf__message{-webkit-animation-delay:.05s;animation-delay:.05s}.notyf__toast--upper{margin-bottom:20px}.notyf__toast--lower{margin-top:20px}.notyf__toast--dismissible .notyf__wrapper{padding-right:30px}.notyf__ripple{height:400px;width:400px;position:absolute;transform-origin:bottom right;right:0;top:0;border-radius:50%;transform:scale(0) translateY(-51%) translateX(13%);z-index:5;-webkit-animation:ripple .4s ease-out forwards;animation:ripple .4s ease-out forwards}.notyf__wrapper{display:flex;align-items:center;padding-top:17px;padding-bottom:17px;padding-right:15px;border-radius:3px;position:relative;z-index:10}.notyf__icon{width:22px;text-align:center;font-size:1.3em;opacity:0;-webkit-animation:notyf-fadeinup .3s forwards;animation:notyf-fadeinup .3s forwards;-webkit-animation-delay:.3s;animation-delay:.3s;margin-right:13px}.notyf__dismiss{position:absolute;top:0;right:0;height:100%;width:26px;margin-right:-15px;-webkit-animation:notyf-fadeinleft .3s forwards;animation:notyf-fadeinleft .3s forwards;-webkit-animation-delay:.35s;animation-delay:.35s;opacity:0}.notyf__dismiss-btn{background-color:rgba(0,0,0,.25);border:none;cursor:pointer;transition:opacity .2s ease,background-color .2s ease;outline:none;opacity:.35;height:100%;width:100%}.notyf__dismiss-btn:after,.notyf__dismiss-btn:before{content:"";background:#fff;height:12px;width:2px;border-radius:3px;position:absolute;left:calc(50% - 1px);top:calc(50% - 5px)}.notyf__dismiss-btn:after{transform:rotate(-45deg)}.notyf__dismiss-btn:before{transform:rotate(45deg)}.notyf__dismiss-btn:hover{opacity:.7;background-color:rgba(0,0,0,.15)}.notyf__dismiss-btn:active{opacity:.8}.notyf__message{vertical-align:middle;position:relative;opacity:0;-webkit-animation:notyf-fadeinup .3s forwards;animation:notyf-fadeinup .3s forwards;-webkit-animation-delay:.25s;animation-delay:.25s;line-height:1.5em}@media only screen and (max-width:480px){.notyf{padding:0}.notyf__ripple{height:600px;width:600px;-webkit-animation-duration:.5s;animation-duration:.5s}.notyf__toast{max-width:none;border-radius:0;box-shadow:0 -2px 7px 0 rgba(0,0,0,.13);width:100%}.notyf__dismiss{width:56px}}</style>'
    );
})();
