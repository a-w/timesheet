<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="html" version="5.0" encoding="UTF-8" indent="yes"/>

    <xsl:template match="timesheet">
        <!-- This form allows only one project. Select first one if there are several -->
        <xsl:variable name="project" select="/timesheet/projects/project[1]/@key"/>
<html lang="de">
<head>
<meta http-equiv="content-type" content="text/html;charset=utf-8"/>
<title><xsl:value-of select="/timesheet/summary/@title"/> [<xsl:value-of select="/timesheet/summary/@start"/> - <xsl:value-of select="/timesheet/summary/@end"/>]</title>
<script>
var Data = {
    Attributes: {
    	<xsl:apply-templates mode="attributes" select="/timesheet/projects/project[@key=$project]/properties/p"/>
    },
    Entries: [
    	<xsl:apply-templates mode="entries" select="/timesheet/entries/entry[@key=$project]"/>
    ]
};

</script>
    <script src="http://code.jquery.com/jquery-1.9.1.min.js"></script>
<style>
body
{
    font-family: Lucida Sans;
    font-size: 9.5pt;
}
h1
{
    font-family: Arial;
    font-size: 22px;
}
div
{
    position: absolute;
    left: 2.5cm;
}
textarea#ETBS_
{
    width: 800px;
    height: 300px;
    white-space: nowrap;
    overflow:    scroll;
    overflow-y:  scroll;
    overflow-x:  scroll;    
}
div#ETBS
{
    display: none;
    z-index: 255;
}
div#header
{
    background-image: url(data:image/jpg;base64,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);
    background-size: 100%;
    top: 0cm;
    width: 5.309cm;
    height: 0.635cm;
    background-repeat: no-repeat;
}
div#address
{
    font-size: 6.5pt;
    top: 5cm;
}
div#content
{
    width: 17cm;
    height: 16.5cm;
    top: 0.8cm;
}
div#content
{
    width: 19cm;
}
div#content div
{
    left: 0cm;
}
div#date
{
    top: 1cm;
    width: 19cm;
    text-align:right;
}
td#date_val
{
    color: red;
}
input.entry_text
{
    border: 0px;
    font-family: Lucida Sans;
    font-size: 9.5pt;
    width: 13cm;
}
input.entry_hours
{
    border: 0px;
    font-family: Lucida Sans;
    font-size: 9.5pt;
    width: 1.5cm;
    text-align:right;
}
div#table
{
    top: 5.7cm;
    height: 16.5cm;
    width: 19cm;
    border: 0px solid silver;
}
table
{
    width: 19cm;
}
thead td
{
    background-color: #EFEFEF;
    font-weight: bold;
}
table#data td
{
    border-top: 1px solid silver;
    font-size: 9.5pt;
}
table#titletable
{
  width:400px;
  font-family: Arial;
  font-size: 18px;
}

table#titletable td:last-child
{
    background-color: #BFBFBF;
    text-align: center;
    width: 50%;
}
div#footer
{
    top: 32cm;
    width: 19cm;
}
div#footer td
{
    font-size: 6pt;
}
</style>
<script>

var fillInfo = function() {
    // get the day of the first entry
    var ent = Data.Entries[0];
    var s = ent.From.split(" ");
    var day = s[0];
    var s = day.split(".");

    var date = $('#date_val');
    date.text(s[1] + " " + s[2]);
    
    var greeting = $('#greeting');
    greeting.text(greeting.text().replace('$WHO',Data.Attributes["AP"]));
};

var log = function(msg) {
    if (window.console)
        window.console.log(msg);
}

var fillData = function()
{
    var tbl=$('#data > tbody');
    // create a struct with sums
    var sumdata = [];
    // iterate all entries
    for (var i in Data.Entries) {
        // get the entries day
        var ent = Data.Entries[i];
        var s = ent.From.split(" ");
        var day = s[0];
        // create a new entry if not exists
        if (sumdata[day] === undefined)
        {
            sumdata[day] = 
            {
                Text: "",
                Duration: 0
            };
        }
        // add text and minutes
        sumdata[day].Text += ( sumdata[day].Text=="" ? ent.Text : ", " + ent.Text );
        sumdata[day].Duration += parseInt(ent.Duration);
        //
    }
    
    // iterate summed data
    for (var day in sumdata) {
        var ent = sumdata[day];
        var row = tbl.append("<tr/>");
        var hours = ent.Duration / 60;
        appendInputCell(row, day, ent.Text, formatHours(hours) );
    }
    
    // sum
    calcSums();
    
    // register for resum on change
    $('input.entry_hours').change(calcSums);
};

var calcSums = function()
{
    var sumHours = 0.0;
    // acquire all hours
    var entries=$('input.entry_hours');
    // iterate
    for (var i=0; i &lt; entries.length; ++i)
    {
        var ent = entries[i];
        var v = ""+ent.value;
        var fv = parseFloat(v.replace(',', '.'));
        if (isNaN(fv))
        {
            $(ent).val('0,00');
            continue;
        }
        $(ent).val(formatHours(fv));
        sumHours += fv;
    }
    
    // update total hours
    $('#h_total').text(formatHours(sumHours) + " h");
};

var formatHours = function (v)
{
    var s = v.toFixed(2);
    return s.replace('.', ',');
};
<xsl:text><![CDATA[
var appendInputCell = function(where, day, text, hours) {
    var td_s = $('<td>'+day+'</td><td><input id="text_'+day+'" value="'+text+'" class="entry_text"/></td><td align="right"><input id="hours_'+day+'" value="'+hours+'" class="entry_hours"/> h</td>');
    where.append(td_s);
}]]>
</xsl:text>

