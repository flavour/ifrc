<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <!-- **********************************************************************
         survey-Response - CSV Import Stylesheet

         2011-Jun-28 / Graeme Foster <graeme AT acm DOT org>

         - Specialist transform file for the 24H rapid assessment form

         - use for import to survey/question_response resource

         - example raw URL usage:
           Let URLpath be the URL to Sahana Eden appliation
           Let Resource be survey/complete/create
           Let Type be s3csv
           Let CSVPath be the path on the server to the CSV file to be imported
           Let XSLPath be the path on the server to the XSL transform file
           Then in the browser type:

           URLpath/Resource.Type?filename=CSVPath&transform=XSLPath

           You can add a third argument &ignore_errors

         CSV fields:
         Template..............survey_template.name
         Series................survey_series.name
         Organisation..........org.organisation.name
         <question code>.......survey_response.question_list

    *********************************************************************** -->
    <xsl:output method="xml"/>
    <xsl:include href="../../xml/commons.xsl"/>

    <xsl:key name="survey_template"
             match="row"
             use="col[@field='Template']"/>
    <xsl:key name="survey_series"
             match="row"
             use="col[@field='Series']"/>

    <!-- ****************************************************************** -->

    <xsl:template match="/">
        <s3xml>
            <xsl:apply-templates select="table/row"/>
            <xsl:for-each select="//row[generate-id(.)=
                                        generate-id(key('survey_template',
                                                        col[@field='Template'])[1])]">
                <xsl:call-template name="Template"/>
            </xsl:for-each>
            <xsl:for-each select="//row[generate-id(.)=
                                        generate-id(key('survey_series',
                                                        col[@field='Series'])[1])]">
                <xsl:call-template name="Series"/>
            </xsl:for-each>
        </s3xml>
    </xsl:template>

    <!-- ****************************************************************** -->
    <xsl:template match="row">

        <resource name="survey_complete">
            <data field="answer_list">
                <xsl:for-each select="col">
                    <xsl:choose>
                        <xsl:when test="@field = 'Template'">
                            <xsl:variable name="Template" select="col[@field='Template']"/>
                        </xsl:when>
                        <xsl:when test="@field = 'Series'">
                            <xsl:variable name="Series" select="col[@field='Series']"/>
                        </xsl:when>
                        <xsl:when test="@field = 'Organisation'">
                            <xsl:variable name="Series" select="col[@field='Series']"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:if test=".!=''">
                                <xsl:value-of select="concat('&quot;', @field, '&quot;,&quot;',.,'&quot;',$newline)"/>
                            </xsl:if>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:for-each>
            </data>
            <!-- Link to Series -->
            <reference field="series_id" resource="survey_series">
                <xsl:attribute name="tuid">
                    <xsl:value-of select="col[@field='Series']"/>
                </xsl:attribute>
            </reference>
        </resource>

    </xsl:template>

    <!-- ****************************************************************** -->
    <xsl:template name="Template">
        <xsl:variable name="template" select="col[@field='Template']/text()"/>

        <!-- Create the survey template -->
        <resource name="survey_template">
            <xsl:attribute name="tuid">
                <xsl:value-of select="$template"/>
            </xsl:attribute>
            <data field="name"><xsl:value-of select="$template"/></data>
            <data field="description"><xsl:value-of select="col[@field='Template Description']"/></data>
            <data field="status"><xsl:value-of select="2"/></data>
        </resource>
    </xsl:template>

    <!-- ****************************************************************** -->

    <xsl:template name="Series">
        <xsl:variable name="series" select="col[@field='Series']/text()"/>
        <xsl:variable name="OrgName" select="col[@field='Organisation']/text()"/>

        <!-- Create the survey series -->
        <resource name="survey_series">
            <xsl:attribute name="tuid">
                <xsl:value-of select="$series"/>
            </xsl:attribute>
            <data field="name"><xsl:value-of select="$series"/></data>
            <!-- Link to Template -->
            <reference field="template_id" resource="survey_template">
                <xsl:attribute name="tuid">
                    <xsl:value-of select="col[@field='Template']"/>
                </xsl:attribute>
            </reference>
            <!-- Link to Organisation -->
            <reference field="organisation_id" resource="org_organisation">
                <xsl:attribute name="tuid">
                    <xsl:value-of select="$OrgName"/>
                </xsl:attribute>
            </reference>
        </resource>
    </xsl:template>
    <!-- ****************************************************************** -->

</xsl:stylesheet>
