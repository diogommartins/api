/**
 * Created by diogomartins on 9/8/15.
 */

WebSocketListenerHelper = function(responseTable, errorTable) {
    this.responseTable = responseTable;
    this.errorTable = errorTable;
    var tableHeaders = $(this.responseTable.selector + " > thead > tr > th");
    var colNames = [];

    tableHeaders.each(function(i){
        colNames.push(tableHeaders[i].textContent);
    });
    this.colNames = colNames;
};

WebSocketListenerHelper.prototype = {
    _parseMessage: function(data){
        var bgcolor = (data['error']? "#CCCC99" : "#99CCCC");   // todo Gambiarra para cor... não deve ser estilizado dessa forma
        var row = $("<tr bgcolor="+ bgcolor +"></tr>");
        for (var i in this.colNames)
            row.append($("<td>").text(data[this.colNames[i]]));
        return row;
    },
    appendBottom: function(msgEvent){
        var data = JSON.parse(msgEvent.data);
        var row = this._parseMessage(data);
        if (data['error'])
            this.errorTable.append(row);
        else
            this.responseTable.append(row);
    },
    appendTop: function(msgEvent){
        var data = JSON.parse(msgEvent.data);
        var row = this._parseMessage(data);
        if (data['error'])
            $(row).prependTo(this.errorTable.selector + " > tbody");
        else
            $(row).prependTo(this.responseTable.selector + " > tbody");
    }
};

var WebSocketListenerHelper = WebSocketListenerHelper || {};

$(document).ready(function(){
    var wsHelper = new WebSocketListenerHelper($("table#ws_result"), $("table#ws_error"));

    if(!$.web2py.web2py_websocket('ws://'+ ws_host +':'+ ws_port +'/realtime/'+ ws_group, function(e){wsHelper.appendTop(e)}))

        alert("html5 websocket not supported by your browser, try Google Chrome");
});