$(document).ready(function() {
    fillInfo();
    fillData();
});

Date.prototype.getWeek = function () {
    // Create a copy of this date object
    var target  = new Date(this.valueOf());
    
    // ISO week date weeks start on monday
    // so correct the day number
    var dayNr   = (this.getDay() + 6) % 7;
    
    // ISO 8601 states that week 1 is the week
    // with the first thursday of that year.
    // Set the target date to the thursday in the target week
    target.setDate(target.getDate() - dayNr + 3);
    
    // Store the millisecond value of the target date
    var firstThursday = target.valueOf();
    
    // Set the target to the first thursday of the year
    // First set the target to january first
    target.setMonth(0, 1);
    // Not a thursday? Correct the date to the next thursday
    if (target.getDay() != 4) {
    target.setMonth(0, 1 + ((4 - target.getDay()) + 7) % 7);
    }
    
    // The weeknumber is the number of weeks between the 
    // first thursday of the year and the thursday in the target week
    return 1 + Math.ceil((firstThursday - target) / 604800000); // 604800000 = 7 * 24 * 3600 * 1000
};

$(document).dblclick(function() {
    var weekday=new Array(7);
    weekday[0]="Sonntag.....";
    weekday[1]="Montag......";
    weekday[2]="Dienstag....";
    weekday[3]="Mittwoch....";
    weekday[4]="Donnerstag..";
    weekday[5]="Freitag.....";
    weekday[6]="Samstag.....";

    var HOURS_PER_CAT = {};
    var HOURS_PER_DAY = new Array(0,0,0,0,0,0,0);
    var commands = "";
    var ldt = 1;
    for (var idx in Data.Entries) {
        var entry = Data.Entries[idx];

        // date
        var from = entry['From'];
        var d = from.split(' ');
        var date = d[0].split('.');
        // take the week day 
        var wd = (new Date(parseInt(date[2]), parseInt(date[1]) - 1, parseInt(date[0])));
        var wwd = wd.getDay() + 1;
        if (wwd >= ldt)
        {
            ldt = wwd;
        }
        // if we are at the end of a week, add an empty line
        else
        {
            ldt = 0;
        }
        var fromday = date[2] + '-' + date[1] + '-' + date[0];
        // hours
        var hh = (parseInt(entry['Duration']) / 60);
        HOURS_PER_DAY[wd.getDay()] += hh;       
        var hours = '"' + ("" + hh).replace(".",",") + '"';
        // entry        
        var txt = entry['Text'];
        var index = txt.indexOf(':');
        var cat = '"' + txt.substr(0, index) + '"';
        var comment = '"' +  $.trim(txt.substr(index + 1)) + '"';
        //
        if (HOURS_PER_CAT[cat] == undefined)
            HOURS_PER_CAT[cat] = 0;
        HOURS_PER_CAT[cat] += hh;        
        //
    }
    
    // now dump the days
    commands += "\n\nHours by day \n";
    for(var i=0;i&lt;7;++i)
    {
        commands += weekday[i] + "  " + HOURS_PER_DAY[i] + "\n";
    }
    
    // now dump the categories
    commands += "\n\nHours by category \n";
    for(var i in HOURS_PER_CAT)
    {
        commands += i + "  " + HOURS_PER_CAT[i] + "\n";
    }

    $('#ETBS').toggle();
    var etbs = $('#ETBS_'); 
    etbs.text(commands);
    etbs.select();
});
</script>
</head>
<body>
<div id="ETBS">
    <fieldset>
        <legend>ETBS Einträge</legend>
        <textarea id="ETBS_"></textarea>
    </fieldset>
</div>
<div id="header"></div>

<div id="address">Hays AG, Administration Services, Postfach 10 01 23, 68001 Mannheim<br/>Tel. 0621-1788-0<p/></div>

<div id="content">
<div id="title" style="font-weight: bold">
<h1>Projektbericht</h1>
<table cellspacing="0" cellpadding="3" id="titletable">
<tbody>
<tr><td>Monat</td><td id="date_val"></td></tr>
<tr><td>Projektnummer</td><td><xsl:value-of select="/timesheet/projects/project/properties/p[@key='ORDER']/@value"/></td></tr>
<tr><td>Name</td><td><xsl:value-of select="/timesheet/projects/project/properties/p[@key='NAME']/@value"/>
</td></tr>
</tbody>
</table>

</div>

<div id="table">
<table cellspacing="0" cellpadding="3" id="data">
<thead>
<tr><td style="width: 2.7cm;">Datum</td><td style="width: 13cm;">Tätigkeit</td><td align="right">Stunden</td></tr>
</thead>
<tbody/>
<tfoot>
<tr><td colspan="2" align="right">Total</td><td align="right"><span id="h_total">0,00 h</span></td></tr>
</tfoot>
</table>
<p/>
Bestätigt / Datum:<p/>&#160;<p/>
<span id="greeting">
Unterschrift Projektleiter ($WHO):
</span>
</div>
</div>
</body>
</html>
	</xsl:template>

	<xsl:template match="entry" mode="entries">
		{From: "<xsl:value-of select="@from"/>", To: "<xsl:value-of select="@to"/>", Duration: "<xsl:value-of select="@minutes"/>", Text: "<xsl:value-of select="@subject"/>" },
	</xsl:template>
	<xsl:template match="p" mode="attributes">
		<xsl:value-of select="@key"/>: "<xsl:value-of select="@value"/>",
	</xsl:template>
	
    <!-- default handler for elements containing text -->
    <xsl:template match="text()"/>

</xsl:stylesheet>
