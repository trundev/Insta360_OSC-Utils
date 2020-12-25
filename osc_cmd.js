const OSC_HOST = "";//"http://192.168.42.1";
const INFO_URL = "/osc/info";
const STATE_URL = "/osc/state";
const CHECKFORUPDATE_URL = "/osc/checkForUpdates";
const COMMAND_EXECUTE_URL = "/osc/commands/execute";
const COMMAND_STATUS_URL = "/osc/commands/status";
COMMAND_POLLING_DELAY = 1000

function html_req(method, url, data, onready, ctx) {
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function() {
    if (this.readyState == 4) {
      onready(ctx, this.status, this.response ? JSON.parse(this.response) : null)
    }
  };
  xmlHttp.open(method, url, true);
  xmlHttp.setRequestHeader("Accept", "application/json");
  xmlHttp.setRequestHeader("X-XSRF-Protected", 1);
  xmlHttp.send(data);
}
function get_req(url, onready, ctx) {
  return html_req("GET", url, null, onready, ctx);
}
function post_req(url, data, onready, ctx) {
  return html_req("POST", url, JSON.stringify(data), onready, ctx);
}
function exec_ready(ctx, st, resp) {
  if (resp && resp.state == "inProgress") {
    setTimeout(function() {
        post_req(COMMAND_STATUS_URL, {id: resp.id}, exec_ready, ctx);
      }, COMMAND_POLLING_DELAY);
  } else {
    ctx[0](ctx[1], st, resp);
  }
}
function run_cmd(cmd_name, params, onready, ctx) {
  onready(ctx,null,null)
  data = {name: cmd_name};
  if (params !== null)
    data.parameters = params;
  return post_req(COMMAND_EXECUTE_URL, data, exec_ready, [onready, ctx]);
}

function render_table(data) {
  var res = "<table><tr><th>Name</th><th>Value</th></tr>";
  for (var el in data) {
    res += "<tr><td>" + el + "</td>";
    val = data[el]
    if (val instanceof Array) {
      res += "<td>" + val.join("<br>") + "</td>"
    } else if (typeof val === 'object') {
      res += "<td class='object'>" + render_table(val) + "</td>"
    } else {
      res += "<td>" + val + "</td>"
    }
    res += "</tr>";
  }
  return res + "</table>";
}

function res_ready(el, st, resp) {
  if (resp === null) {
    if (st === null)
      el.innerHTML = "<i>&lt;retrieving...&gt;<i>";
    else
      el.innerText = "status:" + st;
    return st;
  }
  el.innerHTML = render_table(resp.results === undefined ? resp : resp.results);
}
