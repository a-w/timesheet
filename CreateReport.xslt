<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="xml" encoding="UTF-8" indent="yes"/>
	<xsl:template match="timesheet/projects">
<html>
	<head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
		<title><xsl:value-of select="/timesheet/summary/@title"/> [<xsl:value-of select="/timesheet/summary/@start"/> - <xsl:value-of select="/timesheet/summary/@end"/>]</title>
<style>
@media print {
	table {
		width: 95%;
	 }
	input[id^="sum"]
	{
		border:0px;
	}
}
body
{
font-family: Arial;
}

table
{
padding: 2pt;
}

tr
{
vertical-align:top;
border: 1px solid silver;
}

.comment 
{
	color: silver;
	font-style:italic;
}

th
{
text-align:left;
}

thead th
{
border-bottom: 1px solid gray;
}
tfoot th
{
border-top: 1px solid gray;
}

tr
{

}

td.details {
font-size: 10pt;
}

div.p
{
page-break-after:always;
background: top right no-repeat 
}

.nobr  { white-space:nowrap; font-size: 75%; }

tr.nobr 
{
vertical-align: bottom;
}

thead &lt; tr 
{
border-bottom: 1px solid silver;
}

input
{
border: 1px silver solid;
text-align:right;
}
</style>		
	</head>
	<body>
<!-- details for every project -->
<xsl:apply-templates select="/timesheet/projects/project" mode="projects-details"/>

</body></html>
</xsl:template>

<xsl:template match="timesheet/projects/project" mode="projects-details">
<xsl:variable name="projectKey"><xsl:value-of select="@key"/></xsl:variable>
<div class="p"><xsl:attribute name="id">project_<xsl:value-of select="@key"/></xsl:attribute>
<h1><xsl:value-of select="@title"/></h1>
	<xsl:if test="properties/p/@key='AP'">
		<u>Ansprechpartner:</u>&#160;&#160;<xsl:value-of select="properties/p[@key='AP']/@value"/>&#160;&#160;
	</xsl:if>
	<xsl:if test="properties/p/@key='ORDER'">
		<u>Bestellung:</u>
		&#160;&#160;<xsl:value-of select="properties/p[@key='ORDER']/@value"/>
	</xsl:if>
<p/>
<table><xsl:attribute name="id">tblAp<xsl:value-of select="$projectKey"/></xsl:attribute>
<thead>
	<tr>
		<th>Von</th>
		<th>Bis</th>
		<th style="text-align: right;">Dauer [h]</th>
		<th>Beschreibung</th>
	</tr>
</thead>
	<tbody>
		<tr>
<xsl:apply-templates select="/timesheet/entries/entry[@key=$projectKey]" mode="inTable"/>
		</tr>
	</tbody>
	<tfoot>
		<tr>
			<th colspan="2" style="text-align:right">Summe [h]</th>
			<th style="text-align:right;" name="sum"><xsl:attribute name="id"><xsl:value-of select="$projectKey"/>_sum</xsl:attribute><xsl:value-of select="format-number((sum(/timesheet/entries/entry[@key=$projectKey]/@minutes) div 60),'0.00')"/></th>
			<th style="text-align:right;" colspan="2">&#160;</th>
		</tr>
	</tfoot>
</table>
</div>
</xsl:template>

<xsl:template match="timesheet/entries/entry" mode="inTable">
<tr>
	<td class="nobr"><xsl:value-of select="@from"/></td>
	<td class="nobr"><xsl:value-of select="@to"/></td>
	<td align="right"><xsl:value-of select="format-number((@minutes div 60), '0.00')"/></td>
	<td><xsl:value-of select="@subject"/></td>
</tr>
<xsl:if test="details">
<tr valign="top">
	<td colspan="3"></td>
	<td class="details"><xsl:value-of select="details"/></td>
</tr>
</xsl:if>
</xsl:template>

<!-- default handler for elements containing text -->
<xsl:template match="text()"/>

</xsl:stylesheet>
